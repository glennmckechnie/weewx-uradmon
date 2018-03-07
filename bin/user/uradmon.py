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
import time
import urllib2
import syslog

import weewx
import weewx.engine
import weeutil.weeutil
from weeutil.weeutil import to_bool
import weedb
from weewx.cheetahgenerator import SearchList


# add the required units
weewx.units.obs_group_dict['uvolt'] = 'group_volt'
weewx.units.obs_group_dict['ucpm'] = 'group_sievert'
weewx.units.obs_group_dict['uvoc'] = 'group_ppm'
weewx.units.obs_group_dict['uco2'] = 'group_ppm'
weewx.units.obs_group_dict['uch2o'] = 'group_ppm'
weewx.units.obs_group_dict['upm25'] = 'group_mgram'
weewx.units.obs_group_dict['uptime'] = 'group_elapsed'
weewx.units.obs_group_dict['upres'] = 'group_pressure'
weewx.units.obs_group_dict['utemp'] = 'group_temperature'
weewx.units.obs_group_dict['uhum'] = 'group_percent'

# USUnits would be ????
weewx.units.USUnits['group_sievert'] = 'microsievert'
weewx.units.USUnits['group_ppm'] = 'ppm'
weewx.units.USUnits['group_mgram'] = 'microgram'
weewx.units.MetricUnits['group_sievert'] = 'microsievert'
weewx.units.MetricUnits['group_ppm'] = 'ppm'
weewx.units.MetricUnits['group_mgram'] = 'microgram'
weewx.units.MetricWXUnits['group_sievert'] = 'microsievert'
weewx.units.MetricWXUnits['group_ppm'] = 'ppm'
weewx.units.MetricWXUnits['group_mgram'] = 'microgram'

weewx.units.default_unit_format_dict['microsievert'] = '%.0f'
weewx.units.default_unit_format_dict['ppm'] = '%.1f'
weewx.units.default_unit_format_dict['microgram'] = '%.0f'

weewx.units.default_unit_label_dict['microsievert'] = ' \xc2\xb5Sv/h'
weewx.units.default_unit_label_dict['ppm'] = ' ppm'
weewx.units.default_unit_label_dict['microgram'] = ' \xc2\xb5g/m\xc2\xb3'

urad_version = "0.1.2"

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
    ('usUnits', 'INTEGER NOT NULL'),
    ('interval', 'INTEGER NOT NULL'),
    ('uvolt', 'INTEGER'),
    ('ucpm', 'REAL'),
    ('utemp', 'REAL'),
    ('uhum', 'REAL'),
    ('upres', 'INTEGER'),
    ('uvoc', 'INTEGER'),
    ('uco2', 'INTEGER'),
    ('uch2o', 'REAL'),
    ('upm25', 'INTEGER'),
    ('uptime', 'INTEGER')
]

class UradMonSkin(SearchList):
    def __init__(self, generator):
        SearchList.__init__(self, generator)

        self.uradmon_version = urad_version
        self.unit_id = self.generator.skin_dict['Uradmonitor'].get \
                    ('unit_id', 'xxXxXxXx')
        return

class UradMon(weewx.engine.StdService):
    def __init__(self, engine, config_dict):
        super(UradMon, self).__init__(engine, config_dict)
        loginf('version is %s' % urad_version)
        udict = config_dict.get('UradMon', {})

        self.udebug = to_bool(udict.get('urad_debug', False))
        self.rad_addr = udict.get('uradmon_address', '')
        self.binding = udict.get('binding', 'archive')
        self.data_binding = udict.get('data_binding', 'uradmon_binding')
        self.dbm = self.engine.db_binder.get_manager(data_binding=self.data_binding,
                                                     initialize=True)

        # ensure schema on disk matches schema in memory
        dbcol = self. dbm.connection.columnsOf(self.dbm.table_name)
        dbm_dict = weewx.manager.get_manager_dict(
            config_dict['DataBindings'], config_dict['Databases'], self.data_binding)
        memcol = [x[0] for x in dbm_dict['schema']]
        if dbcol != memcol:
            raise Exception('schema mismatch: %s != %s' %
                            (dbcol, memcol))

        loginf("uRADMonitor address is %s" % self.rad_addr)
        if self.rad_addr != '':
            if self.binding == 'archive':
                self.bind(weewx.NEW_ARCHIVE_RECORD, self.handle_new_archive)
            else:
                self.bind(weewx.NEW_LOOP_PACKET, self.handle_new_loop)
        else:
            loginf("No uRADMonitor address specified, skipping service")

    def handle_new_archive(self, event):
        """save data to database"""
        self.readdata()
        return

    def readdata(self):
        #loginf (" result is ?? %s" % result)
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

        attempts = 3
        assert attempts >= 1
        for _ in range(attempts):
            if self.udebug:
                loginf("connection attempt %s to %s" %(int(_+1), self.rad_addr))
            try:
                time.sleep(_) # crude backoff
                _response = urllib2.urlopen(url, timeout=3)
                break # on success
            except Exception as err:
                if self.udebug:
                    loginf("error (%s) on attempt %s to %s" %(err, int(_+1), self.rad_addr))
        else: # all attempts failed
            logerr("No data fetched, %s after %s attempts to %s" %(err, int(_+1), self.rad_addr))
            attempts = None

        if attempts is not None:
            if self.udebug:
                loginf("%s responded on attempt %s" %(self.rad_addr, int(_+1)))
            json_string = json.loads(_response.read().decode('utf-8'))

            # unused
            #self.uuid = json_string["data"]["id"]
            #self.utype = json_string["data"]["type"]
            #self.udetect = json_string["data"]["detector"]

            timestamp = int(time.time())
            int_one = 1

            rec = {'dateTime': timestamp,
                   'usUnits': weewx.METRIC,
                   'interval': int_one,
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
            if self.udebug:
                loginf(" record is %s" % rec)

            self.dbm.addRecord(rec)
