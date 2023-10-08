

PATH_DEPLOY=.deploy
APP_NAME=retroumuz-cuboid
CONTAINER_PORT=8080
BUILD_VERSION?=0.0.1

export IMAGE_NAME=${APP_NAME}:${BUILD_VERSION}

env-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi

shell-base:
	@echo "make shell-base"
	docker-compose -f ${PATH_DEPLOY}/docker-compose.yml run --rm cuboid-base /bin/bash
.PHONY: shell-base


shell:
	@echo "make shell"
	docker-compose -f ${PATH_DEPLOY}/docker-compose.yml run --rm cuboid /bin/bash
.PHONY: shell

dockerBuild: 
	@echo "make dockerBuild"
	docker build -f Dockerfile . --no-cache -t ${IMAGE_NAME}
.PHONY: dockerBuild

dockerPush:
	@echo "make dockerPush"
	docker push ${IMAGE_NAME}
.PHONY: dockerPush