
import re
from app.url_normalize import url_normalize


class Url(object):
  def __init__(self, url):
    self.url = url


  def checkUrlCodeValid(self):
    ret = True
    urlEncode = False
    subIndex = 0
    for index in xrange(0, len(self.url)):
      if urlEncode:
        if not (self.url[index] >= "a" and self.url[index] <= "f" or \
        self.url[index] >= "A" and self.url[index] <= "F" or \
        self.url[index] >= "0" and self.url[index] <= "9"):
          ret = False
          break
        subIndex += 1
        if subIndex == 2:
          subIndex = 0
          urlEncode = False
      if self.url[index] == "%":
        urlEncode = True
    return ret


  def isValid(self):
    ret = False

    regex = re.match(r'^((ht|f)tp(s?)\:\/\/|~/|/)?([\w]+:\w+@)?([a-zA-Z]{1}([\w\-]+\.)+([\w]{2,5}))(:[\d]{1,5})?/?(\w+\.[\w]{3,4})?((\?\w+=\w+)?(&\w+=\w+)*)?', self.url, re.IGNORECASE)  # pylint: disable=C0301

    ret = regex is not None
    if ret:
      ret = self.checkUrlCodeValid()
    return ret

  def getNormalized(self):
    return url_normalize(self.url)

  def __lt__(self, other):
    return self.url < other.url

  def __le__(self, other):
    return self.url <= other.url

  def __gt__(self, other):
    return self.url > other.url

  def __ge__(self, other):
    return self.url >= other.url

  def __eq__(self, other):
    return self.url == other.url

  ###
  # Parameters:
  #   urls - a list of Url instance objects to display stats for
  #Returns:
  #  A list of stat mappings, a stat mapping has the following fields:
  #    source: the source url
  #    canonicalzed: the canonicalized url
  #    valid: whether the url is valid
  #    source_unique: whether the source is unqiue amongst the urls list
  #    canonicalized_unique: like source_unique but for canonicalized urls
  #
  @staticmethod
  def GetStats(urls):
    stats = []
    canonicalized_list = [url.getNormalized() for url in urls]
    for url in urls:
      url_stat = {}
      canonicalized = url.getNormalized()
      url_stat['source'] = url.url
      url_stat['canonicalized'] = canonicalized
      url_stat['valid'] = url.isValid()
      url_stat['source_unique'] = (urls.count(url) == 1)
      url_stat['canonicalized_unique'] = \
          (canonicalized_list.count(canonicalized) == 1)
      stats.append(url_stat)
    return stats

