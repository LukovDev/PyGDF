@echo off

echo INSTALLING PYPI LIBRARIES:
echo.

pip install -r .\build\pypi.txt

echo.
cd .\src\lgfw\
"pypi.bat"

echo.
pause
