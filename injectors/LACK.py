

from core.options import conf, debug
from core.injector import injector
from dissectors.rtp_entities.payloads import get_ts_usec
from dpkt import *
from nfqueue import NF_DROP
import threading, struct


def sendDelayedPkt(delayed_pkt, delay):

    if debug>2: print '[INJ] delayed packet injected'

    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    s.sendto(delayed_pkt.udp.pack(), (socket.inet_ntoa(delayed_pkt.dst), int(delayed_pkt.udp.dport)))


def getPrimes(low, high):
    return [2]+[x for x in range(low,high)if 2**x%x==2]

class LACK(injector):

    def __init__(self, suggested_mtu):

        self.len_tunmtu = int(conf.get('raw', 'raw_tun_mtu'))

        self.lasttimestamp = -1

        self.rate = int(conf.get('lack','pkt_rate'))
        if self.rate <= 0:
            self.rate = 1
            
        self.delay = float(conf.get('lack', 'delay'))
        self.delay_usec = self.delay/1000000
        
        self.pendingtunpkt = ''
        

        injector.__init__(self, suggested_mtu)

        self.prime = getPrimes(1, ord(self.minikeyhash[0]))[-1]
        
        if self.rate % self.prime == 0:
            print '[ERR] Error initializing linear congruential generator:'
            print 'rate %i is divisible by prime number %i. Change rate or secret.'
        



    def forwardPkt(self,pkt,nf_payload,mode):

        if pkt.diss_params and pkt.diss_params[0] > 0:

            delayed_pkt = ip.IP(str(pkt))
            nf_payload.set_verdict_modified(NF_DROP, str(delayed_pkt), len(delayed_pkt))

            t = threading.Timer(pkt.diss_params[0], sendDelayedPkt, [delayed_pkt, pkt.diss_params[0]])
            t.start()
        else:
            nf_payload.set_verdict_modified(mode, str(pkt), len(pkt))
            
            



    def _receivePkt(self, pkt):

        delta = 0
        if self.lasttimestamp != -1:
            delta = get_ts_usec(pkt.extracted_payload.pt, pkt.extracted_payload.ts) - get_ts_usec(pkt.extracted_payload.pt, self.lasttimestamp)

        self.lasttimestamp = pkt.extracted_payload.ts

        if delta < 0 and -delta > self.delay_usec:
            
            len_pkt_payload = len(pkt.extracted_payload.data)

            formatpack = '<4sh' + str(self._getMsgLenghtFromCoverLength(len_pkt_payload)) + 's'
            unpacked = struct.unpack(formatpack, pkt.extracted_payload.data)


            # Check if first part is self.minikeyhash + self.encapspktsize
            if unpacked[0] == self.minikeyhash:

                if debug: print '[INJ] < %i/%i bytes with %.2fs of delay (seq: %i)' % ( unpacked[1], len_pkt_payload, -delta/1000000.0, pkt.extracted_payload.seq)
                # Sent cutted data
                self.tun.tunWriter(unpacked[2][:unpacked[1]])


    def _sendPkt(self,pkt):
                
                
        if pkt.extracted_payload.seq * self.prime % self.rate == 0:
                    
                    
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
                    newdata = struct.pack(formatpack, self.minikeyhash, len_tunpkt , self.pendingtunpkt)
    
                    old_len = len(pkt.udp.data)
    
                    old_payload = pkt.extracted_payload.data
                    pkt.extracted_payload.data=newdata + old_payload[len(newdata):]
    
                    pkt.udp.data = pkt.extracted_payload
                    pkt.len = pkt.len - old_len + len(pkt.udp.data)
                    pkt.udp.sum = 0
                    pkt.sum = 0
    
                    pkt.diss_params.append(self.delay)
    
                    if debug: print '[INJ] > %i + %i in %i Bytes (%i Bytes) with %.2fs of delay (seq: %i)' % ( len_tunpkt, self.len_stegoheader,  len_pkt_payload, len(pkt.extracted_payload.data), self.delay, pkt.extracted_payload.seq )
                    self.pendingtunpkt = ''


    