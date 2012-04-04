'''
Created on 10/giu/2011

@author: norby
'''

from core.session import *
from core.options import conf, debug
from sdp import *
import core.dissector_dict

class sip_sessions(SessionList):

    def __init__(self):
        """
        sip_sessions entity.
        
        A sip_sessions contains a list of calls calls[], indexed by SIP call-id parameter.

        """

        self.lastcid=0
        self.calls = { }

        SessionList.__init__(self)

    def __str__(self):
        msg=''

        for call in self.calls.values():
            if debug>2 or call['toprint'] == True:
                msg += str(call) + '\n'
                call['toprint'] = False

        return msg[:-1]


    def update(self,new_conn):
        """
        SipSession update.

        This merge new SipCall adding new calls to self.calls, indexed by newcid.

        """
        newcid = new_conn.cid

        if newcid not in self.calls.keys():
            self.calls[newcid]=new_conn
            self.calls[newcid].setNewCallState()
        else:
            if not self.calls[newcid]['ip'] == new_conn['ip']:
                print '[ERR] Same cid but different IP, skipped (old:', inet_ntoa(self.calls[newcid]['ip'].local), inet_ntoa(self.calls[newcid]['ip'].remote), 'new:', inet_ntoa(new_conn['ip'].local), inet_ntoa(new_conn['ip'].remote), ')'
            else:
                self.calls[newcid].updateCallState(new_conn)

        self.lastcid = newcid


    def startCall(self,cid):
        if not (self.calls[cid]['lastsdp'].local and self.calls[cid]['lastsdp'].remote):
            print '[ERR] State ESTABILISHED but less than 2 sdp collected.'
            print '     ', self.calls[cid]['lastsdp'].local, self.calls[cid]['lastsdp'].remote
        else:
            lport, rport = get_SDP_port(self.calls[cid]['lastsdp'])
            if not (lport and rport):
                print '[ERR] State ESTABILISHED but not both media ports are available.'
                print '     ', self.calls[cid]['lastsdp'].local, self.calls[cid]['lastsdp'].remote
            else:
                core.dissector_dict.dissd.loadDissectorsInstances(['rtp'],[(lport,rport)])


    def cleanIdleConnections(self):
        """
        Clean all IDLE calls in self.calls[] list.

        Also unload RTP dissector in case of CALL-STOPPED

        """

        for cid in self.calls.keys():
            if self.calls[cid]['state'] == 'IDLE':
                del self.calls[cid]
            elif self.calls[cid]['state'] == 'IDLE-CALL-STOPPED':
                core.dissector_dict.dissd.unloadDissectorsInstances(['rtp'])
                del self.calls[cid]


