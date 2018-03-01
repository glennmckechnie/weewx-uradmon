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
from array import array
import urllib2

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
        self.data_binding = d.get('data_binding', 'uradmon_binding')

        if self.data_binding is not None:
            dbm_dict = weewx.manager.get_manager_dict(config_dict['DataBindings'], config_dict['Databases'],self.data_binding, default_binding_dict=get_default_binding_dict())
        with weewx.manager.open_manager(dbm_dict, initialize=True) as dbm:
            # ensure schema on disk matches schema in memory
            dbcol = dbm.connection.columnsOf(dbm.table_name)
            memcol = [x[0] for x in dbm_dict['schema']]
            if dbcol != memcol:
                raise Exception('uradmon: schema mismatch: %s != %s' %
                                    (dbcol, memcol))


        if self.binding == 'archive':
            self.bind(weewx.NEW_ARCHIVE_RECORD, self.handle_new_archive)
        else:
            self.bind(weewx.NEW_LOOP_PACKET, self.handle_new_loop)

    def handle_new_archive(self, event):
        """save data to database"""
        self.readData(event.record)
        return

    def readData(self, result):
        """
         As the browser returns it...
        {"data":{ "id":"82000079","type":"8","detector":"SI29BG","voltage":384,
        "cpm":20,"temperature":23.07,"humidity":54.89,"pressure":96424,
        "voc":12648,"co2":784,"ch2o":0.01,"pm25":3,"uptime": 36358}}

         As .decode('utf-8') returns it...
        {u'data': {u'uptime': 36168, u'co2': 785, u'cpm': 18, u'voc': 12619,
         u'humidity': 54.97, u'pressure': 96428, u'voltage': 384, u'ch2o': 0.01,
        u'detector': u'SI29BG', u'type': u'8', u'id': u'82000079', u'pm25': 4,
        u'temperature': 23.07}}
        """

        url = "http://" + self.rad_addr + "/j"

        try:
            _response = urllib2.urlopen(url)
        except (urllib2.URLError), e:
            syslog.syslog(syslog.LOG_DEBUG,
                          "uradmon:  Failed download attempt: %s" %e)
        # useful! https://stackoverflow.com/questions/13921910/python-urllib2-receive-json-response-from-url
        # data = json.loads(respons.read().decode(respons.info().get_param('charset') or 'utf-8'))
        json_string = json.loads(_response.read().decode('utf-8'))
        loginf(" json_string is %s" % json_string)

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
        loginf(" rec is %s" % rec)

        dbm_dict = weewx.manager.get_manager_dict(self.config_dict['DataBindings'], self.config_dict['Databases'],self.data_binding,default_binding_dict=get_default_binding_dict())
        with weewx.manager.open_manager(dbm_dict) as dbm:
            dbm.addRecord(rec)
