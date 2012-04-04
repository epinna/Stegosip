# -*- coding: utf-8 -*-
from core.session import *
import sys, os
sys.path.append('dpkt-1.6')
from dpkt import ip, sip
from nfqueue import NF_ACCEPT
from core.options import conf, debug


class dissector:

    name='GenericDissector'
    protocol='GenericProtocol'
    injpath=''
    injector = None


    def __init__(self,index,ports=[]):
        self.dissector_index = index

        self.__setDirectionMarkers(index)

        self.ports = []
        self._filterPorts(ports)

    def checkPkt(self,pkt):
        return False

    def _savePkt(self,pkt):
        pass

    def processPkt(self, pkt, nf_payload):

        if self.injector:
            self.injector.modifyPkt(pkt)
            self.injector.forwardPkt(pkt,nf_payload,NF_ACCEPT)
            self._savePkt(pkt)
        else:
            nf_payload.set_verdict(NF_ACCEPT)
            self._savePkt(pkt)


    def unload(self):
        self._filterPorts(self.ports, True)

        if self.injector:
            self._unloadInjectorInstance()

    def __setDirectionMarkers(self, index):

        self.incoming = 100+index
        self.outgoing = 200+index

    def _filterPorts(self,ports, delete = False):

        if not ports:
            print '[ERR] No port specified for dissector', self.name
        else:
            for portpair in ports:
                self._iptablesHandler(portpair, delete)
                if not delete:
                    self.ports += [ (portpair) ]

            if delete:
                delstr = 'Deleted'
            else:
                delstr = 'Added'

            print '[' + self.name + '] ' + delstr + ' dissector and netfilter rules on', self._printPorts(ports)


    def _printPorts(self, ports = []):

        if not ports:
            ports = self.ports

        portstring = self.protocol + ' '
        for portpair in ports:
            if len(portpair) == 1:
                portstring += str(portpair[0]) + ', '

            elif len(portpair) == 2:
                portstring += str(portpair[0]) + '<->' + str(portpair[1]) + ', '

        return portstring[:-2] + ' ports.'


    def _containsPorts(self,sport,dport):
        for p in self.ports:
            if len(p) == 2:
                if (sport == p[0] and dport == p[1]) or (sport == p[1] and dport == p[0]):
                    return True
            elif len(p) == 1:
                if (sport == p[0]) or (dport == p[0]):
                    return True

        return False


    def _loadInjectorInstance(self,injector,params = []):

        filelst=os.listdir(self.injpath)

        if self.injpath and injector and (injector + '.py' in filelst):

            completepath = self.injpath.replace('/','.') + injector

            mod = __import__(completepath, fromlist = ["*"])
            classes = getattr(mod,injector)
            self.injector=classes(*params)
            print '[' + self.name + '] Injector \'' + injector + '\' module loaded'

        else:

            print '[ERR] Injector \'' + injector + '\' module not found'

    def _unloadInjectorInstance(self):
        if self.injector:
            del self.injector
            print '[' + self.name + '] Injector module unloaded'
            self.injector = None


    def _iptablesHandler(self,ports,delete=False):

        if delete:
            delstr = '-D'
        else:
            delstr = '-I'

        local_ip = conf.get('global','default_iface_ip')

        if local_ip:
            loc_ipstr_src = '-s ' + local_ip
            loc_ipstr_dst = '-d ' + local_ip
        else:
            loc_ipstr_src = ''
            loc_ipstr_dst = ''


        if len(ports) == 2:
            os.system('iptables ' + delstr + ' INPUT ' + loc_ipstr_dst + ' -j NFQUEUE -p ' + self.protocol + ' --sport ' + str(ports[1]) + ' --dport ' + str(ports[0]))
            os.system('iptables -t mangle ' + delstr + ' INPUT ' + loc_ipstr_dst + ' -j MARK --set-mark ' + str(self.incoming) + ' -p ' + self.protocol + ' --sport ' + str(ports[1]) + ' --dport ' + str(ports[0]))

            os.system('iptables ' + delstr + ' OUTPUT ' + loc_ipstr_src + ' -j NFQUEUE -p ' + self.protocol + ' --sport ' + str(ports[0]) + ' --dport ' + str(ports[1]))
            os.system('iptables -t mangle ' + delstr + ' OUTPUT ' + loc_ipstr_src +  ' -j MARK --set-mark ' + str(self.outgoing) + ' -p ' + self.protocol  + ' --sport ' + str(ports[0]) + ' --dport ' + str(ports[1]))

        elif len(ports) == 1:
            os.system('iptables ' + delstr + ' INPUT ' + loc_ipstr_dst + ' -j NFQUEUE -p ' + self.protocol + ' --dport ' + str(ports[0]))
            os.system('iptables -t mangle ' +  delstr + ' INPUT ' + loc_ipstr_dst + ' -j MARK --set-mark ' + str(self.incoming) + ' -p ' + self.protocol + ' --dport ' + str(ports[0]))

            os.system('iptables ' + delstr + ' OUTPUT ' + loc_ipstr_src +  ' -j NFQUEUE -p ' + self.protocol + ' --sport ' + str(ports[0]))
            os.system('iptables -t mangle ' + delstr + ' OUTPUT ' + loc_ipstr_src +  ' -j MARK --set-mark ' + str(self.outgoing) + ' -p ' + self.protocol  + ' --sport ' + str(ports[0]))
