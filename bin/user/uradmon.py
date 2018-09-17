#   Copyright (c) 2017 Glenn McKechnie <glenn.mckechnie@gmail.com>
#   Credit to Tom Keffer <tkeffer@gmail.com>, Matthew Wall and the core
#   weewx team, whom I've borrowed ideas and code from.
#   This code is based on the csv, pmon and cmon extensions by mwall
#   Copyright 2017 Glenn McKechnie <glenn.mckechnie@gmail.com>
#
#   Mistakes are mine, corrections and or improvements welcomed
#      https://github.com/glennmckechnie/weewx-uradmon
#   and this section edited by Duane Groth
#
# import weedb
# import weeutil.weeutil
#

import json
import time
import urllib2
import syslog

import weewx
import weewx.engine
from weeutil.weeutil import to_bool, to_int
from weewx.cheetahgenerator import SearchList


# add the required units
weewx.units.obs_group_dict['uvolt'] = 'group_volt'
weewx.units.obs_group_dict['ucpm'] = 'group_sievert'
weewx.units.obs_group_dict['uvoc'] = 'group_ppm'
weewx.units.obs_group_dict['uco2'] = 'group_ppm'
weewx.units.obs_group_dict['unoise'] = 'group_db'
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
weewx.units.USUnits['group_db'] = 'db'
weewx.units.MetricUnits['group_sievert'] = 'microsievert'
weewx.units.MetricUnits['group_ppm'] = 'ppm'
weewx.units.MetricUnits['group_mgram'] = 'microgram'
weewx.units.MetricUnits['group_db'] = 'db'
# crash# weewx.units.MetricUnits['group_pressure'] = 'Pa'
weewx.units.MetricWXUnits['group_sievert'] = 'microsievert'
weewx.units.MetricWXUnits['group_ppm'] = 'ppm'
weewx.units.MetricWXUnits['group_mgram'] = 'microgram'
weewx.units.MetricWXUnits['group_db'] = 'db'

weewx.units.default_unit_format_dict['microsievert'] = '%.0f'
weewx.units.default_unit_format_dict['ppm'] = '%.1f'
weewx.units.default_unit_format_dict['microgram'] = '%.0f'
weewx.units.default_unit_format_dict['db'] = '%.0f'

weewx.units.default_unit_label_dict['microsievert'] = ' \xc2\xb5Sv/h'
weewx.units.default_unit_label_dict['ppm'] = ' ppm'
weewx.units.default_unit_label_dict['microgram'] = ' \xc2\xb5g/m\xc2\xb3'
weewx.units.default_unit_label_dict['db'] = ' dB'

# crash#weewx.units.conversionDict['Pa'] = {'mbar': lambda x: x * 1000}

urad_version = "0.1.3"


def logmsg(level, msg):
    syslog.syslog(level, 'uradmon: %s' % msg)


def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)


def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)


def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)


# the default schema, for A3
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
    ('unoise', 'REAL'),
    ('uch2o', 'REAL'),
    ('upm25', 'INTEGER'),
    ('uptime', 'INTEGER')
]
"""
# alternative schema, for A model
schema_A = [
    ('dateTime', 'INTEGER NOT NULL UNIQUE PRIMARY KEY'),
    ('usUnits', 'INTEGER NOT NULL'),
    ('interval', 'INTEGER NOT NULL'),
    ('uvolt', 'INTEGER'),
    ('ucpm', 'REAL'),
    ('utemp', 'REAL'),
    ('uptime', 'INTEGER')
]

# alternative schema, for D model
# apparently the D model can be slow to respond to a json query?
schema_D = [
    ('dateTime', 'INTEGER NOT NULL UNIQUE PRIMARY KEY'),
    ('usUnits', 'INTEGER NOT NULL'),
    ('interval', 'INTEGER NOT NULL'),
    ('uvolt', 'INTEGER'),
    ('ucpm', 'REAL'),
    ('utemp', 'REAL'),
    ('uhum', 'REAL'),
    ('upres', 'INTEGER'),
    ('uvoc', 'INTEGER'),
    ('upm25', 'INTEGER'),
    ('ubat', 'REAL'),  # battery
    ('uptime', 'INTEGER'),
    ('urtc', 'INTEGER')  # RTC
]
"""

