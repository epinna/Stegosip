# -*- coding: utf-8 -*-

from dissectors.rtp_entities.payloads import set_dynamic_pt, get_pt_name
from core.options import conf, debug
from core.session import SessionError

def get_SDP_port(sdps):
    """
    It should match the common media ports between local and remote

    """
    video = int(conf.get('sdp','prefer_video'))

    if video:
        if sdps.local.video_port and sdps.local.video_port[0] and sdps.remote.video_port and sdps.remote.video_port[0]:
            return sdps.local.video_port[0], sdps.remote.video_port[0]

    if sdps.local.audio_port and sdps.local.audio_port[0] and sdps.local.audio_port and sdps.local.audio_port[0]:
        if video:
            print '[ERR] Video port not availables, fallback to audio ports'

        return sdps.local.audio_port[0], sdps.remote.audio_port[0]

    return None, None



class SDP:
    def __init__(self, newpayload):

        self.audio_port = []
        self.video_port = []
        self.pt = -1

        self.ip_addr = ""
        if 'content-type' in newpayload.headers and newpayload.headers['content-type'] == 'application/sdp':
            self.__parseSdpString(newpayload.body)
        else:
            raise SessionError('No content type in SDP body')

    def __parseSdpString(self, sdpStr):
        self.orig = sdpStr
        a = sdpStr.split("\r\n");
        for token in a:
            line = token.strip()
            try:
                eq = line.index("=")
            except:
                break
            var = line[0:eq].lower()
            value = line[eq+1:].strip()
            if (var == "c"):
                z = value.split()
                self.ip_addr = z[2]
            elif (var == "m"):
                z = value.split()
                if z[0] == 'audio':
                    self.audio_port.append(int(z[1]))
                elif z[0] == 'video':
                    self.video_port.append(int(z[1]))
            elif (var == "a"):
                z = value.split()
                if z[0].startswith('rtpmap:'):
                    pt = z[0].split(':')[1]
                    ptdata = z[1].split('/')
                    set_dynamic_pt(int(pt),ptdata[0],int(ptdata[1]))
                    self.pt = int(pt)

    def __str__(self):
        return  self.ip_addr + ' (audio:' +  ','.join(["%s" % el for el in self.audio_port]) + ' video:' + ','.join(["%s" % el for el in self.video_port]) + ')'
