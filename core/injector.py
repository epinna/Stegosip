# -*- coding: utf-8 -*-
import hashlib
import core.tunnel as tunnel
from core.options import conf, debug

class injector:

    len_stegoheader = 6

    def __init__(self, suggested_mtu):

        self.key=conf.get('global','secret')

        self.len_pktmtu_suggested=suggested_mtu

        self.minikeyhash=hashlib.md5(self.key).digest()[:4]

        print '[INJ] Tunnel MTU: %i, stegosip header: %i, cover-paket payload MTU: %i' % (self.len_tunmtu, self.len_stegoheader, self._getCoverLenghtFromMsgLength(self.len_tunmtu))

        self.tun = tunnel.Tunnel(self.key, self.len_tunmtu)


    def _getCoverLenghtFromMsgLength(self, len_tunpkt):
        return len_tunpkt + self.len_stegoheader

    def _getMsgLenghtFromCoverLength(self, len_payload):
        return len_payload - self.len_stegoheader
      

    def modifyPkt(self,pkt):

        if pkt.incoming:
            self._receivePkt(pkt)
        else:
            self._sendPkt(pkt)

    def __del__(self):
        self.tun.stop()

    def forwardPkt(self,pkt,nf_payload,mode):
        nf_payload.set_verdict_modified(mode, str(pkt), len(pkt))
