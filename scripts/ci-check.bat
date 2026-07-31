@echo off
REM ContestRuleGuard CI check script
echo === Backend Tests ===
cd backend
..\.venv\Scripts\python.exe -m pytest tests -q
if %errorlevel% neq 0 exit /b %errorlevel%

echo === Lint ===
..\.venv\Scripts\python.exe -m ruff check src tests
if %errorlevel% neq 0 exit /b %errorlevel%

echo === Type Check ===
..\.venv\Scripts\python.exe -m mypy src
if %errorlevel% neq 0 exit /b %errorlevel%

echo === All checks passed ===
