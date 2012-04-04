# -*- coding: utf-8 -*-

from dpkt import ip
from socket import AF_INET, AF_INET6, inet_ntoa


class SessionInfo:
    local=None
    remote=None

    def __init__(self):
        pass

    def __str__(self):

        st = ''
        if self.local:
            st+='local: ' + str(self.local) + ' '
        if self.remote:
            st+='remote:' + str(self.remote) + ' '
        return st

    def __eq__(self,ci):
        return (ci.local == self.local and ci.remote == self.remote)

    def slack_compare(self,ci):
        return (ci.local == self.local and ci.remote == self.remote) or (ci.local == self.remote and ci.remote == self.local)

class SessionError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class SessionList:
    def __init__(self):
        pass
