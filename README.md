Stegosip
========

This software was part of the dissertation that I presented the 04/07/2011 for the master degree in computer engineering under the title “Steganography over SIP/RTP protocols”. The work was conducted under the supervision of professor Luigi Ciminiera at the Politecnico di Torino.

StegoSIP covers an IP tunnel into SIP/RTP protocol using LSB and LACK steganographic methods. The hidden channel is a point-to-point IP tunnel between the two peers communicating via the SIP call.

Install
-------

Install the required dependencies.

```bash
$ sudo apt-get install nfqueue-bindings-python python-dpkt
```

Download StegoSIP in both endpoints PC-Alice and PC-Bob. Make sure to specify the tunnel IP addresses of the two endpoints as shown below.

```bash
# On PC-Alice
$ gedit stegosip.conf        # set Alice IP option address as 10.0.0.1
```

```bash
# On PC-Bob
$ gedit stegosip.conf          # set Bob IP address as 10.0.0.2
```

Usage
-----

Start StegoSIP in Alice and Bob hosts

```bash
# On PC-Alice
$ sudo ./stegosip.py
```

```bash
# On PC-Bob
$ sudo ./stegosip.py
```

StegoSIP starts inspecting the SIP traffic on the machines waiting for inbound or outbound SIP calls. When it detects a RTP stream, it would raise a stego0 network interface in both endpoints which can be used as a private hidden network between the peers.

Example
-------

The software is SIP client agnostic, but has been tested with Ekiga. Find below a commented example of an outgoing call from PC-Alice to PC-Bob which is used to establish the covert channel.

```bash
# PC-Alice. 
# The command must be run on PC-Bob as well.
$ sudo ./stegosip.py

# Load filter to incercept incoming and outgoing SIP calls
[SIP] added dissector and netfilter rules on udp 5060 ports.
# Outgoing-call between alice and bob intercepted 
[SIP] [OUTGOING-CALL:647604] alice@192.168.1.3->bob@192.168.1.4 
[SIP] [OUTGOING-CALL-ESTAB:647604] alice@192.168.1.3->bob@192.168.1.4 
# Extract RTP port and other parameters from collected SDP
[SDP] local: 192.168.1.3:5072 remote:192.168.1.4:5076 
# Load filter to intercept RTP connection
[RTP] added dissector and netfilter rules on udp 5072<->5076 ports.
# Starting stego0 interface with ip 10.0.0.1
[TUN] Started Interface stego0 up 10.0.0.1 netmask 255.255.255.0 mtu 1392
# Module to inject and extract data from tunnel loaded.
[RTP] Injector 'LACK' module loaded
```

Alice and Bob can now communicate using 10.0.0.1 and 10.0.0.2 hosts.

```bash
# PC-Alice
$ ping 10.0.0.2

PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_req=1 ttl=64 time=50.1 ms
64 bytes from 10.0.0.2: icmp_req=2 ttl=64 time=58.7 ms
...
```