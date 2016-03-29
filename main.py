#!/usr/bin/python 
#-*-coding:utf-8-*-


if __name__=='__main__':
    from master import *
    lock=threading.RLock()
    a=master(thread_size=10,domain='yichin.url.ph',lock=lock,tasks=['http://yichin.url.ph/'])
    a.begin()
  