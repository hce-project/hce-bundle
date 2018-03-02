'''
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects functional tests.

@package: dtm
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import dtm.EventObjects


if __name__ == "__main__":
  TEST_TITLE = "Test "
  TEST_TITLE_OBJECT = " object:\n"

  #Test NewTask object auto-generated task Id
  t = dtm.EventObjects.NewTask("ls")
  t.setSessionVar("WIDTH", 80)
  t.setSessionVar("LANG", "POSIX")
  t.setSessionVar("time_max", 30000)
  t.setFile(("file1.txt", "test file content 1",
              dtm.EventObjects.Task.FILE_ACTION_CREATE_BEFORE | dtm.EventObjects.Task.FILE_ACTION_DELETE_AFTER))
  t.setFile(("file2.txt", "test file content 2", dtm.EventObjects.Task.FILE_ACTION_DELETE_AFTER))
  t.setStrategyVar(t.STRATEGY_PRIORITY, 2)
  t.setStrategyVar(t.STRATEGY_DATE, "2014-09-09 11:00:00")
  print TEST_TITLE + t.__class__.__name__ + TEST_TITLE_OBJECT, vars(t)
  print t.toJSON()


  #Test NewTask object explicit task Id
  t = dtm.EventObjects.NewTask("ls", 18446744073103260337L)
  print TEST_TITLE + t.__class__.__name__ + TEST_TITLE_OBJECT, vars(t)
  print t.toJSON()

  #Test UpdateTask object
  t = dtm.EventObjects.UpdateTask(1)
  t.setSessionVar("WIDTH", 80)
  t.setSessionVar("LANG", "POSIX")
  print TEST_TITLE + t.__class__.__name__ + TEST_TITLE_OBJECT, vars(t)


  #Test CheckTaskState object
  ts = dtm.EventObjects.CheckTaskState(1, dtm.EventObjects.CheckTaskState.TYPE_SIMPLE)
  print TEST_TITLE + ts.__class__.__name__ + TEST_TITLE_OBJECT, vars(ts)
  print ts.toJSON()


  #Test GetTasksStatus object
  ts = dtm.EventObjects.GetTasksStatus((1, 2))
  ts.setFilterVar(ts.FILTER_CDATE_FROM, "2014-09-09 12:00")
  ts.setFilterVar(ts.FILTER_CDATE_TO, "2014-09-09 13:00")
  ts.setFilterVar(ts.FILTER_INPROGRESS, 1)
  print TEST_TITLE + ts.__class__.__name__ + TEST_TITLE_OBJECT, vars(ts)


  #Test FetchTaskResults object
  fr = dtm.EventObjects.FetchTasksResults(1, dtm.EventObjects.FetchTasksResults.TYPE_SAVE)
  print TEST_TITLE + fr.__class__.__name__ + TEST_TITLE_OBJECT, vars(fr)
  print fr.toJSON()


  #Test FetchTasksResultsFromCache object
  fr = dtm.EventObjects.FetchTasksResultsFromCache((1, 2))
  print TEST_TITLE + t.__class__.__name__ + TEST_TITLE_OBJECT, vars(t)


  #Test DeleteTask object
  dt = dtm.EventObjects.DeleteTask(1)
  print TEST_TITLE + dt.__class__.__name__ + TEST_TITLE_OBJECT, vars(dt)
  print dt.toJSON()


  #Test ExecuteTasks object
  et = dtm.EventObjects.ExecuteTask(1)
  print TEST_TITLE + et.__class__.__name__ + TEST_TITLE_OBJECT, vars(et)


  #Test GetScheduledTasks object
  gt = dtm.EventObjects.GetScheduledTasks(100)
  print TEST_TITLE + gt.__class__.__name__ + TEST_TITLE_OBJECT, vars(gt)


  #Test GetScheduledTasksResponse object
  gtr = dtm.EventObjects.GetScheduledTasksResponse((1, 2, 3))
  print TEST_TITLE + gtr.__class__.__name__ + TEST_TITLE_OBJECT, vars(gtr)


  #Test GeneralResponse object
  gr = dtm.EventObjects.GeneralResponse()
  print TEST_TITLE + gr.__class__.__name__ + TEST_TITLE_OBJECT, vars(gr)
  gr = dtm.EventObjects.GeneralResponse(3, "Error, data not found!")
  gr.statuses.append((2435515, 0))
  gr.statuses.append((2435516, 1))
  print TEST_TITLE + gr.__class__.__name__ + TEST_TITLE_OBJECT, vars(gr)
  print gr.toJSON()


  #Test DeleteTaskData object
  dtd = dtm.EventObjects.DeleteTaskData(1)
  print TEST_TITLE + dtd.__class__.__name__ + TEST_TITLE_OBJECT, vars(dtd)

  #Test FetchEEResponseData object
  fd = dtm.EventObjects.FetchEEResponseData(1)
  print TEST_TITLE + fd.__class__.__name__ + TEST_TITLE_OBJECT, vars(fd)


  drd = dtm.EventObjects.DeleteEEResponseData(1)
  print TEST_TITLE + drd.__class__.__name__ + TEST_TITLE_OBJECT, vars(drd)


  ftd = dtm.EventObjects.FetchTaskData(1)
  print TEST_TITLE + ftd.__class__.__name__ + TEST_TITLE_OBJECT, vars(ftd)


  erd = dtm.EventObjects.EEResponseData(1)
  erd.errorCode = 2
  erd.errorMessage = "Process terminated by VRAM limitation"
  erd.pId = 2343253
  erd.type = dtm.EventObjects.EEResponseData.REQUEST_TYPE_CHECK
  print TEST_TITLE + erd.__class__.__name__ + TEST_TITLE_OBJECT, vars(erd)
  print erd.toJSON()


  st = dtm.EventObjects.ScheduledTask(1, 0, 0, dtm.EventObjects.ScheduledTask.STATE_PLANNED, 0)
  print TEST_TITLE + st.__class__.__name__ + TEST_TITLE_OBJECT, vars(st)


  st = dtm.EventObjects.GetScheduledTask()
  print TEST_TITLE + st.__class__.__name__ + TEST_TITLE_OBJECT, vars(st)


  r = dtm.EventObjects.Resource("localhost:5660")
  print TEST_TITLE + r.__class__.__name__ + TEST_TITLE_OBJECT, vars(r)


  ravg = dtm.EventObjects.ResourcesAVG()
  print TEST_TITLE + ravg.__class__.__name__ + TEST_TITLE_OBJECT, vars(ravg)


  utf = dtm.EventObjects.UpdateTaskFields(1)
  utf.fields["state"] = 1
  print TEST_TITLE + utf.__class__.__name__ + TEST_TITLE_OBJECT, vars(utf)

  gtmf = dtm.EventObjects.GetTaskManagerFields(1)
  print TEST_TITLE + gtmf.__class__.__name__ + TEST_TITLE_OBJECT, vars(gtmf)


  tmf = dtm.EventObjects.TaskManagerFields(1)
  tmf.fields["state"] = 2
  print TEST_TITLE + tmf.__class__.__name__ + TEST_TITLE_OBJECT, vars(tmf)


  st1 = dtm.EventObjects.ScheduledTask(1, 0, 0, dtm.EventObjects.ScheduledTask.STATE_PLANNED, 0)
  st2 = dtm.EventObjects.ScheduledTask(2, 0, 0, dtm.EventObjects.ScheduledTask.STATE_PLANNED, 0)
  ust = dtm.EventObjects.UpdateScheduledTasks([st1, st2])
  print TEST_TITLE + ust.__class__.__name__ + TEST_TITLE_OBJECT, vars(ust)

