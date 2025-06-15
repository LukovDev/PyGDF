@echo off

echo INSTALLING PYPI LIBRARIES:
echo.

pip install -r .\build\pypi.txt

echo.
cd .\src\gdf\_scripts\
"pypi.bat"

echo.
pause
