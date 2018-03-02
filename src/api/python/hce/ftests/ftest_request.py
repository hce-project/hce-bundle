# coding: utf-8
'''
HCE project, Python bindings, DC dependencies
The requests research tests.

@package: drce
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2017 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import logging
import requests
import requests.exceptions

from app.Utils import varDump
from app.Utils import getTracebackInfo
from dc_crawler.RequestsRedirectWrapper import RequestsRedirectWrapper


def getLogger():
  # create logger
  logger = logging.getLogger('hce')
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

logger = getLogger()

# http://docs.python-requests.org/en/latest/api/

url = 'https://api.github.com/user'
payload = ''
headers = {}

# request(method, url, params=None, data=None, headers=None, cookies=None, files=None, auth=None, timeout=None, allow_redirects=True, proxies=None,
#        hooks=None, stream=None, verify=None, cert=None, json=None)

# r = requests.get(url, auth=('user', 'pass'))
# r = requests.post(url, data=json.dumps(payload), headers=headers)
# r = requests.put("http://httpbin.org/put")
# r = requests.delete("http://httpbin.org/delete")
# r = requests.head("http://httpbin.org/get")
# r = requests.options("http://httpbin.org/get")
# r = requests.head("http://feedproxy.google.com/~r/tpm-news/~3/41c5vi-4njA/senate-confirms-wilbur-ross-as-secretary-of-commerce")
# r = requests.get('https://www.nytimes.com/2017/02/27/science/arctic-plants-spring-global-warming.html?partner=rss&emc=rss')

# s = requests.Session()
# r = s.get('http://httpbin.org/get')
# print str(r)
# with requests.Session() as s:
#  s.get('http://httpbin.org/get')
#  print str(r)

# req = requests.Request('GET', 'http://httpbin.org/get')
# r = req.prepare()
# s = requests.Session()
# s.send(r)
#
# print varDump(obj=r, stringify=True, strTypeMaxLen=256, strTypeCutSuffix='...', stringifyType=1, ignoreErrors=False,
#               objectsHash=None, depth=0, indent=2, ensure_ascii=False, maxDepth=15)
#
# print varDump(r.headers)
# print varDump(r.cookies)
# print varDump(r.history)
# print str(len(r.history))
# print varDump(r.history[0].cookies)
# print varDump(r.history[1].cookies)
# print "====="
# r = requests.head("https://www.nytimes.com/2017/02/27/science/arctic-plants-spring-global-warming.html?partner=rss&emc=rss")
#
# print varDump(obj=r, stringify=True, strTypeMaxLen=256, strTypeCutSuffix='...', stringifyType=1, ignoreErrors=False,
#               objectsHash=None, depth=0, indent=2, ensure_ascii=False, maxDepth=15)
# print varDump(r.cookies)
# print str(requests.utils.dict_from_cookiejar(r.cookies))
# print str(type(requests.utils.dict_from_cookiejar(r.cookies)))

# maxRedirects = 12

# req = requests.Request('HEAD', 'http://thecaucus.blogs.nytimes.com/feed')
# req = requests.Request('HEAD', 'http://scotsman.com/cmlink/swts-news-dynmc-politics-feed-1-957044')
# req = requests.Request('HEAD', 'https://www.nytimes.com/politics/first-draft/feed/')
# r = req.prepare()
#
# s = requests.Session()
# s.max_redirects = int(maxRedirects)
# res = s.send(r)
#
# print varDump(res)
#
# print('Url: ' + str(res.request.url))
# url = 'http://www.forbes.com/sites/jonentine/2014/04/30/infographic-on-4-ways-to-breed-crops-by-scrambling-genes-youll-be-surprised-which-ones-are-regulated/'
# url = 'http://www.forbes.com/sites/blakeoestriecher/2017/04/04/wwe-smackdown-5-ways-shinsuke-nakamura-will-change-the-blue-brand/'
# url = 'http://rssfeeds.usatoday.com/~/477545908/0/usatodaycomworld-topstories~Japanese-PM-Shinzo-Abe-vows-aposcountermeasuresapos-against-North-Korea/'
# url = 'http://rssfeeds.usatoday.com/~/476998866/0/usatodaycomworld-topstories~All-the-presidentaposs-men-and-women-Trumplike-leaders-proliferate/'
url = 'http://rssfeeds.usatoday.com/~/477506178/0/usatodaycomworld-topstories~London-fights-pollution-by-charging-drivers-of-older-polluting-cars/'
# url = 'http://thecaucus.blogs.nytimes.com/feed'
# url = 'https://www.nytimes.com/politics/first-draft/feed/'
# url = 'http://scotsman.com/cmlink/swts-news-dynmc-politics-feed-1-957044'
method = 'head'
method = 'get'
timeout = 101
# headers = {'Accept-Language':'en-US,en;q=0.8,en;q=0.6,us;q=0.4,us;q=0.2,ja;q=0.2', 'Accept-Encoding':'gzip, deflate', 'Cache-Control':'no-cache', 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36', 'Connection':'close', 'Referer':u'http://www.scotsman.com/news/politics/indyref2-scotland-in-union-group-launches-project-listen-1-4392095', '--allow-running-insecure-content':'', 'Pragma':'no-cache', '--disable-setuid-sandbox':'', '--allow-file-access-from-files':'', '--disable-web-security':''}
headers = {'Accept-Language':'en-US,en;q=0.8,en;q=0.6,us;q=0.4,us;q=0.2,ja;q=0.2', 'Accept-Encoding':'gzip, deflate', 'Cache-Control':'no-cache', 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36', 'Connection':'close', '--allow-running-insecure-content':'', 'Pragma':'no-cache', '--disable-setuid-sandbox':'', '--allow-file-access-from-files':'', '--disable-web-security':''}
allowRedirects = True
proxySetting = {'http': 'http://dev.hce-project.com:312'}
auth = None
data = None
maxRedirects = 10
filters = None

try:
  reqv = RequestsRedirectWrapper()
  res = reqv.request(url, method, timeout, headers, allowRedirects, proxySetting, auth, data, maxRedirects, filters)

  print varDump(res)
  print('Url: ' + str(res.request.url))
  print('res.cookies: ' + varDump(res.cookies) + ' type: ' + str(type(res.cookies)))
  cookies = requests.utils.dict_from_cookiejar(res.cookies)
  print('cookies: ' + varDump(cookies) + ' type: ' + str(type(cookies)))

  print('len(res.content) = ' + str(len(res.content)))
#   print('res.iter_content() = ' + varDump(res.iter_content()))
#   out = list(res.iter_content())
#   print('out = ' + varDump(''.join(out)))

#   domain = None
#   path = None
#   name = None
#   value = None
#   for key, value in res.cookies.items():
#     domain = key
#     print('value: ' + str(value) + ' type: ' + str(type(value)))
#
#   print('domain: ' + str(domain) + ', path: ' + str(path) + ', name: ' + str(name) + ', value: ' + str(value))

except requests.exceptions.RequestException, err:
  print ("!!! RequestException: " + str(err))
except Exception, err:
  print ("!!! Exception: " + str(err))
  print (getTracebackInfo())

# try:
#   req = requests.Request(method, url, headers)
#   r = req.prepare()
#
#   s = requests.Session()
#   s.max_redirects = int(maxRedirects)
#   res = s.send(r)
#   # print varDump(res)
#   print varDump(res.headers)
#   print varDump(res.headers['content-type'])
#
#   print('Url: ' + str(res.request.url))
# except requests.exceptions.RequestException, err:
#   print ("!!! RequestException: %s", str(err))
# except Exception, err:
#   print ("!!! Exception: %s", str(err))

