#!/usr/bin/env python

__author__ = "Matthieu Fatrez"
__copyright__ = "Copyright 2018, Matthieu Fatrez"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Matthieu Fatrez"
__email__ = "matthieu@fatrez.fr"

from common import credentials
import dateutil.parser
from datetime import datetime, timedelta
import sys, getopt, re, logging, xmlrpclib

client = credentials.spacewalkConnect()
key = credentials.spacewalkGetKey(client)

yesterday = datetime.today() - timedelta(days=1)

def usage():
    print 'This script create reports for clients'
    print 'Usage: %s [-h] [-g group]' % sys.argv[0]
    print '    -h, --help          this help'
    print '    -g, --group=        name of the group'
    print ' ex :'
    print '    report_by_group.py -g group'

def createReport(group_name):
    list_systems_in_group = ""

    try:
        list_systems_in_group = client.systemgroup.listSystems(key, group_name)
    except xmlrpclib.Fault:
        print "Unable to get info from group"
        logging.debug("Unable to get info from group")

    print "-------------------------------------------------------------------------------------------------------------------------------------------------------------------"
    print "|{:^161}|".format(group_name)
    print "-------------------------------------------------------------------------------------------------------------------------------------------------------------------"
    print "| Hostname                                                     | R |  S-P  |  B-P  |  E-P  |  O-P  | Channel Labels                                               |"
    print "-------------------------------------------------------------------------------------------------------------------------------------------------------------------"
#            XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX | AAAAA | BBBBB | CCCCC | DDDDD | FFFF
    for system in list_systems_in_group:
         security_patch = len(client.system.getRelevantErrataByType(key, system['id'], "Security Advisory"))
         bug_patch = len(client.system.getRelevantErrataByType(key, system['id'], "Bug Fix Advisory"))
         enhancement_patch = len(client.system.getRelevantErrataByType(key, system['id'], "Product Enhancement Advisory"))
         outdated_packages = sorted(client.system.getId(key, system['hostname']), key=lambda sort_date: sort_date['last_checkin'])[-1]['outdated_pkg_count']
         repository_name = client.system.getSubscribedBaseChannel(key, system['id'])['label']

         osa_status = sorted(client.system.getId(key, system['hostname']), key=lambda sort_date: sort_date['last_checkin'])[-1]['last_checkin']

         osa = " "
         if osa_status < yesterday:
             osa = "X"

         print "| {:<60} | {:<1} | {:>5} | {:>5} | {:>5} | {:>5} | {:<60} |".format(system['hostname'], osa, security_patch, bug_patch, enhancement_patch, outdated_packages, repository_name)

    print "-------------------------------------------------------------------------------------------------------------------------------------------------------------------"
    print " R   -> Reachable"
    print " S-P -> Security Patch"
    print " B-P -> Bug Patch"
    print " E-P -> Enhance Patch"
    print " O-P -> Outdated Package"

#name	Security Patches	Bug Patches	Enhancement Patches	Outdated Packages	Channel Labels
#clplincft01.intra-coliposte.fr	200	146	9	331	coliposte-20180102-sles11-sp4-pool-x86_64
#clplinlad60.intra-coliposte.fr	192	146	9	328	coliposte-20180102-sles11-sp4-pool-x86_64

def main():
    debug = 0
    group_name = ""

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hdg:e:", ["help", "debug", "group=", "email="])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)

    for k, v in opts:
        if k in ("-h", "--help"):
            usage()
            sys.exit()
        elif k in ("-d", "--debug"):
            debug = 1
        elif k in ("-g", "--group"):
            group_name = v
        elif k in ("-e", "--email"):
            email = v
        else:
            usage()
            sys.exit(2)

    debug_level = logging.INFO
    if debug == 1:
        debug_level = logging.DEBUG

    logging.basicConfig(stream=sys.stderr, level=debug_level)

    if group_name:
        createReport(group_name)
        sys.exit()
    else:
        print "Error : parameter missing"
        usage()
        sys.exit(2)

if __name__ == "__main__":
    main()

credentials.spacewalkLogout(client, key)