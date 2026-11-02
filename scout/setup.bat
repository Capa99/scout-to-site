@echo off
REM Installazione Scout su Windows - non servono permessi di amministratore.
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    set PY=py -3
) else (
    set PY=python
)

%PY% --version >nul 2>nul
if errorlevel 1 (
    echo.
    echo Python non trovato. Installalo da https://www.python.org/downloads/
    echo oppure dal Microsoft Store, scegliendo l'installazione "solo per l'utente".
    pause
    exit /b 1
)

if not exist .venv (
    echo Creo l'ambiente virtuale...
    %PY% -m venv .venv || goto errore
)

echo Installo le dipendenze...
.venv\Scripts\python.exe -m pip install --upgrade pip >nul
.venv\Scripts\python.exe -m pip install -r requirements.txt || goto errore_pip

if not exist ..\prospect mkdir ..\prospect
echo.
echo Fatto. Prova con:
echo   .venv\Scripts\python.exe scout.py tutto --comune Vigevano -o ..\prospect\vigevano.csv
pause
exit /b 0

:errore_pip
echo.
echo Installazione fallita. Se sei dietro un proxy aziendale, imposta prima:
echo   set HTTPS_PROXY=http://indirizzo-proxy:porta
echo e rilancia setup.bat. L'indirizzo del proxy lo trovi in
echo Impostazioni ^> Rete e Internet ^> Proxy, oppure chiedilo all'IT.
pause
exit /b 1

:errore
echo Errore nella creazione dell'ambiente virtuale.
pause
exit /b 1
