#!/bin/bash
#
# edge device register unregister pattern policy
# #
#

usage() {                      
  echo "Usage: $0 -e -k -r -u -p -l"
  echo "where "
  echo "   -e file path to environemnt veriables "
  echo "   -k framework tflite | vino | mvi"
  echo "   -r register "
  echo "   -u unregister "
  echo "   -p pattern based deployment "
  echo "   -l policy based deployment "
}

fn_chk_env() {
    if [ -z $HZN_ORG_ID ]; then 
	echo "Must set HZN_ORG_ID in ENV file "
    fi

    if [ -z $HZN_EXCHANGE_USER_AUTH ]; then 
	echo "Must set HZN_EXCHANGE_USER_AUTH in ENV file "
    fi
}

fn_register_with_policy() {
    echo "Registering with ... "
    echo "   node_policy_${FMWK}.json"
    echo "   user_input_app_${FMWK}.json"

    . $envvar

    fn_chk_env

    hzn exchange node create -n $HZN_EXCHANGE_NODE_AUTH
    hzn register --policy=node_policy_${FMWK}.json --input-file user_input_app_${FMWK}.json
}

fn_register_with_mms_pattern() {
    echo "Registering with pattern... "

    . $envvar

    fn_chk_env

    ARCH=`hzn architecture`

    hzn exchange node create -n $HZN_EXCHANGE_NODE_AUTH
    hzn register --pattern "${HZN_ORG_ID}/pattern-${EDGE_OWNER}.${EDGE_DEPLOY}.mms-${ARCH}" --input-file user-input-app.json --policy=node_policy_privileged.json
}

fn_register_with_pattern() {
    echo "Registering with pattern... "

    . $envvar

    fn_chk_env

    ARCH=`hzn architecture`

    hzn exchange node create -n $HZN_EXCHANGE_NODE_AUTH
    hzn register --pattern "${HZN_ORG_ID}/pattern-${EDGE_OWNER}.${EDGE_DEPLOY}.tflite-${ARCH}" --input-file user-input-app.json --policy=node_policy_privileged.json
}

fn_unregister() {
    echo "Un-registering... "

    . $envvar

    fn_chk_env

    hzn unregister -vrD
}

while getopts 'e:k:rlupm' option; do
  case "$option" in
    h) usage
       exit 1
       ;;
    e) envvar=$OPTARG
       ;;
    k) FMWK=$OPTARG
       ;;
    r) register=1
       ;;
    l) policy=1
       ;;
    u) unregister=1
       ;;
    p) pattern=1
       ;;
    m) mmspattern=1
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

if [ -z $envvar ]; then
    echo ""
    echo "Must provide one of the options to set ENV vars ENV_HZN_DEV, ENV_HZN_DEMO etc"
    echo ""
    usage
    exit 1
fi

if [ -z $FMWK ]; then
    echo ""
    echo "Must provide one of the options to set framework vino | tflite | mvi"
    echo ""
    usage
    exit 1
elif [ "$FMWK" = "tflite" ] || [ "$FMWK" = "vino" ] || [ "$FMWK" = "mvi" ]; then
    echo "Framework $FMWK"
else
    echo ""
    echo "Must provide one of the options to set framework vino | tflite | mvi"
    echo ""
    usage
    exit 1
fi

if [ ! -z $register ]; then
    if [ ! -z $pattern ]; then
	fn_register_with_pattern
    elif [ ! -z $mmspattern ]; then
	fn_register_with_mms_pattern
    elif [ ! -z $policy ]; then
	fn_register_with_policy
    else
       echo "Must provide one of the options -p or -l"
       usage
       exit 1
    fi
elif [ ! -z $unregister ]; then
    fn_unregister
else
    echo "Must provide one of the options -r or -u"
    usage
    exit 1
fi


