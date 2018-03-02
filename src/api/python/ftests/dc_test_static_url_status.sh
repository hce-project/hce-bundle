#!/bin/bash

../bin/dc-client.py --config=../ini/dc-client.ini --command=URL_STATUS --file=../data/ftests/dcc_url_status_static.json >> ../log/$0.log
