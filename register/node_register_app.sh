#!/bin/bash
#
# edge device register with policy
# 
#

usage() {                      
  echo "Usage: $0 -e -k -m -c -f -r -v "
  echo "where "
  echo "   -e file path to environemnt veriables "
  echo "   -k framework tflite | vino | mvi | mvi_p100 | pth_cpu | pth_gpu"
  echo "   -m file path to ML model file "
  echo "   -c Video source as a comma separated list of camera devices or all"
  echo "   -f Video source as a comma separated list of video files "
  echo "   -r Video source as a comma separated list of RTSP streams "
  echo "   -v View columns "
}

fn_chk_env() {
    if [ -z $HZN_ORG_ID ]; then 
	echo "Must set HZN_ORG_ID in ENV file "
    fi

    if [ -z $HZN_EXCHANGE_USER_AUTH ]; then 
	echo "Must set HZN_EXCHANGE_USER_AUTH in ENV file "
    fi

    if [ -z $APP_BIND_HORIZON_DIR ]; then 
	echo "Must set APP_BIND_HORIZON_DIR in ENV file "
    fi
}

fn_register_with_policy() {
    echo "Registering with ..."
    echo "   node_policy_${FMWK}.json"
    echo "   user_input_app_${FMWK}.json"

    hzn exchange node create -n $HZN_EXCHANGE_NODE_AUTH
    hzn register --policy=node_policy_${FMWK}.json --input-file user_input_app_${FMWK}.json
}

while getopts 'e:k:m:c:f:r:v:' option; do
  case "$option" in
    h) usage
       exit 1
       ;;
    e) ENVVAR=$OPTARG
       ;;
    k) FMWK=$OPTARG
       ;;
    m) MI_MODEL=$OPTARG
       ;;
    c) CAMERAS=$OPTARG
       ;;
    f) VIDEO_FILES=$OPTARG
       ;;
    r) RTSPS=$OPTARG
       ;;
    v) VIEW_COLUMNS=$OPTARG
       ;;
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

if [ -z "$CAMERAS" ]; then
    export APP_CAMERAS="-"
else
    if [ "$CAMERAS" = "all" ]; then
	export APP_CAMERAS="all"
    else
	devices=(${CAMERAS//,/ })
	for device in "${devices[@]}"; do
	    if [[ ! "$device" =~ ^[0-9]+$ ]]; then 
		echo "Not an integer $device. Must be an Integer to identifying one or more of /dev/video"
		usage
		exit 1
	    fi
	done
	export APP_CAMERAS="$CAMERAS"
    fi
fi

if [ -z "$VIDEO_FILES" ]; then
    export APP_VIDEO_FILES="-"
else
    files=(${VIDEO_FILES//,/ })
    for file in "${files[@]}"; do
	if [ ! -f $file ]; then
	    echo "File does not exist $file. Provide a valid file name "
	    usage
	    exit 1
	fi
    done
    export APP_VIDEO_FILES="$VIDEO_FILES"
fi

if [ -z "$RTSPS" ]; then export APP_RTSPS="-"; else export APP_RTSPS="$RTSPS"; fi

if [ -z "$VIEW_COLUMNS" ]; then export APP_VIEW_COLUMNS=1; else export APP_VIEW_COLUMNS="$VIEW_COLUMNS"; fi

if [ -z $ENVVAR ]; then
    echo ""
    echo "Must provide one of the options to set ENV vars ENV_HZN_DEV, ENV_HZN_DEMO etc"
    echo ""
    usage
    exit 1
fi

if [ -z "$CAMERAS" ] && [ -z "$VIDEO_FILES" ] && [ -z "$RTSPS" ] ; then
    echo ""
    echo "Must provide one of the options -c -f -r "
    echo ""
    usage
    exit 1
fi

if [ -z $FMWK ]; then
    echo ""
    echo "Missing -k . Must provide one of the options to set framework vino | tflite | mvi | mvi_p100 | pth_cpu | pth_gpu"
    echo ""
    usage
    exit 1
elif [ "$FMWK" = "tflite" ] || [ "$FMWK" = "vino" ] || [ "$FMWK" = "mvi" ] || [ "$FMWK" = "mvi_p100" ] || [ "$FMWK" = "pth_cpu" ] || [ "$FMWK" = "pth_gpu" ]; then

    . $ENVVAR

    fn_chk_env

    if [ "$FMWK" = "tflite" ] || [ "$FMWK" = "mvi" ] || [ "$FMWK" = "pth_cpu" ] || [ "$FMWK" = "pth_gpu" ]; then
	if [ ! -z $MI_MODEL ]; then 
	    if [ -f $MI_MODEL ]; then 
		MODEL_DIR="$APP_BIND_HORIZON_DIR/ai/mi/model/$FMWK"
		echo "Creating directory $MODEL_DIR"
		mkdir -p $MODEL_DIR
		if [ -d $MODEL_DIR ]; then 
		    export APP_MI_MODEL="$(basename $MI_MODEL)"
		    if [ "$FMWK" = "mvi" ]; then
			echo "Copying $MI_MODEL $MODEL_DIR/mi_mvi_model.zip"
			cp $MI_MODEL $MODEL_DIR/mi_mvi_model.zip
		    else
			echo "Copying $MI_MODEL to $MODEL_DIR"
			cp $MI_MODEL "$MODEL_DIR/default-$APP_MI_MODEL"
		    fi
		else
		    echo "Failed creating directoy $MODEL_DIR"
		    echo "Provide 777 privilege to $APP_BIND_HORIZON_DIR directory so that model files can be copied."
		    exit 1
		fi
	    else
		echo "Model file $MI_MODEL does not exist."
		exit 1
	    fi
	else
	    echo "For $FMWK, must provide a valid ML model using -m option."
	    exit 1
	fi
    elif [ "$FMWK" = "mvi_p100" ]; then
	export APP_MI_MODEL="Remote model"
	echo "Make sure that remote model detector is running"
    else
	export APP_MI_MODEL="Local model $FMWK"
    fi
else
    echo ""
    echo "Must provide one of the options to set framework vino | tflite | mvi | mvi_p100 | pytorch"
    echo ""
    usage
    exit 1
fi

echo "Application ML Model Framework: $FMWK"
if [ "$APP_CAMERAS" != "-" ]; then echo "Video Source: Cameras: $APP_CAMERAS"; fi
if [ "$APP_VIDEO_FILES" != "-" ]; then echo "Video Source: Files: $APP_VIDEO_FILES"; fi
if [ "$APP_RTSPS" != "-" ]; then echo "Video Source: RTSP Streams: $APP_RTSPS"; fi
echo "View column: $APP_VIEW_COLUMNS"
echo "Application bind directory: $APP_BIND_HORIZON_DIR"

fn_register_with_policy

