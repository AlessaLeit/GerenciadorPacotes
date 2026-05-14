@echo off
REM ========================================
REM Banho & Tosa - Startup 1-Clique (Backend + Frontend)
REM ========================================

echo.
echo 🚀 Iniciando Banho ^& Tosa Manager...
echo ========================================

REM 1. Backend - Instalar deps se necessario
echo.
echo 📦 [1/4] Instalando backend dependencies...
echo   💾 Usando venv e verificando dependencias...
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate

REM Verifica se o requirements está na raiz ou dentro da pasta backend
if exist "backend\requirements.txt" (
    set REQS_PATH=backend\requirements.txt
) else (
    set REQS_PATH=requirements.txt
)

call pip install -r %REQS_PATH% --quiet
if %errorlevel% neq 0 (
    echo ❌ Erro instalando backend deps. Execute manualmente.
    pause
    exit /b %errorlevel%
)

REM 2. Start Backend (nova janela)
echo.
echo ⚙️  [2/4] Iniciando Backend FastAPI (porta 8000)...
start "Backend FastAPI" cmd /k "cd /d %~dp0backend && ..\venv\Scripts\activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM 3. Aguardar Backend
echo.
echo ⏳ [3/4] Aguardando backend iniciar (10s)...
timeout /t 10 /nobreak >nul

REM 4. Frontend (na mesma janela)
echo.
echo 🌐 [4/4] Iniciando Frontend Vue (porta 5173)...
cd /d "%~dp0frontend"
if not exist "node_modules" (
    echo 📦 Instalando frontend deps...
    npm install --silent
)
npm run dev

echo.
echo ✅ Pronto! Acesse:
echo   🔗 Frontend: http://localhost:5173
echo   📚 API Docs:  http://localhost:8000/docs
pause
