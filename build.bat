@echo off

set VERSION=1.0

ROBOCOPY "src" "build" *.py

cd build

py -3-64 -m nuitka^
 --onefile^
 --standalone^
 --disable-console^
 --report=compilation-report.xml^
 --onefile-tempdir-spec="%TEMP%\game_mover\%VERSION%"^
 --enable-plugin=tk-inter^
 --windows-icon-from-ico="%~dp0src\data\icon.png"^
 --include-data-dir="%~dp0src\data"=data^
 --company-name=pivotiii^
 --product-name="Game Mover"^
 --file-version=%VERSION%^
 --product-version=%VERSION%^
 -o game_mover.exe GUI.py