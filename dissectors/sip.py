# -*- coding: utf-8 -*-
from core.dissector import *
import dpkt
from dissectors.sip_entities.sip_calls import *
from dissectors.sip_entities.sip_sessions import *
from dpkt.sip import Request
from dpkt.sip import Response


class sip(dissector):

    name='SIP'
    protocol='udp'

    def __init__(self,index,ports=[]):

        if not ports:
            ports=[(5060,)]

        self.connections=sip_sessions()
        dissector.__init__(self,index,ports)

    def checkPkt(self,pkt):

        if  self._containsPorts(pkt.udp.sport,pkt.udp.dport):

            try:
                payload_request = dpkt.sip.Request(pkt.udp.data)
            except:
                payload_request = None
            else:
                pkt.extracted_payload=payload_request

            try:
                payload_response = dpkt.sip.Response(pkt.udp.data)
            except:
                payload_response = None
            else:
                pkt.extracted_payload=payload_response



    def _savePkt(self,pkt):


        newcall = sip_call(self.connections,pkt.incoming, pkt, pkt.extracted_payload)
        self.connections.update(newcall)
        connprint = str(self.connections)
        if connprint:
            print '[' + self.name + '] ' + connprint
        self.connections.cleanIdleConnections()
