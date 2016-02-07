.PHONY: image

IMAGE_NAME ?= codeclimate/codeclimate-vint

image:
	docker build -t $(IMAGE_NAME) .
