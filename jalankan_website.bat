@echo off
title GuardiVoice — Web Server
echo ========================================================
echo          GuardiVoice: AI Voice Detector Frontend
echo ========================================================
echo Membuka website di browser...
start http://localhost:3000
echo Server berjalan di http://localhost:3000
echo Tekan Ctrl+C untuk menghentikan server.
echo.
python -m http.server 3000 --directory docs
pause
