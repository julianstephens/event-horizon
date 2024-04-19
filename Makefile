USING_POETRY=$(shell grep "tool.poetry" pyproject.toml && echo "yes")

.PHONY: help
help:             ## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep


.PHONY: show
show:             ## Show the current environment.
	@echo "Current environment:"
	@if [ "$(USING_POETRY)" ]; then poetry env info && exit; fi
	@echo "Running using "
	@python -V
	@python -m site

.PHONY: fmt
fmt:              ## Format code using ruff.
	@ruff format .
	@ruff check . --select I --fix

.PHONY: lint
lint:             ## Run ruff & mypy linters.
	@ruff check . --extend-select W --fix

.PHONY: clean
clean:            ## Clean unused files.
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name '__pycache__' -exec rm -rf {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	@rm -rf .cache
	@rm -rf .mypy_cache
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -rf htmlcov
	@rm -rf .tox/

.PHONY: initdb
initdb:           ## Initialize the database.
	 @flask -e .env initdb

.PHONY: routes
routes: 				 ## Show the routes.
	 @flask -e .env routes

.PHONY: run
run: 				 		## Run the flask app
	 @flask -e .env --debug run
