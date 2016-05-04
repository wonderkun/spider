#!/usr/bin/python 
#-*-coding:utf-8-*-


if __name__=='__main__':
    from master import *
    lock=threading.RLock()
    a=master(thread_size=10,domain='www.nwpu.edu.cn',lock=lock,tasks=['http://www.nwpu.edu.cn/info/1007/16445.htm'])
    
    a.begin()
    # print a