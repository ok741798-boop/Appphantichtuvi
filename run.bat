@echo off
rem Tao moi truong ao neu chua co, cai thu vien, chay server va mo trinh duyet.
chcp 65001 >nul
cd /d "%~dp0backend"

rem Moi truong ao tao tu Python da go (vd. ban Microsoft Store) se khong chay duoc, phai tao lai.
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe -c "import sys" >nul 2>&1
    if errorlevel 1 (
        echo Moi truong ao bi hong, dang tao lai...
        rmdir /s /q .venv
    )
)

if not exist .venv\Scripts\python.exe (
    echo Dang tao moi truong ao...
    python -m venv .venv
    if errorlevel 1 goto :python_error
)

echo Dang kiem tra thu vien...
.venv\Scripts\python.exe -m pip install -q --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto :install_error

rem Cho server khoi dong 2 giay roi moi mo trinh duyet.
start "" /b cmd /c "ping -n 3 127.0.0.1 >nul & start http://localhost:5057"

echo TuVi Analyzer dang chay tai http://localhost:5057
echo Giu cua so nay mo trong khi dung app. Dong cua so de tat server.
.venv\Scripts\python.exe app.py
pause
exit /b

:python_error
echo Khong tao duoc moi truong ao. Hay cai Python 3.10 tro len.
pause
exit /b 1

:install_error
echo Khong cai duoc thu vien. Hay kiem tra ket noi mang.
pause
exit /b 1
