@echo off
echo ========================================
echo   ??? ????
echo ========================================
cd /d "%~dp0..\backend"
.venv\Scripts\python.exe -m pytest tests -q --tb=short
echo.
echo All tests passed. Running evaluation demo...
.venv\Scripts\python.exe eval/run.py
echo.
echo Done!
pause
