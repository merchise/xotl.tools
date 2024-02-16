RYE_EXEC ?= rye run
PYTHON_VERSION ?= 3.8
PATH := $(HOME)/.rye/shims:$(PATH)

SHELL := /bin/bash
PYTHON_FILES := $(shell find src/$(PROJECT_NAME) -type f -name '*.py' -o -name '*.pyi')

install:
	rye self update || curl -sSf https://rye-up.com/get | bash
	rye pin --relaxed $(PYTHON_VERSION)
	rye sync
.PHONY: install


format:
	@$(RYE_EXEC) ruff --fix src/ tests/
	@$(RYE_EXEC) isort src/ tests/
	@$(RYE_EXEC) ruff format src/ tests/
.PHONY: format

lint:
	@$(RYE_EXEC) ruff src/ tests/
	@$(RYE_EXEC) ruff format --check src/ tests/
	@$(RYE_EXEC) isort --check src/ tests/
.PHONY: lint

test:
	@$(RYE_EXEC) pytest -l -q --cov=xotl.tools
.PHONY: test

mypy:
	@$(RYE_EXEC) mypy -p xotl.tools --config mypy.ini
.PHONY: mypy
