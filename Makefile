PYTHON_VERSION ?= 3.10

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


REQUIRED_UV_VERSION ?= 0.13.5

.PHONY: bootstrap
bootstrap:
	@INSTALLED_UV_VERSION=$$(uv --version 2>/dev/null | awk '{print $$2}' || echo "0.0.0"); \
    DETECTED_UV_VERSION=$$(printf '%s\n' "$(REQUIRED_UV_VERSION)" "$$INSTALLED_UV_VERSION" | sort -V | head -n1); \
	if [ "$$DETECTED_UV_VERSION" != "$(REQUIRED_UV_VERSION)" ]; then \
		uv self update $(REQUIRED_UV_VERSION) || curl -LsSf https://astral.sh/uv/$(REQUIRED_UV_VERSION)/install.sh | sh; \
	fi
	@echo $(PYTHON_VERSION) > .python-version


.PHONY: install sync
sync install: | bootstrap
	@$(UV) sync --frozen


.PHONY: lock
lock: | bootstrap
ifdef update_all
	@$(UV) lock -U
else
	@$(UV) lock
endif


.PHONY: update
update: | bootstrap
	@$(MAKE) lock update_all=1


.PHONY: build
build: sync
	@$(UV) build

.PHONY: format-python
format-python: sync
	@$(RUN) ruff check --fix src
	@$(RUN) ruff format src


.PHONY: format
format: format-python


.PHONY: lint
lint: sync
	@$(RUN) ruff check src
	@$(RUN) ruff format --check src


.PHONY: shell
shell: sync
	@$(RUN) ipython



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

.PHONY: test
test: sync
	@rm -f .coverage*
	@pytest_workers_args=""; \
    if [ -n "$(PYTEST_WORKERS)" ]; then \
       pytest_workers_args="-n $(PYTEST_WORKERS)"; \
       if [ -n "$(PYTEST_MAXWORKERS)" ]; then \
          pytest_workers_args="$$pytest_workers_args --maxprocesses=$(PYTEST_MAXWORKERS)"; \
       fi \
    fi; \
    $(RUN) pytest $(PYTEST_COVERAGE_ARGS) $$pytest_workers_args $(PYTEST_ARGS) $(PYTEST_PATHS)


.PHONY: doctest
doctest: sync
	@$(MAKE) SPHINXBUILD="$(RUN) sphinx-build" -C docs doctest


.PHONY: mypy
mypy: sync
	@$(RUN) mypy --config-file mypy.ini -p xotl.tools


.PHONY: docs/build
docs/build: sync
	@$(MAKE) SPHINXBUILD="$(RUN) sphinx-build" -C docs html


DOC_SERVER_PORT ?= 6942

.PHONY: docs/browse
docs/browse: docs/build
	@$(RUN) python -m http.server  \
                   --directory $(PWD)/docs/build/html $(DOC_SERVER_PORT)



AUTO_RESTART := $(RUN) watchmedo auto-restart --directory docs --directory src --recursive --pattern '*.py' --pattern '*.rst' --

.PHONY: docs/serve
docs/serve:
	@$(AUTO_RESTART) $(MAKE) docs/browse
