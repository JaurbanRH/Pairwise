SHELL = /bin/bash

acceptance: pylint flake8 mypy black-check

pylint:
	pipenv run pylint ./**/*.py

flake8:
	pipenv run flake8 .

mypy:
	pipenv run mypy .

black-check:
	pipenv run black --check --line-length 120 .

test:
	pipenv run pytest