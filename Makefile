PYTHON_VERSION ?= 3.8

CARGO_HOME ?= $(HOME)/.cargo
PATH := $(HOME)/.rye/shims:$(HOME)/.local/bin:$(CARGO_HOME)/bin:$(PATH)

SHELL := /bin/bash
PYTHON_FILES := $(shell find src/$(PROJECT_NAME) -type f -name '*.py' -o -name '*.pyi')

UV_PYTHON_PREFERENCE ?= only-managed
UV ?= uv
ifdef INSIDE_EMACS
UV_RUN ?= uv run --color never
else
UV_RUN ?= uv run
endif
RUN ?= $(UV_RUN)


REQUIRED_UV_VERSION ?= 0.7.2
bootstrap:
	@INSTALLED_UV_VERSION=$$(uv --version 2>/dev/null | awk '{print $$2}' || echo "0.0.0"); \
    DETECTED_UV_VERSION=$$(printf '%s\n' "$(REQUIRED_UV_VERSION)" "$$INSTALLED_UV_VERSION" | sort -V | head -n1); \
	if [ "$$DETECTED_UV_VERSION" != "$(REQUIRED_UV_VERSION)" ]; then \
		uv self update $(REQUIRED_UV_VERSION) || curl -LsSf https://astral.sh/uv/$(REQUIRED_UV_VERSION)/install.sh | sh; \
	fi
	@echo $(PYTHON_VERSION) > .python-version
.PHONY: bootstrap

sync install: bootstrap
	@$(UV) sync --frozen
.PHONY: install sync

lock: bootstrap
ifdef update_all
	@$(UV) lock -U
else
	@$(UV) lock
endif
.PHONY: lock

update: bootstrap
	@$(MAKE) lock update_all=1
.PHONY: update

build: sync
	@$(UV) build
.PHONY: build

format-python:
	@$(RUN) isort src test
	@$(RUN) ruff check --fix src
	@$(RUN) ruff format src

format: format-python
.PHONY: format format-python

lint:
	@$(RUN) ruff check src
	@$(RUN) ruff format --check src
	@$(RUN) isort --check src
.PHONY: lint

shell:
	@$(RUN) ipython
.PHONY: shell


pytest_paths ?= "src/tests/"
PYTEST_PATHS ?= $(pytest_paths)
HYPOTHESIS_PROFILE ?= dev
PYTEST_HYPOTHESIS_ARGS ?=
PYTEST_EXTRA_ARGS ?=
PYTEST_FAILURE_ARGS ?= --ff --maxfail 1
PYTEST_ARGS ?= -vv $(PYTEST_FAILURE_ARGS) $(PYTEST_EXTRA_ARGS) $(PYTEST_HYPOTHESIS_ARGS)
PYTEST_WORKERS ?= auto
PYTEST_MAXWORKERS ?= 4
PYTEST_COVERAGE_ARGS ?= --cov-config=pyproject.toml --cov=src/

test:
	@rm -f .coverage*
	@pytest_workers_args=""; \
    if [ -n "$(PYTEST_WORKERS)" ]; then \
       pytest_workers_args="-n $(PYTEST_WORKERS)"; \
       if [ -n "$(PYTEST_MAXWORKERS)" ]; then \
          pytest_workers_args="$$pytest_workers_args --maxprocesses=$(PYTEST_MAXWORKERS)"; \
       fi \
    fi; \
    $(RUN) pytest $(PYTEST_COVERAGE_ARGS) $$pytest_workers_args $(PYTEST_ARGS) $(PYTEST_PATHS)
.PHONY: test


doctest:
	@$(MAKE) SPHINXBUILD="$(RUN) sphinx-build" -C docs doctest
.PHONY: test

mypy:
	@$(RUN) mypy --config-file mypy.ini -p xotl.tools
.PHONY: mypy

docs/build:
	@$(MAKE) SPHINXBUILD="$(RUN) sphinx-build" -C docs html
.PHONY: docs/build

DOC_SERVER_PORT ?= 6942
docs/browse: docs/build
	@$(RUN) python -m http.server  \
                   --directory $(PWD)/docs/build/html $(DOC_SERVER_PORT)
.PHONY: docs/browse


AUTO_RESTART := $(RUN) watchmedo auto-restart --directory docs --directory src --recursive --pattern '*.py' --pattern '*.rst' --
docs/serve:
	@$(AUTO_RESTART) $(MAKE) docs/browse
.PHONY: docs/serve
