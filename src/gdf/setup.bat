@echo off

echo COMPILING CYTHON FILES:
echo.

python setup.py build_ext --inplace

echo.
pause
