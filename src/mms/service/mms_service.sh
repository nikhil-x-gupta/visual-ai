#!/bin/bash

fn_parse_mms_request() {
    read request
    while /bin/true; do
	read header
	[ "$header" == $'\r' ] && break;
    done
    url="${request#GET /}"
    eval "$1='${url% HTTP/*}'"
}

MMS_ACTION=""
fn_parse_mms_request MMS_ACTION

OBJECT_TYPE=""
OBJECT_ID=""
if [ "$MMS_ACTION" = "mmsconfig" ]; then 
    OBJECT_TYPE="$HZN_DEVICE_ID.tflite-mms"
    OBJECT_ID=config.json
elif [ "$MMS_ACTION" = "mmsmodel" ]; then 
    OBJECT_TYPE="$HZN_DEVICE_ID.tflite-model-mms"
    OBJECT_ID=model.json
else
    OBJECT_TYPE="$HZN_DEVICE_ID.tflite-mms"
    OBJECT_ID=config.json
fi


USER=$(cat ${HZN_ESS_AUTH} | jq -r ".id")
PW=$(cat ${HZN_ESS_AUTH} | jq -r ".token")

AUTH="-u ${USER}:${PW}"
CERT="--cacert ${HZN_ESS_CERT}"
SOCKET="--unix-socket ${HZN_ESS_API_ADDRESS}"
BASEURL='https://localhost/api/v1/objects'

HTTP_CODE=$(curl -sSLw "%{http_code}" -o objects.meta ${AUTH} ${CERT} $SOCKET $BASEURL/$OBJECT_TYPE) 
if [[ "$HTTP_CODE" != '200' && "$HTTP_CODE" != '404' ]]; then echo "Error: HTTP code $HTTP_CODE from: curl -sSLw %{http_code} -o objects.meta ${AUTH} ${CERT} $SOCKET $BASEURL/$OBJECT_TYPE"; fi

OBJ_ID=$(jq -r ".[] | select(.objectID == \"$OBJECT_ID\") | .objectID" objects.meta)

ACTION="unchanged"
if [[ "$HTTP_CODE" == '200' && "$OBJ_ID" == $OBJECT_ID ]]; then
    # Handle the case in which MMS is telling us the config file was deleted
    DELETED=$(jq -r ".[] | select(.objectID == \"$OBJECT_ID\") | .deleted" objects.meta)  # if not found, jq returns 0 exit code, but blank value
    if [[ "$DELETED" == "true" ]]; then
	ACTION="deleted"
        # Acknowledge that we saw that it was deleted, so it won't keep telling us
        HTTP_CODE=$(curl -sSLw "%{http_code}" -X PUT ${AUTH} ${CERT} $SOCKET $BASEURL/$OBJECT_TYPE/$OBJECT_ID/deleted)
        if [[ "$HTTP_CODE" != '200' && "$HTTP_CODE" != '204' ]]; then echo "Error: HTTP code $HTTP_CODE from: curl -sSLw %{http_code} -X PUT ${AUTH} ${CERT} $SOCKET $BASEURL/$OBJECT_TYPE/$OBJECT_ID/deleted"; fi
        # Revert back to the original config file from the docker image
        cp ${OBJECT_ID}.original $OBJECT_ID
    else
	ACTION="updated"
        # Read the new file from MMS
        HTTP_CODE=$(curl -sSLw "%{http_code}" -o $OBJECT_ID ${AUTH} ${CERT} $SOCKET $BASEURL/$OBJECT_TYPE/$OBJECT_ID/data)
        if [[ "$HTTP_CODE" != '200' ]]; then echo "Error: HTTP code $HTTP_CODE from: curl -sSLw %{http_code} -o $OBJECT_ID ${AUTH} ${CERT} $SOCKET $BASEURL/$OBJECT_TYPE/$OBJECT_ID/data"; fi
        # Acknowledge that we got the new file, so it won't keep telling us
        HTTP_CODE=$(curl -sSLw "%{http_code}" -X PUT ${AUTH} ${CERT} $SOCKET $BASEURL/$OBJECT_TYPE/$OBJECT_ID/received)
        if [[ "$HTTP_CODE" != '200' && "$HTTP_CODE" != '204' ]]; then echo "Error: HTTP code $HTTP_CODE from: curl -sSLw %{http_code} -X PUT ${AUTH} ${CERT} $SOCKET $BASEURL/$OBJECT_TYPE/$OBJECT_ID/received"; fi

    fi
fi

OBJECT_VALUE=`cat $OBJECT_ID`
BODY="{\"mms_action\":\"${ACTION}\",\"value\":${OBJECT_VALUE}}" 

HEADERS="Content-Type: text/json; charset=ISO-8859-1"
HTTP="HTTP/1.1 200 OK\r\n${HEADERS}\r\n\r\n${BODY}\r\n"
echo -en $HTTP
