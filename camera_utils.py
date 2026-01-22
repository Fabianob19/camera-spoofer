"""
Camera Spoofer - Utilitários de Câmera
Funções para detectar câmeras e modificar seus nomes no registro do Windows.
"""

import winreg
import json
import os
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from real_cameras import is_virtual_camera, get_suggested_name


# Arquivo para backup dos nomes originais
BACKUP_FILE = "camera_backup.json"


def get_backup_path() -> Path:
    """Retorna o caminho do arquivo de backup."""
    # Salva no mesmo diretório do executável
    if hasattr(os, 'frozen'):
        base_dir = Path(os.path.dirname(os.sys.executable))
    else:
        base_dir = Path(__file__).parent
    return base_dir / BACKUP_FILE


def get_cameras_via_directshow() -> List[Dict]:
    """
    Obtém lista de câmeras usando DirectShow via pygrabber.
    Detecta se a câmera é virtual baseado em:
    1. Nome contém padrões de câmera virtual (OBS, NDI, vMix, etc.)
    2. Ou nome NÃO é de uma marca de hardware conhecida
    
    Returns:
        Lista de dicionários com informações das câmeras
    """
    cameras = []
    
    # Marcas de câmeras físicas conhecidas
    KNOWN_BRANDS = [
        'logitech', 'microsoft', 'dell', 'hp', 'lenovo', 'asus', 'razer',
        'creative', 'acer', 'genius', 'trust', 'elgato', 'anker', 'obsbot',
        'insta360', 'avermedia', 'a4tech', 'canyon', 'papalook', 'webcam',
        'facecam', 'lifecam', 'brio', 'kiyo', 'integrated', 'built-in', 'usb'
    ]
    
    try:
        import pythoncom
        pythoncom.CoInitialize()
        
        try:
            from pygrabber.dshow_graph import FilterGraph
            
            graph = FilterGraph()
            device_names = graph.get_input_devices()
            
            for idx, name in enumerate(device_names):
                name_lower = name.lower()
                
                # Primeiro verifica se tem padrão de câmera virtual
                if is_virtual_camera(name):
                    is_virtual = True
                # Senão verifica se é de uma marca conhecida
                elif any(brand in name_lower for brand in KNOWN_BRANDS):
                    is_virtual = False
                else:
                    # Se não reconhecemos, assume que é virtual (mais seguro)
                    is_virtual = True
                
                cameras.append({
                    'name': name,
                    'device_id': str(idx),
                    'pnp_device_id': str(idx),
                    'status': 'OK',
                    'is_virtual': is_virtual,
                    'manufacturer': 'Unknown',
                })
        finally:
            pythoncom.CoUninitialize()
            
    except ImportError:
        print("pygrabber não instalado. Instale com: pip install pygrabber")
    except Exception as e:
        print(f"Erro ao enumerar dispositivos: {e}")
    
    return cameras


def get_cameras_via_registry() -> List[Dict]:
    """
    Obtém lista de câmeras diretamente do registro do Windows.
    Método alternativo - busca em múltiplos locais do registro.
    
    Returns:
        Lista de dicionários com informações das câmeras
    """
    cameras = []
    
    # Busca câmeras no registro de dispositivos de vídeo (Device Classes)
    video_device_path = r"SYSTEM\CurrentControlSet\Control\DeviceClasses\{e5323777-f976-4f5b-9b55-b94699c46e44}"
    
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, video_device_path) as key:
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey_path = f"{video_device_path}\\{subkey_name}"
                    
                    # Tenta obter o FriendlyName
                    try:
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{subkey_path}\\#\\Device Parameters") as param_key:
                            friendly_name, _ = winreg.QueryValueEx(param_key, "FriendlyName")
                            
                            cameras.append({
                                'name': friendly_name,
                                'device_id': subkey_name,
                                'pnp_device_id': subkey_name,
                                'status': 'OK',
                                'is_virtual': is_virtual_camera(friendly_name),
                                'manufacturer': 'Unknown',
                                'registry_path': subkey_path,
                            })
                    except (FileNotFoundError, OSError):
                        pass
                    
                    i += 1
                except OSError:
                    break
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Erro ao buscar câmeras no registro: {e}")
    
    return cameras


def find_camera_registry_entries(camera_name: str) -> List[Tuple[str, str, str]]:
    """
    Encontra todas as entradas do registro que contêm o nome da câmera.
    
    Args:
        camera_name: Nome da câmera para buscar
        
    Returns:
        Lista de tuplas (chave, valor, caminho) com as entradas encontradas
    """
    entries = []
    
    # Busca em vários locais do registro
    search_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\DeviceClasses"),
        (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Enum"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes\CLSID"),
    ]
    
    def search_key(hkey, path, depth=0):
        """Busca recursivamente no registro."""
        if depth > 6:  # Limita profundidade
            return
        
        try:
            with winreg.OpenKey(hkey, path, 0, winreg.KEY_READ) as key:
                # Verifica valores
                try:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            if isinstance(value, str) and camera_name.lower() in value.lower():
                                entries.append((path, name, value))
                            i += 1
                        except OSError:
                            break
                except Exception:
                    pass
                
                # Busca subchaves
                try:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            search_key(hkey, f"{path}\\{subkey_name}", depth + 1)
                            i += 1
                        except OSError:
                            break
                except Exception:
                    pass
        except (FileNotFoundError, PermissionError):
            pass
    
    for hkey, path in search_paths:
        search_key(hkey, path)
    
    return entries


