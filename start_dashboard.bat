@echo off
echo 🚀 Lancement du Dashboard Web3 Opportunities Tracker
echo ====================================================

cd /d "D:\Web3-Opps-Tracker"

REM Activer l'environnement virtuel
call .venv312\Scripts\activate.bat

echo ✅ Environnement virtuel activé
echo 📊 Lancement de Streamlit sur http://localhost:8501
echo.
echo 🔧 Commandes utiles:
echo    - Ctrl+C : Arrêter le serveur
echo    - R : Recharger le dashboard dans le navigateur
echo.

REM Lancer Streamlit
streamlit run dashboard.py --server.port 8501 --server.headless false

pause
