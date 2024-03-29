# -*- coding: utf-8 -*-
#   Copyright (c) 2017 -2022 Glenn McKechnie <glenn.mckechnie@gmail.com>
#   Credit to Tom Keffer <tkeffer@gmail.com>, Matthew Wall and the core
#   weewx team, whom I've borrowed ideas and code from.
#   This code is based on the csv, pmon and cmon extensions by mwall
#
#   Mistakes are mine, corrections and or improvements welcomed
#      https://github.com/glennmckechnie/weewx-uradmon
#   and this section edited by Duane Groth
#

import json
import time
# adapt python2.7 code for python3 weewx
try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

import weewx
import weewx.engine
from weeutil.weeutil import to_bool, to_int
from weewx.cheetahgenerator import SearchList

"""
https://www.uradmonitor.com/wp-content/uploads/2019/01/manual_a3_107_comp.pdf
https://www.uradmonitor.com/wp-content/uploads/2021/08/
 a3_datasheet_v109_en_compressed.pdf
"""

# add the required units
#
# FIXME - to test
# Testing with group_urad_pressure to avoid clashes with existing
# group_pressure units.
# Also using group_ion_radiation for much the same reason, although that
# doesn't appear to clash (has only one unit, with no existing conversions.)
# group_fraction exists in 4.6.0. Renaming / keeping for compatability
# group_concentration exists in 4.6.0. Renaming / keeping for compatability
# / plus extra entry.
weewx.units.obs_group_dict['uvolt'] = 'group_volt'
weewx.units.obs_group_dict['ucpm'] = 'group_ion_radiation'
weewx.units.obs_group_dict['uvoc'] = 'group_fraction'
weewx.units.obs_group_dict['uco2'] = 'group_fraction'
weewx.units.obs_group_dict['unoise'] = 'group_db'
weewx.units.obs_group_dict['uch2o'] = 'group_fraction'
weewx.units.obs_group_dict['upm25'] = 'group_concentration'
weewx.units.obs_group_dict['uptime'] = 'group_elapsed'
weewx.units.obs_group_dict['upres'] = 'group_urad_pressure'
weewx.units.obs_group_dict['utemp'] = 'group_temperature'
weewx.units.obs_group_dict['uhum'] = 'group_percent'

weewx.units.USUnits['group_ion_radiation'] = 'cpm'
weewx.units.USUnits['group_concentration'] = 'microgram_per_meter_cubed'
weewx.units.USUnits['group_fraction'] = 'ppm'
weewx.units.USUnits['group_urad_pressure'] = 'Pa'

weewx.units.MetricUnits['group_ion_radiation'] = 'cpm'
weewx.units.MetricUnits['group_concentration'] = 'microgram_per_meter_cubed'
weewx.units.MetricUnits['group_fraction'] = 'ppm'
weewx.units.MetricUnits['group_urad_pressure'] = 'Pa'

# possibly not needed as definitions because MetricUnits form the base of
# MetricWX?
# FIXME - to test
weewx.units.MetricWXUnits['group_ion_radiation'] = 'cpm'
weewx.units.MetricWXUnits['group_concentration'] = 'microgram_per_meter_cubed'
weewx.units.MetricWXUnits['group_fraction'] = 'ppm'
weewx.units.MetricWXUnits['group_urad_pressure'] = 'Pa'

weewx.units.default_unit_format_dict['cpm'] = '%.0f'
weewx.units.default_unit_format_dict['ppm'] = '%.0f'
weewx.units.default_unit_format_dict['micro_sievert_hour'] = '%.2f'
weewx.units.default_unit_format_dict['Pa'] = '%.0f'

weewx.units.default_unit_label_dict['cpm'] = ' cpm'
weewx.units.default_unit_label_dict['ppm'] = 'ppm'
weewx.units.default_unit_label_dict['micro_sievert_hour'] = ' µSv/h'
weewx.units.default_unit_label_dict['Pa'] = 'Pa '

# weewx.units.conversionDict.update(
#         {'Pa': {'hPa': lambda x: x * 100},
#          'hPa': {'Pa': lambda x: x * 0.01}})
# FIXME ... more testing required.
weewx.units.conversionDict.update(
         {'Pa': {'inHg': lambda x: x * 0.0295299875 * 0.01,
                 'mmHg': lambda x: x * 0.0075, 'mbar': lambda x: x * 0.01,
                 'kPa': lambda x: x * 0.0001, 'hPa': lambda x: x * 0.01}})

