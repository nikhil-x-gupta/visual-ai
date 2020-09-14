#
# Makefile: A tensorflow lite and OpenCV based videostream object classification
#

# Checks required environment variables
-include env.check.mk

export ARCH ?= $(shell hzn architecture)

all: publish deploy-policy

publish: publish-http publish-mms publish-tflite 

publish-http:
	make -C src/http
	make -C src/http push
	make -C src/http publish-service

publish-mms:
	make -C src/mms
	make -C src/mms push
	make -C src/mms publish-service

publish-tflite:
	make -C src/tflite
	make -C src/tflite push
	make -C src/tflite publish-service

deploy-policy:
	make -C src/mms deploy-policy
	make -C src/tflite deploy-policy

