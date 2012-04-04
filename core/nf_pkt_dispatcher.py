# -*- coding: utf-8 -*-
import asyncore
from socket import AF_INET
from dpkt import ip
import nfqueue
import dissector_dict


class stegoIP(ip.IP):

    def __init__(self, *args, **kwargs):
        self.extracted_payload = None
        self.incoming = False

        self.diss_params = []

        ip.IP.__init__(self, *args, **kwargs)


class nf_pkt_dispatcher(asyncore.file_dispatcher):
    """
    An asyncore dispatcher of nfqueue events.

    """

    def __init__(self, nqueue=0, family=AF_INET, maxlen=5000, map=None):
        self._q = nfqueue.queue()
        self._q.set_callback(self.cb)
        self._q.fast_open(nqueue, family)
        self._q.set_queue_maxlen(maxlen)
        self.fd = self._q.get_fd()
        asyncore.file_dispatcher.__init__(self, self.fd, map)
        self._q.set_mode(nfqueue.NFQNL_COPY_PACKET)

    def handle_read(self):
        #print "Processing at most 5 events"
        self._q.process_pending(5)

    # We don't need to check for the socket to be ready for writing
    def writable(self):
        return False



    def cb(self,i,nf_payload):
        """
        Callback function of packet processing.

        Get corresponding dissector and direction of packets with .getLoadedDissectorByMarker()
        and send to the correct dissector using checkPkt() and processPkt().

        """

        data = nf_payload.get_data()
        pkt = stegoIP(data)

        marker = nf_payload.get_nfmark()

        dissector, incoming = dissector_dict.dissd.getLoadedDissectorByMarker(marker)
        pkt.incoming = incoming

        if not dissector:
            nf_payload.set_verdict(nfqueue.NF_ACCEPT)
        else:
            dissector.checkPkt(pkt)
            if pkt.extracted_payload:
                dissector.processPkt(pkt, nf_payload)

        return 1
