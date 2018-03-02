#coding: utf-8
'''
HCE project, Python bindings, DC dependencies
The selenium research tests.

@package: drce
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2015 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import sys
reload(sys)
sys.setdefaultencoding('utf8')
import time
import re
import ctypes


from selenium import webdriver
import selenium.webdriver.support.ui


timeout = 10
out_dir = "/tmp/00/"
macro_execute = True

#u="http://www.google.com/"
#out_file = "www.google.com.html"

u = "http://www.nytimes.com/2015/06/18/us/politics/gop-is-wary-that-health-care-win-could-have-its-own-risks.html?hp&action=click&pgtype=Homepage&module=first-column-region&region=top-news&WT.nav=top-news&_r=0"
out_file = "www.nytimes.com.html"


timeout = 5

#u = "http://www.intel.co.uk/content/www/uk/en/processors/core/core-i5-processor.html"
#out_file = "www.intel.co.uk.html"
#timeout = 5

#u = "http://www.afpbb.com/articles/-/3046087"
#out_file = "www.afpbb.com.html"
#timeout = 10

#u = "http://www.dhtmlgoodies.com/scripts/ajax-dynamic-content/ajax-dynamic-content.html"
#out_file = "www.dhtmlgoodies.com.html"
#timeout = 5

#u = "http://tr.dc4.hce-project.com/wp-content/uploads/revslider/home-business-slide2/img-slide3.png"
#out_file = "tr.dc4.hce-project.com.png"
#timeout = 5

#u = "http://hierarchical-cluster-engine.com/docs/pdf/DC_client_setup.pdf"
#out_file = "hierarchical-cluster-engine.com.pdf"
#timeout = 5


#Errors simulation
#u = "http://wrongurlwrongurlwrongurlwrongurlwrongurl.com/"
#out_file = "wrongurlwrongurlwrongurlwrongurlwrongurl.com.html"
#timeout = 1
#"Failed to load resource: net::ERR_NAME_NOT_RESOLVED"

#u = "http://127.0.0.1/retcode.php?c=404"
#out_file = "404.html"
#timeout = 1
#"404 (Not Found)"

#u = "http://127.0.0.1/retcode.php?c=403"
#out_file = "403.html"
#timeout = 1
#"403 (Forbidden)"

#u = "http://127.0.0.1/retcode.php?c=500"
#out_file = "500.html"
#timeout = 1
#"500 (Internal Server Error)"

#u = "http://127.0.0.1/redirect.php?c=303&n=100&u=http://127.0.0.1/"
#out_file = "redirect303.html"
#timeout = 5
#Failed to load resource: net::ERR_TOO_MANY_REDIRECTS


exec_path = "../../bin/"
#--verbose --log-path=chromedriver32.log
driver_name = "chromedriver"
driver_release = "_chrome50"
error_msg = ""
driver = None


'''
from pyvirtualdisplay import Display
from selenium import webdriver
display = Display(visible=0, size=(800, 600))
display.start()
browser = webdriver.Chrome()
browser.get('http://www.google.com')
print browser.title
browser.quit()
display.stop()
'''


try:
  #Get driver
  #driver = webdriver.Chrome(executable_path=exec_path + driver_name + str(ctypes.sizeof(ctypes.c_voidp) * 8))
  #driver = webdriver.Remote(command_executor="http://127.0.0.1:36454",
  #                          desired_capabilities=webdriver.DesiredCapabilities.CHROME)

  disable_setuid_sandbox = "--disable-setuid-sandbox"
  chrome_option = webdriver.ChromeOptions()
  chrome_option.add_argument(disable_setuid_sandbox)
  driver = webdriver.Chrome(executable_path=exec_path + driver_name + str(ctypes.sizeof(ctypes.c_voidp) * 8) + driver_release, chrome_options=chrome_option)
except Exception, err:
  error_msg = "Error: " + str(err)
  error_code = 1
except:
  error_msg = "Error: General driver initialization!"
  error_code = 2

if error_msg != "":
  if driver is not None:
    driver.quit()
  print error_msg
  sys.exit()

#print "session_id: " + str(driver.session_id)
#print "capabilities: " + str(driver.capabilities)

driver.set_page_load_timeout(timeout)
driver.get(u)

#Get logs
log_types = driver.log_types
if 'browser' in log_types:
  log_list = driver.get_log('browser')
  for item_dict in log_list:
    if "message" in item_dict and item_dict["message"] != '' and u in item_dict["message"]:
      error_msg += item_dict["message"] + "\n"

error_code = 0
if error_msg != "":
  entrances = [
      (r"(.*)net::ERR_NAME_NOT_RESOLVED(.*)", 10),
      (r"(.*)net::ERR_TOO_MANY_REDIRECTS(.*)", 11),
      (r"(.*)403 \(Forbidden\)(.*)", 403),
      (r"(.*)404 \(Not Found\)(.*)", 404),
      (r"(.*)500 \(Internal Server Error\)(.*)", 500),
      (r"(.*)net::(.*)", 520)]
  for item in entrances:
    regex = re.compile(item[0])
    r = regex.search(error_msg)
    if r:
      error_code = item[1]
      break

if error_code == 0:
  time.sleep(timeout)

content_type = None
charset = None
attr = None

try:
  #attr = driver.find_element_by_xpath('//meta[@http-equiv="content-type"]').get_attribute("content")
  attr = driver.find_element_by_xpath(".//meta[translate(@http-equiv,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='content-type']").get_attribute("content")
  regex = re.compile(r"(.*); charset=(.*)", re.IGNORECASE)
  items = regex.search(attr)
  if items is not None:
    items = items.groups()
    if len(items) > 1:
      content_type = items[0]
      charset = items[1]
except Exception, err:
  pass

if content_type is None:
  try:
    attr = driver.find_element_by_xpath('//html')
    content_type = "text/html"
  except Exception, err:
    pass

if content_type is not None and charset is None:
  try:
    charset = driver.find_element_by_xpath('//meta[@charset]').get_attribute("charset")
  except Exception, err:
    pass

if charset is None:
  try:
    charset = driver.execute_script("return document.characterSet;")
  except Exception, err:
    print str(err)

print "attr=" + str(attr) + ", charset=" + str(charset) + ", content-type=" + str(content_type)


#print str(driver.get_log('driver'))
#GET_SESSION_LOGS, STATUS

html = driver.page_source
cookies = driver.get_cookies()
#print str(cookies)
print driver.current_url

#Macro execution functionality
if macro_execute:
  m = "function aaa(){location.replace('https://www.congress.gov/bill/114th-congress/senate-bill/1016/text');} return aaa();"
  m1 = "function bbb(){return 1;} return bbb();"
  r = driver.execute_script(m)
  r1 = driver.execute_script(m1)
  html_macro = driver.page_source
  print "after macro execution:\n" + "driver.current_url: " + driver.current_url + "\nreturned: " + str(r) + "\nreturned1: " + str(r1)
  f = open(out_dir + out_file + "_macro", "w")
  f.write(html_macro)
  f.close()

driver.quit()

f = open(out_dir + out_file, "w")
f.write(html)
f.close()

if error_msg != "":
  print "ERRORS, code " + str(error_code) + ":\n" + error_msg


