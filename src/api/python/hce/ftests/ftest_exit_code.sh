#!/bin/bash
EXIT_CODE_RETRY=111
TRYITER=0
MAXTRYES=2

#./ftest_exit_code_simple.py
./ftest_exit_code.py -c ../../ini/rtc-finalizer.ini -rb aaa -rc "$EXIT_CODE_RETRY" < ftest_exit_code.sh
if (( $? == EXIT_CODE_RETRY )) && (( TRYITER < MAXTRYES ))
then
  ((TRYITER++))
fi

echo "TRYITER=$TRYITER"
