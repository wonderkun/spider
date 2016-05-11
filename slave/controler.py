#!/usr/bin/python 
#-*-coding:utf-8-*- 


import threading
import time 
import Queue

from domainRecorder import  *   


class controler(threading.Thread):
    def __init__(self,father=None,lock=None):
        threading.Thread.__init__(self)
        self.father=father
        self.alive=True
        self.lock=lock
    
    def __time(self):
        return time.strftime("%H:%M:%S",time.localtime(time.time()))
        
             
    def run(self):
        i=0 
        
        while self.alive:
            # print len(self.father.visited),len(self.father.pages)
            
                
            print "[%s] [INFO] I am controler!!"%(self.__time())
                        
            print "[%s] [INFO] visited:%d,unvisited:%s ..."%(self.__time(),len(self.father.visited),len(self.father.pages))
            if len(self.father.visited)==len(self.father.pages):
                if self.father.task_queue.qsize()==0 and self.father.wait_queue.qsize()==0:
                    i+=1
                    if i==3:
                        self.father.dead_all=True
                else:
                    i=0
            
            count=0
            
            for thread in self.father.threads:
                # self.lock.acquire()           #读取子进程获取的url到父进程中来
                if len(thread.pages)>0:
                
                    while  len(thread.pages)>0:   #如果pages中有数据
                        page=thread.pages.pop(0)  #从最前面开始删除
                        
                        if self.__judgePath(page):    
                            #如果是在同一域名下且是同一目录下 
                            if  self.father.in_pages(page):  #如果已经添加了
                                continue
                                
                            self.father.add_pages(page)
                            self.father.wait_queue.put(page) 
                        
                        else:  #如果不是,就添加到server的等待队列中去
                        
                            print "[%s] [INFO] %s is not in same directory or domain with master ..." %(self.__time(),page)
                            try:    
                                self.father.father.task_queue.put(page)
                            except Exception,e:
                                print e     
                                          
                else:
                    count=count+1
                    if count==len(self.father.threads): #说明所有的页面都没有返回 pages
                        time.sleep(3)
                        count=0                        
                    print "[%s] [WARNING]  %s is  not return pages ..."%(self.__time(),thread.name)
                # self.lock.release()
    def __judgePath(self,page):   #判断跟父线程发布的任务的域名关系和路径关系  
        
        domainTmp=domainRecorder(rootDomain=self.father.rootDomain)
        
        domainTmp.reInit(page)  #重新初始化 
         
        if domainTmp==self.father.domain:
            return True 
        return False 
                                                  
    def stop(self):
        if self.alive!=False:
            self.alive=False
            
