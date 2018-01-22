#!/usr/bin/env python

__author__ = "Matthieu Fatrez"
__copyright__ = "Copyright 2017, Matthieu Fatrez"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Matthieu Fatrez"
__email__ = "matthieu@fatrez.fr"

from common import credentials
import sys, getopt, re, datetime, logging
import dateutil.parser as dp

client = credentials.spacewalkConnect()
key = credentials.spacewalkGetKey(client)

listInactive = client.system.listInactiveSystems(key)

for inactive in listInactive:
  listGroups = client.system.listGroups(key, inactive['id'])
  res_name = inactive['name']
  res_last = inactive['last_checkin']

  for group in listGroups:
    if group['subscribed'] == 1:
       res_group = group['system_group_name']
    

  print "{:<80} {:<40} {:<40}".format(res_name, res_group, res_last)

credentials.spacewalkLogout(client, key)
