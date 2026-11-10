@echo off
echo ===================================================
echo   SEHAT SAATHI - AI FITNESS & DIET PLANNER AGENT
echo ===================================================

if not exist ".venv\Scripts\python.exe" (
    echo [1/4] Creating Python virtual environment...
    python -m venv .venv
)

echo [2/4] Installing / verifying dependencies...
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

if not exist "backend\ml_models\goal_predictor.pkl" (
    echo [3/4] Training ML models...
    .\.venv\Scripts\python.exe backend\ml_models\train.py
)

if not exist "app.db" (
    echo [3.5/4] Populating initial demo database & FAISS RAG index...
    .\.venv\Scripts\python.exe populate_test_cases.py
)

echo [4/4] Starting Flask Server at http://127.0.0.1:5000 ...
start http://127.0.0.1:5000
.\.venv\Scripts\python.exe run.py
pause
