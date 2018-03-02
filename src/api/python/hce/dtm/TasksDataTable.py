'''
Created on Mar 10, 2014

@package: dtm
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

##Class describes structures of  task item used in TaskDataManager module
#
Base = declarative_base()
class TasksDataTable(Base):  # pylint: disable-all
  __tablename__ = "tasks_data_table"
  __table_args__ = {'mysql_engine': 'MyISAM'}
  id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True)
  data = sqlalchemy.Column(sqlalchemy.Text, unique=False, index=False)


  def __init__(self):
    pass

