#!/bin/bash
#Make API tests, if no cli argument all tests performed; if not - argument treated as input json file

apiToken=$2
HTTP_URL="http://127.0.0.1/tr/app/TagsReaperUI/api"

if [ "$apiToken" == "" ]
then
	apiToken="bhWgTtA4ULBWNwDrl%2BuBjJGI%2FycxMIEHbdLXoBHebChzevNwy7koQiplcEPqw3jIpgRO5%2Bko3%2Frlj3N7nZ%2BWHA%3D%3D"	## 114
	HTTP_URL="http://192.168.253.114:8080/TagsReaperUI/api?apiToken=$apiToken"	## 114
fi

LOG="$0.log"

if [ "$1" == "" ]; then
  echo "Tests started" > $LOG
  #Wrong json format 1
  wget -S -o "$0.bad00.log" -O "$0.result.bad00.json" --post-file "api_test.bad00.json" $HTTP_URL > $LOG
  #Wrong json format 2
  wget -S -o "$0.bad01.log" -O "$0.result.bad01.json" --post-file "api_test.bad01.json" $HTTP_URL > $LOG
  #Good news scraping static fetcher
  wget -S -o "$0.good_news_static00.log" -O "$0.result.good_news_static00.json" --post-file "api_test.good_news_static00.json" $HTTP_URL > $LOG
  #Good news scraping static fetcher depth=2 internal
  wget -S -o "$0.good_news_static01.log" -O "$0.result.good_news_static01.json" --post-file "api_test.good_news_static01.json" $HTTP_URL > $LOG
  #Good news scraping static fetcher depth=2 external
  wget -S -o "$0.good_news_static02.log" -O "$0.result.good_news_static02.json" --post-file "api_test.good_news_static02.json" $HTTP_URL > $LOG
  #Good news scraping dynamic fetcher
  wget -S -o "$0.good_news_dynamic00.log" -O "$0.result.good_news_dynamic00.json" --post-file "api_test.good_news_dynamic00.json" $HTTP_URL > $LOG

  #Good rss scraping static fetcher feed's data external site
  wget -S -o "$0.good_rss_static00.log" -O "$0.result.good_rss_static00.json" --post-file "api_test.good_rss_static00.json" $HTTP_URL > $LOG
  ##Good rss scraping static fetcher feed's data internal site
  wget -S -o "$0.good_rss_static01.log" -O "$0.result.good_rss_static01.json" --post-file "api_test.good_rss_static01.json" $HTTP_URL > $LOG
  #Good rss scraping static fetcher articles data internal site
  wget -S -o "$0.good_rss_static02.log" -O "$0.result.good_rss_static02.json" --post-file "api_test.good_rss_static02.json" $HTTP_URL > $LOG
  ##Good rss scraping static fetcher articles data external site
  wget -S -o "$0.good_rss_static03.log" -O "$0.result.good_rss_static03.json" --post-file "api_test.good_rss_static03.json" $HTTP_URL > $LOG

  ##api_test.good_template_dynamic00.json

  #Good contents simple
  wget -S -o "$0.good_url_content00.log" -O "$0.result.good_url_content00.json" --post-file "api_test.good_url_content00.json" $HTTP_URL?cmd=1 > $LOG
  #Good contents multi
  wget -S -o "$0.good_url_content01.log" -O "$0.result.good_url_content01.json" --post-file "api_test.good_url_content01.json" $HTTP_URL?cmd=1 > $LOG

  #Good news scraping dynamic fetcher with social task usage
  wget -S -o "$0.good_news_dynamic_social_task00.log" -O "$0.result.good_news_dynamic_social_task00.json" --post-file "api_test.good_news_dynamic_social_task00.json" $HTTP_URL > $LOG

  echo "Tests finished" >> $LOG
else
  wget -S -o "$1.log" -O "$1.result.json" --post-file "$1" $HTTP_URL > $LOG
fi