class UradMonSkin(SearchList):

    def __init__(self, generator):
        SearchList.__init__(self, generator)

    def get_extension_list(self, timespan, db_lookup):
        """
        Skin - SLE for report generation

        #urad_all  = {db_lookup().getSql("SELECT * FROM archive ORDER BY
                                                datetime DESC LIMIT 1")}
        # uradmon: skin all = set([(1521421527, 16, 1, 379, 19.0, 19.52, 53.08,
                                          96438, 98337, 482, 0.0, 3, 1244368)])
        #loginf("skin all = %s" % urad_all)
        """
        unit_id = self.generator.skin_dict['Uradmonitor'].get(
            'unit_id', 'xxXxXxXx')
        unit_model = self.generator.skin_dict['Uradmonitor'].get(
            'unit_model', 'uRADMonitor')
        unit_link = self.generator.skin_dict['Uradmonitor'].get(
            'unit_link', '\"https://www.uradmonitor.com/products/\"')

        urad_all = db_lookup().getSql("SELECT * FROM archive ORDER BY"
                                      " datetime DESC LIMIT 1")

        # do we want these ?? maybe one day :-)
        # uvolt = urad_all[3]
        # ucpm = urad_all[4]
        # utemp = urad_all[5]
        # uhum = urad_all[6]
        # upres = urad_all[7]
        # uvoc = urad_all[8]
        # uco2 = urad_all[9]
        # uch2o = urad_all[10]
        # upm25 = urad_all[11]

        urad_uptime = urad_all[12]
        # convert the seconds uptime output to a human readable string
        urad_uptime_str = weewx.units.ValueHelper(value_t=(
            urad_uptime, "second", "group_deltatime"))

        urad_ext = {'urad_uptime': urad_uptime_str, 'unit_id': unit_id,
                    'unit_model': unit_model, 'unit_link': unit_link,
                    'uradmon_version': urad_version}

        return [urad_ext]


