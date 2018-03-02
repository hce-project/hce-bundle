#!/usr/bin/python
# coding: utf-8
"""
HCE project, Python bindings, Crawler application.
ScraperLangDetector tests.

@package: dc
@file ftest_ScraperLangDetector.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2017 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""

import os
import sys
import logging

from dc_processor.ScraperLangDetector import ScraperLangDetector
from dc_processor.scraper_result import Result
import dc_processor.Constants as CONSTS
from app.Utils import varDump

def getLogger():
  # create logger
  log = logging.getLogger('test')
  log.setLevel(logging.DEBUG)

  # create console handler and set level to debug
  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)

  # create formatter
  formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')

  # add formatter to ch
  ch.setFormatter(formatter)

  # add ch to logger
  log.addHandler(ch)

  return log


class TestScraperLangDetector(object):
  # # Initialization
  def __init__(self, properties, log):
    self.properties = properties
    self.logger = log


  # # Test processing method
  def run(self, response):

    langDetector = ScraperLangDetector(self.properties[CONSTS.LANG_PROP_NAME])
    langDetector.process(response, self.logger)
    langTagsDict = langDetector.getLangTags()
    langTagsNames = langDetector.getLangTagsNames()
    self.logger.debug("langTagsDict: %s", varDump(langTagsDict))
    self.logger.debug("langTagsNames: %s", varDump(langTagsNames))
    # self.logger.debug("response: %s", varDump(response, stringifyType=0))


if __name__ == '__main__':

  properties = {"SCRAPER_LANG_DETECT":{"prefix":"lang_", "suffix":"_lang", "tags":["title", "content_encoded", "description"]}}
  properties = {"SCRAPER_LANG_DETECT":{"suffix":"_lang", "tags":["title", "content_encoded", "description"]}}
  properties = {"SCRAPER_LANG_DETECT":{"suffix":"_lang", "tags":["content_encoded"], "maps":{"en":["fr", "es", "*"], "ja":["ja-123", "zh", "za"], "ru":["ru", "uk"], "pl":["pl"], "de":["de"]}, "size":100}}
  properties = {"SCRAPER_LANG_DETECT":{"tags":["content_encoded"]}}

  response = Result(None, None)
  response.tags['title'] = {'xpath': '', 'extractor': 'GooseExtractor', 'lang_suffix': '_language', 'lang': 'en', 'type': None, 'data': 'None of the victims really wanted to die', 'name': 'title'}
  response.tags['content_encoded'] = {'xpath': '', 'extractor': 'GooseExtractor', 'lang_suffix': '_language', 'lang': 'en', 'type': None, 'data': '東京都江東区の路上で職業不詳太田智子さん（４７）の遺体が見つかった事件で、警視庁捜査１課は３日、死体遺棄容疑で、交際相手の大田区職員上田一美容疑者（５５）＝大田区久が原＝を逮捕した。「首をネクタイで絞めて殺し、死体を捨てた」と話しているといい、殺人容疑でも捜査する。', 'name': 'content_encoded'}
#  response.tags['content_encoded'] = {'xpath': '', 'extractor': 'GooseExtractor', 'lang_suffix': '_language', 'lang': 'en', 'type': None, 'data': '東京', 'name': 'content_encoded'}

  testScraperLangDetector = TestScraperLangDetector(properties=properties, log=getLogger())
  testScraperLangDetector.run(response)







