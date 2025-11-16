@echo off
set arg=%1
shift

@RD /S /Q ".\build"

@RD /S /Q ".\dist"

pyinstaller --onefile %arg% --name I5G-Tools --icon icon.ico --add-data="icon.ico;."

xcopy ".\LICENSE" ".\dist"

xcopy ".\README.md" ".\dist"

REM rename ".\dist\main.exe" I5G-Tools.exe

mkdir .\dist\installer

"C:\Program Files (x86)\Install Creator\ic.exe" /B .\Install.iit

exit