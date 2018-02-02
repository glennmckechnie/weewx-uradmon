#!/usr/bin/python3
#####!/usr/bin/env python3
import json
import datetime
import time
import mysql.connector
import sys
#2.7 import urllib
#2.7 import urllib2
import urllib.request
import configparser
#2.7 from optparse import OptionParser
from array import array
#from array import array
#import urllib
#import urllib2

def ConvertJSON(json_string):

    #    Get the variables in which we're interested
    uuid = json_string["data"]["id"]
    utype = json_string["data"]["type"]
    udetect = json_string["data"]["detector"]
    uvolt = json_string["data"]["voltage"]
    ucpm = json_string["data"]["cpm"]
    utemp = json_string["data"]["temperature"]
    uhum = json_string["data"]["humidity"]
    upres = json_string["data"]["pressure"]
    uvoc = json_string["data"]["voc"]
    uco2 = json_string["data"]["co2"]
    uch2o = json_string["data"]["ch2o"]
    upm25 = json_string["data"]["pm25"]
    uptime = json_string["data"]["uptime"]

    uarray = [[uuid, utype, udetect, uvolt, ucpm, utemp, uhum, upres, uvoc, uco2, uch2o, upm25, uptime]]

    return uarray

def openDBconnection():
    try:
          cnx = mysql.connector.connect(host=sql_host,
                                        user=sql_user,
                                        password=sql_user_pwd,
                                        database=sql_db)
    except mysql.connector.Error as err:
 #       if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
 #           print("Something is wrong with your user name or password")
 #       elif err.errno == errorcode.ER_BAD_DB_ERROR:
 #           print("Database does not exists")
 #       else:
            print(err)

    else:
        return cnx

def getLastDate():

  con = openDBconnection()
  cursor = con.cursor()
  cursor.execute("SELECT max(timestamp) from S129BG")

  record = cursor.fetchone()

  con.close()

  return record[0]

# ============
#     Start
# ============

# Read configuration file
config = configparser.ConfigParser()
config.sections()
config.read("uradmon.conf")

radmon_ip = config['radmonitor']['radmon_ip']
sql_host = config['mysql']['dbhost']
sql_db = config['mysql']['db']
sql_user = config['mysql']['dbuser']
sql_user_pwd = config['mysql']['dbpwd']

url = "http://" + radmon_ip + "/j"
#url = "http://192.168.0.235/j"

print (url)
d_data = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
# 2.7d_data = json.loads(urllib.Request.urlopen(url).read().decode('utf-8'))
#d_data = json.loads(urllib.Request.urlopen(url).read().decode('utf-8'))

data_dict = ConvertJSON(d_data)

con = openDBconnection()
cursor = con.cursor()
row_count = 0

for row in data_dict:
    timestamp = int(time.time());

    sql = "INSERT INTO S129BG (timestamp, uuid, utype, udetect, uvolt, ucpm, utemp, uhum, upres, uvoc, uco2, uch2o, upm25, uptime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (timestamp, row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12])
    print (values)
    cursor.execute(sql, values)
    recordID = cursor.lastrowid
    row_count += 1

con.commit()
cursor.close()
con.close()

# Write LOG-File
#logfile = open('/home/pi/PV-Logger/PVLogger.log', "a")
#logfile.write("%s: URL: %s\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), url))
#logfile.write("%s: First entry from: %s\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), str(firstTime)))
#logfile.write("%s: Last Entry from: %s\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), str(lastTime)))
#logfile.write("%s: %s records written\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), str(row_count)))
#logfile.write("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
#logfile.close
