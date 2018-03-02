#coding: utf-8
'''
HCE project, Python bindings, DRCE module
Event objects functional tests.

@package: drce
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2015 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import re
# #The Response class
# represents an web page response
class SimpleCharsetDetector(object):


  def __init__(self, content=None):
    #content
    self.content = content

  def detect(self, content=None):
    ret = None

    try:
      if content is None:
        cnt = self.content
      else:
        cnt = content

      pattern = r'<meta(?!\s*(?:name|value)\s*=)(?:[^>]*?content\s*=[\s"\']*)?([^>]*?)[\s"\';]*charset\s*=[\s"\']*([^\s"\'/>]*)'
      matchObj = re.search(pattern, cnt, re.I | re.M | re.S)
      if matchObj:
        ret = matchObj.group(2)

    except Exception, err:
      del err

    return ret


print SimpleCharsetDetector().detect("<html>\n" + '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />' + "\n")
print SimpleCharsetDetector().detect('<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />')
