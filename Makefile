DIR := ${CURDIR}
USER := retr0h
TAG := latest
IMAGE := $(USER)/molecule:$(TAG)

build:
	@echo "+ $@"
	docker build -t $(IMAGE) .

push:
	@echo "+ $@"
	docker push $(IMAGE)
