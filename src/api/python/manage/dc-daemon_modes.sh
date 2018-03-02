#!/bin/bash

#Manage the modes of all periodic processing types and classes
if [ "$1" = "" ]; then
  echo "Usage: $0 < all | crawling | processing | purging | recall | rcrawling | icrawling | recrawling | aging > [ 0 | 1 ]"
  echo "To get current state of all periodic processes:"
  echo "$0 all"
  echo ""
  echo "To disable all periodic processes:"
  echo "$0 all 0"
  echo ""
  echo "To enable all periodic processes:"
  echo "$0 all 1"
  echo ""
  echo "To disable crawling (all but not processing):"
  echo "$0 crawling 0"
else
  if [ "$1" = "all" ]; then
    if [ "$2" = "" ]; then
      #Get all modes
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="GET" --fields="RegularCrawlingMode,ReturnURLsMode,IncrMode,PurgeMode,AgingMode" --classes=BatchTasksManager > ../log/$0.log
      echo "" >> ../log/$0.log
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="GET" --fields="ProcessingMode" --classes=BatchTasksManagerProcess >> ../log/$0.log
      echo "" >> ../log/$0.log
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="GET" --fields="RecrawlSiteMode" --classes=SitesManager >> ../log/$0.log
      exit
    else
      #Set all modes
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="SET" --fields="RegularCrawlingMode:$2,ReturnURLsMode:$2,IncrMode:$2,PurgeMode:$2,AgingMode:$2" --classes=BatchTasksManager > ../log/$0.log
      echo "" >> ../log/$0.log
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="SET" --fields="ProcessingMode:$2" --classes=BatchTasksManagerProcess >> ../log/$0.log
      echo "" >> ../log/$0.log
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="SET" --fields="RecrawlSiteMode:$2" --classes=SitesManager >> ../log/$0.log
    fi
  fi

  if [ "$1" = "crawling" ]; then
    if [ "$2" = "" ]; then
      #Get crawling modes
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="GET" --fields="RegularCrawlingMode,ReturnURLsMode,IncrMode,PurgeMode,AgingMode" --classes=BatchTasksManager > ../log/$0.log
      echo "" >> ../log/$0.log
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="GET" --fields="RecrawlSiteMode" --classes=SitesManager >> ../log/$0.log
    else
      #Set crawling modes
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="SET" --fields="RegularCrawlingMode:$2,ReturnURLsMode:$2,IncrMode:$2,PurgeMode:$2,AgingMode:$2" --classes=BatchTasksManager > ../log/$0.log
      echo "" >> ../log/$0.log
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="SET" --fields="RecrawlSiteMode:$2" --classes=SitesManager >> ../log/$0.log
    fi
  fi

  if [ "$1" = "processing" ]; then
    if [ "$2" = "" ]; then
      #Get processing mode
     ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="GET" --fields="ProcessingMode" --classes=BatchTasksManagerProcess > ../log/$0.log
    else
      #Set processing mode
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="SET" --fields="ProcessingMode:$2" --classes=BatchTasksManagerProcess > ../log/$0.log
    fi
  fi

  if [ "$1" = "purging" ]; then
    if [ "$2" = "" ]; then
      #Get purging mode
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="GET" --fields="PurgeMode" --classes=BatchTasksManager > ../log/$0.log
    else
      #Set purging mode
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="SET" --fields="PurgeMode:$2" --classes=BatchTasksManager > ../log/$0.log
    fi
  fi

  if [ "$1" = "recall" ]; then
    if [ "$2" = "" ]; then
      #Get urls recall mode
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="GET" --fields="ReturnURLsMode" --classes=BatchTasksManager > ../log/$0.log
    else
      #Set urls recall mode
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="SET" --fields="ReturnURLsMode:$2" --classes=BatchTasksManager > ../log/$0.log
    fi
  fi

  if [ "$1" = "rcrawling" ]; then
    if [ "$2" = "" ]; then
      #Get regular crawling mode
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="GET" --fields="RegularCrawlingMode" --classes=BatchTasksManager > ../log/$0.log
    else
      #Set regular crawling mode
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="SET" --fields="RegularCrawlingMode:$2" --classes=BatchTasksManager > ../log/$0.log
    fi
  fi

  if [ "$1" = "icrawling" ]; then
    if [ "$2" = "" ]; then
      #Get incremental crawling mode
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="GET" --fields="IncrMode" --classes=BatchTasksManager > ../log/$0.log
    else
      #Set incremental crawling mode
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="SET" --fields="IncrMode:$2" --classes=BatchTasksManager > ../log/$0.log
    fi
  fi

  if [ "$1" = "recrawling" ]; then
    if [ "$2" = "" ]; then
      #Get recrawling mode
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="GET" --fields="RecrawlSiteMode" --classes=SitesManager > ../log/$0.log
    else
      #Set recrawling mode
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="SET" --fields="RecrawlSiteMode:$2" --classes=SitesManager > ../log/$0.log
    fi
  fi

  if [ "$1" = "aging" ]; then
    if [ "$2" = "" ]; then
      #Get aging mode
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="GET" --fields="AgingMode" --classes=BatchTasksManager > ../log/$0.log
    else
      #Set aging mode
      ../bin/dtm-admin.py --config=../ini/dc-admin.ini --cmd="SET" --fields="AgingMode:$2" --classes=BatchTasksManager > ../log/$0.log
    fi
  fi

fi
