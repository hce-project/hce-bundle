#!/bin/bash

../bin/dc-client.py --config=../ini/dc-client.ini --command=URL_HISTORY --file=../data/ftests/dcc_url_history.json > ../log/$0.log

