#!/usr/bin/python
#-*-coding:utf-8-*-

import  time
import sys
import Queue
from multiprocessing.managers import BaseManager
import random


from   domainRecorder import *
from HttpServer import *
from  DnsBrute import * 
import threading 
from threading import Timer 



class TaskManager(BaseManager):
    '''
       这个类的作用   
       1.控制开启子域名爆破模块,可以设置爆破子域名的线程数 
       2.在8000端口开启httpserver,供客户端连接,加载执行代码 
       3.基于BaseManager,在本地的6666端口,开启分布式结构,连接密码默认是123456
       ,在网络上注册task_queue 和response_queue,用于分布式节点之间的通讯 
       
       4.pushTask用于把response_queue队列中的任务加载到task_queue  
       
       
    '''
    
    def __init__(self,address='127.0.0.1',port=6666,authkey='',rootDomain='',digSubDomain=False,threads_num=1):
        BaseManager.__init__(self,(address,int(port)),authkey)
        task_queue_n=Queue.Queue()
        response_queue_n=Queue.Queue()
        
        # self.address=address
        self.port=port
        self.authkey=authkey
        self.register('task_queue_n',callable=lambda:task_queue_n)
        self.register('response_queue_n',callable=lambda:response_queue_n)

        self.digSubDomain=digSubDomain
        self.DnsThread=None 
        self.httpserverThread=None         
        self.START_FLAG=True     
        self.count=0   #访问错误计数
        self.delay=0  #延时时间 
        
        self.threads_num=threads_num #爆破子域名的线程数 
        self.domain=domainRecorder(rootDomain=rootDomain,domain=rootDomain,path='/',isSubDomain=True)
        
    
    def __time(self):   #格式化输出时间 
    
        return time.strftime("%H:%M:%S",time.localtime(time.time()))   
        
    def __digSubDomain(self):
        
        self.DnsBrute=DnsBrute(father=self,rootDomain=self.domain.rootDomain,threads_num=self.threads_num)
        self.DnsThread=threading.Thread(target=self.DnsBrute.run)
        self.DnsThread.setDaemon(True)
        self.DnsThread.start()
        
    def init__work(self):
    
        self.start()
        self.task_queue=self.task_queue_n()
        self.response_queue=self.response_queue_n()
        # self.task_queue.put(self.domain)
        
        if self.digSubDomain:  #开启子域名爆破模块 
           self.__digSubDomain()
        self.__start_httpserver()
        self.__print_self()
        
        self.response_queue.put(self.domain)
        
    def __print_self(self):
        
        print "[%s] [*] Http server starting on %s:%d  ..."%(self.__time(),self.address[0],8000)
        print "[%s] [*] Start Server on %s:%d  ..."%(self.__time(),self.address[0],self.port)
        print "[%s] [*] Server authkey is %s"%(self.__time(),self.authkey)
        print "[%s] [*] To get help information,please visite %s:%d"%(self.__time(),self.address[0],8000)
        print "\n"
        
    def __start_httpserver(self):
        
        self.httpserver=HttpServer
        self.httpserverThread=threading.Thread(target=self.httpserver)
        self.httpserverThread.setDaemon(True)
        self.httpserverThread.start()
              
    def __push_task(self):
        # time.sleep(self.delay)
        if self.response_queue.empty()==True:
            self.count+=1
            print "[%s] [INFO] I am delaying,  %ds..."%(self.__time(),self.delay)    
            return 
        # self.__printTaskQueue()  #打印出来任务队列 
        
        
        self.count=0    
        domain=self.response_queue.get()
        domain.printSelf()
        self.task_queue.put(domain)
        
        
    def  __printTaskQueue(self):
        lists=[]
        listdomain=[]
        
        while self.task_queue.empty()==False:
            lists.append(self.task_queue.get())
        # print type(lists)
        
        for i in lists:
            self.task_queue.put(i)
        
        for i in lists:
            listdomain.append(i.domain)
              
        print "[INFO] This is task_queue ",listdomain
                 
    def pushTask(self):
        self.count=0
        while self.START_FLAG:
            try:
                time.sleep(self.delay)
            except KeyboardInterrupt,e:
                self.START_FLAG=False
                if self.digSubDomain:
                    self.DnsBrute.STOP_ME=True     
                print "[%s] [WARNING] User aborted, wait all slave threads to exit..."%(self.__time())
                # 
                self.shutdown_work()
                
            else:
                  # 运行二进制指数退避算法   
                self.delay=random.randint(0,2**self.count)
                self.__push_task()
            # time.sleep(1)
            
    def  shutdown_work(self):
        self.shutdown()
        
              
if __name__=="__main__":

    from  argparse import  ArgumentParser
    p=ArgumentParser()
    p.add_argument('--port',default=6666,type=int,action="store",help="The port to start the server")
    p.add_argument('domain',type=str,action="store",help="The domain to craw")
    p.add_argument('--authkey',action='store',type=str,default=b'123456',help="The authkey to connect to the server")
    p.add_argument('-i',action="store_true",help="Whether to craw subdomain")
    p.add_argument('-T',action="store",type=int,default=10,help="The thread to burte subdomain")
    args=p.parse_args() 
    
    #start server 
            
    manager=TaskManager(authkey=args.authkey,rootDomain=args.domain,digSubDomain=args.i,port=args.port,threads_num=args.T)
# manager.start_work()
    manager.init__work()
    manager.pushTask()
    manager.shutdown_work()
    