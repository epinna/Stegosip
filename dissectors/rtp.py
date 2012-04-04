# -*- coding: utf-8 -*-
from core.dissector import SessionList, SessionInfo, dissector
from core.options import conf, debug
from rtp_entities.rtp_sessions import *
from rtp_entities.rtp_connections import *
import dpkt


class rtp(dissector):

    name='RTP'
    protocol='udp'
    injpath='injectors/'

    def __init__(self,index,ports=[]):

        self.connections = rtp_sessions()
        self.first_payload = False

        self.injector_name=conf.get('global','injector')

        dissector.__init__(self,index,ports)


    def checkPkt(self,pkt):

        if self._containsPorts(pkt.udp.sport,pkt.udp.dport):

            try:
                payload = dpkt.rtp.RTP(pkt.udp.data)
            except:
                pass
            else:
                if not self.first_payload:
                    self._loadInjectorInstance(self.injector_name,[ len(payload.data), ])
                    self.first_payload = True

                pkt.extracted_payload = payload



    def _savePkt(self,pkt):


        newconn = rtp_connections(pkt.incoming, pkt, pkt.extracted_payload)
        self.connections.update(newconn)
