#!/usr/bin/env python

__author__ = "Matthieu Fatrez"
__copyright__ = "Copyright 2017, Matthieu Fatrez"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Matthieu Fatrez"
__email__ = "matthieu@fatrez.fr"

from common import credentials
import logging, os, sys, random, xmlrpclib

client = credentials.spacewalkConnect()
key = credentials.spacewalkGetKey(client)

###
###
###
def usage():
    print """createDistChannel:
to do..."""
    exit(0)

###
###
###
def extractDataFromFile(filename):
    logging.info('Processing extractDataFromFile = %s', filename)

    if(os.path.isfile(filename)):
        with open(filename) as f:
            content = f.read().splitlines() 
    else:
        logging.debug('File does not exist')
        print """File does not exist"""
        usage()

    i = 0
    parent = ""
    for repo in content:

        r = repo.split('|')
        chan_name = r[0]
        chan_label = r[0].lower()
        repo_label = r[1]
        chan_url = r[2]

        if chan_name.startswith("#"):
            logging.debug("Comment : ignoring")
            continue

        if(i < len(content)):
            channels_list = client.channel.listSoftwareChannels(key)

            try:
                logging.debug("client.channel.software.create({}, {}, {}, {}, {}, {})".format(key, chan_label, chan_name, "summary for " + chan_label, "channel-x86_64", parent))
                client.channel.software.create(key, chan_label, chan_name, "summary for " + chan_label, "channel-x86_64", parent)
            except xmlrpclib.Fault:
                logging.info("Channel {} already exist".format(chan_label))

            try:
                logging.debug("client.channel.software.createRepo({}, {}, {}, {})".format(key, repo_label, 'yum', chan_url))
                client.channel.software.createRepo(key, repo_label, 'yum', chan_url)
            except xmlrpclib.Fault:
                logging.info("Repository {} already exist".format(repo_label))

            logging.debug("client.channel.software.associateRepo({}, {}, {})".format(key, chan_label, repo_label))
            client.channel.software.associateRepo(key, chan_label, repo_label)
            logging.debug("client.channel.software.syncRepo({}, {}, {})".format(key, chan_label, "0 " + str(random.randint(0,59)) + " " + str(random.randint(0,3)) + " ? * *"))
            client.channel.software.syncRepo(key, chan_label, "0 " + str(random.randint(0,59)) + " " + str(random.randint(0,3)) + " ? * *")

            if(parent == ""):
                parent = chan_label
                logging.debug("set parent : {}".format(parent))

        i += 1

###
###
###
def main():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    if len(sys.argv) > 1:
        logging.info("createDistChannel {}".format(sys.argv[1]))
        extractDataFromFile(sys.argv[1])
    else:
        usage()

    sys.exit(0)

###
###
###
if __name__ == '__main__':
    main()

credentials.spacewalkLogout(client, key)
