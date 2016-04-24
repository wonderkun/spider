#!/usr/bin/python
#-*-coding:utf-8-*-

import  time
import sys
import Queue
from multiprocessing.managers import BaseManager
import random
from domainRecorder import *


        
        
class TaskManager(BaseManager):
    def __init__(self,address='127.0.0.1',port=6666,authkey='',rootDomain='',digSubDomain=False):
        BaseManager.__init__(self,(address,int(port)),authkey)
        task_queue_n=Queue.Queue()
        response_queue_n=Queue.Queue()
        self.register('task_queue_n',callable=lambda:task_queue_n)
        self.register('response_queue_n',callable=lambda:response_queue_n)
        self.rootDomain=domainRecorder(domain=rootDomain,path='/')
        self.digSubDomain=digSubDomain
        
    def digSubDomain():
        pass 
        
        
            
    def start_work(self):
        self.start()
        self.task_queue=self.task_queue_n()
        self.response_queue=self.response_queue_n()
        
        self.task_queue.put(self.rootDomain)
        
        
        # for i in range(10):
        #     n=random.randint(0,1000000)
        #     print "Put task_queue"
        #     self.task_queue.put(n)
        
        print "Try to get result"
        
        for i in range(10):
            r=self.response_queue.get(timeout=10)
            print "Result:"+r
    def  shutdown_work(self):
        self.shutdown()
        
manager=TaskManager(authkey=b"12345",rootDomain="www.baidu.com")
manager.start_work()
# manager.shutdown_work()


