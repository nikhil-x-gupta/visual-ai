#
# Makefile: A tensorflow lite, OpenVINO and OpenCV based videostream object classification
#

# Checks required environment variables
-include env.check.mk

export ARCH ?= $(shell hzn architecture)

ifeq ($(ARCH),arm64)
all: tflite-all
else
all: arch-all
endif

arch-all: publish-all deploy-policy-all

tflite-all: publish-http publish-mms publish-tflite deploy-policy-tflite

vino-all: publish-http publish-mms publish-vino deploy-policy-vino

publish-all: publish-http publish-mms publish-tflite publish-vino publish-mvi-fm publish-mvi-hv

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

publish-mvi-fm:
	make -C src/infer max-mvi-fm-publish-service
	make -C src/infer mvi-fm-build
	make -C src/infer mvi-fm-push
	make -C src/infer mvi-fm-publish-service

publish-mvi-hv:
	make -C src/infer max-mvi-hv-publish-service
	make -C src/infer mvi-hv-build
	make -C src/infer mvi-hv-push
	make -C src/infer mvi-hv-publish-service

deploy-policy-all:
	make -C src/mms deploy-policy
	make -C src/infer tflite-deploy-policy
	make -C src/infer vino-deploy-policy
	make -C src/infer mvi-fm-deploy-policy
	make -C src/infer mvi-hv-deploy-policy

deploy-policy-tflite:
	make -C src/mms deploy-policy
	make -C src/infer tflite-deploy-policy

deploy-policy-vino:
	make -C src/mms deploy-policy
	make -C src/infer vino-deploy-policy

deploy-policy-mvi:
	make -C src/mms deploy-policy
	make -C src/infer mvi-deploy-policy

deploy-policy-mvi-hv:
	make -C src/mms deploy-policy
	make -C src/infer mvi-hv-deploy-policy

