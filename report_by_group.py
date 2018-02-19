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
import sys, time, getopt, re, logging, xmlrpclib
import ConfigParser, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import email.message
import email.utils

client = credentials.spacewalkConnect()
key = credentials.spacewalkGetKey(client)

config = ConfigParser.RawConfigParser()
config.read('config.ini')
email_sender = config.get('smtp', 'email_sender')
email_copy   = config.get('smtp', 'email_copy')
smtp_service = config.get('smtp', 'smtp_service')

yesterday = datetime.today() - timedelta(days=1)

def usage():
    print 'This script create reports for clients'
    print 'Usage: %s [-h] [-g group]' % sys.argv[0]
    print '    -h, --help          this help'
    print '    -g, --group=        name of the group'
    print '    -e, --email         send repport by mail'
    print ' ex :'
    print '    report_by_group.py -g group'

def getInformation(group_name):
    logging.debug("METHOD START : getInformation")

    list_systems_in_group = ""

    try:
        list_systems_in_group = client.systemgroup.listSystems(key, group_name)
    except xmlrpclib.Fault:
        logging.debug("METHOD : getInformation - EXCEPTION : Unable to get info from group")
        print "Unable to get info from group"

    information = []

    for system in list_systems_in_group:
         logging.debug("METHOD : getInformation - Get info from : %s - %s" % (system['id'], system['hostname']))

         inf = {}
         repository = client.system.getSubscribedBaseChannel(key, system['id'])
         osa_status = sorted(client.system.getId(key, system['hostname']), key=lambda sort_date: sort_date['last_checkin'])[-1]['last_checkin']

         inf['hostname']          = system['hostname']
         inf['security_patch']    = len(client.system.getRelevantErrataByType(key, system['id'], "Security Advisory"))
         inf['bug_patch']         = len(client.system.getRelevantErrataByType(key, system['id'], "Bug Fix Advisory"))
         inf['enhancement_patch'] = len(client.system.getRelevantErrataByType(key, system['id'], "Product Enhancement Advisory"))
         inf['outdated_packages'] = sorted(client.system.getId(key, system['hostname']), key=lambda sort_date: sort_date['last_checkin'])[-1]['outdated_pkg_count']
         inf['repository']        = repository['label']
         inf['email']             = repository['maintainer_email']

         osa = "OK"
         if osa_status < yesterday:
             osa = "NOK"

         inf['osa'] = osa

         information.append(inf)

    logging.debug("METHOD END  : getInformation")
    return information

def genPrintReportEmail(group_name, informations):
    logging.debug("METHOD START : genPrintReportEmail")

    logging.debug("METHOD : genPrintReportEmail - Print header - START")
    message  = "<html>\n"
    message += "<head>\n"
    message += "<title>{}</title>\n".format(group_name)
    message += "<style>\n"
    message += "  table {\n"
    message += "    border-collapse: collapse;\n"
    message += "  }\n"
    message += "  th, td {\n"
    message += "    border: 1px solid green;\n"
    message += "    padding: 10px;\n"
    message += "    text-align: left;\n"
    message += "  }\n"
    message += "  tr:nth-child(even) {\n"
    message += "    background-color: #eee;\n"
    message += "  }\n"
    message += "  tr:nth-child(odd) {\n"
    message += "    background-color: #fff;\n"
    message += "  }\n"
    message += "</style>\n"
    message += "</head>\n"
    message += "<body>\n"


    message += "<table>\n"
    message += "  <tr>\n"
    message += "    <th width='300px'>Hostname</th>\n"
    message += "    <th width='30px'>R</th>\n"
    message += "    <th width='30px'>S-P</th>\n"
    message += "    <th width='30px'>B-P</th>\n"
    message += "    <th width='30px'>E-P</th>\n"
    message += "    <th width='30px'>O-P</th>\n"
    message += "    <th width='450px'>Channel Labels</th>\n"
    message += "  </tr>\n"

    for inf in informations:
      message += "  <tr>\n"
      if inf['security_patch'] > 0 or inf['bug_patch'] > 0 or inf['enhancement_patch'] > 0 or inf['outdated_packages'] > 0:
        message += "    <td><font color='red'>{} (upgrade required)</font></td>\n".format(inf['hostname'])
      else:
        message += "    <td>{}</td>\n".format(inf['hostname'])

      if inf['osa'] == "NOK":
        message += "    <td><font color='red'>{}</font></td>\n".format(inf['osa'])
      else:
        message += "    <td><font color='green'>{}</font></td>\n".format(inf['osa'])

      message += "    <td>{}</td>\n".format(inf['security_patch'])
      message += "    <td>{}</td>\n".format(inf['bug_patch'])
      message += "    <td>{}</td>\n".format(inf['enhancement_patch'])
      message += "    <td>{}</td>\n".format(inf['outdated_packages'])
      message += "    <td>{}</td>\n".format(inf['repository'])
      message += "  </tr>\n"

    message += "</table>\n"

    message += "<ul>\n"
    message += "  <li>R   -> Reachable</li>\n"
    message += "  <li>S-P -> Security Patch</li>\n"
    message += "  <li>B-P -> Bug Patch</li>\n"
    message += "  <li>E-P -> Enhance Patch</li>\n"
    message += "  <li>O-P -> Outdated Package</li>\n"
    message += "</ul>\n"

    message += "</body>\n"
    message += "</html>\n"

    
    logging.debug("METHOD : genPrintReportEmail : {}".format(message))


    logging.debug("METHOD : genPrintReportEmail - Print footer - END")

    logging.debug("METHOD END   : genPrintReportEmail")

    return message

