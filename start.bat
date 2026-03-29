@echo off
REM Start Yamaha PSR-i455 Professional MIDI Studio

echo.
echo ================================================
echo  Loading Yamaha PSR-i455 Professional Studio...
echo ================================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start the application
python studio.py

REM If program closed, keep window open for user to see any errors
if errorlevel 1 (
    echo.
    echo An error occurred. Check the output above.
    echo.
    pause
)
