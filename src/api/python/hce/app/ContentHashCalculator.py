'''
Created on Sep 11, 2015

@package: app
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import hashlib
import re
import app.Utils as Utils  # pylint: disable=F0401


logger = Utils.MPLogger().getLogger()


class ContentHashCalculator(object):

  ALGO_INCOME_BUF = 1
  ALGO_SIMPLE_SPLITTING = 2
  ALGO_SNOWBALL_SPLITTING = 3
  ALGO_SOUNDEX_SPLITTING = 4

  RE_SPLITTER = r'\s'


  @staticmethod
  def langDetect(incomeBuf, convertToFullName=True):
    ret = None

    try:
      from langdetect import detect
      langSmallName = detect(incomeBuf).split('-')[0]
      if convertToFullName:
        import pycountry
        ret = pycountry.languages.get(iso639_1_code=langSmallName).name.lower()
      else:
        ret = langSmallName
    except Exception as ecxp:
      logger.debug(">>> Some snowball exception = " + str(ecxp))

    return ret


  @staticmethod
  def commonSplitMethod(incomeBuf, minWLen):
    ret = re.split(ContentHashCalculator.RE_SPLITTER, incomeBuf, flags=re.LOCALE)

    if len(ret) > 0:
      ret = list(set(ret))
      ret.sort()
      ret = [x for x in ret if len(x) >= minWLen]

    return ret


  @staticmethod
  def hashCalculateSimple(incomeBuf, minWLen):
    ret = None

    splittedList = ContentHashCalculator.commonSplitMethod(incomeBuf, minWLen)
    if len(splittedList) > 0:
      ret = hashlib.md5(''.join(splittedList)).hexdigest()

    return ret


  @staticmethod
  def hashCalculateSnowball(incomeBuf, minWLen, additionData, stemmerLang):  # pylint: disable=W0613
    ret = None
    try:
      import snowballstemmer
      if stemmerLang is None:
        stemmerLang = ContentHashCalculator.langDetect(incomeBuf)
        if stemmerLang is None:
          stemmerLang = 'english'

      # if additionData is not None and type(additionData) in types.StringTypes:
      splittedList = ContentHashCalculator.commonSplitMethod(incomeBuf, minWLen)
      if len(splittedList) > 0:
        stemmer = snowballstemmer.stemmer(stemmerLang)
        for i in xrange(0, len(splittedList)):
          try:
            splittedList[i] = stemmer.stemWord(splittedList)
          except Exception as ecxp:
            splittedList[i] = ""
        ret = hashlib.md5(''.join(splittedList)).hexdigest()
    except Exception as ecxp:
      logger.debug(">>> Some snowball exception = " + str(ecxp))

    return ret


  @staticmethod
  def hashCalculateSoundex(incomeBuf, minWLen):
    ret = None
    try:
      import soundex
      splittedList = ContentHashCalculator.commonSplitMethod(incomeBuf, minWLen)
      if len(splittedList) > 0:
        s = soundex.getInstance()
        for i in xrange(0, len(splittedList)):
          try:
            splittedList[i] = s.soundex(splittedList[i])
          except Exception as ecxp:
            splittedList[i] = ""
        ret = hashlib.md5(''.join(splittedList)).hexdigest()
    except Exception as ecxp:
      logger.debug(">>> Some soundex exception = " + str(ecxp))

    return ret


  @staticmethod
  def hashCalculate(incomeBuf, algo, minWLen=3, additionData=None, stemmerLang=None):
    ret = None
    incomeBuf = incomeBuf.lower()
    if algo == ContentHashCalculator.ALGO_INCOME_BUF:
      ret = hashlib.md5(incomeBuf).hexdigest()
    elif algo == ContentHashCalculator.ALGO_SIMPLE_SPLITTING:
      ret = ContentHashCalculator.hashCalculateSimple(incomeBuf, minWLen)
    elif algo == ContentHashCalculator.ALGO_SNOWBALL_SPLITTING:
      ret = ContentHashCalculator.hashCalculateSnowball(incomeBuf, minWLen, additionData, stemmerLang)
    elif algo == ContentHashCalculator.ALGO_SOUNDEX_SPLITTING:
      ret = ContentHashCalculator.hashCalculateSoundex(incomeBuf, minWLen)

    return ret

