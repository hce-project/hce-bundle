#!/bin/bash

cp ../data/ftests/dtm_limits/dtm_check_bad.json ../data/ftests/dtm_limits/dcb.json
cp ../data/ftests/dtm_limits/dtm_new_bad.json ../data/ftests/dtm_limits/dnb.json
cp ../data/ftests/dtm_limits/dtm_status_bad.json ../data/ftests/dtm_limits/dsb.json
cp ../data/ftests/dtm_limits/dtm_check_ok.json ../data/ftests/dtm_limits/dco.json
cp ../data/ftests/dtm_limits/dtm_new_ok.json ../data/ftests/dtm_limits/dno.json
cp ../data/ftests/dtm_limits/dtm_status_ok.json ../data/ftests/dtm_limits/dso.json

substr1='s/tid/'$1'/g'
substr2='s/tid/'$2'/g'
sed -i $substr1 ../data/ftests/dtm_limits/dcb.json
sed -i $substr1 ../data/ftests/dtm_limits/dnb.json
sed -i $substr1 ../data/ftests/dtm_limits/dsb.json
sed -i $substr2 ../data/ftests/dtm_limits/dco.json
sed -i $substr2 ../data/ftests/dtm_limits/dno.json
sed -i $substr2 ../data/ftests/dtm_limits/dso.json
#../manage/dtm-daemon_start.sh
sleep 10
cd ../bin && ./dtm-client.py -t NEW -f ../data/ftests/dtm_limits/dno.json --config ../ini/dtm-client.ini > ../data/ftests/dtm_limits/dno_ret.json
sleep 30
cd ../bin && ./dtm-client.py -t CHECK -f ../data/ftests/dtm_limits/dco.json --config ../ini/dtm-client.ini > ../data/ftests/dtm_limits/dco_ret.json
sleep 10
cd ../bin && ./dtm-client.py -t STATUS -f ../data/ftests/dtm_limits/dso.json --config ../ini/dtm-client.ini > ../data/ftests/dtm_limits/dso_ret.json
sleep 10
cd ../bin && ./dtm-client.py -t NEW -f ../data/ftests/dtm_limits/dnb.json --config ../ini/dtm-client.ini > ../data/ftests/dtm_limits/dnb_ret.json
sleep 10
cd ../bin && ./dtm-client.py -t CHECK -f ../data/ftests/dtm_limits/dcb.json --config ../ini/dtm-client.ini > ../data/ftests/dtm_limits/dcb_ret.json
sleep 10
cd ../bin && ./dtm-client.py -t STATUS -f ../data/ftests/dtm_limits/dsb.json --config ../ini/dtm-client.ini > ../data/ftests/dtm_limits/dsb_ret.json
#../manage/dtm-daemon_stop.sh

echo "----------------------- DTM-NEW-OK check --------------------------"
cd ../bin && ./json-checker.py --file=../data/ftests/dtm_limits/dno_ret.json --path=errorCode --value=0
if [ $? -eq 0 ]
then
    echo ">>> Ok"
else
    echo ">>> Error [ErrorCode != 0]"
    cd ../bin && ./json-checker.py --file=../data/ftests/dtm_limits/dno_ret.json --path=errorCode --value=1001
    if [ $? -eq 0 ]
    then
	echo ">>> (Not unique task id["$2"])"
    fi
fi
cd ../bin && ./json-checker.py --file=../data/ftests/dtm_limits/dno_ret.json --path=errorMessage --value=""
if [ $? -eq 0 ]
then
    echo ">>> Ok"
else
    echo ">>> Error [ErrorCode != 0]"
fi
echo "----------------------- DTM-CHECK-OK check ------------------------"
cd ../bin && ./json-checker.py --file=../data/ftests/dtm_limits/dco_ret.json --path=id --value=$2
if [ $? -eq 0 ]
then
    echo ">>> Ok"
else
    echo ">>> Error [Wrong \"id\" value]"
fi
cd ../bin && ./json-checker.py --file=../data/ftests/dtm_limits/dco_ret.json --path=state --value=0
if [ $? -eq 0 ]
then
    echo ">>> Ok"
else
    echo ">>> Error [\"state\" field != 0]"
fi
cd ../bin && ./json-checker.py --file=../data/ftests/dtm_limits/dco_ret.json --path=errorCode --value=0
if [ $? -eq 0 ]
then
    echo ">>> Ok"
else
    echo ">>> Error [\"errorCode\" field != 0]"
fi
echo "----------------------- DTM-SATUS-OK check ------------------------"
cd ../bin && ./json-checker.py --file=../data/ftests/dtm_limits/dso_ret.json --path=taskManagerFieldsList[0].id --value=$2
if [ $? -eq 0 ]
then
    echo ">>> Ok"
else
    echo ">>> Error [Wrong \"id\" value]"
fi
cd ../bin && ./json-checker.py --file=../data/ftests/dtm_limits/dso_ret.json --path=taskManagerFieldsList[0].fields.state --value=0
if [ $? -eq 0 ]
then
    echo ">>> Ok"
else
    echo ">>> Error [Wrong \"fields.state\" value]"
fi
echo "----------------------- DTM-NEW-BAD check -------------------------"
cd ../bin && ./json-checker.py --file=../data/ftests/dtm_limits/dno_ret.json --path=errorCode --value=0
if [ $? -eq 0 ]
then
    echo ">>> Ok"
else
    echo ">>> Error [ErrorCode != 0]"
    if [ $? -eq 0 ]
    then
	echo ">>> (Not unique task id["$1"])"
    fi
fi
cd ../bin && ./json-checker.py --file=../data/ftests/dtm_limits/dno_ret.json --path=errorMessage --value=""
if [ $? -eq 0 ]
then
    echo ">>> Ok"
else
    echo ">>> Error [ErrorCode != 0]"
fi
echo "----------------------- DTM-CHECK_BAD check -----------------------"
cd ../bin && ./json-checker.py --file=../data/ftests/dtm_limits/dcb_ret.json --path=id --value=$1
if [ $? -eq 0 ]
then
    echo ">>> Ok"
else
    echo ">>> Error [Wrong \"id\" value]"
fi
cd ../bin && ./json-checker.py --file=../data/ftests/dtm_limits/dcb_ret.json --path=state --value=3
if [ $? -eq 0 ]
then
    echo ">>> Ok"
else
    echo ">>> Error [\"state\" field != 0]"
fi
cd ../bin && ./json-checker.py --file=../data/ftests/dtm_limits/dcb_ret.json --path=errorCode --value=3
if [ $? -eq 0 ]
then
    echo ">>> Ok"
else
    echo ">>> Error [\"errorCode\" field != 3]"
fi
echo "----------------------- DTM-STATUS_BAD check ----------------------"
cd ../bin && ./json-checker.py --file=../data/ftests/dtm_limits/dsb_ret.json --path=taskManagerFieldsList[0].id --value=$1
if [ $? -eq 0 ]
then
    echo ">>> Ok"
else
    echo ">>> Error [Wrong \"id\" value]"
fi
cd ../bin && ./json-checker.py --file=../data/ftests/dtm_limits/dsb_ret.json --path=taskManagerFieldsList[0].fields.state --value=106
if [ $? -eq 0 ]
then
    echo ">>> Ok"
else
    echo ">>> Error [Wrong \"fields.state\" value]"
fi