def genPrintReportShow(group_name, informations):
    logging.debug("METHOD START : genPrintReportShow")

    logging.debug("METHOD : genPrintReportShow - Print header - START")
    message  = "-------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
    message += "|{:^161}|\n".format(group_name)
    message += "-------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
    message += "| Hostname                                                     | R |  S-P  |  B-P  |  E-P  |  O-P  | Channel Labels                                               |\n"
    message += "-------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
    logging.debug("METHOD : genPrintReportShow - Print header - END")

    logging.debug("METHOD : genPrintReportShow - show informations")
    for inf in informations:
         message += "| {:<60} | {:<1} | {:>5} | {:>5} | {:>5} | {:>5} | {:<60} |\n".format(inf['hostname'], inf['osa'], inf['security_patch'], inf['bug_patch'], inf['enhancement_patch'], inf['outdated_packages'], inf['repository'])

    logging.debug("METHOD : genPrintReportShow - Print footer - START")
    message += "-------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
    message += " R   -> Reachable\n"
    message += " S-P -> Security Patch\n"
    message += " B-P -> Bug Patch\n"
    message += " E-P -> Enhance Patch\n"
    message += " O-P -> Outdated Package"

    logging.debug("METHOD : genPrintReportShow - Print footer - END")

    logging.debug("METHOD END   : genPrintReportShow")

    return message

def emailReport(message, group_name, emails):
    logging.debug("METHOD START : emailReport")

    try:
      for receiver in emails:
          msg = MIMEMultipart()
          msg['From'] = email_sender
          msg['To'] = receiver
          msg['Subject'] = "Suse Manager Email report for {}".format(group_name)
          msg.attach(MIMEText(message, 'html'))

          smtp_obj = smtplib.SMTP(smtp_service)
          smtp_obj.sendmail(msg['From'], [msg['To']], msg.as_string())
          smtp_obj.quit()

          logging.debug("Email sent to {}".format(receiver))
          logging.debug("Pausing 1 seconde")
          time.sleep(1)
    except smtplib.SMTPException:
      logging.debug("Unable to send email")

    logging.debug("METHOD END   : emailReport")

def createReport(group_name, email):
    logging.debug("METHOD START : createReport")

    informations = getInformation(group_name)

    emails = []
    for inf in informations:
        emails.append(inf['email'])
    emails = sorted(set(emails))

    if email == "NotDefined":
        messagePrint = genPrintReportShow(group_name, informations)
        print messagePrint
    else:
        messageSend = genPrintReportEmail(group_name, informations)
        emailReport(messageSend, group_name, emails)

    logging.debug("METHOD END : createReport")

def main():
    debug = 0
    group_name = ""
    email = "NotDefined"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hdg:e", ["help", "debug", "group=", "email"])
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
            email = "Define"
        else:
            usage()
            sys.exit(2)

    debug_level = logging.INFO
    if debug == 1:
        debug_level = logging.DEBUG

    logging.basicConfig(stream=sys.stderr, level=debug_level)

    if group_name:
        createReport(group_name, email)
        sys.exit()
    else:
        print "Error : parameter missing"
        usage()
        sys.exit(2)

if __name__ == "__main__":
    main()

credentials.spacewalkLogout(client, key)
