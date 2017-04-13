#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

__author__ = "Matthieu Fatrez"
__copyright__ = "Copyright 2017, Matthieu Fatrez"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Matthieu Fatrez"
__email__ = "matthieu@fatrez.fr"

from math import *
from common import credentials
import logging, ConfigParser, getopt, os, sys, re, time, datetime, smtplib

client = credentials.spacewalkConnect()
key = credentials.spacewalkGetKey(client)

###
###
###
config = ConfigParser.RawConfigParser()
config.read('config.ini')
max_days     = config.get('alerting', 'max_days')
email_sender = config.get('smtp', 'email_sender')
email_copy   = config.get('smtp', 'email_copy')
smtp_service = config.get('smtp', 'smtp_service')

###
###
###
def usage():
    print 'This script alert if a custom repository have more than ' + str(max_days)
    print 'Usage: %s [-h] [-d]' % sys.argv[0]
    print '    -h, --help          this help'
    print '    -d, --debug         debug'

###
###
###
def getCustomRepo():
    logging.debug("- Start trt --------------------------------------------------------------------")
    channels = client.channel.listSoftwareChannels(key)

    for channel in channels:

        if channel['parent_label'] == '' and re.search(".*\d{8}", channel['label']):
            logging.debug("Get parent channel : {}".format(channel['label']))
            channel_detail = client.channel.software.getDetails(key, channel['label'])
            email = channel_detail['maintainer_email']

            if email != '':
                r = re.search(".*(?P<date_repo_text>\d{8})", channel_detail['label'])

                if r is not None:
                    date_repo = time.strptime(r.group('date_repo_text'), "%Y%m%d")
                    date_now  = time.gmtime()
                    delta = (time.mktime(date_now)-time.mktime(date_repo)) / 86400
                    logging.debug("Check how many days have parent channel {}".format(channel['label']))

                    if delta > max_days:
                        logging.debug("Parent channel have more than {} days Sending email to {} for {}".format(max_days, email, channel['label']))
                        list_hosts = client.channel.software.listSubscribedSystems(key, channel['label'])
                        sendmail(email, channel['label'], list_hosts)
                    else:
                        logging.debug("Parent channel {} have {} days".format(channel['label'], ceil(delta)))

    logging.debug("- End trt ----------------------------------------------------------------------")

###
###
###
def sendmail(email, channel_label, list_hosts):
    receivers = [email, email_copy]
    message =  """From: SuseManager <""" + email_sender + """>\n"""
    message += """To: AdmGroup <""" + email + """>\n"""
    message += """Cc: Admin-Unix-Loos <""" + email_copy + """>\n"""
    message += """Subject: Update of repository : """ + channel_label + """\n"""
    message += """\n"""
    message += """Hello,\n"""
    message += """\n"""
    message += """The repository """ + channel_label + """ has more than """ + str(max_days) + """ days.\n"""
    message += """It's time to think about starting an update campaign of the operating system!\n"""
    message += """\n"""
    message += """List of impacted systems :\n"""
    for system in list_hosts:
      message += """     - """ + system['name'] + """\n"""
    message += """\n"""
    message += """Could be a good chance for you to ask the Unix System team to help you for this OS update..\n"""
    message += """\n"""
    message += """Best regards,\n"""
    message += """Unix System Team"""
    try:
      smtpObj = smtplib.SMTP(smtp_service)
      smtpObj.sendmail(email_sender, receivers, message)
      logging.debug("Email sent to {} for repository {}".format(email, channel_label))
    except SMTPException:
      logging.debug("Unable to send email")

###
###
###
def main():

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd", ["help", "debug"])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)

    debug_level = logging.INFO
    for k, v in opts:
        if k in ("-h", "--help"):
            usage()
            sys.exit()
        elif k in ("-d", "--debug"):
            debug_level = logging.DEBUG
        else:
            debug_level = logging.INFO

    logging.basicConfig(stream=sys.stderr, level=debug_level)
    getCustomRepo()
    sys.exit(0)

###
###
###
if __name__ == '__main__':
    main()

credentials.spacewalkLogout(client, key)
