#!/bin/bash

if [[ $USER == 'root' ]]
then
  echo "You run script from root or sudo. Run from user. Exit"
  exit 1
fi

BUNDLE_DIR=$HOME'/hce-node-bundle'
JSONDIR=$BUNDLE_DIR'/api/python/data/ftests/real_time_api_tests/simple'

for ARG in $*
do
    case $ARG in
    'directory='*|'-directory='*|'--directory='*) JSONDIR=$(echo $ARG | awk -F\= '{print $2}');;
    'help'|'-help'|'--help'|*) echo "Usage: $0 [directory='custom_dir' or -directory='custom_dir' or --directory='custom_dir': custom directory with jsons and out files] [help or -help or --help: this help]"
        exit 1;;
    esac
done

COMPARATOR=$BUNDLE_DIR'/api/php/bin/formats-standards-comparator.php'
JSON_FIELD=$BUNDLE_DIR'/api/python/bin/json-field.py'
INI_FILE='../ini/dc-client.ini'
LOG_DIR='/tmp/TBS'
FIELD_PATH='itemsList:0:itemObject:0:processedContents:0:buffer'
FIELD_PATH_START='itemsList:0:itemObject:'
FIELD_PATH_END=':processedContents:0:buffer'
FORMAT_PATH='items:0:properties:template:templates:0:output_format:name'
TYPE_PATH='items:0:properties:template:templates:0:output_format:type'
IGNORED_FIELDS=('0:pubdate')
SITE_URL='http://127.0.0.1'
CANONICALIZE_0='index1_template_based_canonicalizeURLs_0_url_all_response_json.json'
CANONICALIZE_1='index1_template_based_canonicalizeURLs_1_url_all_response_json.json'
CANONICALIZE_IMG_PATH='items:0:properties:template:templates:0:tags:image:0:canonicalizeURLs'
CANONICALIZE_LINK_PATH='items:0:properties:template:templates:0:tags:link:0:canonicalizeURLs'
FAIL=()
SUCCESS=()

RED='\e[1;31m'
BLUE='\e[1;34m'
TUR='\e[1;36m'
YEL='\e[1;33m'
DEF='\e[0m'

if [[ ! -d $JSONDIR ]]
then
    echo -e $RED"Directory "$JSONDIR" not found. Exit"$DEF
    exit 1
fi
if [[ ! -f $COMPARATOR ]]
then
    echo -e $RED"File "$COMPARATOR" not found. Exit"$DEF
    exit 1
fi

if [[ ! -d $LOG_DIR ]]
then
    mkdir $LOG_DIR
fi

TEMPFILE=$(mktemp /tmp/$(basename $0).XXXXX)
trap "rm -f $TEMPFILE" 0 1 2 5 15


function checkIgnored() {
    # $1 - input to check
    echo -n > $TEMPFILE
    echo "$1" | while read LINE
    do
        for I in "${IGNORED_FIELDS[@]}"
        do
            if [[ ! "$LINE" =~ "$I" ]]
            then
                echo -e $JSONFILE" -$RED fail, $LINE"$DEF >> $TEMPFILE
            fi
        done
    done
}

cd $BUNDLE_DIR/api/python/bin

