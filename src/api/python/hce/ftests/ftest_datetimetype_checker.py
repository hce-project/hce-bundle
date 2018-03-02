#!/usr/bin/python
# coding: utf-8

import os
import sys
import logging

from datetime import tzinfo  # pylint: disable=W0611
from cement.core import foundation
from datetime import datetime
import datetime
import time
from sys import stdout
from sys import stderr

from dc_processor.PDateTimezonesHandler import PDateTimezonesHandler
from app.DateTimeType import DateTimeType

import re
import time

import json
from time import sleep
import random


def getLogger():
  # create logger
  logger = logging.getLogger('test')
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


# # Test executon functional
#
# @param fileName - input file name for test
# @param ext - allowed extention of file
# @return - None
def testExecution(fileName, ext='.list'):

  if fileName.rfind(ext) > 0:
    # stdout.write('\nOpen file: ' + str(fileName))
    f = open(fileName, 'r')
    lineList = f.readlines()
    f.close()

    for rawPubdate in lineList:
      if rawPubdate.find('%pubdate%') < 0:
        s = rawPubdate
        d = DateTimeType.parse(s)
        if d is None:
          print('fail: ' + str(s))
        else:
          pass

  else:
    pass


def dateutilTest():
  logger = getLogger()
  for period in ['years', 'months', 'days', 'hours', 'minutes']:
    for testStr in ['22  ' + period + ' left', '23 ' + period + ' left']:
      print('=======\ninput: ' + str(testStr))
      d = DateTimeType.parse(testStr, True, logger, True)
      if d is not None:
        print('parse: ' + str(d.isoformat(' ')))
      else:
        print('parse: NONE')


