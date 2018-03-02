#!/usr/bin/python
# coding: utf-8

import os
import sys
import logging
from dc_crawler.HTTPCookieResolver import HTTPCookieResolver
from app.Utils import varDump
from app.Utils import parseHost
import app.Consts as APP_CONSTS


def getLogger():
  # create logger
  logger = logging.getLogger(APP_CONSTS.LOGGER_NAME)
  logger.setLevel(logging.DEBUG)

  # create console handler and set level to debug
  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)

  # create formatter
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

  # add formatter to ch
  ch.setFormatter(formatter)

  # add ch to logger
  logger.addHandler(ch)

  return logger


if __name__ == '__main__':

  logger = getLogger()

  # testUrl = 'http://www.nytimes.com/pages/realestate/index.html'
  # testUrl = 'http://mainichi.jp/auth/check_cookie_set.php?url=%2Farticles%2F20161101%2Fdde%2F041%2F200%2F060000c'
  testUrl = 'http://thecaucus.blogs.nytimes.com/feed'
  # testCookie = 'RMID=007f010001ef57ecce0c0044; Expires=Fri, 29 Sep 2017 08:17:16 GMT; Path=/; Domain=.nytimes.com;, adxcs=-; path=/; domain=.nytimes.com'
  # testCookie = 'nyt-a=404c415521b8f3e8d92e2623d60ed4af;path=/;domain=.nytimes.com;expires=Fri, 29 Sep 2017 08:16:31 UTC, RMID=007f010116a357eccddf000a;path=/;domain=.nytimes.com;expires=Fri, 29 Sep 2017 08:16:31 UTC'
  # testCookie = 'AWSELB=2D635D7F085943AF3ED70A1AE907E156AF95FD853A1E9DE41257D736BB0878FA62AACDB3328FCEE98FCA65B7ACC78DD533A33CA7252F22C4169A8EDB2A037EDCE533C6706E;PATH=/;MAX-AGE=3600'
  # testCookie = 'ckcheck=20161101203738; path=/; domain=.mainichi.jp, ck=1; path=/; domain=.mainichi.jp'
  # testCookie = 'PHPSESSID=dmk9qv40ejptcf34n5005895o6; path=/; domain=.mainichi.jp, PHPSESSID=dmk9qv40ejptcf34n5005895o6; path=/; domain=.mainichi.jp, PHPSESSID=ri3eoe3tfn4jkhutb0l45f2an3; path=/; domain=.mainichi.jp, PHPSESSID=ri3eoe3tfn4jkhutb0l45f2an3; path=/; domain=.mainichi.jp'
  # testCookie = 'NYT-S=0MzycNAz.DKnTDXrmvxADeHw9CANpeHfgkdeFz9JchiAIUFL2BEX5FWcV.Ynx4rkFI; expires=Fri, 02-Dec-2016 08:13:55 GMT; path=/; domain=.nytimes.com, NYT-BCET=1480666435%7CUD9ePFkvdXpfhpUrb1QP%2FzMtX0g%3D%7C4AKhntb6qrGHHvrp1CH2J0vL000x7RbLgKUF%2BQ2nJYs%3D; expires=Mon, 01-May-2017 08:13:55 GMT; path=/; domain=.nytimes.com; httponly'
  testCookie = '2e207a62fe17ce9f8bbbb86a50498c41=nk8srbd1hsmia5j9mf7to6oj80\r\nja_t3_blank_tpl; '
  # testJSON = "{\"nytimes.com\":{\"stage\":4, \"cookie\":\"12345\"}}"
  # testJSON = "{\"nytimes.com\":{\"stage\":4}}"
  testJSON = "{\"%s\":{\"stage\":4}}" % (parseHost(testUrl))


  cookieResolver = HTTPCookieResolver(testJSON)
  cookieResolver.addCookie(testUrl, testCookie)
  cookie = cookieResolver.getCookie(testUrl)
  logger.debug('cookie: ' + str(cookie))

