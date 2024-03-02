#!/bin/bash

. mms_inc.sh

MMS_ACTION=""
fn_parse_mms_request MMS_ACTION

# Initialize ESS query params and vars
fn_initialize_creds

#Set object type 
OBJECT_TYPE=$MMS_ACTION

#OBJECT_TYPE="mmsconfig"
#ACTION="unchanged"

OBJECT_VALUES=""
OBJECT_META_FILE=objects.meta.$OBJECT_TYPE
HTTP_CODE=$(curl -sSLw "%{http_code}" -o $OBJECT_META_FILE ${AUTH} ${CERT} $SOCKET $BASEURL/$OBJECT_TYPE) 
MESSAGE="OK"

if [ "$HTTP_CODE" == '200' ]; then 
    OBJS=("config.json")

    for OBJECT_ID in $OBJS
    do
	OBJECT=$(jq -r ".[] | select(.objectID == \"$OBJECT_ID\")" $OBJECT_META_FILE)
	DELETED=$(echo $OBJECT | jq -r  '.deleted')
	if [ "$DELETED" == "true" ]; then
	    # Handle the case in which MMS is telling us the config file was deleted
            HTTP_CODE=$(curl -sSLw "%{http_code}" -X PUT ${AUTH} ${CERT} $SOCKET $BASEURL/$OBJECT_TYPE/$OBJECT_ID/deleted)
            if [[ "$HTTP_CODE" != '200' && "$HTTP_CODE" != '204' ]]; then
		MESSAGE="Error:-Object-deletion"
	    fi
	    ACTION="deleted"
	else
	    ACTION="updated"
            # Read the new file from ESS
            HTTP_CODE=$(curl -sSLw "%{http_code}" -o $OBJECT_ID ${AUTH} ${CERT} $SOCKET $BASEURL/$OBJECT_TYPE/$OBJECT_ID/data)
            if [[ "$HTTP_CODE" != '200' ]]; then
		MESSAGE="Error:-Object-reading"
	    fi

            # Acknowledge that we got the new file, so it won't keep telling us
            HTTP_CODE=$(curl -sSLw "%{http_code}" -X PUT ${AUTH} ${CERT} $SOCKET $BASEURL/$OBJECT_TYPE/$OBJECT_ID/received)
            if [[ "$HTTP_CODE" != '200' && "$HTTP_CODE" != '204' ]]; then
		MESSAGE="Error:-Object-update-received"
	    fi

	    OBJECT_VALUES="["`cat $OBJECT_ID | jq -c`
	fi
    done
elif [ "$HTTP_CODE" == '404' ]; then 
    MESSAGE="$OBJECT_TYPE-not-found.Publish-at-least-one-object."
else
    MESSAGE="Unknown"
fi

if [ -z $OBJECT_VALUES ]; then OBJECT_VALUES="["; fi
OBJECT_VALUES=${OBJECT_VALUES}"]"

fn_output $HTTP_CODE $MESSAGE $ACTION $OBJECT_VALUES

