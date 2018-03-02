#coding: utf-8
'''
HCE project, Python bindings, DC dependencies
The cement app research tests.

@package: drce
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2015 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


from cement.core import foundation, controller

class MyController(controller.CementBaseController):
  class Meta:
    label = 'base'
    arguments = [(['-f', '--foo'], dict(help='Notorious foo option')), ]
    config_defaults = dict(
      debug=False,
      some_config_param='some_value',
      )

  @controller.expose(help='This is the default command', hide=True)
  def default(self):
    #print str(self.app._meta.__dict__)
    print('Hello World')

class MyApp(foundation.CementApp):
  class Meta:
    label = 'helloworld'
    extensions = ['daemon', 'json', ]
    base_controller = MyController

app = MyApp()
try:
  app.setup()
  app.run()
finally:
  app.close()


