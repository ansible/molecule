USER := retr0h
TAG := latest
IMAGE := $(USER)/molecule:$(TAG)

build:
	@echo "+ $@"
	sudo docker build \
		--rm=true \
		--no-cache \
		-t $(IMAGE) .


push:
	@echo "+ $@"
	sudo docker push $(IMAGE)
