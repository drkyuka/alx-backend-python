#!/bin/bash
# Python 3.13 Environment Activation Script
echo "Activating Python 3.13 environment..."
export PIPENV_IGNORE_VIRTUALENVS=1
exec pipenv shell

