@echo off
title GuardiVoice — Backend API
echo ========================================================
echo          GuardiVoice: FastAPI Backend Server
echo ========================================================
echo Menjalankan FastAPI server pada http://localhost:8000
echo Dokumentasi Swagger UI: http://localhost:8000/docs
echo.
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
