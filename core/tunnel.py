# -*- coding: utf-8 -*-
import select, os, struct, time
from fcntl import ioctl
import thread
from core.options import conf, debug

TUNSETIFF = 0x400454ca
IFF_TUN   = 0x0001
IFF_TAP   = 0x0002

TUNMODE = IFF_TUN


class Tunnel:

    def __init__(self, sessionkey, tun_mtu):


        self.len_tunmtu = tun_mtu
        self.len_tunmtu_eth = tun_mtu + 4 # Ethernet

        self.bufferToInject = []

        self.tun_fd = os.open("/dev/net/tun", os.O_RDWR)
        ifs = ioctl(self.tun_fd, TUNSETIFF, struct.pack("16sH", "stego%d", TUNMODE))
        self.ifname = ifs[:16].strip("\x00")


        self.tun_ip = conf.get('global', 'tun_ip')
        self.tun_netmask = conf.get('global', 'tun_netmask')

        ifcommand = ['/sbin/ifconfig', self.ifname, 'up', self.tun_ip, 'netmask', self.tun_netmask, 'mtu', str(self.len_tunmtu)]
        os.system(' '.join(ifcommand))

        print '[TUN] Started Interface ' + ' '.join(ifcommand[1:])

        thread.start_new_thread(self.tunListener, (None,))
        self.keep_running = True
        self.is_stopped = False


    def getDataToInject(self):
        if self.bufferToInject:
            return self.bufferToInject.pop(0)


    def tunListener(self, dummy):

        del self.bufferToInject[:]

        while self.keep_running:
            r = select.select([self.tun_fd],[],[],1)[0]
            if r and r[0] == self.tun_fd:
                tosend = os.read(self.tun_fd, self.len_tunmtu_eth)
                if debug>1: print '[TUN] Read', len(tosend), 'byte from', self.ifname
                self.bufferToInject.append(tosend)

        self.is_stopped = True

    def tunWriter(self,data):
        if debug>1: print '[TUN] Write', len(data), 'byte to', self.ifname
        os.write(self.tun_fd, data)

    def stop(self):
        self.keep_running = False
        while not self.is_stopped:
            time.sleep(0.5)

        ifcommand = ['/sbin/ifconfig', self.ifname, 'down', self.tun_ip, 'netmask', self.tun_netmask, 'mtu', str(self.len_tunmtu)]
        os.system(' '.join(ifcommand))

        os.close(self.tun_fd)
        print '[TUN] Stopped interface', self.ifname, 'listener'


#def rc4crypt(data, key):
        #x = 0
        #box = range(256)
        #for i in range(256):
            #x = (x + box[i] + ord(key[i % len(key)])) % 256
            #box[i], box[x] = box[x], box[i]
        #x = 0
        #y = 0
        #out = []
        #for char in data:
            #x = (x + 1) % 256
            #y = (y + box[x]) % 256
            #box[x], box[y] = box[y], box[x]
            #out.append(chr(ord(char) ^ box[(box[x] + box[y]) % 256]))

        #return ''.join(out)
