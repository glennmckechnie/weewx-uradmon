#
#    Copyright (c) 2009-2015 Tom Keffer <tkeffer@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

"""User extensions module

This module is imported from the main executable, so anything put here will be
executed before anything else happens. This makes it a good place to put user
extensions.
"""

import locale
import weewx.units
# This will use the locale specified by the environment variable 'LANG'
# Other options are possible. See:
# http://docs.python.org/2/library/locale.html#locale.setlocale
locale.setlocale(locale.LC_ALL, '')

# uRADMon
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

weewx.units.USUnits['group_sievert'] = 'microsievert'
weewx.units.USUnits['group_ppm'] = 'ppm'
weewx.units.USUnits['group_mgram'] = 'microgram'
weewx.units.MetricUnits['group_sievert'] = 'microsievert'
weewx.units.MetricUnits['group_ppm'] = 'ppm'
weewx.units.MetricUnits['group_mgram'] = 'microgram'
weewx.units.MetricWXUnits['group_sievert'] = 'microsievert'
weewx.units.MetricWXUnits['group_ppm'] = 'ppm'
weewx.units.MetricWXUnits['group_mgram'] = 'microgram'

weewx.units.default_unit_format_dict['uvolt'] = '%.1f'
weewx.units.default_unit_format_dict['ucpm'] = '%.1f'
weewx.units.default_unit_format_dict['uvoc'] = '%.1f'
weewx.units.default_unit_format_dict['uco2'] = '%.1f'
weewx.units.default_unit_format_dict['uch2o'] = '%.1f'
weewx.units.default_unit_format_dict['upm25'] = '%.1f'
weewx.units.default_unit_format_dict['uptime'] = '%.1f'
weewx.units.default_unit_format_dict['upres'] = '%.1f'

weewx.units.default_unit_label_dict['microsievert'] = ' \xc2\xb5Sv/h'
weewx.units.default_unit_label_dict['ppm'] = ' ppm'
weewx.units.default_unit_label_dict['microgram'] = ' \xc2\xb5g/m\xc2\xb3'

#weewx.units.conversionDict['Pa'] = {'Pa': lambda x: x * 0.01}
