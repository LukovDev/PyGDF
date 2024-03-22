@echo off

echo INSTALLING PYPI LIBRARIES:
echo.

pip install -r .\build\pypi.txt

echo.
cd .\src\gdf\
"pypi.bat"

echo.
pause
