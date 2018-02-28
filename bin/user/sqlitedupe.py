# $Id: csv.py 1319 2015-05-10 08:27:43Z mwall $
# Copyright 2015 Matthew Wall
#
# sqlitedupe.py
# based on the csv, pmon and cmon extensions by mwall
# Copyright 2017 Glenn McKechnie
# glenn.mckechnie@gmail.com


#import os
#import os.path
#import time
import syslog

import weewx
import weewx.engine
import weeutil.weeutil
import weedb

VERSION = "0.1"

def logmsg(level, msg):
    syslog.syslog(level, 'sqlitedupe: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)

schema = [
    ('dateTime', 'INTEGER NOT NULL UNIQUE PRIMARY KEY'),
    ('heatindex', 'REAL'),
    ('outHumidity', 'REAL'),
    ('maxSolarRad', 'REAL'),
    ('hail', 'REAL'),
    ('inTempBatteryStatus', 'REAL'),
    ('rainBatteryStatus', 'REAL'),
    ('hailRate', 'REAL'),
    ('altimeter', 'REAL'),
    ('outTempBatteryStatus', 'REAL'),
    ('radiation', 'REAL'),
    ('inTemp', 'REAL'),
    ('inDewpoint', 'REAL'),
    ('barometer', 'REAL'),
    ('windchill', 'REAL'),
    ('dewpoint', 'REAL'),
    ('windrun', 'REAL'),
    ('rain', 'REAL'),
    ('humidex', 'REAL'),
    ('pressure', 'REAL'),
    ('ET', 'REAL'),
    ('rainRate', 'REAL'),
    ('usUnits', 'INTEGER NOT NULL'),
    ('rainCount4', 'REAL'),
    ('rainCount3', 'REAL'),
    ('rainCount1', 'REAL'),
    ('appTemp', 'REAL'),
    ('windBatteryStatus', 'REAL'),
    ('interval', 'INTEGER NOT NULL'),
    ('windDir', 'REAL'),
    ('outTemp', 'REAL'),
    ('windSpeed', 'REAL'),
    ('inHumidity', 'REAL'),
    ('windGust', 'REAL'),
    ('windGustDir', 'REAL'),
    ('cloudbase', 'REAL')
]

class SQLiteDupe(weewx.engine.StdService):
    def __init__(self, engine, config_dict):
        super(SQLiteDupe, self).__init__(engine, config_dict)
        d = config_dict.get('SQLiteDupe', {})
        self.binding = d.get('binding', 'archive')
        if self.binding == 'archive':
            self.bind(weewx.NEW_ARCHIVE_RECORD, self.handle_new_archive)
        #else:
        #    self.bind(weewx.NEW_LOOP_PACKET, self.handle_new_loop)

        # get the database parameters we need to function
        binding = d.get('data_binding', 'sqlitedupe_binding')
        self.dbm = self.engine.db_binder.get_manager(data_binding=binding,
                                                     initialize=True)

        # be sure database matches the schema we have
        dbcol = self.dbm.connection.columnsOf(self.dbm.table_name)
        dbm_dict = weewx.manager.get_manager_dict_from_config(config_dict, binding)
        dupecol = [x[0] for x in dbm_dict['schema']]
        if dbcol != dupecol:
            raise Exception('sqlitedupe schema mismatch: %s != %s' % (dbcol, dupecol))

    def handle_new_archive(self, event):
        """save data to database"""
        self.dbm.addRecord(event.record)


     # loginf('new_archive_record %s' %(event.record))
     # loginf('new_archive_record %s' %(event))
     # data record {'heatindex': 17.296875000000004, 'outHumidity': 72.454275, 'maxSolarRad': 782.7650660547766, 'hail': 0.0, 'inTempBatteryStatus': 4.93, 'rainBatteryStatus': 4.95, 'hailRate': 0.0, 'altimeter': 1016.2321988390987, 'outTempBatteryStatus': 4.96, 'radiation': 1400.0322500000002, 'inTemp': 21.65625, 'inDewpoint': 48.14709605637118, 'barometer': 1015.294, 'windchill': 17.296875000000004, 'dewpoint': 12.293227803655595, 'windrun': 20.47582442781085, 'rain': 0.0, 'humidex': 19.710957581208838, 'pressure': 963.4797924584669, 'ET': 0.010438185627416401, 'rainRate': 0.0, 'usUnits': 17, 'rainCount4': 987.0, 'rainCount3': 835.0, 'rainCount1': 20227967.0, 'appTemp': 15.479917358792356, 'windBatteryStatus': 4.95, 'interval': 1, 'dateTime': 1507163160.0, 'windDir': 241.28352189240834, 'outTemp': 17.296875000000004, 'windSpeed': 3.609926636088604, 'inHumidity': 44.3086, 'windGust': 3.823387430030153, 'windGustDir': 247.47474747474746, 'cloudbase': 1073.9298293015042}
