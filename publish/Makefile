#
# Makefile: A tensorflow lite and OpenCV based videostream object classification
#

# Checks required environment variables
-include env.check.mk

export ARCH ?= $(shell hzn architecture)

all: publish deploy-policy

publish: publish-http publish-mms publish-tflite publish-vino deploy-policy

publish-http:
	make -C src/http
	make -C src/http push
	make -C src/http publish-service

publish-mms:
	make -C src/mms
	make -C src/mms push
	make -C src/mms publish-service

publish-tflite:
	make -C src/infer tflite-build
	make -C src/infer tflite-push
	make -C src/infer tflite-publish-service

publish-vino:
	make -C src/infer vino-build
	make -C src/infer vino-push
	make -C src/infer vino-publish-service

deploy-policy:
	make -C src/mms deploy-policy
	make -C src/infer tflite-deploy-policy
	make -C src/infer vino-deploy-policy

