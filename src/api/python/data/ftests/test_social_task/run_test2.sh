#!/bin/bash

CUR_DIR=`pwd`

cd /home/hce/hce-node-bundle/api/python/bin

./digest.py -f 1 -lang=en -sa @file://../ini/digest.ini.sentiment.social.json -l @file://../ini/digest.ini.tagsLimits.social.json -statlog {\"file\":\"@auto\"} -oj {\"file\":\"../log/digest_sentiment_us_us_out.json\"} -m 5000 -mi 0  -mif 0 -c ../ini/digest.ini.social -t ../ini/digest_template_news.html -i $CUR_DIR/input_file5.json -o $CUR_DIR/output_file.json.result.json_us.html -lOverride {\"pubdate\":{\"senility\":1440000}} --popwordslog $CUR_DIR/output_popwords.json --popwords @file://$CUR_DIR/digest.ini.popwordsLog.social.json

# -l @file://../ini/digest.ini.tagsLimits.sentiment.json 


