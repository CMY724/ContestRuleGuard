@echo off
echo ========================================
echo   ??? ContestRuleGuard ????
echo ========================================
echo.

REM Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.12+
    pause
    exit /b 1
)

REM Setup backend
cd /d "%~dp0backend"
if not exist ".venv" (
    echo [SETUP] Creating Python virtual environment...
    python -m venv .venv
    .venv\Scripts\python.exe -m pip install -e ".[dev]"
)

echo [OK] Backend ready

REM Setup frontend
cd /d "%~dp0frontend"
where pnpm >nul 2>&1
if %errorlevel% neq 0 (
    echo [SETUP] Installing pnpm...
    npm install -g pnpm
)
if not exist "node_modules" (
    echo [SETUP] Installing frontend dependencies...
    pnpm install
)

echo [OK] Frontend ready

REM Run DB migrations
cd /d "%~dp0backend"
echo [DB] Running migrations...
.venv\Scripts\python.exe -m alembic -c alembic.ini upgrade head

echo.
echo ========================================
echo   ????
echo   ??: http://localhost:8000
echo   ??: http://localhost:5173
echo   API??: http://localhost:8000/docs
echo ========================================
echo.

REM Start backend in background
start "??? Backend" cmd /c ".venv\Scripts\python.exe -m uvicorn src.contest_rule_guard.main:app --host 0.0.0.0 --port 8000 --reload"

REM Start frontend
cd /d "%~dp0frontend"
echo Starting frontend...
pnpm dev
