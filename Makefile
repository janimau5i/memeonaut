# Basic Makefile to do manage python venv stuff

PYTHON_MAIN?=memeonaut.py

# name of env folder
ENV_NAME?=env
# python command to be used both to create and to use inside venv
PYTHON?=python3
ENV_BIN?=$(ENV_NAME)/bin
# python executable inside venv
ENV_PYTHON?=$(ENV_BIN)/$(PYTHON)


env: $(ENV_BIN)/activate

# This will create the virtual environment if required. 
# Changes to requirements.txt will also trigger a dependency reinstall.
$(ENV_BIN)/activate: requirements.txt
	test -d $(ENV_NAME) || $(PYTHON) -m venv $(ENV_NAME)
	$(ENV_PYTHON) -m pip install --upgrade pip
	$(ENV_PYTHON) -m pip install -r requirements.txt
	touch ./$(ENV_BIN)/activate

# Run the thing! (inside virtual environment)
# No piping to tee for now because this makes the stack traces dissappear and I have no idea why
run: env
	$(ENV_PYTHON) $(PYTHON_MAIN) 
kill:
	# signal 11 because I hate python
	pkill --signal 11 python3
