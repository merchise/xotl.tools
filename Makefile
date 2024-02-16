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
	@$(RYE_EXEC) tox -e system-unit,system-greenlets
.PHONY: test

doctest:
	@$(RYE_EXEC) tox -e system-doctest
.PHONY: test

mypy:
	@$(RYE_EXEC) mypy -p xotl.tools --config mypy.ini
.PHONY: mypy

docs:
	make SPHINXBUILD="$(RYE_EXEC) sphinx-build" -C docs html
.PHONY: docs


CADDY_SERVER_PORT ?= 9999
caddy: docs
	@docker run --rm -p $(CADDY_SERVER_PORT):$(CADDY_SERVER_PORT) \
         -v $(PWD)/docs/build/html:/var/www -it caddy \
         caddy file-server --browse --listen :$(CADDY_SERVER_PORT) --root /var/www
.PHONY: caddy
