@echo off
set arg=%1
shift

@RD /S /Q ".\build"

@RD /S /Q ".\dist"

pyinstaller --onefile %arg% --icon icon.ico

xcopy ".\LICENSE" ".\dist"

xcopy ".\README.md" ".\dist"

rename ".\dist\main.exe" I5G-Tools.exe

mkdir .\dist\installer

"C:\Program Files (x86)\Install Creator\ic.exe" /B .\Install.iit

exit