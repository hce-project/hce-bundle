#!/bin/bash

../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="GET" --fields="V1" --classes="AdminInterfaceServer" > ../log/$0.log

../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="SET" --fields="V1:test value string" --classes="AdminInterfaceServer" >> ../log/$0.log

../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="GET" --fields="V1" --classes="AdminInterfaceServer" >> ../log/$0.log
