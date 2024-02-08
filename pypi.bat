@echo off

echo INSTALLING PYPI LIBRARIES:
echo.

pip install -r .\build\tools\pypi.txt

echo.
cd .\src\lgfw\
"pypi.bat"

echo.
pause
