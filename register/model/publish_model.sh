#!/bin/bash
#
# MMS publish model script
# 

MODEL_ROOT_DIR=../model

usage() {                      
  echo "Usage: $0 -e -k -m -f -v "
  echo "where "
  echo "   -e Environemnt veriables full file path"
  echo "   -k Framework tflite | pth "
  echo "   -v ML model version"
# Not needed, they are built from k and v . Expect model-file-name and publish defintion file in fixed format
#  echo "   -f ML model file "
#  echo "   -m Model definition file full path"
}

#while getopts 'he:k:v:f:m:' option; do
while getopts 'he:k:v:' option; do
  case "$option" in
    h) usage
       exit 1
       ;;
    e) ENVVAR=$OPTARG
       ;;
    k) MODEL_FMWK=$OPTARG
       ;;
    v) MODEL_VERSION=$OPTARG
       ;;
#    f) MODEL_FILE=$OPTARG
#       ;;
#    m) MODEL_DEF_FILE=$OPTARG
#       ;;
    :) printf "missing argument for -%s\n" "$OPTARG" >&2
       usage
       exit 1
       ;;
    \?) printf "illegal option: -%s\n" "$OPTARG" >&2
       usage
       exit 1
       ;;
  esac
done
shift $((OPTIND - 1))

if [ -z $ENVVAR ]; then
    echo ""
    echo "Must provide ENV vars file. Needs HZN_ORG_ID, EDGE_OWNER, EDGE_DEPLOY"
    echo ""
    usage
    exit 1
else 
    if [ -z $MODEL_FMWK ]; then
	echo ""
	echo "Missing -k "
	echo "Must provide one framework  tflite | pth_cpu "
	echo ""
	usage
	exit 1
    else 
	if [ -z $MODEL_VERSION ]; then
	    echo ""
	    echo "Missing -v "
	    echo "Must provide model version "
	    echo ""
	    usage
	    exit 1
	else 
	    if [ -d "$MODEL_ROOT_DIR/$MODEL_FMWK/$MODEL_VERSION" ]; then
		MODEL_FILE="$MODEL_ROOT_DIR/$MODEL_FMWK/$MODEL_VERSION/$MODEL_FMWK-model-$MODEL_VERSION-mms.zip"
		if [ ! -f $MODEL_FILE ]; then
		    echo ""
		    echo "Must provide model file $MODEL_FILE"
		    echo ""
		    usage
		    exit 1
		else
		    MODEL_DEF_FILE="$MODEL_ROOT_DIR/$MODEL_FMWK/$MODEL_VERSION/$MODEL_FMWK.model.publish.definition.json"
		    if [ ! -f $MODEL_DEF_FILE ]; then
			echo ""
			echo "Must provide model definition file $MODEL_DEF_FILE"
			echo ""
			usage
			exit 1
		    else
			echo "Publish $MODEL_FILE using $MODEL_DEF_FILE"
			. $ENVVAR
			envsubst < $MODEL_DEF_FILE | jq
			read -p "Continue? (Y/N) " yn
			case $yn in
			    [Yy]* ) ;;
			    [Nn]* ) exit;;
			esac
			envsubst < $MODEL_DEF_FILE | hzn mms object publish -m- -f $MODEL_FILE
		    fi
		fi
	    else
		echo ""
		echo "No such directory $MODEL_ROOT_DIR/$MODEL_FMWK/$MODEL_VERSION"
		echo "Machine learning models must be specified in this directory."
		echo ""
		usage
		exit 1
	    fi
	fi
    fi
fi
