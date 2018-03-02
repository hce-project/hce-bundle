#!/bin/bash

STATE="7"
REQUEST_JSON="../data/ftests/dcc_url_content_static_multi.json"
RESULTS_JSON="../log/$0.result.json"

echo "URLs contents with date range condition:" > ../log/$0.log 2>&1
../manage/dc-client_start.sh "--command=URL_CONTENT --file=$REQUEST_JSON" > "$RESULTS_JSON" 2>&1
