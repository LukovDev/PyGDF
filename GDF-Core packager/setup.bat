@echo off

echo PACKAGING GDF CORE:
echo.

pip install --upgrade wheel
pip install --upgrade setuptools

python setup.py bdist_wheel

echo.
pause
