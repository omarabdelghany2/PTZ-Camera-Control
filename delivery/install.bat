@echo off

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python not found. Installing Python...

    :: Set Python installer download URL (customize the URL to match the latest version you need)
    set PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe
    set PYTHON_INSTALLER=python_installer.exe

    :: Download Python installer
    powershell -command "Invoke-WebRequest -Uri %PYTHON_INSTALLER_URL% -OutFile %PYTHON_INSTALLER%"

    :: Install Python silently (including pip) and add to PATH
    %PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1

    :: Clean up installer
    del %PYTHON_INSTALLER%
) else (
    echo Python is already installed.
)

:: Check if pip is installed
pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Pip not found. Installing pip...

    :: Use ensurepip if available
    python -m ensurepip --default-pip
)

:: Upgrade pip to the latest version
python -m pip install --upgrade pip

:: Create a requirements file
echo -i https://pypi.org/simple > requirements.txt
echo certifi==2024.8.30; python_version >= '3.6' >> requirements.txt
echo charset-normalizer==3.4.0; python_full_version >= '3.7.0' >> requirements.txt
echo idna==3.10; python_version >= '3.6' >> requirements.txt
echo obsws-python==1.1.0; python_version >= '3.10' >> requirements.txt
echo requests==2.32.3; python_version >= '3.8' >> requirements.txt
echo toml==0.10.2; python_version >= '2.6' and python_version not in '3.0, 3.1, 3.2, 3.3' >> requirements.txt
echo tomli==2.0.2; python_version < '3.11' >> requirements.txt
echo urllib3==2.2.3; python_version >= '3.8' >> requirements.txt
echo websocket-client==1.8.0; python_version >= '3.8' >> requirements.txt

:: Install packages from requirements.txt
pip install -r requirements.txt

:: Clean up requirements file
del requirements.txt

echo All done!
pause
