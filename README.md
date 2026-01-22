<p align="center">
  <img src="assets/banner.png" alt="Camera Spoofer Banner" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows" alt="Windows">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
</p>

**Camera Spoofer** é uma ferramenta para Windows que permite renomear suas câmeras de forma fácil e rápida. Ideal para organização, privacidade ou personalização do nome exibido pelos dispositivos de vídeo.

## ✨ Funcionalidades

- 🔍 **Detecção Automática**: Identifica todas as câmeras instaladas no sistema
- 🏷️ **Renomeação via Registro**: Modifica o nome do dispositivo no Windows Registry
- 💾 **Backup Automático**: Salva o nome original antes de qualquer modificação
- ↩️ **Restauração Fácil**: Permite reverter para o nome original a qualquer momento
- 🎨 **Interface Moderna**: GUI intuitiva com tema escuro (CustomTkinter)
- 📦 **Executável Portátil**: Distribuído como arquivo `.exe` único

## 📸 Preview

A interface permite selecionar qualquer câmera detectada e escolher um novo nome de uma lista de webcams reais populares:

- Logitech (C920, BRIO, StreamCam, etc.)
- Microsoft (LifeCam Studio, Modern Webcam, etc.)
- Dell, HP, Lenovo, Razer, Elgato e outras

## 🚀 Como Usar

### Executável (Recomendado)

1. Baixe o arquivo `Camera Spoofer.exe` da pasta `dist/`
2. Clique com o botão direito → **Executar como Administrador**
3. Selecione a câmera que deseja renomear
4. Escolha um nome de câmera real no dropdown
5. Clique em **Renomear Selecionada**
6. Reinicie os aplicativos que usam a câmera

### A partir do Código Fonte

```bash
# Clone o repositório
git clone https://github.com/Fabianob19/camera-spoofer.git
cd camera-spoofer

# Instale as dependências
pip install -r requirements.txt

# Execute (como Administrador)
python main.py
```

## 🔧 Requisitos

- Windows 10/11
- Python 3.10+ (para desenvolvimento)
- Privilégios de Administrador (para modificar o registro)

### Dependências

```
customtkinter>=5.0.0
wmi>=1.5.1
pywin32>=305
pygrabber>=0.2
```

## 📁 Estrutura do Projeto

```
camera-spoofer/
├── main.py              # Interface gráfica principal
├── camera_utils.py      # Detecção e renomeação de câmeras
├── real_cameras.py      # Lista de câmeras virtuais e reais
├── admin_utils.py       # Gerenciamento de privilégios
├── build.bat            # Script para gerar executável
├── requirements.txt     # Dependências Python
└── dist/
    └── Camera Spoofer.exe
```

## 🛠️ Compilar o Executável

Para gerar o arquivo `.exe`:

```bash
# Windows
.\build.bat
```

O executável será criado em `dist/Camera Spoofer.exe`.

## ⚠️ Avisos Importantes

> **Privilégios de Administrador**: O programa precisa de permissões elevadas para modificar o Registro do Windows.

> **Backup Automático**: Antes de qualquer modificação, o programa salva um backup em `camera_backup.json`. Use o botão "Restaurar Original" para desfazer.

> **Reinicie os Aplicativos**: Após renomear, feche e reabra os programas que usam a câmera para que a mudança tenha efeito.

## 🔒 Como Funciona

1. **Detecção**: Usa DirectShow (COM) e o Registro do Windows para listar todas as câmeras
2. **Identificação**: Compara nomes com padrões conhecidos de câmeras virtuais
3. **Modificação**: Altera valores `FriendlyName` no registro do dispositivo
4. **Backup**: Armazena valores originais em JSON para restauração futura

## 📋 Câmeras Virtuais Suportadas

| Software | Padrão Detectado |
|----------|------------------|
| OBS Studio | `OBS Virtual Camera` |
| NDI Tools | `NDI Video`, `NDI Webcam Input` |
| ManyCam | `ManyCam Virtual Webcam` |
| XSplit | `XSplit VCam` |
| Snap Camera | `Snap Camera` |
| DroidCam | `DroidCam Source` |
| E outros... | |

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abrir um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
