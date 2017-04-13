import xmlrpclib, ConfigParser, os

config = ConfigParser.RawConfigParser()
config.read('config.ini')

SPACEWALK_URL      = config.get('spacewalk', 'url')
SPACEWALK_LOGIN    = config.get('spacewalk', 'login')
SPACEWALK_PASSWORD = config.get('spacewalk', 'password')

def spacewalkConnect():
    return xmlrpclib.Server(SPACEWALK_URL, verbose=0)

def spacewalkGetKey(client):
    return client.auth.login(SPACEWALK_LOGIN, SPACEWALK_PASSWORD)

def spacewalkLogout(client,key):
    client.auth.logout(key)
