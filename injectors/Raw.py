# -*- coding: utf-8 -*-

import core.tunnel as tunnel
from core.options import conf, debug
from core.injector import injector
import struct

class Raw(injector):

    def __init__(self, suggested_mtu):


        self.len_tunmtu = int(conf.get('raw', 'raw_tun_mtu'))
        self.keep_original_payload_size = conf.get('raw', 'keep_pkt_size')

        self.pendingtunpkt = ''

        injector.__init__(self, suggested_mtu)


        
        
    def _receivePkt(self, pkt):

        len_pkt_payload = len(pkt.extracted_payload.data)

        formatpack = '<4sh' + str(self._getMsgLenghtFromCoverLength(len_pkt_payload)) + 's'
        unpacked = struct.unpack(formatpack, pkt.extracted_payload.data)

        # Check if first part is self.minikeyhash + self.encapspktsize
        if unpacked[0] == self.minikeyhash:

            if debug: print '[INJ] < %i/%i bytes' % ( unpacked[1], len_pkt_payload)
            # Sent cutted data
            self.tun.tunWriter(unpacked[2][:unpacked[1]])


    def _sendPkt(self,pkt):

        if not self.pendingtunpkt:
            self.pendingtunpkt=self.tun.getDataToInject()

        if self.pendingtunpkt:

            len_tunpkt = len(self.pendingtunpkt)
            len_pkt_payload = len(pkt.extracted_payload.data)
            len_min_payload = self._getCoverLenghtFromMsgLength(len_tunpkt)

            if self.keep_original_payload_size and len_pkt_payload < len_min_payload:
                if debug>1: print '[INJ] Packet payload %i small to contains %i bytes.' % ( len_pkt_payload, len_min_payload )
            else:

                formatpack = '<4sh' + str(len_tunpkt) + 's'
                newdata = struct.pack(formatpack, self.minikeyhash, len_tunpkt , self.pendingtunpkt)

                old_len = len(pkt.udp.data)

                if self.keep_original_payload_size:
                    old_payload = pkt.extracted_payload.data
                    pkt.extracted_payload.data=newdata + old_payload[len(newdata):]
                else:
                    pkt.extracted_payload.data = newdata

                pkt.udp.data = pkt.extracted_payload
                pkt.len = pkt.len - old_len + len(pkt.udp.data)
                pkt.udp.sum = 0
                pkt.sum = 0

                if debug: print '[INJ] > %i + %i in %i Bytes (%i Bytes)' % ( len_tunpkt, self.len_stegoheader,  len_pkt_payload, len(pkt.extracted_payload.data) )
                self.pendingtunpkt = ''
