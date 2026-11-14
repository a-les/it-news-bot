@echo off
chcp 65001 > nul
echo Отправка обновлений в GitHub...
cd /d "%~dp0"
git add .
git commit -m "update bot"
git push -u origin master
echo Готово!
pause
