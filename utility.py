""" Utility """
import os
import logging

# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

class Dedup:
    seen_ids = {}
    def add(self, id):
        if id in self.seen_ids:
            return False
        self.seen_ids[id]=True
        return True
    def len(self):
        return len(self.seen_ids)

def accessToken():
    if 'fbToken' in os.environ:
        return os.environ['fbToken']
    return ""

def storeDSN():
    if 'dsn' in os.environ:
        return os.environ['dsn']
    return ""

def httpLogging():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
