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


from drce.Commands import TaskExecuteRequest
from drce.Commands import TaskCheckRequest
from drce.Commands import TaskGetDataRequest
from drce.Commands import TaskTerminateRequest
from drce.Commands import TaskDeleteRequest

c = TaskExecuteRequest(125)
print c.toJSON()

c = TaskCheckRequest(125, 0)
print c.toJSON()

c = TaskGetDataRequest(125, 0)
print c.toJSON()

c = TaskTerminateRequest(125)
print c.toJSON()

c = TaskDeleteRequest(125)
print c.toJSON()
