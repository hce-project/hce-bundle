#!/bin/bash

cd ../bin && ./dtm-client.py --config ../ini/dtm-client.ini -t NEW --file=../data/ftests/test_dtm_delete_task/dtm_new.json
sleep 5
cd ../bin && ./dtm-client.py --config ../ini/dtm-client.ini -t CHECK --file=../data/ftests/test_dtm_delete_task/dtm_check.json > ../data/ftests/test_dtm_delete_task/check1.json
echo "----------------------- 1th CHECK check --------------------------"
cd ../bin && ./json-checker.py --file=../data/ftests/test_dtm_delete_task/check1.json --path=state --value=1
if [ $? -eq 0 ]
then
    echo ">>> 1th CHECK Ok"
else
    echo ">>> 1th CHECK Fail"
fi
cd ../bin && ./dtm-client.py --config ../ini/dtm-client.ini -t TERMINATE --file=../data/ftests/test_dtm_delete_task/dtm_delete.json
sleep 5
cd ../bin && ./dtm-client.py --config ../ini/dtm-client.ini -t CHECK --file=../data/ftests/test_dtm_delete_task/dtm_check.json > ../data/ftests/test_dtm_delete_task/check2.json
echo "----------------------- 2th CHECK check --------------------------"
cd ../bin && ./json-checker.py --file=../data/ftests/test_dtm_delete_task/check2.json --path=state --value=1
if [ $? -eq 0 ]
then
    echo ">>> 2th CHECK Ok"
else
    echo ">>> 2th CHECK Fail"
fi
sleep 50
cd ../bin && ./dtm-client.py --config ../ini/dtm-client.ini -t CHECK --file=../data/ftests/test_dtm_delete_task/dtm_check.json > ../data/ftests/test_dtm_delete_task/check3.json
echo "----------------------- 3th CHECK check --------------------------"
cd ../bin && ./json-checker.py --file=../data/ftests/test_dtm_delete_task/check3.json --path=state --value=0
if [ $? -eq 0 ]
then
    echo ">>> 3th CHECK Ok"
else
    echo ">>> 3th CHECK Fail"
fi
cd ../bin && ./dtm-client.py --config ../ini/dtm-client.ini -t TERMINATE --file=../data/ftests/test_dtm_delete_task/dtm_delete.json
sleep 5
cd ../bin && ./dtm-client.py --config ../ini/dtm-client.ini -t CHECK --file=../data/ftests/test_dtm_delete_task/dtm_check.json > ../data/ftests/test_dtm_delete_task/check4.json
echo "----------------------- 4th CHECK check --------------------------"
cd ../bin && ./json-checker.py --file=../data/ftests/test_dtm_delete_task/check4.json --path=errorCode --value=3
if [ $? -eq 0 ]
then
    echo ">>> 4-1th CHECK Ok"
else
    echo ">>> 4-1th CHECK Fail"
fi
cd ../bin && ./json-checker.py --file=../data/ftests/test_dtm_delete_task/check4.json --path=errorMessage --value="Task not found in queue!"
if [ $? -eq 0 ]
then
    echo ">>> 4-2th CHECK Ok"
else
    echo ">>> 4-2th CHECK Fail"
fi
cd ../bin && ./json-checker.py --file=../data/ftests/test_dtm_delete_task/check4.json --path=state --value=3
if [ $? -eq 0 ]
then
    echo ">>> 4-3th CHECK Ok"
else
    echo ">>> 4-3th CHECK Fail"
fi