if __name__ == '__main__':

  app = foundation.CementApp('DateTimeType')
  app.setup()
  app.add_arg('-f', '--file', action='store', metavar='input_file', help='input file with date list')
  app.add_arg('-d', '--dir', action='store', metavar='input_file', help='input directory name with files dates')
  app.run()

  fileName = app.pargs.file
  dirName = app.pargs.dir
  app.close()

  if dirName is not None:
    files = os.listdir(dirName)
    for inputFile in files:
      testExecution(inputFile)

  elif fileName is not None:
    testExecution(fileName)
  else:
    # handle test
    # s = 'pubdate=Published On: Nov 03 2015 02:34:13 PM CST'
    # s = 'pubdate=| October 29, 2015 12:14pm'
    # s = 'pubdate=Posted: 11/03/2015 08:02 PM EST'
    # s = 'pubdate=Updated 2255 GMT (0655 HKT) November 3, 2015'
    # s = 'pubdate=11/3/2015 03:05 PM Connect Directly'
    # s = 'pubdate=04 листопада 2015'
    # s = 'pubdate=3 листопада'
    # s = 'pubdate=17 вересня, 2015'
    # s = 'pubdate=1446606656'
    # s = '31 August 2015'
    # s = 'pubdate=Wed, 30 Sep 2015 22:25:27 -0000'
    # s = 'pubdate=| October 29, 2015 12:14pm'
    # s = 'pubdate=Last updated at 20:00 GMT'
    # s = 'pubdate=By:  , November 4th, 2015 08:43 AM'
    # s = 'pubdate=| October 15, 2015 8:54am |'
    # s = 'pubdate=2015-11-04 09:48:00'
    # s = 'pubdate=November 3, 2015 @ 5:08 pm'
    # s = 'pubdate=- Associated Press - Tuesday, November 3, 2015'
    # s = 'pubdate=%pubdate%'
    # s = 'pubdate=25/08/2014'
    # s = 'Сьогодні 12:14'
    # s = 'Вчора 12:14'
    # s = 'Позавчора 12:14'
    # s = 'pubdate=17:25'
    # s = 'pubdate=2015-11-05T16:22:00+09:00'
    # s = 'pubdate=2015年11月5日20時10分'
    # s = '2015年11月5日20時10分'
    # s = 'pubdate=2015年10月24日'
    # s = 'pubdate=11月5日   18時05分'
    # s = '11月5日   18時05分'
    # s = 'pubdate=16/09/2015'
    # s = 'pubdate=3rd November 2015, 17:15'
    # s = '2015-11-06 10:33:08'
    # s = 'November 6, 2015'
    # s = '2015/10/27'
    # s = '20150416'
    # s = '31 August 2015'
    # s = '2015-08-31T14:24:05+01:00'
    # s = '2015-05-09T16:20:15Z 2015-05-11T07:54:39Z'
    # s = '20151120T1212+0200Z'
    # s = '01.12.2015 12:01 Uhr'
    # s = 'B81D5A241AD4BAFB0252A0D687615E0E'
    # s = '2015-08-31T14:24:05+01:00'
    # s = '2015年04月22日 10:41　'
    # s = '2015年04月22日 10:41　 発信地：リッセ/オランダ'
    # s = 'JANUARY 6, 2016 09:00AM EST'
    # s = '2015年 04月 22日 10:41 JST'
    # s = 'POSTED: 01/21/16, 4:54 PM PST '
    # s = '15:53 GMT, 27 January 2016'
    # s = 'Вторник, 09.02.2016'  ##
    # s = '06:5509.02.2016'
    # s = '09.02.2016 - 14:42'
    # s = 'Лютий 10th, 2016'
    # s = 'Wed Jan 6, 2016 2:48pm EST'
    # s = '2/13/2016 10:05 AM Connect Directly'
    # s = '2/12/2016 09:06 AM Connect Directly'
    # s = 'February 9, 2016'
    # s = 'Updated Feb. 26, 2015 10:53 a.m. ET'
    # s = '17. February 2016 15:54'
    # s = '17.2.2016, 15:57 Uhr'
    # s = 'February 17, 2016 @ 12:52 pm'
    # s = '17. February 2016 20:50'
    # s = 'Last updated at 22:19 GMT'
    # s = 'February 18 at 5:15 PM'
    # s = '2.18.16 | 11:26PM'
    # s = '2015-05-07 02:03:14'
    # s = 'Fri Feb 19, 2016 11:14am EST'
    # s = ' 18 лютого'
    # s = 'B81D5A241AD4BAFB0252A0D687615E0E'
    # s = '2016-01-06T19:48:47+0100'
    # s = '<time datetime="06 Jan 2016 19:45 GMT">06 Jan 2016 19:45 GMT</time>'
    # s = '2016年3月22日'
    # s = 'Вчера, 18:59'
    # s = '1545'
    # s = '2016-03-01T09:32:02+00:00'
    # s = 'April 14–17, 2016'
    # s = '5B44585918D69318CA2120B5FA20D85C'
    # s = 'January 5'
    # s = '12:09 a.m. EST March 2, 2016'
    # s = 'March 4 at 9:36 AM'
    # s = 'This was first published in  March 2016'
    # s = '2  days left'
    # s = '7 hours'
    # s = '08 Мар 2016'
    # s = '2  days\xa0left'
    # s = '2016\xe5\xb9\xb420\xe6\x9c\x8841\xe6\x97\xa5 00:00'
    # s = '2016年20月41日 00:00'
    # s = 'Published on 13th May 2016 by Gareth Halfacree'

    # s = '20160324T0410+0200Z'
    # s = u'\u0432 \u041c\u0430\u0440\u0442 23, 2016'
    # s = '5日前'  #  5 дней назад'
    # s = '1時間前'  #  час назад
    # s = '1 Hour Ago'
    # s = '2016-05-10 2016-05-16 2016-05-16 2016-05-16 2016-05-16 2016-05-17 2016-05-17 2016-05-17 2016-05-16 2016-05-10'
    # s = '2016-05-16 12:56:00'
    # s = 'May 16, 2016, 12:56 pm EDT'

    # s = ' Пʼятниця, 19 лютого 2016, 04:59'
    # s = 'Mon Mar 21, 2016 3:20am EDT'
    # s = 'Wed Jan 6, 2016 2:48pm EST'
    # s = '2016-05-02T17:21:59+09:00'

    # s = '2016年5月24日（火）'

    # s = 'FEBRUARY 22, 2016 | 12:00 PM'
    # s = '2016.05.29 Sun posted at 18:58 JST'
    # s = '1464373928'
    # s = '2016/4/22付'
    # s = '平成28年５月２５日'
    # s = '平成28年5月25日'
    # s = 'May 21, 2016 — Ron Chusid'
    # s = '2016-05-26T06:14-500'
    # s = '<div class="post-item__info">Корреспондент.biz, Сегодня, 01:12</div>'
    # s = '`Корреспондент.biz, Сегодня, 01:1'
    # s = 'Дек 18'

    # s = ' в Май 23, 2016'
    # s = ' 21 июня 2016, вторник, 23:58'
    # s = '24.12.15'
    # s = '2013/6/26'
    # s = '2016-07-05T12:11:13:00.000Z'
    # s = '2016年 05月 9日 10:15 JST'
    # s = 'Wed, 20 Jul 2016 09:08:25 +0000'
    # s = '2016年7月26日23時28分'
    # s = '2016年07月21日 10:36 '  # 2016-07-21 strange time ignore http://www.afpbb.com/articles/-/3094693
    # #s = '02.07.2016 16:28'  # month and date are not placed right http://zovzakona.org/gugl-v-pomoshh-politsii
    # s = '1464373928'  # WRONG TZ should be GMT, http://www.bbc.com/news/uk-politics-36381328
    # s = '2016\xe5\xb9\xb408\xe6\x9c\x8809\xe6\x97\xa5 16:33\xe3\x80\x80'
    # s = u'23 \u0430\u0432\u0433\u0443\u0441\u0442\u0430 2016, 09:00'
    # s = '10:20:11'
    # s = '2016-10-22T12:00:34.295Z'
    # s = 'Nov 6th 2016 8:40PM'  # http://www.aol.com/article/2016/11/06/trump-reacts-to-fbi-clearing-clinton-in-email-probe-she-is-bei/21599923/
    # s = '11/06/16, 3:22 PM PST'
    # s = 'Posted 11-28-2016'
    # s = '15 hours ago'
    # s = 'Tue, 13 Dec 2016 07:14:00 +1300'
    s = '2017/3/12 19:42 (2017/3/12 23:31更新)'
    s = u'2017/3/12 19:42 (2017/3/12 23:31\u66f4\u65b0)'

    logger = getLogger()
    # print('getLang = ' + str(DateTimeType.getLang(s, logger, True)))
    # sys.exit()

    d = DateTimeType.parse(s, True, logger, True)
    if d is not None:
      print('parse: ' + str(d.isoformat(' ')))
      # print('strftime: ' + str(d.strftime("%Y-%m-%d %H:%M")))

      d, timezone = DateTimeType.split(d)
      print('datetime: ' + str(d.isoformat(' ')) + ' timezone: ' + str(timezone))
    else:
      print('parse: NONE')


    # utcOffset = DateTimeType.extractUtcOffset(s, logger, True)
    # logger.debug('utcOffset: ' + str(utcOffset))
#     try:
#       s = s.lower()
#       print type(s)
#       print s.find(u'Сегодня')
#       print s
#     except Exception, err:
#       sys.stderr.write(str(err))
