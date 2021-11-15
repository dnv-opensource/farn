# Installing instructions for Farn model verification framework
## Getting the code
Use git to clone the Farn repository. Open Command.exe (Windows) or a terminal window (Linux, Bash) and navigate to a location of your choice:
```
cd <YOUR_REPO_DIR>
git clone https://github.com/dnv-opensource/farn
cd farn
git pull
```
## Requirements
Farn requires only
* python 3.9 or higher
* the packages as listed in farn/requirements.txt
Open a terminal window and check your python installation with
```
python --version
```
## Installing the packages in Windows
If you have no Python yet, just install https://www.anaconda.com/products/individual and follow the instructions.
Take care of saying yes when Anaconda asks you if it shall append the python paths to your environment.
If pip is not yet installed download get-pip.py here
https://bootstrap.pypa.io/get-pip.py
Open Command.exe, navigate to your repo location and do a
```
python get-pip.py
```
Check version of pip with
```
pip --version
```
Check for outdated modules
```
pip list --outdated
```
update pip and setuptools
```
python -m pip install --upgrade pip setuptools
```
And finally install all the requirements
```
pip install -r .\requirements.txt
```

### Update environment variables
Open the Control Panel/Environment Variables and add to User Variables/Path the path of your farn installation script files
```
C:\Users\<YOUR_NAME>\<YOUR_REPO_LOCATION\farn\cli
```
Generate a new variable PYTHONPATH and add
```
C:\Users\<YOUR_NAME>\<YOUR_REPO_LOCATION\farn
C:\Users\<YOUR_NAME>\<YOUR_REPO_LOCATION\farn\cli
```
to it.
### Update/Modify the registry
By default, the Windows registry is not prepared to run python script files as executables with multiple arguments. The following entry fixes this problem.
Associate .py file ending with python files:
```
assoc .py=Python.File
```
Associate python files with Windows Python launcher
```
ftype Python.File="C:\windows\py.exe" "%L" %*
```
It can be also done by opening registry.exe and searching for "Python" entries.
### Optional: set up Python virtual environment
Create the virtual environment in the project root folder, so that it resides with the project it is created for. Name it '.venv'
In your project root folder
```
python -m venv .venv
```
Activate the virtual environment
```
.venv\Scripts\activate
````
Update pip and setuptools
```
python -m pip install --upgrade pip setuptools
```

## Installing the packages in Linux (incomplete)

### Optional: set up Python virtual environment
 ~/.bash_profile
alias ae='deactivate &> /dev/null; source ./.venv/bin/activate'
alias de='deactivate'



