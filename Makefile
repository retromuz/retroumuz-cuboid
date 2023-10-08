

PATH_DEPLOY=.deploy
APP_NAME=cuboid
CONTAINER_PORT=8080
BUILD_VERSION_BASE?=0.0.1
BUILD_VERSION?=0.0.1
IMG_PROVIDER=retroumuz

export IMAGE_NAME_BASE=${IMG_PROVIDER}/${APP_NAME}-base:${BUILD_VERSION_BASE}
export IMAGE_NAME=${IMG_PROVIDER}/${APP_NAME}:${BUILD_VERSION}

env-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi

shell-base:
	@echo "make shell-base"
	docker-compose -f ${PATH_DEPLOY}/docker-compose.yml run --rm ${APP_NAME}-base /bin/bash
.PHONY: shell-base


shell:
	@echo "make shell"
	docker-compose -f ${PATH_DEPLOY}/docker-compose.yml run --rm ${APP_NAME} /bin/bash
.PHONY: shell

dockerBaseBuild: 
	@echo "make dockerBaseBuild"
	docker build -f Dockerfile.base . --no-cache -t ${IMAGE_NAME_BASE}
.PHONY: dockerBaseBuild

dockerBuild:
	@echo "make dockerBuild"
	docker build -f Dockerfile . --no-cache -t ${IMAGE_NAME}
	# docker push ${IMAGE_NAME}
.PHONY: dockerBuild