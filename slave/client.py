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
    '''
      当url在同一目录下的时候客户端用url的hash来去重,
      
      如果url没在同一目录下,就发送到server,server来重新发布任务  
      
      如果发现了子域名,也会交给server 处理  
      
      
    '''    
    def __init__(self,server_addr='127.0.0.1',server_port=6666,authkey=b'123456'):
    
        BaseManager.__init__(self,address=(server_addr,server_port), authkey=authkey)
        self.server_addr=server_addr
        self.server_port=server_port
        self.authkey=authkey 
# 由于这个QueueManager只从网络上获取Queue，所以注册时只提供名字:
        self.register('task_queue_n')
        self.register('response_queue_n')
        
        print'[INFO] Connect to server %s...' %(server_addr)
        try:
            self.connect()
        except Exception,e:
            print "[ERROR] Connect to server error , please confirm ip,port and authkey ..."
            exit(0)
                    
        self.task_queue = self.task_queue_n()
        self.response_queue = self.response_queue_n()
        self.Runable=True 
        
# 端口和验证码注意保持与task_master.py设置的完全一致


    def run(self):
        self.times=0   #尝试的次数 
        
        while self.Runable:
            try:
                if self.task_queue.empty()==False:
                
                    self.times=0 
                    domain=self.task_queue.get()
                    domain.printSelf()
                    
                else:
                    print "[INFO] I am waiting for task ..."
                    self.times+=1 
                    time.sleep(2)
                    if(self.times==5):   
                        self.Runable=False 
            except KeyboardInterrupt,e:
                
                print "[WARNING] User aborted, wait all slave threads to exit..."
                self.Runable=False 
                
            except Exception,e:
                print e 
                raise 
                    

if __name__=='__main__':
    
    m=client()
    # m.connect()
    m.run()
    