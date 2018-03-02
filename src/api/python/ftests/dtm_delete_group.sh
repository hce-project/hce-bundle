#!/bin/bash

cd ../bin && ./dtm-client.py --config ../ini/dtm-client.ini -t NEW --file=../data/ftests/test_dtm_group_delete/dtm_new1.json
sleep 2
cd ../bin && ./dtm-client.py --config ../ini/dtm-client.ini -t NEW --file=../data/ftests/test_dtm_group_delete/dtm_new2.json
sleep 2
cd ../bin && ./dtm-client.py --config ../ini/dtm-client.ini -t NEW --file=../data/ftests/test_dtm_group_delete/dtm_new3.json
sleep 2
echo "----------------------- 1th DELETE --------------------------"
cd ../bin && ./dtm-client.py --config ../ini/dtm-client.ini -t TERMINATE --file=../data/ftests/test_dtm_group_delete/dtm_delete.json
sleep 5
echo "----------------------- 2th DELETE --------------------------"
cd ../bin && ./dtm-client.py --config ../ini/dtm-client.ini -t TERMINATE --file=../data/ftests/test_dtm_group_delete/dtm_group_delete.json
sleep 2
echo "----------------------- NEW after stopping --------------------------"
cd ../bin && ./dtm-client.py --config ../ini/dtm-client.ini -t NEW --file=../data/ftests/test_dtm_group_delete/dtm_new1.json
sleep 30