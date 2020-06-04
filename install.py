# installer for uradmon
# Copyright 2016 Matthew Wall
# Co-opted by Glenn McKechnie 2017
# Distributed under the terms of the GNU Public License (GPLv3)

from setup import ExtensionInstaller

def loader():
    return UradmonInstaller()

class UradmonInstaller(ExtensionInstaller):
    def __init__(self):
        super(UradmonInstaller, self).__init__(
            version="0.1.5",
            name='uradmon',
            description='A service that collects data and generates'
                        'a weewx report that displays the values'
                        'returned from an A3 uradmonitor'
                        'https://www.uradmonitor.com',
            author="Glenn McKechnie",
            author_email="glenn.mckechnie@gmail.com",
            process_services='user.uradmon.UradMon',
            config={
                'UradMon': {
                    'data_binding': 'uradmon_binding',
                    'urad_debug': 'True',
                    'uradmon_address': '192.168.0.235'},
                'DataBindings': {
                    'uradmon_binding': {
                        'database': 'uradmon_sqlite',
                        'table_name': 'archive',
                        'manager': 'weewx.manager.DaySummaryManager',
                        'schema': 'user.uradmon.schema'}},
                'Databases': {
                    'uradmon_sqlite': {
                        'database_name': 'uradmon.sdb',
                        'driver': 'weedb.sqlite'},
                    'uradmon_mysql': {
                        'database_name': 'uradmon',
                        'database_type': 'MySQL'}},
                'StdReport': {
                    'uradmon': {
                        'skin': 'uradmon',
                        'HTML_ROOT': 'uradmon'
                        }}},
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
                    ]),
                   ('skins/uradmon/images',
                    ['skins/uradmon/images/urad-favicon.ico',
                    ])
                  ]
        )
