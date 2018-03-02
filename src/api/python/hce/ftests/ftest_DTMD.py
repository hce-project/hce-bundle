#!/usr/bin/python


"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dtm
@file ftest_DTMD.py
@author Oleksii <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


from dtm.DTMD import DTMD 


if __name__ == '__main__':
  dtmd = DTMD()
  dtmd.start()
  daemon = Daemonize(app=DTMD.APP_NAME, pid=DTMD.PID_FILE, action=dtmd.start) 
  daemon.start()
  
