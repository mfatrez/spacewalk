#!/usr/bin/env python

__author__ = "Matthieu Fatrez"
__copyright__ = "Copyright 2017, Matthieu Fatrez"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Matthieu Fatrez"
__email__ = "matthieu@fatrez.fr"

from common import credentials
import sys, getopt, re, datetime, logging

client = credentials.spacewalkConnect()
key = credentials.spacewalkGetKey(client)

date_repo = datetime.datetime.now().strftime('%Y%m%d')

def usage():
    print 'This script to manage group for SuseManager'
    print 'Usage: %s [-h] [-l] [-C -g group] [-D -g group]' % sys.argv[0]
    print '    -h, --help          this help'
    print '    -l, --list          list all groups'
    print '    -C, --create        Create'
    print '    -D, --delete        Delete'
    print '    -g, --group=        name of the group'
    print '    -d, --debug         debug mode'
    print ' ex :'
    print '    manage_group.py -l'
    print '    manage_group.py -C -g group'
    print '    manage_group.py -D -g group'

def listGroups():
    logging.debug("METHOD :listGroups()")
    count = 0
    groups = client.systemgroup.listAllGroups(key)
    for g in groups:
        print "{:<74} {:>5}".format(g['name'], g['system_count'])
        count += int(g['system_count'])

    print "--------------------------------------------------------------------------------"
    print "total {:>74}".format(count)
    logging.debug("END METHOD :listGroups()")

def createGroup(g):
    logging.debug("METHOD :createGroup({})".format(g))
    client.systemgroup.create(key, g, g)
    logging.debug("END METHOD :createGroup({})".format(g))

def deleteGroup(g):
    logging.debug("METHOD :deleteGroup({})".format(g))
    client.systemgroup.delete(key, g)
    logging.debug("END METHOD :deleteGroup({})".format(g))

def main():
    debug = 0
    listgroup = 0
    creategroup = 0
    deletegroup = 0
    group = 0

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hldCDg:", ["help", "list", "debug", "create", "delete", "group="])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)

    for k, v in opts:
        if k in ("-h", "--help"):
            usage()
            sys.exit()
        elif k in ("-l", "--list"):
            listgroup = 1
        elif k in ("-d", "--debug"):
            debug = 1
        elif k in ("-C", "--create"):
            creategroup = 1
        elif k in ("-D", "--delete"):
            deletegroup = 1
        elif k in ("-g", "--group"):
            g = v
        else:
            usage()
            sys.exit(2)

    debug_level = logging.INFO
    if debug == 1:
        debug_level = logging.DEBUG

    logging.basicConfig(stream=sys.stderr, level=debug_level)

    if listgroup == 1:
        listGroups()
        sys.exit()

    if creategroup == 1 and g:
        createGroup(g)
        sys.exit()

    if deletegroup == 1 and g:
        deleteGroup(g)
        sys.exit()

    else:
        print "Error : parameter missing"
        usage()
        sys.exit(2)


if __name__ == "__main__":
    main()

credentials.spacewalkLogout(client, key)
