#coding=utf-8

import unittest

from dc_crawler import LangDetector
import ConfigParser

class LangDetectorTest(unittest.TestCase):

  def testGuessLanguage(self):
    config = ConfigParser.ConfigParser()
    config.add_section(LangDetector.CONFIG_SECTION)
    config.set(LangDetector.CONFIG_SECTION, LangDetector.CONFIG_DETECTOR, LangDetector.DETECTOR_GUESS_LANGUAGE)
    config.set(LangDetector.CONFIG_SECTION, LangDetector.CONFIG_DETECT_MAX_LENGTH, "1000")
    LangDetector.init(config)
    self.assertEqual(LangDetector.detect(u"hello, how old are you, between options"), ["en"])
    self.assertEqual(LangDetector.detect(u"要订餐，上饿了么，现已加入肯德基豪华午餐，学挖掘机那家强"),["zh"])
    self.assertEqual(LangDetector.detect(u"中国の上海で行われたフィギュアスケート"), ["ja"])
    self.assertEqual(LangDetector.detect(u"の人気特急に体験乗車,戦前から戦後にかけて親しまれた京阪電鉄の特急電車"), ["ja"])

  def testLangid(self):
    config = ConfigParser.ConfigParser()
    config.add_section(LangDetector.CONFIG_SECTION)
    config.set(LangDetector.CONFIG_SECTION, LangDetector.CONFIG_DETECTOR, LangDetector.DETECTOR_LANGID)
    config.set(LangDetector.CONFIG_SECTION, LangDetector.CONFIG_DETECT_MAX_LENGTH, "1000")
    LangDetector.init(config)
    self.assertEqual(LangDetector.detect(u"hello, how old are you, between options"), ["en"])
    self.assertEqual(LangDetector.detect(u"要订餐，上饿了么，现已加入肯德基豪华午餐，学挖掘机那家强"),["zh"])
    self.assertEqual(LangDetector.detect(u"中国の上海で行われたフィギュアスケート"), ["ja"])
    self.assertEqual(LangDetector.detect(u"の人気特急に体験乗車,戦前から戦後にかけて親しまれた京阪電鉄の特急電車"), ["ja"])

  def testDetectLanguage(self):
    config = ConfigParser.ConfigParser()
    config.add_section(LangDetector.CONFIG_SECTION)
    config.set(LangDetector.CONFIG_SECTION, LangDetector.CONFIG_DETECTOR, LangDetector.DETECTOR_DETECTLANGUAGE)
    config.set(LangDetector.CONFIG_SECTION, LangDetector.CONFIG_DETECT_MAX_LENGTH, "1000")
    config.set(LangDetector.CONFIG_SECTION, LangDetector.CONFIG_DETECTLANGUAGE_APIKEYS, "a31d934a633d86cfe5a401340d98fb52")
    LangDetector.init(config)
    self.assertEqual(LangDetector.detect(u"hello, how old are you, between options"), ["en"])
    self.assertEqual(LangDetector.detect(u"要订餐，上饿了么，现已加入肯德基豪华午餐，学挖掘机那家强"),["zh"])
    self.assertEqual(LangDetector.detect(u"中国の上海で行われたフィギュアスケート"), ["ja"])
    self.assertEqual(LangDetector.detect(u"往年の人気特急に体験乗車"), ["ja"])
    self.assertEqual(set(LangDetector.detect(u'''学挖掘机那家强,山东济南找蓝翔 
      You might end up using just a few of them, but the rest will still be there for when you need them'''))
    ,set(["zh", "en"]))


if __name__ == '__main__':
  unittest.main()