# The value recorded from our uRADMon counters is listed as cpm, rather than
# micro_sievert/hour.
# using a factor of 1/110 for the conversion!
weewx.units.conversionDict.update(
         {'cpm': {'micro_sievert_hour': lambda x: x * 0.00909},
          'micro_sievert_hour': {'cpm': lambda x: x * 110}})

"""
cpm <to> micro_sievert_hour?

https://physics.stackexchange.com/questions/272649/how-does-a-geiger-
 counter-such-as-rd1706-converts-counts-per-minute-to-micro-s#272761

'Note 2:
In the case of your updated question in the comments, technically there isn't
really a direct equation converting counts per minute (CPM) to microsieverts
because CPM is an electron count and microsieverts is a count of bodily
damage.'

https://sapporohibaku.wordpress.com/2011/10/15/conversion-factor/

SMB values from 1/150 through to 1/360 ??
"""

urad_version = "0.2.9"


try:
    # weewx4 logging
    import weeutil.logger
    import logging
    log = logging.getLogger(__name__)

    def logdbg(msg):
        log.debug(msg)

    def loginf(msg):
        log.info(msg)

    def logerr(msg):
        log.error(msg)

except ImportError:
    # old-style weewx logging
    import syslog

    def logmsg(level, msg):
        syslog.syslog(level, 'uradmon: %s' % msg)

    def logdbg(msg):
        logmsg(syslog.LOG_DEBUG, msg)

    def loginf(msg):
        logmsg(syslog.LOG_INFO, msg)

    def logerr(msg):
        logmsg(syslog.LOG_ERR, msg)

# default schema (include A, A3, D, & Industrial models)
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
    ('uptime', 'INTEGER'),
    ('ubat', 'REAL'),     # Battery
    ('urtc', 'INTEGER'),  # RTC
    ('us1', 'INTEGER'),
    ('us2', 'INTEGER'),
    ('us3', 'INTEGER'),
    ('us4', 'INTEGER'),
    ('upm1', 'INTEGER'),
    ('upm10', 'INTEGER'),
    ('ulat', 'REAL'),
    ('ulong', 'REAL'),
    ('ualt', 'REAL'),
    ('uspeed', 'REAL'),
    ('usats', 'INTEGER')
    ]
