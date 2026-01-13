@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在启动发光飞机粒子效果...
echo.
.\.venv\Scripts\python.exe script.py
pause
