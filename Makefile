# Make all targets .PHONY
.PHONY: $(shell sed -n -e '/^$$/ { n ; /^[^ .\#][^ ]*:/ { s/:.*$$// ; p ; } ; }' $(MAKEFILE_LIST))

include .envs/.app
export

SHELL = /usr/bin/env bash
USER_NAME = $(shell whoami)
BUILD_POETRY_LOCK = /home/$(USER_NAME)/poetry.lock.build

CONTAINER_NAME = cybulde-data
SERVICE_NAME = app

DIRS_TO_VALIDATE = cybulde

ifeq (, $(shell which docker-compose))
	DOCKER_COMPOSE_COMMAND = docker compose
else
	DOCKER_COMPOSE_COMMAND = docker-compose
endif

DOCKER_COMPOSE_RUN = $(DOCKER_COMPOSE_COMMAND) run --rm $(SERVICE_NAME)
DOCKER_COMPOSE_EXEC = $(DOCKER_COMPOSE_COMMAND) exec $(SERVICE_NAME)

## Version data
version-data: up
	$(DOCKER_COMPOSE_EXEC) python ./cybulde/version_data.py

## Get raw data
get-raw-data: up
	$(DOCKER_COMPOSE_EXEC) python ./cybulde/get_raw_data.py

## Process raw data
process-data: up
	$(DOCKER_COMPOSE_EXEC) python ./cybulde/process_data.py

## Starts jupyter lab
notebook: up
	$(DOCKER_COMPOSE_EXEC) jupyter-lab --ip 0.0.0.0 --port 8888 --no-browser

## Sort imports with isort
sort: up
	$(DOCKER_COMPOSE_EXEC) isort --atomic $(DIRS_TO_VALIDATE)

## Format code with black
format: up
	$(DOCKER_COMPOSE_EXEC) black $(DIRS_TO_VALIDATE)

## Format and sort
format-and-sort: format sort

## Lint using flake8
lint: up
	$(DOCKER_COMPOSE_EXEC) flake8 $(DIRS_TO_VALIDATE)

## Check type annotations with mypy
check-type-annotations: up
	$(DOCKER_COMPOSE_EXEC) mypy $(DIRS_TO_VALIDATE)

## Builds docker image
build:
	$(DOCKER_COMPOSE_COMMAND) build $(SERVICE_NAME)

build-for-dependencies:
	rm -f *.lock
	$(DOCKER_COMPOSE_COMMAND) build $(SERVICE_NAME)

## Runs the docker container
up:
	@$(DOCKER_COMPOSE_COMMAND) up -d --remove-orphans

down:
	@$(DOCKER_COMPOSE_COMMAND) down

## Opens an interactive shell in the docker container
exec-in: up
	@docker exec -it $(CONTAINER_NAME) bash

lock-dependencies: build-for-dependencies
	$(DOCKER_COMPOSE_RUN) bash -c "if [ -e $(BUILD_POETRY_LOCK) ]; then cp $(BUILD_POETRY_LOCK) ./poetry.lock; else poetry lock; fi"

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=36 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
