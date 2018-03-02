#!/usr/bin/python


'''
HCE project, Python bindings, Distributed Crawler application.
Simple server listener for the GET request port 9000 application.
http://stackoverflow.com/questions/31371166/reading-json-from-simplehttpserver-post-data

@package: dc
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import SimpleHTTPServer
import SocketServer
import logging

PORT = 9000

class GetHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def do_GET(self):
    logging.error(self.headers)
    SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

  def do_POST(self):
    #print "got post!!"
    content_len = int(self.headers.getheader('content-length', 0))
    post_body = self.rfile.read(content_len)
    #test_data = simplejson.loads(post_body)
    logging.error(self.headers)
    logging.error(post_body)
    #return SimpleHTTPRequestHandler.do_POST(self)

if __name__ == "__main__":
  Handler = GetHandler
  httpd = SocketServer.TCPServer(("", PORT), Handler)

  httpd.serve_forever()
