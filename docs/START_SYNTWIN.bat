@echo off
echo ============================================================
echo    Starting SynTwin Complete System
echo ============================================================
echo.
echo Starting API Server...
echo.
start cmd /k "python start_api_server.py"
timeout /t 3 >nul
echo.
echo Opening Frontend Dashboard...
echo.
start frontend_complete.html
echo.
echo ============================================================
echo    SynTwin is now running!
echo ============================================================
echo.
echo - API Server: http://localhost:8000
echo - Frontend Dashboard: Opened in your browser
echo.
echo Press any key to exit (this won't stop the server)
pause >nul
