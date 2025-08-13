@echo off
echo 🚀 Démarrage du Scheduler Telegram - Web3 Opportunities Tracker
echo ================================================================
echo.
echo 📱 Configuration:
echo   - Notifications toutes les heures
echo   - Seuil ROI minimum: $2.00/min
echo   - Mode: 24h/24, 7j/7
echo.
echo 🛑 Appuyez sur Ctrl+C pour arrêter proprement
echo.
echo ================================================================
echo.

cd /d "D:\Web3-Opps-Tracker"
call .venv312\Scripts\activate.bat
python telegram_scheduler.py

echo.
echo 🛑 Scheduler Telegram arrêté
pause
