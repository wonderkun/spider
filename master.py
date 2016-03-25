#!/usr/bin/python 
#-*-coding:utf-8-*-



import threading
import time 
import Queue 

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
        self.lock=lock   #设置线程锁
        
        # 为实现任务管理设置的标志位 
        
        self.start_flag = False
		self.is_running = False  
		self.finished_all = False
		self.dead_all = False
        
        self.thread_size=thread_size  #设置线程的个数 
        self.task_num=task_num  # 设置任务队列的大小,如果想让跑的快一点,可以在计算机性能允许的范围内,扩大线程数和任务队列的大小
        self.tasks=tasks  #从服务器端接收到的任务,可能不止一个,是多个起始url
        
        self.__init__threads__()  #调用线程初始化函数 
        try:
            self.task_queue=Queue.Queue(int(task_num))
        except:
            self.task_queue=Queue.Queue(5)  #默认是5
        
        def begin(self):
            for task in tasks:
                self.wait_queue.put(task)
            if self.is_running!=True:
                self.start_flag=True
                self.start()
        def run(self):
            #运行的主函数
            '''
            1.分配任务,
            2.保护任务队列
            '''
            while self.start_flag:
                
       
        def __init__threads__(self):   #初始化线程,调用worker类,创建工作线程
            for i in range(thread_size):
                name="Thread %d"%(i)
                substread=worker(father=self,lock=lock,name=name)
                substread.start()  #启动子进程
                self.threads.append(substread)
        
                
            
                    
                
                

print master.__doc__

