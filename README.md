# rapidreview-copilot
This repository compiles tools that assist in the conduct of rapid literature reviews--from text and data extraction to thematic analysis.

# Setting up Environments
## Conda Environment

Considering that you already have conda installed on your pc. 
The `environment.yml` file contains a list of packages and their versions needed to run the `DEMO_SESSION.ipynb`. 

Firstly, open your terminal or command prompt and check if the file path shown is your working directory. Else, use the following code to do that:
```cmd
cd folder-name
```

Use the following code to create your Conda environment:
```cmd
conda create --name <your-environment-name> --file environment.yml
```

Upon creating the environment, you can activate it using the following command:
```cmd
conda activate <your-environment-name>
```

## Virtual Environment
Considering that you already have pip installed on your pc.
The `requirements.txt` file contains a list of packages or libraries needed to run the `DEMO_SESSION.ipynb`. 

Firstly, open your terminal or command prompt and check if the file path shown is your working directory. Else, use the following code to do that:
```cmd
cd folder-name 
```

Next, you will need to create a Conda environment. Code below will create a new Conda environment with a specific Python version (3.9 in this scenario). Virtualenv is tool to set up Python environments. You can install venv to your host Python with the following command:
```cmd
conda create --name <your-environment-name> python=3.9 virtualenv
```

Upon creating the environment, you can activate it using the following command:
```cmd
conda activate <your-environment-name>
```

Change directory to a project folder that you wish to set up your virtual environment.
```cmd
cd <path_to_repo>
```
Then run the following code to create a virtual environment. 
```cmd
python -m venv <your-virtual-environment-name>
```
Check that a folder named <your-virtual-environment-name> has been created. 

Now you will need to activate the virtual environment before you can use it in the project. 

```bash
# MacOS
source <your-virtual-environment-name>/bin/activate
```
```cmd
# Windows
<your-virtual-environment-name>/Scripts/activate
```
Now, run the code below to install all dependencies:
```cmd 
pip install -r requirements.txt
```
Setting up notebook kernel
```
python -m ipykernel install --user --name=<env_name>
```
<b> Deactivate a Virtual Environment </b>
```
 deactivate
```