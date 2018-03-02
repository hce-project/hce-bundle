#!/bin/bash

cd ../bin && ./dtm-client.py --config ../ini/dtm-client.ini -t NEW --file=../data/ftests/test_dtm_get_tasks/dtm_new.json
cd ../bin && ./dtm-client.py --config ../ini/dtm-client.ini -t NEW --file=../data/ftests/test_dtm_get_tasks/dtm_new1.json
cd ../bin && ./dtm-client.py --config ../ini/dtm-client.ini -t NEW --file=../data/ftests/test_dtm_get_tasks/dtm_new2.json

sleep 2

cd ../bin && ./dtm-client.py --config ../ini/dtm-client.ini -t GET_TASKS --file=../data/ftests/test_dtm_get_tasks/dtm_get_tasks.json

sleep 2

cd ../bin && ./dtm-client.py --config ../ini/dtm-client.ini -t GET_TASKS --file=../data/ftests/test_dtm_get_tasks/dtm_get_tasks_full.json
