@echo off
title IT Mentor News Bot
chcp 65001 > nul
echo ===================================================
echo     Запуск IT & AI Mentor News Bot
echo ===================================================
cd /d "%~dp0"
python bot.py
pause
