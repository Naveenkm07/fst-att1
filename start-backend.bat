@echo off
title Scheme Finder Backend (FastAPI)
echo Starting FastAPI Backend on http://localhost:8000 ...
cd "%~dp0scheme-finder-api"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
