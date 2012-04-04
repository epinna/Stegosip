'''
Created on 10/giu/2011

@author: norby
'''

from core.session import *
from sdp import *
import re;


errormsg = re.compile('^[56][0-9][0-9]|^CANCEL|^BYE')

class sip_call(dict):

    def __init__(self, parentconn, incoming, pkt, payload):
        """
        sip_call entity.

        """

        address_fr=re.findall('<?sip:([^>;]*)',payload.headers['from'])
        address_to=re.findall('<?sip:([^>;]*)',payload.headers['to'])

        if not (address_fr and address_to):
            raise SessionError('No from and to sip address.')

        meth=''
        if 'method' in dir(payload):
            meth=payload.method
        elif 'status' in dir(payload) and 'reason' in dir(payload):
            meth=payload.status + ' ' + payload.reason

        sdp=None
        try:
            sdp=SDP(payload)
        except Exception, e:
            if debug>2: print '[ERR] No SDP payload detected:', e

        if 'call-id' in payload.headers:
            self.cid = payload.headers['call-id']
        else:
            raise SessionError('No call-id')

        #INPUT: from=remote, to=local
        if incoming:
            self['sipaddresses']=SessionInfo()
            self['sipaddresses'].local=address_to[0]
            self['sipaddresses'].remote=address_fr[0]
            self['lastsdp']=SessionInfo()
            self['lastsdp'].remote=sdp
            self['lastsdp'].local=None
            self['lastmethod']=SessionInfo()
            self['lastmethod'].remote=meth.strip()
            self['lastmethod'].local=''
            self['ip']=SessionInfo()
            self['ip'].local=pkt.dst
            self['ip'].remote=pkt.src


        #OUTPUT: from=local, to=remote
        else:
            self['sipaddresses']=SessionInfo()
            self['sipaddresses'].local=address_fr[0]
            self['sipaddresses'].remote=address_to[0]
            self['lastsdp']=SessionInfo()
            self['lastsdp'].local=sdp
            self['lastsdp'].remote=None
            self['lastmethod']=SessionInfo()
            self['lastmethod'].local=meth.strip()
            self['lastmethod'].remote=''
            self['ip']=SessionInfo()
            self['ip'].local=pkt.src
            self['ip'].remote=pkt.dst

        self.parentconn = parentconn
        self['incoming'] = incoming
        self['state'] = 'IDLE'
        self['toprint'] = False

    def __str__(self):

        lsdp=''
        if self['lastsdp'].local and self['lastsdp'].remote:
            lsdp='\n[SDP] ' + str(self['lastsdp'])

        if self['incoming']:
            row = '<-'
        else:
            row = '->'

        source = self['sipaddresses'].local
        dest = self['sipaddresses'].remote

        msg = '[' + self['state'] + ':' + self.cid + '] ' + source + row +  dest  + ' '  + ' [ ' + str(self['lastmethod']) + '] ' + lsdp
        return msg


    def setNewCallState(self):
        """
        Method to initialize state of just inserted new calls.

        Summary of state changes:

        if INVITE in uscita
        elif INVITE in entrata
        else return

        """

        #Case: call starting. Local send INVITE.
        if self['lastmethod'].local == 'INVITE':
            self['state'] = 'OUTGOING-CALL'
            self['toprint'] = True
        #Case: call receiving. Remote send INVITE.
        elif self['lastmethod'].remote == 'INVITE':
            self['state'] = 'INCOMING-CALL'
            self['toprint'] = True
        # In unexpected cases, delete it.
        else:
            self['state'] = 'IDLE'



    def updateCallState(self,new):

        old_state = self['state']
        self['incoming'] = new['incoming']

        if new['lastmethod'].local:
            self['lastmethod'].local = new['lastmethod'].local
            self['lastmethod'].remote = ''
        if new['lastmethod'].remote:
            self['lastmethod'].remote = new['lastmethod'].remote
            self['lastmethod'].local = ''


        # ERROR MSG, RETURN TO IDLE STATE
        if errormsg.search(new['lastmethod'].local) or errormsg.search(new['lastmethod'].remote):
            if self['state'].endswith('-CALL-ESTABILISHED'):
                self['state'] = 'IDLE-CALL-STOPPED'
            else:
                self['state'] = 'IDLE'

            self['lastsdp']=SessionInfo()

        # STATE IDLE
        if self['state'] == 'IDLE' or self['state'] == 'IDLE-CALL-STOPPED':

            #outgoing call
            if new['lastmethod'].local == 'INVITE':
                self['lastsdp'].local = new['lastsdp'].local
                self['state'] = 'OUTGOING-CALL'

            #incoming call
            if new['lastmethod'].remote == 'INVITE':
                self['lastsdp'].remote = new['lastsdp'].remote
                self['state'] = 'INCOMING-CALL'

        # STATE OUTGOING-CALL

        elif self['state'] == 'OUTGOING-CALL':

            if new['lastmethod'].remote.startswith('1'):
                pass
            elif new['lastmethod'].remote.startswith('2'):
                self['lastsdp'].remote = new['lastsdp'].remote
                self['state'] = 'OUTGOING-CALL-ESTABILISHED'
                self.parentconn.startCall(self.cid)
            else:
                pass

        # STATE OUTGOING-CALL-ESTABILISHED

        elif self['state'] == 'OUTGOING-CALL-ESTABILISHED':
            pass

        elif self['state'] == 'INCOMING-CALL':
            if new['lastmethod'].local.startswith('1'):
                pass
            elif new['lastmethod'].local.startswith('2'):
                self['lastsdp'].local = new['lastsdp'].local
                self['state'] = 'INCOMING-CALL-ESTABILISHED'
                self.parentconn.startCall(self.cid)
            else:
                pass

        elif self['state'] == 'INCOMING-CALL-ESTABILISHED':
            pass

        if self['state'] != 'IDLE' and self['state'] != old_state:
            self['toprint'] = True



