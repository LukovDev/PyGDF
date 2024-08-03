@echo off

echo COMPILING CYTHON FILES:
echo.

python setup.py build_ext --inplace
python setup.py clean

echo.
pause
