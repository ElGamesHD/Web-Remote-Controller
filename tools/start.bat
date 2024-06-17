@echo off
start cmd /C python ../src/screen_server/controller.py
python ../src/web/web_server.py
pause