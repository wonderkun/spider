#!/usr/bin/python 
#-*-coding:utf-8-*-


import threading
import time 
import Queue 
from worker import *
from controler import *
try:
    import bsddb
except:
    print "import bsddb error!! Please install!"
import os
import hashlib

from domainRecorder import *  



class master(threading.Thread):
    '''
    这是clinet端的多线程任务管理类,负责多线程任务的分发和回收 
    
    类的作用:
         1.控制线程队列
         2.控制任务队列
         3.线程任务的分发和回收
         4.控制线程的个数
         
    '''
    
    def __init__(self,father=None,thread_size=0,domain=None,lock=None):
        threading.Thread.__init__(self)  #初始化父类
        self.visited=None    #访问过的集合
        self.pages=None     #采集到的页面
        self.threads=[]  #存储每个线程
        self.wait_queue=Queue.Queue()  #正在等待的任务组成的队列
        self.lock=lock #设置线程锁
        
        self.domain=domain #从服务器拿到的一个domainRecorder实例  
        
        # 为实现任务管理设置的标志位 
        
        self.start_flag = False
        self.is_running = False  
        self.finished_all = False
        self.dead_all = False
        
        self.thread_size=thread_size  #设置线程的个数 
        self.task_num=self.thread_size*2     # 设置任务队列的大小
        
        
        self.tasks=self.domain.getUrl()  #
        self.father=father   #便于向服务器传输数据  
        
        self.controler=controler(father=self,lock=self.lock)
        self.task_queue=Queue.Queue(self.task_num)
        self.__init_threads__()
        self.__init__bsddb__()
        self.begin_time=time.time()
        
        
    def __init__bsddb__(self):
        print "[INFO] Create the bsddb!!"
        print "[WARNING] Checking if the bsddb is exist"
        if os.path.exists("pages.db"):
            print "[INFO] Delete the exist  db!"
            os.remove("pages.db")
        if os.path.exists("visited.db"):
            print "[INFO] Delete the visited.db"
            os.remove("visited.db")
        try:
            self.pages=bsddb.btopen(file="pages.db",flag='c')
            self.visited=bsddb.btopen(file="visited.db",flag='c')
            print "[INFO] Create db success!!"
        except:
            print "[ERROR] Create db error!!"
                   
    def  __init_threads__(self):   #初始化线程,调用worker类,创建工作线程
        for i in range(self.thread_size):
            name="Thread %d"%(i)
            print "[INFO] %s is start"%(name)
            
            substread=worker(father=self,lock=self.lock,name=name)
            substread.start()  #启动子进程
            self.threads.append(substread)
                            
    def begin(self):
        # for task in self.tasks:
        self.wait_queue.put(task)
        self.add_pages(task)
            
        if self.is_running!=True:
            #启动标志位置位 
            self.start_flag=True
            self.is_running=True  
            self.start()
            self.controler.start()
    def check_url(self,url=""):
        if url!="":
            self.md5hash=hashlib.md5()
            self.md5hash.update(url)
            hash=self.md5hash.hexdigest()  #获取url的MD5值 
            if self.visited.has_key(hash)==1:  #浏览过了
                return 0
            elif self.visited.has_key(hash)!=1 and self.pages.has_key(hash)==1:  #在page中,但是还没有浏览过 
                return 1  #添加到任务队列中去了
            else:  
                #不在pages中的
                return 2
    def  in_visited(self,url=""):
        flag=self.check_url(url)
        if flag==0:
            return True
        else:
            return False
            
    def in_pages(self,url=""):
        flag=self.check_url(url)
        if flag==2:
            return False
        else:
            return True
    def add_visited(self,url=""):
        if url=="":
            return 0
        self.md5hash=hashlib.md5()
        self.md5hash.update(url)
        hash=self.md5hash.hexdigest()
        self.visited[hash]=url
        self.visited.sync()
    def add_pages(self,url=""):
        if url=="":
            return 0
        self.md5hash=hashlib.md5()
        self.md5hash.update(url)
        hash=self.md5hash.hexdigest()
        self.pages[hash]=url
        self.pages.sync()
         
    def run(self):
        #运行的主函数
        '''
        1.分配任务,
        2.保护任务队列
        标志位self.dead_all   控制mater的结束,  
        self.dead_all 是由子线程controler类来控制的 
            
        '''
        while self.start_flag:
            print "\033[49;34mI am master!!\033[0m"
             
            k=0
            for thread  in self.threads:
                if thread.start_flag==False:
                    k+=1
                    
            if k==len(self.threads):      #如果全部任务都完成了,或者还没有开始,会出现这种情况  
                if self.finished_all!=True:
                    self.finished_all=True 
            else:
                self.finished_all=False
                                                    
            while self.task_queue.full()!=True:   #如果任务队列没满,就从等待队列中拷入数据
                if self.wait_queue.qsize()<=0:
                    print "[*] wait_queue is empty!!"
                    time.sleep(0.8)       
                    break
                url_tmp=self.wait_queue.get()
                self.task_queue.put(url_tmp)
            else:
                print "[INFO] Task_queue is full,I am waiting ..."
                time.sleep(0.8)
                                            
            if (self.finished_all==True) and (self.dead_all==True):
                
                print "result".center(197,'+')
                for i in self.pages:
                    print "URL:",self.pages[i]
                                        
                print time.time()-self.begin_time
                self.__stop()  
                                   
    def __stop(self):  #结束所有的子线程
        for thread in self.threads:
            thread.stop()
        self.controler.stop()          
        if self.start_flag!=False:
            self.start_flag=False
        self.pages.close()
        self.visited.close()
        