#!/bin/sh

socat TCP4-LISTEN:7778,fork EXEC:./mms_service.sh


