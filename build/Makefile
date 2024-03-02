#
# Makefile: A tensorflow lite, OpenVINO, MVI, Pytorch  and OpenCV based videostream object classification
#

# Checks required environment variables
-include env.check.mk

export ARCH ?= $(shell hzn architecture)

ifeq ($(ARCH),arm64)
all: tflite-all pth-all publish-pth-nano publish-pth-nx deploy-policy-pth-nano deploy-policy-pth-nx
else
all: arch-all
endif

arch-all: publish-all deploy-policy-all

tflite-all: publish-http publish-mms-config publish-mms-model publish-tflite deploy-policy-tflite

pth-all: publish-http publish-mms-config publish-mms-model publish-pth-cpu deploy-policy-pth-cpu

vino-all: publish-http publish-mms-config publish-mms-model publish-vino deploy-policy-vino

mvi-all: publish-http publish-mms-config publish-mms-model publish-mvi deploy-policy-mvi

publish-all: publish-http publish-mms-config publish-mms-model publish-tflite publish-vino publish-mvi publish-pth-cpu

publish-http:
	make -C src/http build
	make -C src/http push
	make -C src/http publish-service

publish-mms-config:
	make -C src/mms config-build
	make -C src/mms config-push
	make -C src/mms config-publish-service

publish-mms-model:
	make -C src/mms model-build
	make -C src/mms model-push
	make -C src/mms model-publish-service

publish-tflite:
	make -C src/infer tflite-build
	make -C src/infer tflite-push
	make -C src/infer tflite-publish-service

publish-pth-cpu:
	make -C src/infer pth-cpu-build
	make -C src/infer pth-cpu-push
	make -C src/infer pth-cpu-publish-service

publish-pth-nano:
	make -C src/infer pth-nano-build
	make -C src/infer pth-nano-push
	make -C src/infer pth-nano-publish-service

publish-pth-nx:
	make -C src/infer pth-nx-build
	make -C src/infer pth-nx-push
	make -C src/infer pth-nx-publish-service

publish-vino:
	make -C src/infer vino-build
	make -C src/infer vino-push
	make -C src/infer vino-publish-service

publish-mvi:
	make -C src/infer model-mvi-publish-service 
	make -C src/infer model-mvi-p100-publish-service
	make -C src/infer model-mvi-p100-publish-pattern
	make -C src/infer mi-mvi-build 
	make -C src/infer mi-mvi-push
	make -C src/infer mi-mvi-publish-service
	make -C src/infer mi-mvi-p100-publish-service

deploy-policy-all:
	make -C src/mms config-deploy-policy
	make -C src/mms model-deploy-policy
	make -C src/infer tflite-deploy-policy
	make -C src/infer pth-cpu-deploy-policy
	make -C src/infer vino-deploy-policy
	make -C src/infer mi-mvi-deploy-policy
	make -C src/infer mi-mvi-p100-deploy-policy

deploy-policy-tflite:
	make -C src/mms config-deploy-policy
	make -C src/mms model-deploy-policy
	make -C src/infer tflite-deploy-policy

deploy-policy-pth-cpu:
	make -C src/mms config-deploy-policy
	make -C src/mms model-deploy-policy
	make -C src/infer pth-cpu-deploy-policy

deploy-policy-pth-nano:
	make -C src/mms config-deploy-policy
	make -C src/mms model-deploy-policy
	make -C src/infer pth-nano-deploy-policy

deploy-policy-pth-nx:
	make -C src/mms config-deploy-policy
	make -C src/mms model-deploy-policy
	make -C src/infer pth-nx-deploy-policy

deploy-policy-vino:
	make -C src/mms config-deploy-policy
	make -C src/mms model-deploy-policy
	make -C src/infer vino-deploy-policy

deploy-policy-mvi:
	make -C src/mms config-deploy-policy
	make -C src/mms model-deploy-policy
	make -C src/infer mi-mvi-deploy-policy
	make -C src/infer mi-mvi-p100-deploy-policy


