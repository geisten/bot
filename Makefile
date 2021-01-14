MODULE:=blueprint

TAG := $(shell git describe --tags --always --dirty)

run:
	@python -m $(MODULE)

test:
	@pytest

lint:
	@echo "\nRunning Pylint against source and test files...\n"
	@pylint **/*.py
	@echo "\nRunning Flake8 against source and test files...\n"
	@flake8
	@echo "\nRunning Bandit against source files...\n"
	@bandit -r

version:
	@echo $(TAG)

.PHONY: clean test

clean:
	rm -rf .pytest_cache .coverage pytest_cache coverage.xml
