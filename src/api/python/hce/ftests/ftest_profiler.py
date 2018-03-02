import os

#import ppath
#from ppath import sys

import logging.config
from time import sleep

import app.Profiler as Profiler

class SomeClass:
  """A simple class for simulate work"""
  def __init__(self):
    print "SomeClass was created"

  def fewSleepCalls(self):
    self.bigSleep()
    self.smallSleep()

  def bigSleep(self):
    self.__sleep(3)

  def smallSleep(self):
    self.__sleep(1)

  def __sleep(self, seconds):
    print "SomeClass sleep"
    sleep(seconds)
    print "SomeClass wake up"


if __name__ == "__main__":

  # Save current working directory.
  retdir = os.getcwd()
  #For test necessary
  os.chdir('../')

  pr = Profiler.Profiler()

  print('isStarted: ' + str(pr.isStarted))
  print('status: ' + str(pr.status))
  print('loggerConfigName: ' + pr.loggerConfigName)
  print('traceback: ' + str(pr.traceback))

  pr.readConfig(pr.loggerConfigName)

  pr.start()
  pr.start()

  print('isStarted: ' + str(pr.isStarted))

  x = SomeClass()
  x.fewSleepCalls()

  pr.stop()

  print('isStarted: ' + str(pr.isStarted))

  pr.stop()
  # Restore working directory.
  os.chdir(retdir)

