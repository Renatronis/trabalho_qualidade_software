@echo off
REM Cria o ambiente virtual (.venv), instala as dependencias e roda os testes.
REM Uso: duplo clique neste arquivo, ou "configurar_ambiente.bat" no terminal.
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Criando o ambiente virtual .venv ...
    py -3 -m venv .venv 2>nul || python -m venv .venv
    if errorlevel 1 (
        echo ERRO: Python nao encontrado. Instale o Python 3.9+ e tente de novo.
        pause
        exit /b 1
    )
)

echo Instalando dependencias ...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements-test.txt
if errorlevel 1 (
    echo ERRO ao instalar as dependencias.
    pause
    exit /b 1
)

echo.
echo Rodando os testes ...
".venv\Scripts\python.exe" -m pytest -v

echo.
echo Pronto. Para usar o ambiente no terminal: .venv\Scripts\activate
pause
