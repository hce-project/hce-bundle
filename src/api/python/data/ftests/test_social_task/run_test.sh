#!/bin/bash

CUR_DIR=`pwd`

#cho "$CUR_DIR"

#/bin/bash $CUR_DIR/digests.sh source_file=$CUR_DIR/input_file.json output_file=$CUR_DIR/output_file log_dir=/tmp/social input_json_file_format=1 template_file=/home/hce/hce-node-bundle/api/python/ini/digest_template_default.html max_items_total=5000 max_items_per_file=0 extended_log=1 pdf=0 pdf_toc=0 pdf_format=A4 pdf_lowquality=0 pdf_orientation=0 pdf_indent_top=10 pdf_indent_bottom=10 pdf_indent_left=10 pdf_indent_right=10 ini_file=/home/hce/hce-node-bundle/api/python/ini/digest.ini include=$CUR_DIR/social_custom_digest.sh callback_on="0" only_digest_args="1" digest_args="-f=1" 2>&1

##

#/home/hce/hce-node-bundle/api/python/bin/digest.py -f=1 -c=/home/hce/hce-node-bundle/api/python/ini/digest.ini

cd /home/hce/hce-node-bundle/api/python/bin

./digest.py -f 2 -lang=en -sa @file://../ini/digest.ini.sentiment.json -statlog {\"file\":\"@auto\"} -oj {\"file\":\"../log/digest_sentiment_us_us_out.json\"} -m 5000 -mi 0  -mif 0 -c ../ini/digest.ini  -t ../ini/digest_template_news.html -i $CUR_DIR/input_file.json -o $CUR_DIR/output_file.json.result.json_us.html -lOverride {"pubdate":{"senility":1440000}} 
