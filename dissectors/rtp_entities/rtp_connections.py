'''
Created on 10/giu/2011

@author: norby
'''


from core.dissector import SessionList, SessionInfo

class rtp_connections(dict):

    def __init__(self, incoming, pkt, payload):
        """
        rtp_connections entity.

        Is called to initialize new connections.

        """

        #INPUT: from=remote, to=local
        if incoming:
            self['ssrc']=SessionInfo()
            self['ssrc'].remote=payload.ssrc
            self['ssrc'].local=None
            self['type']=SessionInfo()
            self['type'].remote=payload._type
            self['type'].local=''
            self['lastts']=SessionInfo()
            self['lastts'].remote=payload.ts
            self['lastts'].local=''
            self['lastseq']=SessionInfo()
            self['lastseq'].remote=payload.seq
            self['lastseq'].local=''

        #OUTPUT: from=local, to=remote
        else:
            self['ssrc']=SessionInfo()
            self['ssrc'].remote=None
            self['ssrc'].local=payload.ssrc
            self['type']=SessionInfo()
            self['type'].remote=''
            self['type'].local=payload._type
            self['lastts']=SessionInfo()
            self['lastts'].remote=''
            self['lastts'].local=payload.ts
            self['lastseq']=SessionInfo()
            self['lastseq'].remote=''
            self['lastseq'].local=payload.seq

        self['incoming'] = incoming


    def __str__(self):

        if self['incoming']:
            row = '<-'
        else:
            row = '->'

        msg = row + '[SSRC: ' + str(self['ssrc']) + ', TS: ' + str(self['lastts'])  + ', SEQ: ' + str(self['lastseq']) + ']'
        return msg

    def updateConnState(self,new):

        self['incoming'] = new['incoming']

        if new['ssrc'].local:
            self['ssrc'].local = new['ssrc'].local
        elif new['ssrc'].remote:
            self['ssrc'].remote = new['ssrc'].remote

        if new['lastts'].local:
            self['lastts'].local = new['lastts'].local
        elif new['lastts'].remote:
            self['lastts'].remote = new['lastts'].remote


        if new['lastseq'].local:
            self['lastseq'].local = new['lastseq'].local
        elif new['lastseq'].remote:
            self['lastseq'].remote = new['lastseq'].remote
