#!/bin/bash
#
# edge device register with policy
# 
#

usage() {                      
  echo "Usage: $0 -e -k -m -c -f -r -v "
  echo "where "
  echo "   -e file path to environemnt veriables "
  echo "   -k framework tflite | vino | mvi | mvi_p100 | pth_cpu | pth_nano | pth_nx"
  echo "   -m file path to ML model file "
  echo "   -c Video source as a comma separated list of camera devices or all"
  echo "   -f Video source as a comma separated list of video files "
  echo "   -r Video source as a comma separated list of RTSP streams "
  echo "   -v View columns "
}

fn_chk_env() {
    if [ -z $HZN_ORG_ID ]; then 
	echo "Must set HZN_ORG_ID in ENV file "
	exit 1
    fi

    if [ -z $HZN_EXCHANGE_USER_AUTH ]; then 
	echo "Must set HZN_EXCHANGE_USER_AUTH in ENV file "
	exit 1
    fi

    if [ -z $APP_BIND_HORIZON_DIR ]; then 
	echo "Must set APP_BIND_HORIZON_DIR in ENV file "
	exit 1
    fi
}

fn_register_with_policy() {
    echo "Registering with ..."
    echo "   node_policy_${FMWK}.json"
    echo "   user_input_app_${FMWK}.json"
    echo ""

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
    # export later after copying files in bind directory"
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
    echo "Missing -k . Must provide one of the options to set framework vino | tflite | mvi | mvi_p100 | pth_cpu | pth_nano | pth_nx"
    echo ""
    usage
    exit 1
elif [ "$FMWK" = "tflite" ] || [ "$FMWK" = "vino" ] || [ "$FMWK" = "mvi" ] || [ "$FMWK" = "mvi_p100" ] || [ "$FMWK" = "pth_cpu" ] || [ "$FMWK" = "pth_nano" ] || [ "$FMWK" = "pth_nx" ]; then

    . $ENVVAR

    fn_chk_env

    export APP_MODEL_FMWK="$FMWK"

    if [ -z "$VIDEO_FILES" ]; then
	export APP_VIDEO_FILES="-"
    else
	APP_SAMPLE_VIDEO_DIR="$APP_BIND_HORIZON_DIR/sample/video"
	mkdir -p $APP_SAMPLE_VIDEO_DIR
	files=(${VIDEO_FILES//,/ })
	APP_SAMPLE_VIDEO_FILES=""
	echo ""

	for file in "${files[@]}"; do
	    SAMPLE_FILE="$(basename $file)"
	    echo "Copying $file to $APP_SAMPLE_VIDEO_DIR/$SAMPLE_FILE"
	    cp $file "$APP_SAMPLE_VIDEO_DIR/$SAMPLE_FILE"
	    if [ "$APP_SAMPLE_VIDEO_FILES"  == "" ]; then
		APP_SAMPLE_VIDEO_FILES="$APP_SAMPLE_VIDEO_DIR/$SAMPLE_FILE"
	    else
		APP_SAMPLE_VIDEO_FILES="$APP_SAMPLE_VIDEO_FILES,$APP_SAMPLE_VIDEO_DIR/$SAMPLE_FILE"
	    fi 
	done
	export APP_VIDEO_FILES="$APP_SAMPLE_VIDEO_FILES"
    fi

    if [ "$FMWK" = "tflite" ] || [ "$FMWK" = "mvi" ] || [ "$FMWK" = "pth_cpu" ] || [ "$FMWK" = "pth_nano" ] || [ "$FMWK" = "pth_nx" ]; then
	if [ ! -z $MI_MODEL ]; then 
	    if [ -f $MI_MODEL ]; then 
		APP_MODEL_SUB_DIR="ml/model/$FMWK"
		APP_MODEL_DIR="$APP_BIND_HORIZON_DIR/$APP_MODEL_SUB_DIR"

		export APP_MODEL_SUB_DIR="$APP_MODEL_SUB_DIR"
		export APP_MODEL_DIR="$APP_MODEL_DIR"

		echo ""
		echo "Using $APP_BIND_HORIZON_DIR as bind volume"
		echo ""
		echo "Creating directory $APP_MODEL_DIR"

		mkdir -p $APP_MODEL_DIR
		if [ -d $APP_MODEL_DIR ]; then 
		    export APP_MI_MODEL="$(basename $MI_MODEL)"
		    if [ "$FMWK" = "mvi" ]; then
			echo "Copying $MI_MODEL to $APP_MODEL_DIR/mi_mvi_model.zip"
			cp $MI_MODEL $APP_MODEL_DIR/mi_mvi_model.zip
		    else
			echo "Copying $MI_MODEL to $APP_MODEL_DIR"
			if [ -f "$APP_MODEL_DIR/default-$APP_MI_MODEL" ]; then 
			    echo "Skipping... File already exists."
			else
			    cp $MI_MODEL "$APP_MODEL_DIR/default-$APP_MI_MODEL"
			fi
		    fi
		else
		    echo "Failed creating directoy $APP_MODEL_DIR"
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
	export APP_MODEL_DIR="-"
	echo "Make sure that remote model detector is running"
    else
	export APP_MI_MODEL="Local model $FMWK"
	export APP_MODEL_DIR="-"
    fi
else
    echo ""
    echo "Must provide one of the options to set framework vino | tflite | mvi | mvi_p100 | pytorch"
    echo ""
    usage
    exit 1
fi

echo ""
echo "Application ML Model Framework: $FMWK"
if [ "$APP_CAMERAS" = "-" ]; then echo "Video Source: Camera:           None"; else echo "Video Source: Camera:           $APP_CAMERAS"; fi
if [ "$APP_VIDEO_FILES" = "-" ]; then echo "Video Source: File:             None"; else echo "Video Source: File:             $APP_VIDEO_FILES"; fi
if [ "$APP_RTSPS" = "-" ]; then echo "Video Source: RTSP:             None"; else echo "Video Source: RTSP Stream:      $APP_RTSPS"; fi
echo "View column:                    $APP_VIEW_COLUMNS"
echo ""

fn_register_with_policy

