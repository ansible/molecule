USER := retr0h
TAG := latest
IMAGE := $(USER)/molecule:$(TAG)

clean:
	@echo "+ $@"
	rm -rf build/lib/
	rm -rf dist/

build: clean
	@echo "+ $@"
	git clean -d -x -f molecule/cookiecutter/
	./.tox/py27-ansible25-unit/bin/python setup.py sdist bdist_wheel
	./.tox/py36-ansible25-unit/bin/python setup.py sdist bdist_wheel

docker-build:
	@echo "+ $@"
	cd build && sudo docker build \
		--rm=true \
		--no-cache \
		-t $(IMAGE) .

push:
	./.tox/py27-ansible25-unit/bin/twine upload dist/* -r pypi

docker-push:
	@echo "+ $@"
	sudo docker push $(IMAGE)

.PHONY: build
