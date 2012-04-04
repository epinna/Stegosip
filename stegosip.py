#!/usr/bin/python

import asyncore, sys, os
import core.nf_pkt_dispatcher
import core.dissector_dict
from core.options import conf, debug

from optparse import OptionParser


if __name__ == '__main__':

    if os.getuid()!=0:
        print '[ERR] Retry as root.'
        sys.exit(1)
        
    proto =  conf.get('global', 'protocol')
    if not proto:
        print '[ERR] Parameter in stegosip.conf \'protocol\' is mandatory.'
        sys.exit(1)    
        
    try:

        core.dissector_dict.dissd.loadDissectorsInstances([proto,])
        try:
            core.nf_pkt_dispatcher.nf_pkt_dispatcher()
        except Exception, e:
            print '[ERR] Error loading netfilter queue. Have you loaded the kernel module? Try running \'modprobe nfnetlink_queue\'.'
            raise

        asyncore.loop()

    except KeyboardInterrupt:
        print 'Quitting.'
        if core.dissector_dict.dissd:
            core.dissector_dict.dissd.unloadDissectorsInstances()
        sys.exit(0)
    except Exception, e:
        print 'Error: ', str(e)
        if core.dissector_dict.dissd:
            core.dissector_dict.dissd.unloadDissectorsInstances()

        if debug:
            print 'Raised exception:'
            raise
        sys.exit(1)
