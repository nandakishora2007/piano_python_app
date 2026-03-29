@echo off
REM Quick Start Script for Yamaha PSR-i455 Professional MIDI Studio

echo.
echo ================================================
echo  Yamaha PSR-i455 Professional MIDI Studio
echo ================================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check MIDI ports
echo Checking MIDI connectivity...
python main.py

echo.
echo ================================================
echo MIDI Port Check Complete
echo.
echo If you see "Digital Keyboard 0" and "Digital Keyboard 1"
echo your Yamaha is properly connected!
echo.
echo Ready to start? Run: python studio.py
echo ================================================
echo.

pause
