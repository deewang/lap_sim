.PHONY: default build build-image run-container clean clean-build start

MAKEFLAGS += --no-print-directory

# Check if .env file exists at the start
ifeq (,$(wildcard .env))
$(error ERROR: .env file not found! Use .env.example to create one.)
endif

# Load environment variables from .env file if it exists
-include .env
export

DOCKERFILE = Dockerfile

default: build

build-image:
	@echo "Building docker image $(IMAGE_NAME) using $(DOCKERFILE)"; \
	docker build -f $(DOCKERFILE) -t $(IMAGE_NAME) \
		--build-arg IMAGE_BASE=$(IMAGE_BASE) \
		--build-arg IMAGE_TAG=$(IMAGE_TAG) \
		--build-arg PROJECT=$(PROJECT) \
		--build-arg CHRONO_BRANCH=$(CHRONO_BRANCH) \
		--build-arg USERNAME=$(USERNAME) \
		.

run-container:
	@docker run --name $(CONTAINER_NAME) -v $(PWD):/home/fubc/chrono/lap_sim $(IMAGE_NAME)

build:
	@if ! docker image inspect $(IMAGE_NAME) >/dev/null 2>&1; then \
		make build-image; \
	else \
		echo "Image $(IMAGE_NAME) already exists, skipping build"; \
	fi
	@if ! docker ps -a --format '{{.Names}}' | grep -qw $(CONTAINER_NAME); then \
		echo "Creating container $(CONTAINER_NAME)"; \
		docker run --name $(CONTAINER_NAME) -v $(PWD):/home/fubc/chrono/lap_sim -it $(IMAGE_NAME) /bin/bash; \
	else \
		echo "Container $(CONTAINER_NAME) already exists, skipping creation"; \
		make start; \
	fi

clean:
	@make clean-container
	@make clean-image
	@echo "Cleaned up image $(IMAGE_NAME) and container $(CONTAINER_NAME)"

clean-image:
	@docker rmi -f $(IMAGE_NAME)

clean-container:
	@docker rm -f $(CONTAINER_NAME)

clean-build:
	@make clean
	@make build

start:
	@echo "Starting container $(CONTAINER_NAME)"
	@docker start -ai $(CONTAINER_NAME)
