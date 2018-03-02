#!/bin/bash

../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="STAT" --fields="VERSION" --classes="AdminInterfaceServer" > ../log/$0.log
