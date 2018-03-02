#!/bin/bash

for i in `seq 1 10`
do
    sed "s/AXXXA/$i/g" ../data/ftests/test_dtm_suspend/dtm_template.json > ../data/ftests/test_dtm_suspend/dtm_new.json
    cd ../bin && ./dtm-client.py --config ../ini/dtm-client.ini -t NEW --file=../data/ftests/test_dtm_suspend/dtm_new.json
done

sleep 5
cd ../bin && ./dtm-admin.py --cmd=SUSPEND --config=../ini/dtm-admin.ini --fields=1
cd ../bin && ./dtm-admin.py --cmd=STAT --classes=TasksExecutor --config=../ini/dtm-admin.ini --fields=suspendState
for i in `seq 11 20`
do
    sed "s/AXXXA/$i/g" ../data/ftests/test_dtm_suspend/dtm_template.json > ../data/ftests/test_dtm_suspend/dtm_new.json
    cd ../bin && ./dtm-client.py --config ../ini/dtm-client.ini -t NEW --file=../data/ftests/test_dtm_suspend/dtm_new.json
done

sleep 5
cd ../bin && ./dtm-admin.py --cmd=STAT --classes=TasksExecutor --config=../ini/dtm-admin.ini --fields=suspendState
cd ../bin && ./dtm-admin.py --cmd=SUSPEND --config=../ini/dtm-admin.ini --fields=0
for i in `seq 21 25`
do
    sed "s/AXXXA/$i/g" ../data/ftests/test_dtm_suspend/dtm_template.json > ../data/ftests/test_dtm_suspend/dtm_new.json
    cd ../bin && ./dtm-client.py --config ../ini/dtm-client.ini -t NEW --file=../data/ftests/test_dtm_suspend/dtm_new.json
done