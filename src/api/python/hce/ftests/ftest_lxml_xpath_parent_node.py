#coding: utf-8
'''
HCE project, Python bindings, DC dependencies
The scrapy xpath nodes walking research tests.

@package: DC
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2015 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1

http://effbot.org/zone/element-index.htm
http://doc.scrapy.org/en/latest/topics/selectors.html#working-with-relative-xpaths
http://doc.scrapy.org/en/0.7/topics/selectors.html
http://lxml.de/api/lxml.etree._Element-class.html
http://lxml.de/extensions.html

'''


import sys
reload(sys)
sys.setdefaultencoding('utf8')


'''
import feedparser
f = feedparser.parse("http://www.spiegel.de/schlagzeilen/tops/index.rss")
print str(f)

import lxml
parser = lxml.etree.HTMLParser(encoding='utf-8')
ret = lxml.html.fromstring(rendered_unicode_content.encode("utf-8"), parser=parser)
'''


from lxml import etree

r = "\
<div class='content'>\
   <ul>\
      <li>Item 1</li>\
      <li>Item 2</li>\
      <li>Item 3</li>\
   </ul>\
</div>"
root = etree.XML(r)
nodes = root.xpath('//li')
print str(nodes)
print dir(nodes[0])
print nodes[0].text
print nodes[0].tag
p = nodes[0].getparent()
print p.text
print p.tag

text = root.xpath('string(//ul)')
print str(text)