"""
# the default schema, for A3
schema_A3 = [
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
yschema_D = [
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
# schema for industrial
schema_ind = [
    ('dateTime', 'INTEGER NOT NULL UNIQUE PRIMARY KEY'),
    ('usUnits', 'INTEGER NOT NULL'),
    ('interval', 'INTEGER NOT NULL'),
    ('utemp', 'REAL'),
    ('uhum', 'REAL'),
    ('upres', 'INTEGER'),
    ('uvoc', 'INTEGER'),
    ('us1', 'INTEGER'),
    ('us2', 'INTEGER'),
    ('us3', 'INTEGER'),
    ('us4', 'INTEGER'),
    ('upm1', 'INTEGER'),
    ('upm25', 'INTEGER'),
    ('upm10', 'INTEGER'),
    ('unoise', 'REAL'),
    ('uptime', 'INTEGER')
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
            'unit_id', 'Enter_units_ID_Number')
        unit_model = self.generator.skin_dict['Uradmonitor'].get(
            'unit_model', 'uRADMonitor')
        unit_link = self.generator.skin_dict['Uradmonitor'].get(
            'unit_link', '\"https://www.uradmonitor.com/products/\"')

        urad_uptime_secs = db_lookup().getSql("SELECT uptime FROM archive"
                                              " ORDER BY datetime"
                                              " DESC LIMIT 1")
        try:
            loginf("urad_uptime_secs %s" % urad_uptime_secs)
        except Exception as e:
            loginf("urad_uptime not available : %s" % e)

        # convert the seconds uptime output to a human readable string for the
        # charts tool tip
        urad_uptime_str = weewx.units.ValueHelper(value_t=(
                                           urad_uptime_secs,
                                           "second", "group_deltatime"),
                                           context='long_delta',
                                           formatter=self.generator.formatter,
                                           converter=self.generator.converter)

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
        self.dbm_check = to_bool(udict.get('dbm_check', True))
        self.rad_addr = udict.get('uradmon_address', '')
        self.binding = udict.get('binding', 'archive')
        self.data_binding = udict.get('data_binding', 'uradmon_binding')
        self.dbm = self.engine.db_binder.get_manager(
            data_binding=self.data_binding, initialize=True)
        sf_int = to_int(config_dict['StdArchive'].get('archive_interval', 300))
        self.rec_interval = sf_int / 60  # convert to minute for database entry
        loginf("archive_interval in seconds is %s, minutes %s" %
               (sf_int, self.rec_interval))

        # It is possible to use the old database with v0.2.x uradmon.py however
        # the dbm schema check will fail, so a workaround is to disable it for
        # that instance. You'll also need to point the weewx.conf database
        # stanza to the old database, probably uradmon.sdb (sqlite) or
        # uradmon (mysql)
        # To disable this check add
        #   dbm_check = False
        # to the [UradMon] section in weewx.conf
        if self.dbm_check:
            # ensure schema on disk matches schema in memory
            dbcol = self. dbm.connection.columnsOf(self.dbm.table_name)
            dbm_dict = weewx.manager.get_manager_dict(
                                                  config_dict['DataBindings'],
                                                  config_dict['Databases'],
                                                  self.data_binding)
            memcol = [x[0] for x in dbm_dict['schema']]
            if dbcol != memcol:
                logerr('schema mismatch: %s != %s' % (dbcol, memcol))
                logerr('Skipping further uradmon queries until the database' +
                       ' schema mismatch is fixed')
                return
                #raise Exception('schema mismatch: %s != %s' %
                #                (dbcol, memcol))

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
        "voc":12648,"co2":784,"noise":44.08,"ch2o":0.01,"pm25":3,
        "uptime": 36358}}

         As .decode('utf-8') returns it...
        {u'data': {u'uptime': 36168, u'co2': 785, u'cpm': 18, u'voc': 12619,
        u'humidity': 54.97, u'pressure': 96428, u'voltage': 384, u'ch2o': 0.01,
        u'detector': u'SI29BG', u'type': u'8', u'id': u'82000079', u'pm25': 4,
        u'temperature': 23.07}}

        A
        {"data":{ "id":"11000061","type":"1","detector":"SBM20","voltage":379,
        "cpm":24,"temperature":19.50,"uptime": 67088}}
         or
        {"data":{ "id":"51000040","type":"5","detector":"SBM20",
        "cpm":21,"temperature":0.00,"uptime": 1235877}}


        D
        {"data":{"id":"6400001B","type":"6","detector":"LND712","voltage":479,
        "cpm":12,"temperature":33.56,"humidity":40.39,"pressure":100533,
        "voc":8791,"pm25":0.00,"battery":4.18,"uptime":1328,"rtc":1520246972,
        "latitude":-37.675000,"longitude":144.417000,"altitude":131.30,
        "speed":0.36,"sats":5}}

        Industrial
        ip_address/j
        {"data":{"id":"14000089","type":"14","temperature":4.78,"humidity":75.01,
        "pressure":99812,"voc":167555,"s1":0.18,"s2":0.10,"s3":0.01,"s4":0.91,
        "pm1":8,"pm25":10,"pm10":11,"noise":47.35,"uptime":384112}}
        """

        url = "http://" + self.rad_addr + "/j"

        # test for self.self
        # no_sf_int = sf_int
        # print("%s" % no_sf_int)

        # I seemed to get a lot of timeouts, possibly because a cron job and
        # this were hitting the uradmonitor every minute. A note exists that
        # the monitor is sensitive to DDOS attacks and shuts down when that
        # occurs?
        # See post at uradmonitor forum
        # https://www.uradmonitor.com/topic/local-access-unit-can-fail-to-respond-to-local-json-queries/
        #
        # ToDo: use API !
        #
        # It wasn't shutting down for me, but it was slowing down, possibly
        # getting close to it? All seems fine with this code, and with the
        # cronjob cancelled it's a lot better (the cronjob is now redundant
        # anyway)
        attempts = 3   # (0, 1, 2)
        assert attempts >= 1
        for _ in range(attempts):
            """
            if self.udebug:
                # Fix logic for backoff - then test (uncomment and play)
                loginf("START connection attempt %s, %s to %s" %
                       (attempts, int(_+1), self.rad_addr))
                # if attempts is 3 or attempts is 2 or attempts is 1:
                # if attempts is 3 or attempts is 2:
                if attempts == 3:
                    url = "http://192.168.0.235/j"
                else:
                    url = "http://" + self.rad_addr + "/j"
                loginf("connection attempt %s, %s to %s or %s" %
                       (attempts, int(_+1), self.rad_addr, url))
            """
            try:
                time.sleep(_+1)  # crude backoff
                if self.udebug:
                    logdbg("crude backoff is %s seconds" % (_+1))
                # _response = urllib.request.urlopen(url, timeout=3)
                _response = urllib2.urlopen(url, timeout=3)  # local = quick
                break  # on success
            except Exception as err:
                if self.udebug:
                    loginf("error (%s) on attempt %s to %s" %
                           (err, int(_ + 1), self.rad_addr))
                _ = _ - 1
                attempts = int(attempts - 1)
        else:  # all attempts failed
            logerr("No data fetched, after %s attempts to %s" %
                   (int(_ + 2), self.rad_addr))
            attempts = None

        if attempts is not None:
            if self.udebug:
                # loginf("%s responded on attempt %s, %s" % (self.rad_addr,
                #                                            int(_+1),
                #                                            attempts))
                loginf("%s responded on attempt %s" % (self.rad_addr,
                                                       int(_ + 1)))
            json_string = json.loads(_response.read().decode('utf-8'))

            #  from the A3 - unused values
            self.uuid = json_string["data"]["id"]
            self.utype = json_string["data"]["type"]
            self.udetect = json_string["data"]["detector"]
            if self.udebug:
                loginf(" id : %s , type : %s , detector : %s" % (self.uuid,
                                                                 self.utype,
                                                                 self.udetect))

            timestamp = int(time.time())
            # defaults values, always required.
            rec = {'dateTime': timestamp,
                   'usUnits': weewx.METRIC,
                   'interval': self.rec_interval}

            # values that are apparently optional depending on version / unit
            try:
                uvolt = json_string["data"]["voltage"]
            except KeyError:
                uvolt = None
            try:
                ucpm = json_string["data"]["cpm"]
            except KeyError:
                ucpm = None
            # A3 model
            if self.utype == '8':
                # only applies to early units, they had no noise sensor
                try:
                    unoise = json_string["data"]["noise"]
                except KeyError:
                    unoise = None
                rec.update({'uvolt': uvolt,
                            'ucpm': ucpm,
                            'utemp': json_string["data"]["temperature"],
                            'uhum': json_string["data"]["humidity"],
                            'upres': json_string["data"]["pressure"],
                            'uvoc': json_string["data"]["voc"],
                            'uco2': json_string["data"]["co2"],
                            'unoise': unoise,
                            'uch2o': json_string["data"]["ch2o"],
                            'upm25': json_string["data"]["pm25"],
                            'uptime': json_string["data"]["uptime"]})

            # A model
            elif self.utype == '5' or self.utype == '1':
                rec.update({'uvolt': uvolt,
                            'ucpm': ucpm,
                            'utemp': json_string["data"]["temperature"],
                            'uptime': json_string["data"]["uptime"]})

            # Industrial Model
            elif self.utype == '14':
                rec.update({'utemp': json_string["data"]["temperature"],
                            'uhum': json_string["data"]["humidity"],
                            'upres': json_string["data"]["pressure"],
                            'uvoc': json_string["data"]["voc"],
                            'us1': json_string["data"]["s1"],
                            'us2': json_string["data"]["s2"],
                            'us3': json_string["data"]["s3"],
                            'us4': json_string["data"]["s4"],
                            'upm1': json_string["data"]["pm1"],
                            'upm25': json_string["data"]["pm25"],
                            'upm10': json_string["data"]["pm10"],
                            'unoise': json_string["data"]["noise"],
                            'uptime': json_string["data"]["uptime"]})

            # D model
            elif self.utype == '6':
                rec.update({'uvolt': uvolt,
                            'ucpm': ucpm,
                            'utemp': json_string["data"]["temperature"],
                            'uhum': json_string["data"]["humidity"],
                            'upres': json_string["data"]["pressure"],
                            'uvoc': json_string["data"]["voc"],
                            'upm25': json_string["data"]["pm25"],
                            'ubat': json_string["data"]["battery"],
                            'urtc': json_string["data"]["rtc"],
                            'uptime': json_string["data"]["uptime"],
                            'ulat': json_string["data"]["latitude"],
                            'ulong': json_string["data"]["longitude"],
                            'ualt': json_string["data"]["altitude"],
                            'uspeed': json_string["data"]["speed"],
                            'usats': json_string["data"]["sats"]})

            else:
                logerr(" Argh, no hooks! Unit is a type %s. DEBUG info follows"
                       % self.utype)
                logerr(" DEBUG : json_string is %s" % json_string)
            if self.udebug:
                loginf(" record to store %s" % rec)

            self.dbm.addRecord(rec)
