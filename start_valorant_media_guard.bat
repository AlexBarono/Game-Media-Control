@echo off
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 valorant_media_guard.py
) else (
    python valorant_media_guard.py
)

pause
