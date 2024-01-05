@echo off

set VERSION=1.0

ROBOCOPY "src" "build" game_mover.py
ROBOCOPY "src" "build" GUI.py
cd build
REM py -3-32 -m nuitka --onefile --standalone --include-data-dir="D:\Documents\VS Code\nsui_banner_fixer\build\tools=tools" -o nsui_banner_fixer.exe main.py
py -3-64 -m nuitka^
 --onefile^
 --standalone^
 --onefile-tempdir-spec="%TEMP%\game_mover\%VERSION%"^
 --enable-plugin=tk-inter^
 --disable-console^
 --windows-icon-from-ico="D:\Documents\VS Code\game_mover\src\data\icon.png"^
 --include-data-dir="D:\Documents\VS Code\game_mover\src\data"=data^
 --company-name=pivotiii^
 --product-name="Game Mover"^
 --file-version=%VERSION%^
 --product-version=%VERSION%^
 -o game_mover.exe GUI.py