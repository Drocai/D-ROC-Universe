@echo off
echo ========================================
echo GROUP GROOVE - Starting Web App
echo ========================================
echo.
echo Installing http-server if needed...
call npm install -g http-server
echo.
echo Web app will run at: http://localhost:8000
echo Press Ctrl+C to stop
echo.
cd web
http-server -p 8000 -c-1
