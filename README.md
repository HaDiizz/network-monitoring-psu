***To create a virtual environment named pyvenv***

```bash
python -m venv pyvenv
```

***To activate a virtual environment ***

```bash
pyvenv\scripts\activate
```

***To create a requirements.txt file for a Flask project, follow these steps:***
- Activate your virtual environment where you have installed Flask and all the required packages.
- Open the terminal and navigate to the project's root directory.
- Run the following command to generate a list of all installed packages and their versions

```bash
pip freeze > requirements.txt
```
***To install packages from a requirements.txt file, follow these steps:***
- Activate your virtual environment where you want to install the packages.
- Open the terminal and navigate to the project's root directory.
- Run the following command to install all the packages listed in the requirements.txt file:

```bash
pip install -r requirements.txt
```


***run flask in debug mode***

```bash
flask --app app.py run --debug
```