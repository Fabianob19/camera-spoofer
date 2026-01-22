"""
Camera Spoofer - Utilitários de Administrador
Funções para verificar e solicitar privilégios de administrador.
"""

import ctypes
import sys
import os


def is_admin() -> bool:
    """
    Verifica se o programa está rodando com privilégios de administrador.
    
    Returns:
        True se estiver rodando como admin, False caso contrário
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def request_admin_privileges() -> bool:
    """
    Solicita elevação de privilégios (UAC) reiniciando o programa como admin.
    
    Returns:
        True se conseguiu solicitar elevação, False caso contrário
    """
    if is_admin():
        return True
    
    try:
        # Obtém o caminho do executável atual
        if getattr(sys, 'frozen', False):
            # Executando como .exe (PyInstaller)
            script = sys.executable
        else:
            # Executando como script Python
            script = os.path.abspath(sys.argv[0])
        
        # Solicita elevação via ShellExecute com "runas"
        params = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else ''
        
        result = ctypes.windll.shell32.ShellExecuteW(
            None,           # hwnd
            "runas",        # operação (executar como admin)
            sys.executable, # arquivo
            f'"{script}" {params}',  # parâmetros
            None,           # diretório
            1               # SW_SHOWNORMAL
        )
        
        # Se resultado > 32, a operação foi bem-sucedida
        return result > 32
        
    except Exception as e:
        print(f"Erro ao solicitar privilégios de administrador: {e}")
        return False


def ensure_admin_or_exit():
    """
    Garante que o programa está rodando como admin.
    Se não estiver, solicita elevação e encerra o processo atual.
    """
    if not is_admin():
        if request_admin_privileges():
            # Encerra o processo atual, pois um novo foi iniciado como admin
            sys.exit(0)
        else:
            # Não conseguiu solicitar elevação
            print("Este programa requer privilégios de administrador.")
            print("Por favor, execute como administrador.")
            sys.exit(1)
