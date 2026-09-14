@echo off
setlocal
set "PY=C:\Program Files\Python314\python.exe"
set "PROJ=%~dp0"
set "LOG=%PROJ%apod_task.log"

cd /d "%PROJ%"
echo ================================================== >> "%LOG%"
echo Run started: %DATE% %TIME% >> "%LOG%"

if not exist "%PY%" (
    echo ERROR: Python interpreter not found at "%PY%" >> "%LOG%"
    endlocal
    exit /b 9009
)

"%PY%" "%PROJ%apod_wallpaper_setter.py" >> "%LOG%" 2>&1
echo Exit code: %ERRORLEVEL% >> "%LOG%"
endlocal
