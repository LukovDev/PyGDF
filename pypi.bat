@echo off

echo INSTALLING PYPI LIBRARIES:
echo.

pip install -r .\build\tools\pypi.txt

echo.
cd .\src\core\
"pypi.bat"

echo.
pause
