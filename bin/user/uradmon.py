#
#    Copyright (c) 2017 Glenn McKechnie glenn.mckechnie@gmail.com>
#    Credit to Tom Keffer <tkeffer@gmail.com>, Matthew Wall and the core
#    based on the csv, pmon and cmon extensions by mwall
#    Copyright 2017 Glenn McKechnie <glenn.mckechnie@gmail.com>
#
#    Mistakes are mine, corrections and or improvements welcomed
#      https://github.com/glennmckechnie/weewx-uradmon
#
#

import json
import datetime
import time
import mysql.connector
import sys
#import configparser
#2.7 from optparse import OptionParser
from array import array
#from array import array
#import urllib
import urllib2
#import urllib2.request

import syslog

import weewx
import weewx.engine
import weeutil.weeutil
import weedb
from weewx.cheetahgenerator import SearchList

VERSION = "0.1.0"

def logmsg(level, msg):
    syslog.syslog(level, 'uradmon: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

schema = [
    ('dateTime', 'INTEGER NOT NULL UNIQUE PRIMARY KEY'),
    ('usUnits',  'INTEGER NOT NULL'),
    ('interval', 'INTEGER NOT NULL'),
    #('uuid',     'INTEGER'),
    #('utype',    'INTEGER'),
    #('udetect',  'TEXT'),
    ('uvolt',    'INTEGER'),
    ('ucpm',     'REAL'),
    ('utemp',    'REAL'),
    ('uhum',     'REAL'),
    ('upres',    'INTEGER'),
    ('uvoc',     'INTEGER'),
    ('uco2' ,    'INTEGER'),
    ('uch2o',    'REAL'),
    ('upm25',    'INTEGER'),
    ('uptime',   'INTEGER')
]
#-- mysql -u root -p
#-- create database uradmon ;
#-- CREATE USER uradmon''@'localhost' identified by 'uradmon';
#-- GRANT select, update, create, delete, insert ON uradmon.* to uradmon@localhost;
#-- quit;
#--
#-- mysql -u root -p uradmon < uradmon.sql

def get_default_binding_dict():
    return {'database': 'uradmon_sqlite',
            'manager': 'weewx.manager.DaySummaryManager',
            'table_name': 'archive',
            'schema': 'user.uradmon.schema'}


class UradMonSkin(SearchList):
    def __init__(self, generator):
        SearchList.__init__(self, generator)

        self.rad_addr = self.generator.skin_dict['device'].get('uradmon_address','')
        self.sql_host = self.generator.skin_dict['mysql'].get('dbhost','')
        self.sql_db = self.generator.skin_dict['mysql'].get('db','')
        self.sql_user = self.generator.skin_dict['mysql'].get('dbuser','')
        self.sql_user_pwd = self.generator.skin_dict['mysql'].get('dbpwd','')

class UradMon(weewx.engine.StdService):
    def __init__(self, engine,config_dict):
        super(UradMon, self).__init__(engine, config_dict)
        self.d_binding = '1'
        d = config_dict.get('UradMon', {})
        f = config_dict.get('DataBindings'),('uradmon_binding', {})
        loginf("       f is {} %s" % d)

        self.binding = d.get('binding', 'archive')
#        binding = d.get('data_binding', 'uradmon')
        self.data_binding = d.get('data_binding', 'uradmon_binding')

        #loginf("d is {} %s" % d)
        #loginf("databinding is {} %s" % self.data_binding)
        if self.data_binding is not None:
            #loginf("d is still {} %s" % d)
#            dbm_dict = weewx.manager.get_manager_dict_from_config(config_dict, binding)
            dbm_dict = weewx.manager.get_manager_dict(config_dict['DataBindings'], config_dict['Databases'],self.data_binding, default_binding_dict=get_default_binding_dict())
        with weewx.manager.open_manager(dbm_dict, initialize=True) as dbm:
            # ensure schema on disk matches schema in memory
            dbcol = dbm.connection.columnsOf(dbm.table_name)
            memcol = [x[0] for x in dbm_dict['schema']]
            if dbcol != memcol:
                raise Exception('uradmon: schema mismatch: %s != %s' %
                                    (dbcol, memcol))


#        self.binding = self.generator.config_dict['DataBindings']['uradmon'].get('binding', 'archive')
        if self.binding == 'archive':
            self.bind(weewx.NEW_ARCHIVE_RECORD, self.handle_new_archive)
        else:
            self.bind(weewx.NEW_LOOP_PACKET, self.handle_new_loop)

        # get the database parameters we need to function
#        binding = self.generator.config_dict['UradMon'.get('data_binding')
#        self.dbm = self.engine.db_binder.get_manager(data_binding=binding,initialize=True)

        # be sure database matches the schema we have
#        dbcol = self.dbm.connection.columnsOf(self.dbm.table_name)
#        dbm_dict = weewx.manager.get_manager_dict_from_config(self.generator.config_dict, binding)
#        dupecol = [x[0] for x in dbm_dict['schema']]
#        if dbcol != dupecol:
#            raise Exception('uradmon schema mismatch: %s != %s' % (dbcol, dupecol))



    def handle_new_archive(self, event):
        """save data to database"""
       # self.dbm.addRecord(event.record)
        self.readData(event.record)
        return

     # loginf('new_archive_record %s' %(event.record))
     # loginf('new_archive_record %s' %(event))
     # data record {'heatindex': 17.296875000000004, 'outHumidity': 72.454275, 'maxSolarRad': 782.7650660547766, 'hail': 0.0, 'inTempBatteryStatus': 4.93, 'rainBatteryStatus': 4.95, 'hailRate': 0.0, 'altimeter': 1016.2321988390987, 'outTempBatteryStatus': 4.96, 'radiation': 1400.0322500000002, 'inTemp': 21.65625, 'inDewpoint': 48.14709605637118, 'barometer': 1015.294, 'windchill': 17.296875000000004, 'dewpoint': 12.293227803655595, 'windrun': 20.47582442781085, 'rain': 0.0, 'humidex': 19.710957581208838, 'pressure': 963.4797924584669, 'ET': 0.010438185627416401, 'rainRate': 0.0, 'usUnits': 17, 'rainCount4': 987.0, 'rainCount3': 835.0, 'rainCount1': 20227967.0, 'appTemp': 15.479917358792356, 'windBatteryStatus': 4.95, 'interval': 1, 'dateTime': 1507163160.0, 'windDir': 241.28352189240834, 'outTemp': 17.296875000000004, 'windSpeed': 3.609926636088604, 'inHumidity': 44.3086, 'windGust': 3.823387430030153, 'windGustDir': 247.47474747474746, 'cloudbase': 1073.9298293015042}
#####!/usr/bin/env python3

    #def ConvertJSON(self, json_string):

        #uarray = [[uuid, utype, udetect, uvolt, ucpm, utemp, uhum, upres, uvoc, uco2, uch2o, upm25, uptime]]

        #return uarray
        #return (uuid, utype, udetect, uvolt, ucpm, utemp, uhum, upres, uvoc, uco2, uch2o, upm25, uptime)

    def openDBconnection(self):
        try:
            cnx = mysql.connector.connect(host=self.sql_host,
                                          user=self.sql_user,
                                          password=self.sql_user_pwd,
                                          database=self.sql_db)
        except mysql.connector.Error as err:
 #       if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
 #           print("Something is wrong with your user name or password")
 #       elif err.errno == errorcode.ER_BAD_DB_ERROR:
 #           print("Database does not exists")
 #       else:
                print(err)

        else:
            return cnx

    def getLastDate(self):

        con = self.openDBconnection()
        cursor = con.cursor()
        cursor.execute("SELECT max(timestamp) from S129BG")

        record = cursor.fetchone()

        con.close()

        return record[0]

    def readData(self, result):
        self.rad_addr = '192.168.0.235'
        #self.sql_host = _dict['mysql'].get('dbhost','')
        #self.sql_db = self.generator.skin_dict['mysql'].get('db','')
        #self.sql_user = self.generator.skin_dict['mysql'].get('dbuser','')
        #self.sql_user_pwd = self.generator.skin_dict['mysql'].get('dbpwd','')

        url = "http://" + self.rad_addr + "/j"

        print (url)
        try:
            _response = urllib2.urlopen(url)
        except (urllib2.URLError), e:
            syslog.syslog(syslog.LOG_DEBUG,
                          "uradmon:  Failed download attempt: %s" %e)
        # useful! https://stackoverflow.com/questions/13921910/python-urllib2-receive-json-response-from-url
        # data = json.loads(respons.read().decode(respons.info().get_param('charset') or 'utf-8'))
        json_string = json.loads(_response.read().decode('utf-8'))
#        print ("d_data urllib =", d_data)

#        d_data = json.loads(urllib.request.urlopen(url, timeout=5).read().decode('utf-8'))
# 2.7d_data = json.loads(urllib.Request.urlopen(url).read().decode('utf-8'))
#        d_data = json.loads(urllib2.Request.urlopen(url).read().decode('utf-8'))

#        data_dict = self.ConvertJSON(d_data)

        #con = self.openDBconnection()
        #cursor = con.cursor()
        #row_count = 0

        #for row in data_dict:
        #timestamp = int(time.time());

       # sql = "INSERT INTO S129BG (timestamp, uuid, utype, udetect, uvolt, ucpm, utemp, uhum, upres, uvoc, uco2, uch2o, upm25, uptime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        #values = (timestamp, row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12])
	#loginf(" json_string is %s" % json_string)

        timestamp = int(time.time());
	int_one = 1

        rec = {'dateTime': timestamp,
               'usUnits': weewx.METRIC,
               'interval': int_one,
               #'uuid': json_string["data"]["id"],
               #'utype': json_string["data"]["type"],
               #'udetect': json_string["data"]["detector"],
               'uvolt': json_string["data"]["voltage"],
               'ucpm': json_string["data"]["cpm"],
               'utemp': json_string["data"]["temperature"],
               'uhum': json_string["data"]["humidity"],
               'upres': json_string["data"]["pressure"],
               'uvoc': json_string["data"]["voc"],
               'uco2': json_string["data"]["co2"],
               'uch2o': json_string["data"]["ch2o"],
               'upm25': json_string["data"]["pm25"],
               'uptime': json_string["data"]["uptime"]}
	#loginf(" rec is %s" % rec)


        #rec:'  {'dateTime': timestamp,
        #       'usUnits': weewx.METRIC,
        #       'interval': '1',
        #       'uuid': uuid,
        #       'utype': utype,
        #       'udetect': udetect,
        #       'uvolt': uvolt,
        #       'ucpm': upcm,
        #      'utemp':utemp,
        #       'uhum':uhum,
        #       'upres':upres,
        #       'uvoc':uvoc,
        #       'uco2':uco2,
        #       'uch2o': uch2o,
        #       'upm25': upm25,
        #       'uptime': uptime}

        dbm_dict = weewx.manager.get_manager_dict(self.config_dict['DataBindings'], self.config_dict['Databases'],self.data_binding,default_binding_dict=get_default_binding_dict())
##	dbm_dict = weewx.manager.get_manager_dict(config_dict['DataBindings'], config_dict['Databases'],self.data_binding, default_binding_dict=get_default_binding_dict())
        with weewx.manager.open_manager(dbm_dict) as dbm:
            dbm.addRecord(rec)
         #  print (values)
         #  cursor.execute(sql, values)
         #  recordID:'  cursor.lastrowid
         #  row_count += 1

        #con.commit()
        #cursor.close()
        #con.close()
