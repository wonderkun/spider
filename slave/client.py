#!/usr/bin/python
#-*-coding:utf-8-*-

import  time
import sys
import Queue
from multiprocessing.managers import BaseManager
import random


from domainRecorder import *
from  master import *  


# task_worker.py



# 创建类似的QueueManager:
class client(BaseManager):
      
    
    def __time(self):
        return  time.strftime("%H:%M:%S",time.localtime(time.time()))
        
    def __init__(self,server_addr='127.0.0.1',server_port=6666,authkey=b'123456'):
    
        BaseManager.__init__(self,address=(server_addr,server_port), authkey=authkey)
        self.server_addr=server_addr
        self.server_port=server_port
        self.authkey=authkey 
# 由于这个QueueManager只从网络上获取Queue，所以注册时只提供名字:
        self.register('task_queue_n')
        self.register('response_queue_n')
        self.urls=[]
        self.__count=10
        
        print'[%s] [INFO] Connect to server %s...' %(self.__time(),server_addr)
        try:
            self.connect()
        except Exception,e:
            print "[%s] [ERROR] Connect to server error , please confirm ip,port and authkey ..."%(self.__time())
            exit(0)
            
        self.task_queue = self.task_queue_n()
        self.response_queue = self.response_queue_n()
         
        self.Runable=True 
        
# 端口和验证码注意保持与task_master.py设置的完全一致

    def __printResult(self):
        
        print "result".center(160,'+')
            
        for url in self.urls:
            print "URL:",url
                
    def run(self):
        self.times=0   #尝试的次数 
        
        while self.Runable:
            try:
                    
                if self.task_queue.empty()==False:
                    
                    self.times=0 
                    domain=self.task_queue.get()
                    domain.printSelf()
                    lock=threading.RLock()
                    a=master(father=self,thread_size=10,domain=domain,lock=lock)
                    a.begin()
                    while a.start_flag:  #当此结束之后,才可以获取下一个任务  
                        time.sleep(1) 
                        
                else:
                    print  "[%s] [INFO] I am waiting for task ..."%(self.__time())
                    self.times+=1 
                    time.sleep(2)
                    
                    if(self.times==self.__count):   
                        self.Runable=False 
            except KeyboardInterrupt,e:
                print "[%s] [WARNING] User aborted, wait all slave threads to exit..."%(self.__time())
                self.Runable=False 
                
            except Exception,e:
                print e 
                raise    
        
        self.__printResult()
        
        
if __name__=='__main__':
    
    m=client()
    # m.connect()
    m.run()
    