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
    print 'This script create custom repository for SuseManager'
    print 'Usage: %s [-h] [-l] [-L] [-C -c client -e email -r repository] [-D -c client-YYYYMMDD -r repository]' % sys.argv[0]
    print '    -h, --help          this help'
    print '    -l, --list-vendor   list Suse repository'
    print '    -L, --list-custom   list Custom repository'
    print '    -C, --create        Create repository'
    print '    -D, --delete        delete custom repository'
    print '    -c, --client=       name of the client'
    print '    -e, --email=        email of sap administrator'
    print '    -r, --repository=   top level repository to clone'
    print '    -d, --debug         debug mode'
    print ' ex :'
    print '    manage_repo.py -C -c myrepo -e email@sender.to -r sle11-sp4-sap-pool'
    print '    manage_repo.py -D -c myrepo-20161228 -r sle11-sp4-sap-pool'

def checkParam(c, e, r):
    err = 0

    if not re.match(r"[^@]+@[^@]+\.[^@]+", e):
        print "email      : NOK"
        err += 1

    if r not in getSuseRepo():
        print "repository : NOK"
        err += 1

    if err > 0:
        sys.exit(2)

def getSuseRepo():
    suse_top_repo = []

    suse_channels = client.channel.listVendorChannels(key)
    for suse_channel in suse_channels:
        channel_info = client.channel.software.getDetails(key, suse_channel['label'])

        if channel_info['parent_channel_label'] == "":
            suse_top_repo.append(suse_channel['label'])
    return suse_top_repo

def getCustomRepo():
    suse_top_repo = []

    suse_channels = client.channel.listMyChannels(key)
    for suse_channel in suse_channels:
        channel_info = client.channel.software.getDetails(key, suse_channel['label'])

        if channel_info['parent_channel_label'] == "":
            suse_top_repo.append(suse_channel['label'])
    return suse_top_repo

def getAllSuseRepoFromBaseChannel(c):
    suse_top_repo = []

    suse_channels = client.channel.listVendorChannels(key)
    for suse_channel in suse_channels:
        channel_info = client.channel.software.getDetails(key, suse_channel['label'])

        if suse_channel['label'] == c:
            suse_top_repo.insert(0, c)

        if channel_info['parent_channel_label'] == c:
            suse_top_repo.append(suse_channel['label'])
    return suse_top_repo

def getSuseRepoShow():
    print "List of top level Suse Repository :"
    suse_repo = getSuseRepo()
    for channel in suse_repo:
       print "    - " + channel

def getCustomRepoShow():
    print "List of top level Custom Repository :"
    custom_repo = getCustomRepo()
    for channel in custom_repo:
       print "    - " + channel

def createCustomRepo(c, e, r):
   checkParam(c, e, r)

   print "creating repository for " + c
   print "    email      : " + e
   print "    date       : " + date_repo
   print "    repository : " + r

   repo_list = getAllSuseRepoFromBaseChannel(r)
   parent_repo = ""
   for clone_repo in repo_list:
       repo_name = c + "-" + date_repo + "-" + clone_repo
       if clone_repo == r:
           print clone_repo + " -> " + c + "-" + date_repo + "-" + clone_repo
           parent_repo = c + "-" + date_repo + "-" + clone_repo
           channel_array = { 'label'        : repo_name,
                             'name'         : repo_name,
                             'summary'      : repo_name}
           id_repo = client.channel.software.clone(key, clone_repo, channel_array, False)
           client.channel.software.mergeErrata(key, clone_repo, repo_name)
           channel_info = { 'maintainer_name'  : c,
                            'maintainer_email' : e }
           client.channel.software.setDetails(key, id_repo, channel_info)

       else:
           print clone_repo + " -> " + c + "-" + date_repo + "-" + clone_repo + " (parent : " + parent_repo + ")"
           channel_array = { 'label'        : repo_name,
                             'name'         : repo_name,
                             'summary'      : repo_name,
                             'parent_label' : parent_repo}
           client.channel.software.clone(key, clone_repo, channel_array, False)
           client.channel.software.mergeErrata(key, clone_repo, repo_name)

def deleteCustomRepo(client_name, repository):
    repo_to_delete = []
    repo_to_delete_retry = []
    print "delete " + client_name + " - " + repository
    if re.match(r".*-\d{8}", client_name):
        my_regex = r"^" + re.escape(client_name) + r"-" + repository + "$"

        my_channels = client.channel.listMyChannels(key)
        for chan in my_channels:
            channel_info = client.channel.software.getDetails(key, chan['label'])
            if re.match(my_regex, channel_info['parent_channel_label']):
                repo_to_delete.append(chan['label'])
        repo_to_delete.append(client_name + "-" + repository)

        for r in repo_to_delete:
            client.channel.software.delete(key, r)
    else:
        print "incorect format of client : client-YYYYMMDD"


    #if re.match(, ):

def main():
    client_name = ""
    email = ""
    repository = ""
    create = 0
    debug = 0
    delete = 0

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hlLdCDc:e:r:", ["help", "list-vendor", "list-custom", "debug", "create", "delete", "client=", "email=", "repository="])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)

    for k, v in opts:
        if k in ("-h", "--help"):
            usage()
            sys.exit()
        elif k in ("-l", "--list-vendor"):
            getSuseRepoShow()
            sys.exit()
        elif k in ("-L", "--list-custom"):
            getCustomRepoShow()
            sys.exit()
        elif k in ("-d", "--debug"):
            debug = 1
        elif k in ("-C", "--create"):
            create = 1
        elif k in ("-D", "--delete"):
            delete = 1
        elif k in ("-c", "--client"):
            client_name = v
        elif k in ("-e", "--email"):
            email = v
        elif k in ("-r", "--repository"):
            repository = v
        else:
            usage()
            sys.exit(2)

    debug_level = logging.INFO
    if debug == 1:
        debug_level = logging.DEBUG

    logging.basicConfig(stream=sys.stderr, level=debug_level)

    if delete == 1:
        deleteCustomRepo(client_name, repository)
        sys.exit()

    if create == 1 and client_name and email and repository:
        createCustomRepo(client_name, email, repository)
        sys.exit()
    else:
        print "Error : parameter missing"
        usage()
        sys.exit(2)


if __name__ == "__main__":
    main()

credentials.spacewalkLogout(client, key)
