# -*- coding: utf-8 -*-
from ctypes import *
from core.injector import injector
from core.options import conf, debug
import struct, os, itertools


class LSB(injector):



    def __init__(self, suggested_mtu):

        if not os.path.exists('./injectors/LSB/libLSB.so.1'):
            print '[ERR] LibLSB.so.1 not found, trying to compile as shared library'
            os.system('gcc -c ./injectors/LSB/LSB.c -o ./injectors/LSB/LSB.o && gcc -shared -Wl -o ./injectors/LSB/libLSB.so.1 ./injectors/LSB/LSB.o')
            print '[INJ] compiled libLSB.so.1'

        if os.path.exists('./injectors/LSB/libLSB.so.1'):
            self.lsb_dll = CDLL("./injectors/LSB/libLSB.so.1")
        else:
            print '[ERR] File ./injectors/LSB/libLSB.so.1 not found.'

        self.bit_per_byte = int(conf.get('lsb','modified_bit_per_byte'))


        self.len_tunmtu = int(conf.get('lsb', 'lsb_tun_mtu'))


#        # Min size of medium packets
#        self.len_pktmtu = 848/self.bit_per_byte
#
#        # Max size of message
#        self.len_tunmtu = (self.len_pktmtu)/(8/self.bit_per_byte) - self.len_stegoheader - 4
#
#        # Mas size of message with header
#        self.len_tunmtu_w_header = (self.len_pktmtu)/(8/self.bit_per_byte)

        self.pendingtunpkt=''

        self.__initializeStegoPositions(1500)

        injector.__init__(self, suggested_mtu)


    def _getCoverLenghtFromMsgLength(self, len_tunpkt):
        return len_tunpkt * (8/self.bit_per_byte) + self.len_stegoheader

    def _getMsgLengthFromCoverLength(self, len_tunpkt):
        return len_tunpkt / (8/self.bit_per_byte) - self.len_stegoheader

    def _getMsgLengthFromCoverLengthWithHdr(self, len_tunpkt):
        return len_tunpkt / (8/self.bit_per_byte) 


    def __initializeStegoPositions(self, maxSteps, steplist = []):

        stepsNumber = maxSteps
        stepsType = c_int * stepsNumber
        if not steplist:
            steplist = tuple(itertools.repeat(1,stepsNumber))
        steps = stepsType(*steplist)
        self.lsb_dll.initializeSteps(steps, len(steps));




    #def test(self):

        #import itertools

        #f = open('/bin/bash')
        #vector = f.read()[:1500]

        #f1 = open('/usr/bin/yes')
        #tohide = f1.read()[:1500/2]

        #tohide_len=len(tohide)
        #vector_len = len(vector)

        #self.lsb_dll.ModifyBits(tohide,vector,tohide_len,vector_len,4)
        #buf = create_string_buffer(tohide_len)
        #self.lsb_dll.RecoverBits(buf,vector,tohide_len,vector_len,4)
        #print '\n', (buf.raw == tohide)


    def _receivePkt(self, pkt):

        len_pkt_payload = len(pkt.extracted_payload.data)
        self.len_tunmtu_w_header = self._getMsgLengthFromCoverLengthWithHdr(len_pkt_payload)


        tunpkt_w_header = create_string_buffer(self.len_tunmtu_w_header)
        self.lsb_dll.RecoverBits(tunpkt_w_header, pkt.extracted_payload.data, self.len_tunmtu_w_header, len_pkt_payload, self.bit_per_byte)
        tunpkt_w_header = tunpkt_w_header.raw

        formatpack = '<4sh' + str(self.len_tunmtu_w_header - self.len_stegoheader) + 's'
        unpacked = struct.unpack(formatpack, tunpkt_w_header)

        # Check if first part is self.minikeyhash + self.encapspktsize
        if unpacked[0] == self.minikeyhash:
            if debug: print '[INJ] < %i/%i bytes (seq: %i)' % ( unpacked[1], len_pkt_payload, pkt.extracted_payload.seq)
            # Sent cutted data
            self.tun.tunWriter(unpacked[2][:unpacked[1]])




    def _sendPkt(self, pkt):

        if not self.pendingtunpkt:
            self.pendingtunpkt=self.tun.getDataToInject()

        if self.pendingtunpkt:

            len_tunpkt = len(self.pendingtunpkt)
            len_pkt_payload = len(pkt.extracted_payload.data)
            len_min_payload = self._getCoverLenghtFromMsgLength(len_tunpkt)

            if len_pkt_payload < len_min_payload:
                if debug>1: print '[INJ] Packet payload %i small to contains %i bytes.' % ( len_pkt_payload, len_min_payload )
            
            else:

                formatpack = '<4sh' + str(len_tunpkt) + 's'
                len_tunpkt_w_header = struct.calcsize(formatpack)

                tunpkt_w_header = struct.pack(formatpack, self.minikeyhash, len_tunpkt , self.pendingtunpkt)

                newdata = create_string_buffer(len_pkt_payload)
                newdata.raw = pkt.extracted_payload.data
                self.lsb_dll.ModifyBits(tunpkt_w_header, newdata, len_tunpkt_w_header, len_pkt_payload, self.bit_per_byte)

                old_len = len(pkt.udp.data)
                pkt.extracted_payload.data = newdata.raw

                pkt.udp.data = pkt.extracted_payload
                pkt.len = pkt.len - old_len + len(pkt.udp.data)
                pkt.udp.sum = 0
                pkt.sum = 0

                # Testing modified bit

                #buf = create_string_buffer(len_tunpkt_w_header)
                #self.lsb_dll.RecoverBits(buf, pkt.extracted_payload.data, len_tunpkt_w_header, len_pkt_pkt.extracted_payload, self.bit_per_byte)
                #print (buf.raw == tunpkt_w_header)
                if debug: print '[INJ] > %i + %i in %i Bytes (%i Bytes) (seq: %i)' % ( len_tunpkt, self.len_stegoheader,  len_pkt_payload, len(pkt.extracted_payload.data), pkt.extracted_payload.seq  )
                self.pendingtunpkt = ''
