# installer for uradmon
# Copyright 2016 Matthew Wall
# Co-opted by Glenn McKechnie 2017
# Distributed under the terms of the GNU Public License (GPLv3)

from setup import ExtensionInstaller

def loader():
    return uradmonInstaller()

class uradmonInstaller(ExtensionInstaller):
    def __init__(self):
        super(uradmonInstaller, self).__init__(
            version="0.1.0",
            name='uradmon',
            description='Generates a weewx report that displays'
               'the values returned from an A3 uradmonitor'
               'https://www.uradmonitor.com',
            author="Glenn McKechnie",
            author_email="glenn.mckechnie@gmail.com",
            process_services='user.uradmon.UradMon',
            config={
                    'UradMon': {
                        'data_binding': 'uradmon_binding'},
                'DataBindings': {
                    'uradmon_binding': {
                            'database': 'uradmon_sqlite',
                            'table_name': 'archive',
                            'manager': 'weewx.manager.DaySummaryManager',
                            'schema': 'user.uradmon.schema'}},
                    'Databases': {
                        'uradmon_sqlite': {
                        'database_name': 'uradmon.sdb',
                        'driver': 'weedb.sqlite'}},
                'StdReport': {
                    'uradmon': {
                        'skin': 'uradmon',
                        'HTML_ROOT': 'uradmon'
                        }}},
            files=[('bin/user',
                   ['bin/user/uradmon.py',
                    'bin/user/extensions-urad.py']),
                   ('skins/uradmon',
                   ['skins/uradmon/skin.conf',
                    'skins/uradmon/index.html.tmpl',
                    'skins/uradmon/uradmon.inc',
                    ]),
                   ('skins/uradmon/font',
                   ['skins/uradmon/font/OpenSans.woff',
                    'skins/uradmon/font/OpenSans.woff2',
                    ])
                  ]
        )
