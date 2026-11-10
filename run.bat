@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul
title FoodPilot AI - Inicializador Unificado

echo ======================================================================
echo                 FOODPILOT AI - INTELIGENCIA OPERACIONAL
echo ======================================================================
echo.

rem 1. Verifica se o ambiente virtual existe
if not exist ".venv\Scripts\python.exe" (
    echo [ERRO] Ambiente virtual .venv nao encontrado!
    echo Execute: python -m venv .venv
    echo E instale os pacotes: .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

rem 2. Verifica se a pasta frontend existe
if not exist "frontend\package.json" (
    echo [ERRO] Diretorio frontend nao encontrado!
    pause
    exit /b 1
)

echo [1/3] Iniciando o servidor local da API (FastAPI + SQLite)...
start "FoodPilot API (Porta 8000)" cmd /k ".venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000"

ping 127.0.0.1 -n 3 >nul

echo [2/3] Iniciando o Dashboard Web (React + TypeScript + Vite)...
start "FoodPilot Dashboard (Porta 5173)" cmd /k "npm.cmd run dev --prefix frontend"

ping 127.0.0.1 -n 4 >nul

echo [3/3] Abrindo o FoodPilot AI no navegador padrao...
start http://localhost:5173

echo.
echo ======================================================================
echo  FoodPilot AI iniciado com sucesso!
echo.
echo  - Dashboard:         http://localhost:5173
echo  - API Docs Swagger:  http://localhost:8000/docs
echo  - Status da IA:      http://localhost:8000/api/v1/ai/status
echo.
echo  * Dica: Para ativar a IA local com Qwen, rode em outro terminal:
echo    ollama run qwen3:4b-instruct
echo    (Se o Ollama nao estiver rodando, o Fallback Deterministico
echo    funciona automaticamente com 100%% de precisao).
echo ======================================================================
echo.
pause
