#!/usr/bin/python 
#-*-coding:utf-8-*-


import threading
import time 
import Queue 
from worker import *
from controler import *


class master(threading.Thread):
    '''
    这是clinet端的多线程任务管理类,负责多线程任务的分发和回收 
    
    类的作用:
         1.控制线程队列
         2.控制任务队列
         3.线程任务的分发和回收
         4.控制线程的个数
         
    '''
    
    def __init__(self,thread_size=0,task_num=5,domain="",lock=None,tasks=[]):
        threading.Thread.__init__(self)  #初始化父类
        self.visited=set()    #访问过的集合
        self.pages=set()     #采集到的页面
        self.threads=[]  #存储每个线程
        self.wait_queue=Queue.Queue()  #正在等待的任务组成的队列
        self.lock=lock #设置线程锁
        
        self.domain=domain #在这个域名范围内爬　
        
        # 为实现任务管理设置的标志位 
        
        self.start_flag = False
        self.is_running = False  
        self.finished_all = False
        self.dead_all = False
        
        self.thread_size=thread_size  #设置线程的个数 
        self.task_num=task_num  # 设置任务队列的大小,如果想让跑的快一点,可以在计算机性能允许的范围内,扩大线程数和任务队列的大小
        self.tasks=tasks  #从服务器端接收到的任务,可能不止一个,是多个起始url 
        self.controler=controler(father=self,lock=self.lock)
        
        try:
            self.task_queue=Queue.Queue(int(task_num))
        except:
            self.task_queue=Queue.Queue(5)  #默认是5
        self.__init_threads__()
        self.begin_time=time.time()
        
    def  __init_threads__(self):   #初始化线程,调用worker类,创建工作线程
        for i in range(self.thread_size):
            name="Thread %d"%(i)
            print name,"is start"
            substread=worker(father=self,lock=self.lock,name=name)
            substread.start()  #启动子进程
            self.threads.append(substread)
                        
    def begin(self):
        for task in self.tasks:
            self.wait_queue.put(task)
            self.pages.add(task)
            
        if self.is_running!=True:
            #启动标志位置位 
            self.start_flag=True
            self.is_running=True  
            self.start()
            self.controler.start()
            
    def run(self):
        #运行的主函数
        '''
        1.分配任务,
        2.保护任务队列
        
        标志位self.dead_all 和 self.finished_all  控制mater的结束,
            如果 都置位,说明任务结束,master也结束了  
            self.dead_all 是由子线程controler类来控制的 
                
        '''
        while self.start_flag:
            k=0
            for thread  in self.threads:
                if thread.start_flag==False: 
                    k+=1
            if k==len(self.threads):      #如果全部任务都完成了,或者还没有开始,会出现这种情况  
                if self.finished_all!=True:
                    self.finished_all=True 
            else:
                self.finished_all=False
                                                                 
            if self.task_queue.empty()==False:
                for thread in self.threads:
                    if thread.start_flag==False:
                        if self.task_queue.empty()==True:
                            continue                   #如果任务队列空了,并且线程处于结束状态,就什么也不干,否则就给这个线程分配任务 
                        self.lock.acquire()
                        tmp=self.task_queue.get()
                        self.pages.add(tmp)
                        self.lock.release()
                        thread.url=tmp
                        thread.start_flag=True    #标志位置位 
            else: 
                if self.wait_queue.qsize()<=0:  #任务队列空了并且等待队列也空了,很有可能是所有任务已经完成了 
                    pass 
                    
            while self.task_queue.full()!=True:   #如果任务队列没满,就从等待队列中拷入数据 
                if self.wait_queue.qsize()<=0:
                    # if self.task_queue.empty() == True: 
                    #     pass       
                    break
                self.lock.acquire()
                url_tmp=self.wait_queue.get()
                self.task_queue.put(url_tmp)
                self.lock.release()
                             
            if (self.finished_all==True) and (self.dead_all==True):
                print "result".center(197,'+')
                
                for i in self.pages:
                    print "URL:",i
                print time.time()-self.begin_time
                
                self.__stop()
                  
                                   
    def __stop(self):  #结束所有的子线程
        for thread in self.threads:
            thread.stop()
        self.controler.stop()          
        if self.start_flag!=False:
            self.start_flag=False
            
                                
    
        
