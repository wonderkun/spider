#!/usr/bin/python
#-*-coding:utf-8-*-

import  time
import sys
import Queue
from multiprocessing.managers import BaseManager
import random
from domainRecorder import *


from HttpServer import *
from  DnsBrute import * 
import threading 

        
class TaskManager(BaseManager):
    def __init__(self,address='127.0.0.1',port=6666,authkey='',rootDomain='',digSubDomain=False):
        BaseManager.__init__(self,(address,int(port)),authkey)
        task_queue_n=Queue.Queue()
        response_queue_n=Queue.Queue()
        
        # self.address=address
        self.port=port
        self.authkey=authkey
        self.register('task_queue_n',callable=lambda:task_queue_n)
        self.register('response_queue_n',callable=lambda:response_queue_n)
        self.domain=domainRecorder(rootDomain=rootDomain,domain="",path='/')
        self.digSubDomain=digSubDomain
        self.DnsThread=None 
        self.httpserverThread=None         
        self.START_FLAG=True
          
    def __digSubDomain(self):
        self.DnsBrute=DnsBrute(rootDomain=self.domain.rootDomain)
        self.DnsThread=threading.Thread(target=self.DnsBrute.run)
        self.DnsThread.setDaemon(True)
        self.DnsThread.start()
        
        
    def init__work(self):
        
        self.start()
        self.task_queue=self.task_queue_n()
        self.response_queue=self.response_queue_n()
        self.task_queue.put(self.domain)
        
        if self.digSubDomain:  #开启子域名爆破模块 
           self.__digSubDomain()
           
        self.__start_httpserver()
        
        self.__print_self()
        
        # self.domain.printSelf()
        
        
        # self.httpserver()  #开启webserver  
    
    
    def __print_self(self):
        print "[*] Http server starting on %s:%d  ..."%(self.address[0],8000)
        print "[*] Server authkey is %s"%(self.authkey)
        print "[*] To get help information,please visite %s:%d"%(self.address[0],8000)
                
        
    def __start_httpserver(self):
        
        self.httpserver=HttpServer
        self.httpserverThread=threading.Thread(target=self.httpserver)
        self.httpserverThread.setDaemon(True)
        self.httpserverThread.start()
             
             
                
    def pushTask(self):
        
        while True:        
            if(self.response_queue.empty()==False):
                domain=self.response_queue.get()
                print domain.getUrl()
                self.task_queue.put(domain)
            # time.sleep(1)
                
    def  shutdown_work(self):
        self.shutdown()
        

if __name__=="__main__":

    from  argparse import  ArgumentParser
    p=ArgumentParser()
    p.add_argument('--port',default=6666,type=int,action="store",help="The port to start the server")
    p.add_argument('domain',type=str,action="store",help="The domain to craw")

    p.add_argument('--authkey',action='store',type=str,default=b'123456',help="The authkey to connect to the server")
    p.add_argument('-i',action="store_true",help="Weather to craw subdomain")
    
    args=p.parse_args()         
    manager=TaskManager(authkey=args.authkey,rootDomain=args.domain,digSubDomain=args.i,port=args.port)
    
# manager.start_work()

    manager.init__work()
# manager.shutdown_work()

    manager.pushTask()
