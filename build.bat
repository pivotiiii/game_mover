@echo off
ROBOCOPY "src" "build" game_mover.py
ROBOCOPY "src" "build" GUI.py
cd build
REM py -3-32 -m nuitka --onefile --standalone --include-data-dir="D:\Documents\VS Code\nsui_banner_fixer\build\tools=tools" -o nsui_banner_fixer.exe main.py
py -3-64 -m nuitka --onefile --standalone --enable-plugin=tk-inter -o game_mover.exe GUI.py