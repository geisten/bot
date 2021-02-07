MODULE:=bot

TAG := $(shell git describe --tags --always --dirty)

run:
	@python -m $(MODULE)

test:
	@pytest

lint:
	@echo "\nRunning Pylint against source and test files...\n"
	@-pylint --max-line-length=120 **/*.py
	@echo "\nRunning Flake8 against source and test files...\n"
	@-flake8 --max-line-length=120 --exclude .git,__pycache__,venv,.eggs,.venv
	@echo "\nRunning mypy against source and test files...\n"
	@-mypy **/*.py
	@echo "\nRunning Bandit against source files...\n"
	@-bandit -r -x **/test_*.py **/*.py

version:
	@echo $(TAG)

.PHONY: clean test

clean:
	rm -rf .pytest_cache .coverage pytest_cache coverage.xml
