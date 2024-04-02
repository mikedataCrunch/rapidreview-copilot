# rapidreview-copilot
This repository compiles tools that assist in the conduct of rapid literature reviews--from text and data extraction to thematic analysis.

## Setting up Environments
The steps below assume that the current working directory is the repository top level dir. The steps also assume some `conda` is installed in the user's machine.

### Using `conda` environment.yml

1. Use the following code to create your the `rrc_env` from the environment.yml file:
    ```cmd
    conda env create --file environment.yml
    ```
2. Upon creating the environment, you can activate/deactivate it using the following command:
```cmd
conda activate rrc_env
conda deactivate
```

### Using `pip` requirements.txt

1. Create a conda environment with `python` installed: The specific Python version (3.9 in this scenario). Alternatively, `virtualenv` can also be used to set up a `venv` based environment (not shown).
```cmd
conda create --name rrc_env python=3.9 virtualenv
```

2. Upon creating the environment, you can activate/deactivate it using the following command:
```cmd
conda activate rrc_env
conda deactivate
```
3. Now, run the code below (while rrc_env is active) to install all dependencies using `pip` and the requirements.txt file provided:
```cmd 
pip install -r requirements.txt
```

### Setting up notebook kernel
1. Install `ipykernel`.
2. To use the conda environment as a notebook kernel, we must run the the script below.
```
python -m ipykernel install --user --name=<env_name>
```
Ensure that the `rrc_env` kernel is selected when running the `tutorials/` noteebooks/