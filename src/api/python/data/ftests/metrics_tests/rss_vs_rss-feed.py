import MySQLdb as mdb
import MySQLdb.cursors
from contextlib import closing

dbHost="127.0.0.1"
dbPort=3306
dbUser="hce"
dbPWD="hce12345"
dbName="dc_urls"
rssTable = "urls_2f105d68146db820c23aa3fc6010888d"
rssFeedTable = "urls_c241444dcd1b03bf04549448830c8942"
clause = "TagsCount<>0"

connector = mdb.connect(dbHost, dbUser, dbPWD, dbName, dbPort)


sites_list = [rssTable, rssFeedTable]
rss = set()
rss_feed = set()
urls = {}

A = {"urls_2f105d68146db820c23aa3fc6010888d": set(), "urls_c241444dcd1b03bf04549448830c8942": set()}
C = {}

try:
  with closing(connector.cursor()) as cursor:
    for key in A.keys():
      query = "select URLMd5, URL, ParentMd5 from %s where %s" %(key, clause)
      print query
      cursor.execute(query)
      connector.commit()
      ret = cursor.fetchall()
      for r in ret:
        urls[r[0]] = r[2]
        A[key].update([r[0]])
      #print "site: " + key + " Contents: " + str(len(A[key]))
  B = A["urls_c241444dcd1b03bf04549448830c8942"].difference(A["urls_2f105d68146db820c23aa3fc6010888d"])
  #print "urls:" , urls
  #print "rss & rss_feed: " , len(A["urls_2f105d68146db820c23aa3fc6010888d"].intersection(A["urls_c241444dcd1b03bf04549448830c8942"]))
  print "rss_feed - rss  : " , len(B)
  #from urlparse import urlparse
  for b in B:
    #print urls[b]
    #a = urlparse(urls[b])
    if urls[b] in C:
      C[urls[b]].append(b)
    else:
      C[urls[b]] = [b]
  #print C.keys()
  URLS = []
  with closing(connector.cursor()) as cursor:
    for site in C.keys():
      query = "select URL from urls_2f105d68146db820c23aa3fc6010888d where URLMd5='%s' limit 1" %(site)
      cursor.execute(query)
      connector.commit()
      ret = cursor.fetchall()
      URLS.append(ret[0])
  print URLS

  #D = sorted(C.items(), key=lambda x: (len(x[1])), reverse=True)
  #print D
except mdb.Error as err:
  dbConnection.rollback()
  errString = "%s %s message = %s" % (err.args[0], err.args[1], str(err.message))
  print errString
