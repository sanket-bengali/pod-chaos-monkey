#!/usr/bin/env bash

RCFILE="$(pwd)/.coveragerc"

python -m coverage run --source=app/ -m unittest discover
python -m coverage report --fail-under=90 --rcfile=${RCFILE}
python -m coverage xml -o ./coverage.xml --rcfile=${RCFILE}
