.PHONY: default build build-image run-container setup clean clean-image clean-container clean-setup start bash stop

MAKEFLAGS += --no-print-directory

ifeq (,$(wildcard .env))
$(error ERROR: .env file not found! Use .env.example to create one.)
endif

-include .env
export

COMPOSE_FILE = docker-compose.yml
SERVICE_NAME = chrono

# helper to fail at runtime when a host-only target is invoked inside a container
define host_check
if [ -f /.dockerenv ]; then \
  echo "ERROR: '$(1)' must be run on the host, not inside a container"; \
  exit 1; \
fi
endef

default: build

# Build the docker image using docker compose
build-image:
	@$(call host_check,build-image)
	@echo "Building docker image using $(COMPOSE_FILE)"; \
	docker compose -f $(COMPOSE_FILE) build

run-container:
	@$(call host_check,run-container)
	@docker compose -f $(COMPOSE_FILE) up -d

setup:
	@$(call host_check,setup)
	@CHRONO_EXISTS=$$(docker ps -a --format '{{.Names}}' | grep -qw $(PROJECT) && echo yes || echo no); \
	VNC_EXISTS=$$(docker ps -a --format '{{.Names}}' | grep -qw "$(COMPOSE)-vnc" && echo yes || echo no); \
	if [ "$$CHRONO_EXISTS" = "no" ] || [ "$$VNC_EXISTS" = "no" ]; then \
		echo "Creating and starting containers"; \
		docker compose -f $(COMPOSE_FILE) up -d; \
	else \
		echo "All containers already exist"; \
		CHRONO_RUNNING=$$(docker ps --format '{{.Names}}' | grep -qw $(PROJECT) && echo yes || echo no); \
		VNC_RUNNING=$$(docker ps --format '{{.Names}}' | grep -qw "$(COMPOSE)-vnc" && echo yes || echo no); \
		if [ "$$CHRONO_RUNNING" = "no" ] || [ "$$VNC_RUNNING" = "no" ]; then \
			echo "Starting containers"; \
			docker compose -f $(COMPOSE_FILE) start; \
		else \
			echo "All containers are already running"; \
		fi; \
	fi

clean:
	@$(call host_check,clean)
	@echo "Cleaning up containers and images"
	@docker compose -f $(COMPOSE_FILE) down --rmi all

clean-image:
	@$(call host_check,clean-image)
	@docker compose -f $(COMPOSE_FILE) down --rmi all

clean-container:
	@$(call host_check,clean-container)
	@docker compose -f $(COMPOSE_FILE) down

clean-setup:
	@$(call host_check,clean-setup)
	@make clean
	@make setup

bash:
	@$(call host_check,bash)
	@if ! docker ps -a --format '{{.Names}}' | grep -qw $(PROJECT); then \
		echo "ERROR: Container $(PROJECT) does not exist. Run 'make setup' or 'make run-container' first."; \
		exit 1; \
	fi
	@if docker ps --filter "name=^$(PROJECT)$$" --format '{{.Names}}' | grep -qw $(PROJECT); then \
		docker compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) /bin/bash; \
	else \
		echo "Starting container $(PROJECT)"; \
		docker compose -f $(COMPOSE_FILE) start $(SERVICE_NAME); \
		docker compose -f $(COMPOSE_FILE) exec $(SERVICE_NAME) /bin/bash; \
	fi

start:
	@$(call host_check,start)
	@if ! docker ps -a --format '{{.Names}}' | grep -qw $(PROJECT); then \
		echo "ERROR: Container $(PROJECT) does not exist. Run 'make setup' first."; \
		exit 1; \
	fi
	@docker compose -f $(COMPOSE_FILE) start $(SERVICE_NAME)
	@echo "Container $(PROJECT) started in detached mode"

stop:
	@$(call host_check,stop)
	@if ! docker ps -a --format '{{.Names}}' | grep -qw $(PROJECT); then \
		echo "ERROR: Container $(PROJECT) does not exist."; \
		exit 1; \
	fi
	@docker compose -f $(COMPOSE_FILE) stop $(SERVICE_NAME)
	@echo "Container $(PROJECT) stopped"

build:
	@if ! docker ps -a --format '{{.Names}}' | grep -qw $(PROJECT); then \
		echo "ERROR: Container $(PROJECT) does not exist. Run 'make setup' first."; \
		exit 1; \
	fi
	@echo "No project to build :("
