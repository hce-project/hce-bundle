#coding: utf-8
'''
HCE project, Python bindings, DC dependencies
The isHostAvailable method tests.

@package: drce
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


def isHostAvailable(url, parameters, logger=None, timeout=0.5):
  ret = True

  try:
    if 'method' in parameters and int(parameters['method']) == 0:
      from urlparse import urlparse
      pr = urlparse(url)
      print str(pr)
      pr = pr.netloc.split(':')
      if len(pr) == 1:
        port = 80
      else:
        port = pr[1]
      host = pr[0]
      print host, port
      if 'domain_name_resolve' in parameters and int(parameters['domain_name_resolve']) == 1:
        import socket
        ai = socket.getaddrinfo(host, port, 0, 0, socket.IPPROTO_TCP)
        print ai
        if 'connect_resolve' in parameters and int(parameters['connect_resolve']) == 1:
          if 'connection_timeout' in parameters and float(parameters['connection_timeout']) > 0:
            timeout = float(parameters['connection_timeout'])
          for item in ai:
            af, socktype, proto, canonname, sa = item
            s = socket.socket(af, socktype, proto)
            s.settimeout(float(timeout))
            try:
              s.connect(sa)
            except Exception, err:
              ret = False
              print 'ERROR:', str(sa), str(err)
              if logger is not None:
                logger.debug("Host %s connect check error: %s", str(sa), str(err))
              continue
            s.close()
            ret = True
            break

  except Exception, err:
    ret = False
    print 'ERROR:', str(err)
    if logger is not None:
      logger.debug("Host %s availability check error: %s", str(url), str(err))

  return ret


p = {"method":0, "domain_name_resolve":1, "connect_resolve":1, "connection_timeout":0.5}
#print isHostAvailable('http://rss.feedsportal.com/a', p)
#print isHostAvailable('http://docs.python.org', p)
#print isHostAvailable('http://192.168.0.1', p)
#print isHostAvailable('http://54.191.242.90:8083', p)
print isHostAvailable('http://108.59.13.38:13010', p)

