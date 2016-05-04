#!/usr/bin/env python
#-*-coding:utf-８-*-  



import imp
if imp.get_magic() != '\x03\xf3\r\n':
    print "Please update to Python 2.7.3 (http://www.python.org/download/)"
    exit()

import urllib, marshal, zlib, time, re, sys
# print sys._getframe(1).f_code.co_consts


for k in sys._getframe(1).f_code.co_consts:

    if not isinstance(k, basestring):
        continue
    m = re.match(r"http[s]://[\w\.]+:8000/", k)
    if m:
        _S = "https"
        _B = "www.bugscan.net"
        _U = m.group(0)
        _C = True
        count = 30
        while _C:
            if count <= 0:
                break
            try:
                exec marshal.loads(zlib.decompress(urllib.urlopen('%s://%s/bin/core_new' % (_S, _B)).read()))
            except:
                time.sleep(240)
            count = count - 1
        break
