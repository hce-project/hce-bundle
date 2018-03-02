#!/usr/bin/python


"""
  HCE project,  Python bindings, Distributed Tasks Manager application.
  Event objects definitions.
  
  @package: dc
  @file duplicates_checker.py
  @author Oleksii <developers.hce@gmail.com>
  @link: http://hierarchical-cluster-engine.com/
  @copyright: Copyright &copy; 2013-2014 IOIX Ukraine
  @license: http://hierarchical-cluster-engine.com/license/
  @since: 0.1
  """


import tarfile
import os
import glob
import json
import sys
import shutil


unpack_dir = "/tmp/archive"
A = {}
C = ""

def unpackArchive(archivefile):
  # check if temporary dir exists:
  if not os.path.exists(unpack_dir):
    os.makedirs(unpack_dir)
  else:
    files = glob.glob(unpack_dir+"/*")
    for f in files:
      os.remove(f)
  tar = tarfile.open(archivefile)
  tar.extractall(unpack_dir)
  tar.close()


def countContents():
  site = ""
  id = ""
  number = 0
  with open(unpack_dir+"/dc_test_japan_sites_contents_snatz_rss.sh.log") as f:
    lines = f.readlines()
    for line in lines:
      if "Site:" in line:
        site = line.split()[0].split("Site:")[1]
        id = line.split()[1].split("id:")[1]
        id = id if id!="" else site
      if "Items number" in line:
        number = int(line.split()[2])
        if id in A:
          A[id]["number"] = A[id]["number"] + number
        else:
          A[id] = {"site":site, "number":number, "urls":{}, "duplicates":0}
  #print A


def checkDuplicates():
  print "Archive: " + str(C)
  files = glob.glob(unpack_dir+"/*.json")
  for f in files:
    localDuplicates = {}
    id = f.split(".")[1].split("_")[-1]
    B = json.loads(open(f,"rb").read())
    if len(B["itemsList"])>0 and (B["itemsList"][0]["itemObject"] is not None) and len(B["itemsList"][0]["itemObject"])>0:
      for item in B["itemsList"][0]["itemObject"]:
        urlMd5 = str(item["urlMd5"])
        siteId = str(item["siteId"])
        if urlMd5 in localDuplicates:
          print "Local duplicate site id: "+ str(siteId) + " urlMD5: " + str(urlMd5)
        else:
          localDuplicates[urlMd5] = urlMd5
        if urlMd5 in A[siteId]["urls"]:
          print "Duplicate: site id: " + str(siteId) + " urlMD5: " + str(urlMd5) + " First archive: " + str(A[siteId]["urls"][urlMd5]) + " Duplicate archive: " + C
          A[siteId]["duplicates"] = A[siteId]["duplicates"] +1
        else:
          A[siteId]["urls"][urlMd5] = C


def showResults():
  for site in A.keys():
    print "Site name: " + str(A[site]["site"])
    print "Site id: " + str(str(site))
    print "Site contents: " + str(A[site]["number"])
    print "Site duplicates:" + str(A[site]["duplicates"])


if __name__ == "__main__":
  if len(sys.argv)<2:
    print "/usr/bin/python ./duplicates_checker.py <path to archive>"
  else:
    archive_dir = sys.argv[1]
    archives = glob.glob(archive_dir+"/*")
    for archive in archives:
      C = archive
      unpackArchive(archive)
      countContents()
      checkDuplicates()
      shutil.rmtree(unpack_dir, ignore_errors=True)
    showResults()
