@echo off

echo COMPILING CYTHON FILES:
echo.

python -I compile.py build_ext --inplace

echo.
pause
