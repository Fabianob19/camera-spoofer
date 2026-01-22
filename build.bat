@echo off
echo ========================================
echo   Camera Spoofer - Build Script
echo ========================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale Python 3.10 ou superior.
    pause
    exit /b 1
)

REM Instala dependências
echo [1/3] Instalando dependencias...
pip install -r requirements.txt pyinstaller --quiet

if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias!
    pause
    exit /b 1
)

echo.
echo [2/3] Gerando executavel...
echo.

REM Gera o executável
pyinstaller --onefile ^
    --windowed ^
    --name "Camera Spoofer" ^
    --icon "assets\icon.ico" ^
    --add-data "real_cameras.py;." ^
    --hidden-import wmi ^
    --hidden-import win32com ^
    --hidden-import win32api ^
    --hidden-import pythoncom ^
    --hidden-import customtkinter ^
    --hidden-import pygrabber ^
    --collect-all customtkinter ^
    --collect-all pygrabber ^
    main.py

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao gerar executavel!
    pause
    exit /b 1
)

echo.
echo [3/3] Limpando arquivos temporarios...
rmdir /s /q build 2>nul
del /q *.spec 2>nul

echo.
echo ========================================
echo   BUILD CONCLUIDO COM SUCESSO!
echo ========================================
echo.
echo O executavel foi gerado em:
echo   dist\Camera Spoofer.exe
echo.
echo Copie este arquivo para distribuir!
echo.
pause
