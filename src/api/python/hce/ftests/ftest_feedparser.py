#coding: utf-8
'''
HCE project, Python bindings, DC dependencies
The feedparser research tests.

@package: drce
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2015 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import feedparser
import requests

def _parse_date_fixes(aDateString):
  ret = None
  ds = aDateString

  # Assumes that date format broken and contains the semicolon ":" in TZ like: "Wed, 19 Aug 2015 08:45:53 +01:00"
  parts = ds.split(' ')
  if ("+" in parts[len(parts) - 1] or "-" in parts[len(parts) - 1]) and ":" in parts[len(parts) - 1]:
    parts[len(parts) - 1] = parts[len(parts) - 1].replace(":", "")
    ds = " ".join(parts)
    #ret = feedparser._parse_date_rfc822(ds)
    ret = feedparser._parse_date(ds)

  return ret


feedparser.registerDateHandler(_parse_date_fixes)


#a = "Mon, 17 Aug 2015 17:29:47 +0000"
a = "Wed, 19 Aug 2015 08:45:53 +01:00"
#print feedparser._parse_date(a)

print feedparser._FeedParserMixin._start_pubdate

#url = 'http://www.dailyfinance.com/rss.xml'
#url = 'http://washingtonmonthly.com/ten-miles-square/atom.xml'
url = 'http://www.politico.com/rss/politicopicks.xml'
r = requests.get(url)
d = feedparser.parse(r.content)
print dict(d)
print "\nentries=" + str(len(d.entries))

for e in d.entries:
  if hasattr(e, 'link'):
    print e.link
  else:
    print 'item ' + str(e) + ' has no link field'

