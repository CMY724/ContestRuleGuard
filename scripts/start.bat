@echo off
echo ========================================
echo   ContestRuleGuard Launcher
echo ========================================
echo.

REM Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.12+
    pause
    exit /b 1
)

REM Get script directory and project root
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

REM Setup backend
cd /d "%PROJECT_ROOT%ackend"
if not exist ".venv" (
    echo [SETUP] Creating Python virtual environment...
    python -m venv .venv
    .venv\Scripts\python.exe -m pip install -e ".[dev]"
)

echo [OK] Backend ready

REM Setup frontend
cd /d "%PROJECT_ROOT%rontend"
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
cd /d "%PROJECT_ROOT%ackend"
echo [DB] Running migrations...
.venv\Scripts\python.exe -m alembic -c alembic.ini upgrade head

echo.
echo ========================================
echo   ContestRuleGuard is starting...
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:8000/docs
echo ========================================
echo.

REM Start backend in background
start "ContestRuleGuard Backend" cmd /c ".venv\Scripts\python.exe -m uvicorn contest_rule_guard.main:app --host 0.0.0.0 --port 8000 --reload"

REM Start frontend
cd /d "%PROJECT_ROOT%rontend"
echo Starting frontend...
pnpm dev
