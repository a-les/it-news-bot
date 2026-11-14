@echo off
cd /d "%~dp0"
set HTTP_PROXY=http://127.0.0.1:10809
set HTTPS_PROXY=http://127.0.0.1:10809
"C:\Program Files\Git\cmd\git.exe" push -u origin main
pause
