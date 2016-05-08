#!/usr/bin/env python
#-*-coding:utf-８-*-  



from threading import Timer

def delayed(seconds):
    def decorator(f):
        def wrapper(*args, **kargs):
            t = Timer(seconds, f, args, kargs)
            t.start()
        return wrapper
    return decorator



delay=3


@delayed(delay)
def xiaorui():
    print "xiaorui.cc"





# for i in range(10):
xiaorui()
    


    