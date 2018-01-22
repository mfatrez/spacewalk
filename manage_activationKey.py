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
    print 'This script create Activation key'
    print 'Usage: %s [-h] [-l] [-C -c client -e description -r repository -g group] [-D -c client]' % sys.argv[0]
    print '    -h, --help          this help'
    print '    -l, --list          list all activation key'
    print '    -C, --create        Create repository'
    print '    -D, --delete        delete custom repository'
    print '    -c, --cle=          name of the activation key'
    print '    -e, --description   description'
    print '    -g, --group         group'
    print '    -r, --repository=   top level repository'
    print ' ex :'
    print '    manage_activationKey.py -C -c client -e descroption -r repo -g group'

def listActivationKey():
    logging.debug("METHOD : listActivationKey({})")

    print "list Activation Key"
    activKey = client.activationkey.listActivationKeys(key)

    for a in activKey:
        print "{:<40} | {:^40} | {:<44}".format(a['description'], a['key'], a['base_channel_label'])

def notexistActivationKey(activationKeyName):
    logging.debug("METHOD : notexistActivationKey({})".format(activationKeyName))
    i = 0
    activKeyResult = client.activationkey.listActivationKeys(key)
    for a in activKeyResult:
        if a['key'] == activationKeyName:
            logging.debug("METHOD : notexistActivationKey : found ")
            i += 1
    if i == 0:
        print "Key does not exist"
        logging.debug("METHOD : notexistActivationKey : not found -> exit ")
        sys.exit(2)

def existActivationKey(activationKeyName):
    logging.debug("METHOD : existActivationKey({})".format(activationKeyName))
    activKeyResult = client.activationkey.listActivationKeys(key)

    for a in activKeyResult:
        if a['key'] == activationKeyName:
            logging.debug("METHOD : existActivationKey : found -> exist")
            sys.exit(2)

def existGroup(group):
    logging.debug("METHOD : existGroup({})".format(group))
    i = 0
    groupResult = client.systemgroup.listAllGroups(key)
    for g in groupResult:
        if g['name'] == group:
            logging.debug("METHOD : existGroup : found")
            i += 1
            return g['id']

    if i == 0:
        logging.debug("METHOD : existGroup : not found")
        sys.exit(2)

    logging.debug("METHOD : existGroup : END METHOD")

def getAllChannelsFrom(baseChannel):
    logging.debug("METHOD : getAllChannelsFrom({})".format(baseChannel))
    repo_array = []
    f = client.channel.listSoftwareChannels(key)
    for i in f:
        if i['parent_label'] == baseChannel:
            if not re.search(r".*(smt|sdk|webyast|openstack|packagehub|hpc|proxy).*", i['name']):
                repo_array.append(i['name'])

    return repo_array

def createActivationKey(activationKeyName, description, baseChannel, group):
    logging.debug("METHOD : createActivationKey({}, {}, {}, {})".format(activationKeyName, description, baseChannel, group))
    existActivationKey(str("1-"+activationKeyName))
    addOn = []

    logging.debug("METHOD : createActivationKey create activation key")
    activKeyResult = client.activationkey.create(key, activationKeyName, description, baseChannel, addOn, False)

    logging.debug("METHOD : createActivationKey join existing group")
    gid = existGroup(group)
    groups = [gid]
    client.activationkey.addServerGroups(key, activKeyResult, groups)

    packages_to_add = [{'name': 'rhncfg-client'}, {'name': 'rhncfg'}, {'name': 'rhncfg-actions'}, {'name': 'rhnmd'}]
    logging.debug("METHOD : createActivationKey add packages {}".format(packages_to_add))
    client.activationkey.addPackages(key, str("1-"+activationKeyName), packages_to_add)

    logging.debug("METHOD : createActivationKey add all repos")
    childChannel = getAllChannelsFrom(baseChannel)
    client.activationkey.addChildChannels(key, str("1-"+activationKeyName), childChannel)

    print "key {} is created".format(activKeyResult)

def deleteActivationKey(activationKeyName):
    logging.debug("METHOD :deleteActivationKey({})".format(activationKeyName))
    print "delete Activation Key"
    notexistActivationKey(activationKeyName)
    client.activationkey.delete(key, activationKeyName)
    print "Remove key : {}".format(activationKeyName)

def main():
    activationKeyName = ""
    description = ""
    baseChannel = ""
    repository = ""
    group = ""
    create = 0
    debug = 0
    delete = 0

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hldCDc:r:e:g:", ["help", "list", "debug", "create", "delete", "client=", "repository=", "group="])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)

    for k, v in opts:
        if k in ("-h", "--help"):
            usage()
            sys.exit()
        elif k in ("-l", "--list"):
            listActivationKey()
            sys.exit()
        elif k in ("-d", "--debug"):
            debug = 1
        elif k in ("-C", "--create"):
            create = 1
        elif k in ("-D", "--delete"):
            delete = 1
        elif k in ("-g", "--group"):
            group = v
        elif k in ("-e", "--description"):
            description = v
        elif k in ("-c", "--cle"):
            activationKeyName = v
        elif k in ("-r", "--repository"):
            baseChannel = v
        else:
            usage()
            sys.exit(2)

    debug_level = logging.INFO
    if debug == 1:
        debug_level = logging.DEBUG

    logging.basicConfig(stream=sys.stderr, level=debug_level)


    if delete == 1 and activationKeyName:
        deleteActivationKey("1-"+activationKeyName)
        sys.exit()

    if create == 1 and activationKeyName and description and baseChannel and group:
        createActivationKey(activationKeyName, description, baseChannel, group)
        sys.exit()
    else:
        print "Error : parameter missing"
        usage()
        sys.exit(2)


if __name__ == "__main__":
    main()

credentials.spacewalkLogout(client, key)
