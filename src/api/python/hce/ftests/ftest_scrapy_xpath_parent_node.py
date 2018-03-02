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
'''


import sys
reload(sys)
sys.setdefaultencoding('utf8')

from scrapy.selector import Selector
r = "\
<div class='content'>\
   <ul>\
      <li>Item 1a</li>\
      <li>Item 2a</li>\
      <li>Item 3a</li>\
   </ul>\
   <ul>\
      <li>Item 1b</li>\
      <li>Item 2b</li>\
      <li>Item 3b</li>\
   </ul>\
   <ul>\
      <li>Item 1c</li>\
      <li>Item 2c</li>\
      <li>Item 3c</li>\
   </ul>\
</div>"
sel = Selector(text=r)
print "-->" + str(sel._root) + "<--"
#c = sel.xpath('//div[@class="content"]/ul/li')
c = sel.xpath('//li')
print str(c)
print "-->" + str(c[0]._root) + "<--"
print "-->>" + str(dir(c[0])) + "<<--"

d = c[0].xpath('../../*')
print str(d)
print "-->" + str(d[0]._root) + "<--"
print "-->>" + str(dir(d[0]._root)) + "<<--"
print "prefix -->>" + str(d[0]._root.prefix) + "<<--"
print "tag -->>" + str(d[0]._root.tag) + "<<--"
print "text -->>" + str(d[0]._root.text) + "<<--"

d = c[0]._root.getparent()
print str(d)
print "-->>" + str(dir(d)) + "<<--"
print "prefix -->>" + str(d.prefix) + "<<--"
print "tag -->>" + str(d.tag) + "<<--"
print "text -->>" + str(d.text) + "<<--"


def get_path(etreeElement, path=None):
  if path is None:
    rpath = []
  else:
    rpath = path

  p = etreeElement.getparent()
  if p is not None:
    index = p.index(etreeElement) + 1
    rpath.insert(0, (etreeElement.tag, str(index)))
    return get_path(p, rpath)
  else:
    rpath.insert(0, (etreeElement.tag, 0))
    return rpath

for ci in c:
  print get_path(ci._root)


