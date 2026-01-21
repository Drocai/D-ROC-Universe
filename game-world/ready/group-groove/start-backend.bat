@echo off
echo ========================================
echo GROUP GROOVE - Starting Backend
echo ========================================
echo.
echo Backend will run at: http://localhost:8787
echo Press Ctrl+C to stop
echo.
cd backend
wrangler dev --port 8787
