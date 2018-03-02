#!/bin/bash

../bin/dtm-admin.py --config=../ini/dtm-admin.ini --cmd="SUSPEND" --fields="1" > ../log/$0.log