class UradMon(weewx.engine.StdService):
    """
    Service to fetch data, store it in an appropriate database so that it's
    available for the above SLE

    """
    def __init__(self, engine, config_dict):
        super(UradMon, self).__init__(engine, config_dict)
        loginf('service version is %s' % urad_version)
        udict = config_dict.get('UradMon', {})

        self.udebug = to_bool(udict.get('urad_debug', False))
        self.rad_addr = udict.get('uradmon_address', '')
        self.binding = udict.get('binding', 'archive')
        self.data_binding = udict.get('data_binding', 'uradmon_binding')
        self.dbm = self.engine.db_binder.get_manager(
            data_binding=self.data_binding, initialize=True)
        sf_int = to_int(config_dict['StdArchive'].get('archive_interval', 300))
        loginf("archive_interval in seconds is %s" % sf_int)
        self.rec_interval = sf_int / 60  # convert to minutes for database entry
        loginf("archive_interval in minutes is %s" % self.rec_interval)

        # ensure schema on disk matches schema in memory
        dbcol = self. dbm.connection.columnsOf(self.dbm.table_name)
        dbm_dict = weewx.manager.get_manager_dict(config_dict['DataBindings'],
                                                  config_dict['Databases'],
                                                  self.data_binding)
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
        """
        A3
         As the browser returns it...
        {"data":{ "id":"82000079","type":"8","detector":"SI29BG","voltage":384,
        "cpm":20,"temperature":23.07,"humidity":54.89,"pressure":96424,
        "voc":12648,"co2":784,"noise":44.08,"ch2o":0.01,"pm25":3,"uptime": 36358}}

         As .decode('utf-8') returns it...
        {u'data': {u'uptime': 36168, u'co2': 785, u'cpm': 18, u'voc': 12619,
        u'humidity': 54.97, u'pressure': 96428, u'voltage': 384, u'ch2o': 0.01,
        u'detector': u'SI29BG', u'type': u'8', u'id': u'82000079', u'pm25': 4,
        u'temperature': 23.07}}

        A
        {"data":{ "id":"11000061","type":"1","detector":"SBM20","voltage":379,
        "cpm":24,"temperature":19.50,"uptime": 67088}}

        D
        {"data":{"id":"6400001B","type":"6","detector":"LND712","voltage":479,
        "cpm":12,"temperature":33.56,"humidity":40.39,"pressure":100533,
        "voc":8791,"pm25":0.00,"battery":4.18,"uptime":1328,"rtc":1520246972,
        "latitude":-37.675000,"longitude":144.417000,"altitude":131.30,
        "speed":0.36,"sats":5}}
        """

        url = "http://" + self.rad_addr + "/j"

        # test for self.self
        # no_sf_int = sf_int
        # print("%s" % no_sf_int)

        # I seemed to get a lot of timeouts, possibly because a cron job and
        # this were hitting the uradmonitor every minute. A note exists that
        # the monitor is sensitive to DDOS attacks and shuts down when that
        # occurs?
        # It wasn't shutting down for me, but it was slowing down, possibly
        # getting close to it? All seems fine with this code, and with the
        # cronjob cancelled it's a lot better (the cronjob is now redundant
        # anyway)
        attempts = 3   # (0, 1, 2)
        assert attempts >= 1
        for _ in range(attempts):
            # if self.udebug:
                ## Fix logic for backoff - then test (uncomment and play)
                # loginf("START connection attempt %s, %s to %s" % (attempts, int(_+1),
                #                                        self.rad_addr))
                ## if attempts is 3 or attempts is 2 or attempts is 1:
                ## if attempts is 3 or attempts is 2:
                #if attempts is 3:
                #    url = "http://192.168.0.236/j"
                #else:
                #    url = "http://" + self.rad_addr + "/j"
                #loginf("connection attempt %s, %s to %s or %s" % (attempts, int(_+1),
                #                                                  self.rad_addr, url))
            try:
                time.sleep(_)  # crude backoff
                _response = urllib2.urlopen(url, timeout=3)  # local = quick
                break  # on success
            except Exception as err:
                if self.udebug:
                    loginf("error (%s) on attempt %s, %s to %s" %
                           (err, attempts, int(_+1), self.rad_addr))
                _ = _ - 1
                attempts = int(attempts - 1)
        else:  # all attempts failed
            logerr("No data fetched, after %s attempts to %s" %
                   (int(_+1), self.rad_addr))
            attempts = None

        if attempts is not None:
            if self.udebug:
                # loginf("%s responded on attempt %s, %s" % (self.rad_addr,
                #                                            int(_+1), attempts))
                loginf("%s responded on attempt %s" % (self.rad_addr,
                                                           int(_+1)))
            json_string = json.loads(_response.read().decode('utf-8'))

            #  from the A3 - unused values
            # self.uuid = self.json_string["data"]["id"]
            # self.utype = self.json_string["data"]["type"]
            # self.udetect = self.json_string["data"]["detector"]

            timestamp = int(time.time())
            try:
                unoise = json_string["data"]["noise"]
            except KeyError:
                unoise = None

            # defaults for the A3 model
            rec = {'dateTime': timestamp,
                   'usUnits': weewx.METRIC,
                   'interval': self.rec_interval,
                   'uvolt': json_string["data"]["voltage"],
                   'ucpm': json_string["data"]["cpm"],
                   'utemp': json_string["data"]["temperature"],
                   'uhum': json_string["data"]["humidity"],
                   'upres': json_string["data"]["pressure"],
                   'uvoc': json_string["data"]["voc"],
                   'uco2': json_string["data"]["co2"],
                   'unoise': unoise,
                   'uch2o': json_string["data"]["ch2o"],
                   'upm25': json_string["data"]["pm25"],
                   'uptime': json_string["data"]["uptime"]}
            if self.udebug:
                loginf(" record to store %s" % rec)

            self.dbm.addRecord(rec)
