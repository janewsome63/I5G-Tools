@echo off
set arg=%1
shift

@RD /S /Q ".\build"

@RD /S /Q ".\dist"

pyinstaller main.spec

xcopy ".\LICENSE" ".\dist"

xcopy ".\README.md" ".\dist"

rename ".\dist\I5G-Tools*.exe" I5G-Tools.exe

mkdir .\dist\installer

"C:\Program Files (x86)\Install Creator\ic.exe" /B .\Install.iit

exit