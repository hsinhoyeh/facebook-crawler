""" Utility """
import os

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


