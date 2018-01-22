#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

__author__ = "Matthieu Fatrez"
__copyright__ = "Copyright 2017, Matthieu Fatrez"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Matthieu Fatrez"
__email__ = "matthieu@fatrez.fr"

from common import credentials
import os, sys, getopt, re, time, datetime, smtplib

client = credentials.spacewalkConnect()
key = credentials.spacewalkGetKey(client)

def main():
  print "Get All Physical : "
  systems = client.system.listPhysicalSystems(key)
  for system in systems:
    print " - " + system['name']

if __name__ == "__main__":
  main()
  credentials.spacewalkLogout(client, key)
