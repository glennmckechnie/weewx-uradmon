# installer for uradmon
#    Copyright (c) 2019 Tom Keffer <tkeffer@gmail.com>
# Co-opted by Glenn McKechnie 2017 - 2022
# Distributed under the terms of the GNU Public License (GPLv3)

try:
    # Python 2
    from StringIO import StringIO
except ImportError:
    # Python 3
    from io import StringIO

import configobj
from weecfg.extension import ExtensionInstaller

urad_config = """
                [UradMon]
                    data_binding = uradmon_binding
                    urad_debug = True
                    # change dbm_check to False if schema mismatch + v0.1.x
                    # data see site README
                    dbm_check = True
                    uradmon_address = weewx.conf-Enter_your_network_address
                [DataBindings]
                    [[uradmon_binding]]
                        database = uradmon_sqlite
                        table_name = archive
                        manager = weewx.manager.DaySummaryManager
                        schema = user.uradmon.schema
                [Databases]
                    [[uradmon_sqlite]]
                        database_name = uradmon2.sdb
                        driver = weedb.sqlite
                    [[uradmon_mysql]]
                        database_name = uradmon2
                        database_type = MySQL
                [StdReport]
                    [[uradmon]]
                        enable = true
                        skin = uradmon
                        lang = en
                        # a reminder that the unit outputs METRIC. You can
                        # change this to suit your setup. Options are US,
                        # METRIC, METRICWX
                        unit_system = METRIC
                        HTML_ROOT = uradmon
                       [[[Units]]]
                           [[[[Groups]]]]
                              # These are the default units from the uradmon
                              # unit and driver. Change these to suit your needs
                              # Pressure options are 'inHg', 'mmHg', 'mbar', or 'hPa'
                              group_urad_pressure = Pa
                              # Degree options are 'degree_F' or 'degree_C'
                              group_temperature = degree_C
                              # Time options are second', 'day ', 'hour,
                              group_elapsed = second
                              # Radiation options are 'cpm' or
                              # 'micro_sievert_hour'
                              group_ion_radiation = cpm

"""


urad_dict = configobj.ConfigObj(StringIO(urad_config))


def loader():
    return UradmonInstaller()


class UradmonInstaller(ExtensionInstaller):
    def __init__(self):
        super(UradmonInstaller, self).__init__(
            version="0.2.9",
            name='uradmon',
            description='A service that collects data and generates'
                        'a weewx report that displays the values'
                        'returned from a uradmonitor unit'
                        'https://www.uradmonitor.com',
            author="Glenn McKechnie",
            author_email="glenn.mckechnie@gmail.com",
            process_services='user.uradmon.UradMon',
            config=urad_dict,
            files=[('bin/user',
                    ['bin/user/uradmon.py']),
                   ('skins/uradmon',
                    ['skins/uradmon/skin.conf',
                     'skins/uradmon/index.html.tmpl',
                     'skins/uradmon/about.inc',
                     'skins/uradmon/uradmon.inc',
                     'skins/uradmon/seasons.css',
                     'skins/uradmon/standard.js',
                     ]),
                   ('skins/uradmon/font',
                    ['skins/uradmon/font/OpenSans.woff',
                     'skins/uradmon/font/OpenSans.woff2',
                     'skins/uradmon/font/OpenSans-Bold.ttf',
                     'skins/uradmon/font/OpenSans-Regular.ttf',
                     ]),
                   ('skins/uradmon/images',
                    ['skins/uradmon/images/urad-favicon.ico',
                     ]),
                   ('skins/uradmon/lang',
                    ['skins/uradmon/lang/en.conf',
                     ])
                   ]
        )
