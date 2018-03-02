#coding: utf-8

import re
from string import punctuation

##Get words count in string with different methods
#
#@param string to calculate words count
#@return the words number
def getWordsCount(string, method=0):
  ret = 0

  if method == 0:
    r = re.compile(r'[{}]'.format(punctuation))
    new_strs = r.sub(' ', string)
    ret = len(new_strs.split())
  elif method == 1:
    ret = len(re.findall(r'\w+', string))
  else:
    ret = len(string.split())

  return ret


##Get sentences from content
#
#@param tagValue
#@param maxSentences
#@param maxWordsTotal
#@return content contains sentences that was cut with limits
def getSentencesString(tagValue, maxSentences=1, maxWordsTotal=0):
  ret = tagValue

  sDelimChars = ['.', '!', '?']
  entrances = 0
  pos = 0
  while True:
    for sDelimChar in sDelimChars:
      pos = tagValue.find(sDelimChar, pos + 1)
      if pos != -1:
        entrances += 1
        break
    if pos == -1 or (pos != -1 and entrances >= maxSentences) or ((pos + 1) >= len(tagValue)):
      break

  if pos != -1 and pos < len(tagValue):
    ret = tagValue[:pos + 1]

  if maxWordsTotal > 0:
    wc = getWordsCount(ret)
    if wc > maxWordsTotal:
      pos = 0
      posRes = 0
      wc = 0
      while True:
        pos = ret.find(' ', pos + 1)
        if (pos != -1) and (wc < maxWordsTotal) and ((pos + 1) < len(ret)):
          wc += 1
          posRes = pos
        else:
          break
      if posRes != -1:
        ret = ret[:posRes]

  return ret

ss = ["",
      " ",
      ".",
      "..",
      ". .",
      " . .",
      "The test sentence1. The sentence2. The sentence 3..",
      ".The test sentence1. The sentence2. The sentence 3..",
      " . The test sentence1. The sentence2. The sentence 3..",
      "Thetestsentence1Thesentence2Thesentence",
     ]
for s in ss:
  print '{' + s + '}'
  print '[' + getSentencesString(s, 2, 4) + ']'
  print '--------------'