for OUT in $(ls $JSONDIR | grep '.json.out')
do
    JSONFILE=${OUT%.out}

    if [[ $($JSON_FIELD  --field=$TYPE_PATH < $JSONDIR/$JSONFILE) == 'rss' ]]
    then
        MAXCOUNT=2
        TYPE='rss'
    else
        MAXCOUNT=0
        TYPE='news'
    fi

    for COUNT in $(seq 0 $MAXCOUNT)
    do
        FORMAT=$($JSON_FIELD  --field=$FORMAT_PATH < $JSONDIR/$JSONFILE)

        ./dc-client.py --config=$INI_FILE --command=BATCH --file=$JSONDIR/$JSONFILE > $TEMPFILE
        cp $TEMPFILE /tmp/test.json.out

        CHECK=$($COMPARATOR --original=$JSONDIR/$OUT --compare=$TEMPFILE --path=$FIELD_PATH_START$COUNT$FIELD_PATH_END --format=$FORMAT --input_type=$TYPE)

        if [[ -z $CHECK ]]
        then
            SUCCESS+=("$JSONFILE")
            echo -e $JSONFILE" -$BLUE success $DEF"
        else
            checkIgnored "$CHECK"
            CHECK_LINE=$(wc -l $TEMPFILE | awk '{print $1}')
            if [[ $CHECK_LINE -gt 0 ]]
            then
                FAIL+=("$JSONFILE")
                echo -e $JSONFILE" -$RED fail $DEF, $CHECK"
            else
                SUCCESS+=("$JSONFILE")
                echo -e $JSONFILE" -$BLUE success $DEF"
            fi
        fi

    done
done

# CHECK CANONIZATION. CANONIZATION=0 #
if [[ -f $JSONDIR/$CANONICALIZE_0 || -f $JSONDIR/$CANONICALIZE_1 ]]
then
    ./dc-client.py --config=$INI_FILE --command=BATCH --file=$JSONDIR/$CANONICALIZE_0 > $TEMPFILE
    CANONICALIZE_OUT=$($JSON_FIELD  --field=$FIELD_PATH < $TEMPFILE | base64 -d)
    CANONICALIZE_OUT_LINK_0=$($JSON_FIELD  --field='0:link' <<< $CANONICALIZE_OUT)
    CANONICALIZE_OUT_IMAGE_0=$($JSON_FIELD  --field='0:image' <<< $CANONICALIZE_OUT)

    # CHECK CANONIZATION. CANONIZATION=1 #
    ./dc-client.py --config=$INI_FILE --command=BATCH --file=$JSONDIR/$CANONICALIZE_1 > $TEMPFILE
    CANONICALIZE_OUT=$($JSON_FIELD  --field=$FIELD_PATH < $TEMPFILE | base64 -d)
    CANONICALIZE_OUT_LINK_1=$($JSON_FIELD  --field='0:link' <<< $CANONICALIZE_OUT)
    CANONICALIZE_OUT_IMAGE_1=$($JSON_FIELD  --field='0:image' <<< $CANONICALIZE_OUT)
    if [[ "$CANONICALIZE_OUT_LINK_1" == "$SITE_URL$CANONICALIZE_OUT_LINK_0" ]]
    then
        SUCCESS+=("CANONICALIZE_LINK")
        echo -e $BLUE"Canonization url for link tag success"$DEF
    else
        FAIL+=("CANONICALIZE_LINK")
        echo -e $RED"Fail, canonization url check for link tag, $CANONICALIZE_OUT_LINK_1 != $SITE_URL $CANONICALIZE_OUT_LINK_0"$DEF
    fi
    if [[ "$CANONICALIZE_OUT_IMAGE_1" == "$SITE_URL$CANONICALIZE_OUT_IMAGE_0" ]]
    then
        SUCCESS+=("CANONICALIZE_IMAGE")
        echo -e $BLUE"Canonization url for image tag success"$DEF
    else
        FAIL+=("CANONICALIZE_IMAGE")
        echo -e $RED"Fail, canonization url check for image tag, $CANONICALIZE_OUT_IMAGE_1 != $SITE_URL $CANONICALIZE_OUT_IMAGE_0"$DEF
    fi
else
    echo -e $RED"Jsons for check canonization url not found"$DEF
fi
# OUT #
if [[ ${SUCCESS[@]} ]]
then
    echo -e $BLUE"Number of success: "${#SUCCESS[@]} $DEF
fi

if [[ ${FAIL[@]} ]]
then
    echo -e $RED"Number of fails: "${#FAIL[@]} $DEF
    exit 1
fi

exit 0