def get_all_cameras() -> List[Dict]:
    """
    Obtém lista de todas as câmeras do sistema.
    Usa DirectShow (COM) para detectar câmeras por DevicePath.
    
    Returns:
        Lista de dicionários com informações das câmeras
    """
    cameras = []
    
    # Usa DirectShow COM para detecção precisa de virtual vs real
    cameras = get_cameras_via_directshow()
    
    # Se não encontrou nada, tenta via registro
    if not cameras:
        cameras = get_cameras_via_registry()
    
    # Remove duplicatas baseado no nome
    seen_names = set()
    unique_cameras = []
    for cam in cameras:
        if cam['name'] not in seen_names:
            seen_names.add(cam['name'])
            unique_cameras.append(cam)
    
    return unique_cameras


def save_backup(camera_name: str, registry_entries: List[Tuple[str, str, str]]):
    """
    Salva backup do nome original da câmera.
    
    Args:
        camera_name: Nome original da câmera
        registry_entries: Entradas do registro que serão modificadas
    """
    backup_path = get_backup_path()
    
    # Carrega backup existente ou cria novo
    if backup_path.exists():
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
    else:
        backup_data = {}
    
    # Adiciona nova entrada
    backup_data[camera_name] = {
        'original_name': camera_name,
        'registry_entries': [
            {'path': path, 'value_name': name, 'original_value': value}
            for path, name, value in registry_entries
        ]
    }
    
    # Salva
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)


def load_backup() -> Dict:
    """
    Carrega backup dos nomes originais.
    
    Returns:
        Dicionário com dados de backup
    """
    backup_path = get_backup_path()
    
    if backup_path.exists():
        with open(backup_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return {}


def rename_camera_in_registry(old_name: str, new_name: str) -> Tuple[bool, str]:
    """
    Renomeia uma câmera no registro do Windows.
    
    Args:
        old_name: Nome atual da câmera
        new_name: Novo nome para a câmera
        
    Returns:
        Tupla (sucesso, mensagem)
    """
    try:
        # Encontra todas as entradas com o nome antigo
        entries = find_camera_registry_entries(old_name)
        
        if not entries:
            return False, f"Não foi possível encontrar '{old_name}' no registro."
        
        # Salva backup
        save_backup(old_name, entries)
        
        # Modifica cada entrada
        modified_count = 0
        for path, value_name, old_value in entries:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, 
                                   winreg.KEY_SET_VALUE | winreg.KEY_READ) as key:
                    new_value = old_value.replace(old_name, new_name)
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, new_value)
                    modified_count += 1
            except PermissionError:
                continue
            except Exception as e:
                print(f"Erro ao modificar {path}: {e}")
        
        if modified_count > 0:
            return True, f"Câmera renomeada com sucesso! ({modified_count} entradas modificadas)"
        else:
            return False, "Não foi possível modificar nenhuma entrada. Execute como administrador."
            
    except Exception as e:
        return False, f"Erro ao renomear câmera: {str(e)}"


def restore_camera_name(camera_name: str) -> Tuple[bool, str]:
    """
    Restaura o nome original de uma câmera a partir do backup.
    
    Args:
        camera_name: Nome da câmera para restaurar (nome original)
        
    Returns:
        Tupla (sucesso, mensagem)
    """
    try:
        backup_data = load_backup()
        
        if camera_name not in backup_data:
            return False, f"Backup não encontrado para '{camera_name}'"
        
        entry_data = backup_data[camera_name]
        restored_count = 0
        
        for reg_entry in entry_data['registry_entries']:
            try:
                path = reg_entry['path']
                value_name = reg_entry['value_name']
                original_value = reg_entry['original_value']
                
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0,
                                   winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, original_value)
                    restored_count += 1
            except Exception as e:
                print(f"Erro ao restaurar {path}: {e}")
        
        if restored_count > 0:
            return True, f"Nome original restaurado! ({restored_count} entradas)"
        else:
            return False, "Não foi possível restaurar. Execute como administrador."
            
    except Exception as e:
        return False, f"Erro ao restaurar: {str(e)}"


def get_backed_up_cameras() -> List[str]:
    """
    Retorna lista de câmeras que têm backup salvo.
    
    Returns:
        Lista de nomes de câmeras com backup
    """
    backup_data = load_backup()
    return list(backup_data.keys())
