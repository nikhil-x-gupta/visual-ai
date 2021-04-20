#!/bin/sh

socat TCP4-LISTEN:7771,fork EXEC:./mms_service_config.sh


