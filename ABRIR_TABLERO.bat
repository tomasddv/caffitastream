@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title DDV - Indicadores Comerciales
color 1F
echo ================================================
echo   DASHBOARD DDV - INICIO EN WINDOWS
echo ================================================
echo.
if not exist "app.py" (
  echo ERROR: No se encuentra app.py.
  echo Extrae TODOS los archivos del ZIP a una carpeta y abre este BAT desde alli.
  goto :ERROR
)
if exist ".venv\Scripts\python.exe" goto :INSTALAR
set "PY_CMD="
where py >nul 2>&1
if not errorlevel 1 (
  py -3 -c "import sys;sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
  if not errorlevel 1 set "PY_CMD=py -3"
)
if not defined PY_CMD (
  where python >nul 2>&1
  if not errorlevel 1 (
    python -c "import sys;sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
    if not errorlevel 1 set "PY_CMD=python"
  )
)
if not defined PY_CMD (
  echo ERROR: Se necesita Python 3.10 o mas nuevo para ejecutar Streamlit.
  echo Instalalo desde https://www.python.org/downloads/windows/
  echo Durante la instalacion, activa "Add Python to PATH".
  goto :ERROR
)
echo Preparando entorno virtual local... (solo la primera vez)
%PY_CMD% -m venv ".venv"
if errorlevel 1 (
  echo ERROR: No se pudo crear el entorno virtual.
  goto :ERROR
)
:INSTALAR
if not exist ".venv\Scripts\python.exe" (
  echo ERROR: No se encontro Python en el entorno virtual.
  goto :ERROR
)
".venv\Scripts\python.exe" -m pip show gdown >nul 2>&1
if errorlevel 1 (
  echo Instalando Streamlit y dependencias. La primera vez requiere Internet.
  ".venv\Scripts\python.exe" -m pip install -r "requirements.txt"
  if errorlevel 1 (
    echo ERROR: Fallo la instalacion. Verifica Internet y el mensaje anterior.
    goto :ERROR
  )
)
echo.
echo Abriendo el tablero. Python seleccionara un puerto disponible...
echo Si el navegador no abre solo, utiliza el enlace que aparece debajo.
echo.
".venv\Scripts\python.exe" "iniciar_dashboard.py"
if errorlevel 1 (
  echo.
  echo ERROR: No se pudo iniciar el dashboard. Mira el mensaje anterior.
  goto :ERROR
)
goto :FIN
:ERROR
echo.
echo Copia o saca una foto de este mensaje para diagnosticar el problema.
pause
:FIN
endlocal
