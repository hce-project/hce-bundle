"""@package docstring
 @file scraper_utils.py
 @author Alexey <developers.hce@gmail.com>
 @link http://hierarchical-cluster-engine.com/
 @copyright Copyright &copy; 2013 IOIX Ukraine
 @license http://hierarchical-cluster-engine.com/license/
 @package HCE project node API
 @since 0.1
"""


import base64
import md5


# convert plain text to base64 encoded string
def encode(text):
  return base64.b64encode(text)
# convert base64 encoded string to plain text
def decode(text):
  return base64.b64decode(text)


def unicode_decode(text):
  return str(text).decode("utf-8")


def md5_encode(text):
  return str(md5.new(unicode_decode(text)).hexdigest())
