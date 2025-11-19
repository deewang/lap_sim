.PHONY: default build build-image run-container setup clean clean-image clean-container clean-setup start bash

MAKEFLAGS += --no-print-directory

ifeq (,$(wildcard .env))
$(error ERROR: .env file not found! Use .env.example to create one.)
endif

-include .env
export

DOCKERFILE = Dockerfile

# helper to fail at runtime when a host-only target is invoked inside a container
define host_check
if [ -f /.dockerenv ]; then \
  echo "ERROR: '$(1)' must be run on the host, not inside a container"; \
  exit 1; \
fi
endef

# runtime check whether the named container exists (yes/no)
CONTAINER_EXISTS := $(shell docker ps -a --format '{{.Names}}' 2>/dev/null | grep -qw $(CONTAINER_NAME) && echo yes || echo no)

default: build

# PROJECT is the only environment variable that strictly must be passed
build-image:
	@$(call host_check,build-image)
	@echo "Building docker image $(IMAGE_NAME) using $(DOCKERFILE)"; \
	docker build -f $(DOCKERFILE) -t $(IMAGE_NAME) \
		--build-arg IMAGE_BASE=$(IMAGE_BASE) \
		--build-arg IMAGE_TAG=$(IMAGE_TAG) \
		--build-arg PROJECT=$(PROJECT) \
		--build-arg CHRONO_BRANCH=$(CHRONO_BRANCH) \
		--build-arg USERNAME=$(USERNAME) \
		.

run-container:
	@$(call host_check,run-container)
	@docker run -d --name $(CONTAINER_NAME) -v $(PWD):/home/fubc/chrono/lap_sim $(IMAGE_NAME)

setup:
	@$(call host_check,setup)
	@if ! docker image inspect $(IMAGE_NAME) >/dev/null 2>&1; then \
		make build-image; \
	else \
		echo "Image $(IMAGE_NAME) already exists, skipping build"; \
	fi
	@if ! docker ps -a --format '{{.Names}}' | grep -qw $(CONTAINER_NAME); then \
		echo "Creating container $(CONTAINER_NAME)"; \
		docker run -d --name $(CONTAINER_NAME) -v $(PWD):/home/fubc/chrono/lap_sim $(IMAGE_NAME); \
	else \
		echo "Container $(CONTAINER_NAME) already exists, skipping creation"; \
		make start; \
	fi

clean:
	@$(call host_check,clean)
	@make clean-container
	@make clean-image
	@echo "Cleaned up image $(IMAGE_NAME) and container $(CONTAINER_NAME)"

clean-image:
	@$(call host_check,clean-image)
	@docker rmi -f $(IMAGE_NAME)

clean-container:
	@$(call host_check,clean-container)
	@docker rm -f $(CONTAINER_NAME)

clean-setup:
	@$(call host_check,clean-setup)
	@make clean
	@make setup

bash:
	@$(call host_check,bash)
	@if ! docker ps -a --format '{{.Names}}' | grep -qw $(CONTAINER_NAME); then \
		echo "ERROR: Container $(CONTAINER_NAME) does not exist. Run 'make setup' or 'make run-container' first."; \
		exit 1; \
	fi
	@if docker ps --filter "name=^$(CONTAINER_NAME)$$" --format '{{.Names}}' | grep -qw $(CONTAINER_NAME); then \
		docker exec -it $(CONTAINER_NAME) /bin/bash; \
	else \
		echo "Starting container $(CONTAINER_NAME)"; \
		docker start $(CONTAINER_NAME) >/dev/null; \
		docker exec -it $(CONTAINER_NAME) /bin/bash; \
	fi

start:
	@$(call host_check,start)
	@if ! docker ps -a --format '{{.Names}}' | grep -qw $(CONTAINER_NAME); then \
		echo "ERROR: Container $(CONTAINER_NAME) does not exist. Run 'make setup' first."; \
		exit 1; \
	fi
	@docker start $(CONTAINER_NAME) >/dev/null
	@echo "Container $(CONTAINER_NAME) started in detached mode"

stop:
	@$(call host_check,stop)
	@if ! docker ps -a --format '{{.Names}}' | grep -qw $(CONTAINER_NAME); then \
		echo "ERROR: Container $(CONTAINER_NAME) does not exist."; \
		exit 1; \
	fi
	@docker stop $(CONTAINER_NAME) >/dev/null
	@echo "Container $(CONTAINER_NAME) stopped"

build:
	@if ! docker ps -a --format '{{.Names}}' | grep -qw $(CONTAINER_NAME); then \
		echo "ERROR: Container $(CONTAINER_NAME) does not exist. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "No project to build :("
