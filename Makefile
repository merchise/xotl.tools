RYE_EXEC ?= rye run
PYTHON_VERSION ?= 3.12
PATH := $(HOME)/.rye/shims:$(PATH)

SHELL := /bin/bash
PYTHON_FILES := $(shell find src/$(PROJECT_NAME) -type f -name '*.py' -o -name '*.pyi')

USE_UV ?= true
install:
	@uv --version || curl -LsSf https://astral.sh/uv/install.sh | sh
	@rye self update || curl -sSf https://rye-up.com/get | bash
	@rye config --set-bool behavior.use-uv=$(USE_UV)
	@rye pin --relaxed $(PYTHON_VERSION)
	@rye sync --no-lock
	@cp requirements-dev.lock requirements-dev-py$$(echo $(PYTHON_VERSION) | sed "s/\.//").lock
.PHONY: install


sync:
	@rye config --set-bool behavior.use-uv=$(USE_UV)
	@rye pin --relaxed $(PYTHON_VERSION)
	@rye sync --no-lock
.PHONY: sync

lock:
	@rye config --set-bool behavior.use-uv=$(USE_UV)
	@rye pin --relaxed $(PYTHON_VERSION)
	@rye sync
	@cp requirements-dev.lock requirements-dev-py$$(echo $(PYTHON_VERSION) | sed "s/\.//").lock
.PHONY: lock

build: sync
	@rye config --set-bool behavior.use-uv=$(USE_UV)
	@rye build
.PHONY: build


format:
	@$(RYE_EXEC) ruff check --fix src/ tests/
	@$(RYE_EXEC) ruff format src/ tests/
	@$(RYE_EXEC) isort src/ tests/
.PHONY: format

lint:
	@$(RYE_EXEC) ruff check src/ tests/
	@$(RYE_EXEC) ruff format --check src/ tests/
	@$(RYE_EXEC) isort --check src/ tests/
.PHONY: lint

test:
	@$(RYE_EXEC) tox -e system-unit,system-greenlets -- -n auto
.PHONY: test

doctest:
	@$(RYE_EXEC) tox -e system-doctest
.PHONY: test

mypy:
	@$(RYE_EXEC) tox -e system-staticcheck
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
