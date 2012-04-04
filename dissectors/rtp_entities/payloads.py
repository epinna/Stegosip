# -*- coding: utf-8 -*-


payloads = {
0: ('PCMU' ,8000), #A [RFC3551]
1: ('Reserved', -1),
2: ('Reserved', -1),
3: ('GSM', 8000 ), #A [RFC3551]
4: ('G723', 8000), #A [RFC3551]
5: ('DVI4', 8000), #A                 [RFC3551]
6: ('DVI4', 16000), #A [RFC3551]
7: ('LPC', 8000), #A        [RFC3551]
8: ('PCMA', 8000), #A [RFC3551]
9: ('G722', 8000), #A [RFC3551]
10: ('L16',44100), #A [RFC3551] (2ch
11: ('L16', 44100), #A     [RFC3551]
12: ('QCELP', 8000), #[RFC3551]
13: ('CN',  8000), # A [RFC3389]
14: ('MPA',  90000), #A [RFC3551][RFC2250]
15: ('G728', 8000), #A [RFC3551]
16: ('DVI4',  11025), #A [DiPol]
17: ('DVI4', 22050), #A    [DiPol]
18: ('G729', 8000), #[RFC3551]
19: ('Reserved', -1), #        A
20: ('Unassigned', -1), #        A
21: ('Unassigned', -1), #        A
22: ('Unassigned', -1), #        A
23: ('Unassigned', -1), #        A
24: ('Unassigned', -1), #        V
25: ('CelB', 90000), #V    [RFC2029]
26: ('JPEG', 90000), #V   [RFC2435]
27: ('Unassigned', -1), #        V
28: ('nv', 90000), # V [RFC3551]
29: ('Unassigned', -1), #        V
30: ('Unassigned', -1), #        V
31: ('H261', 90000), # V [RFC4587]
32: ('MPV',  90000), # V [RFC2250]
33: ('MP2T',  90000), # AV   [RFC2250]
34: ('H263',  90000) #V   [Zhu]
#35-71     Unassigned      ?
#72-76     Reserved for RTCP conflict avoidance                                  [RFC3551]
#77-95     Unassigned      ?
#96-127    dynamic         ?                                                     [RFC3551]
}

def set_dynamic_pt(pt, name, freq):
    payloads[pt]  = (name, freq)

def get_pt_name(pt):
    if pt in payloads:
        return payloads[pt][0]
    else:
        return 'none'

def get_ts_usec(pt, ts):
    return ((ts / payloads[pt][1])*1000000) + (((ts % payloads[pt][1]) / (payloads[pt][1] / 8000))) * 125
