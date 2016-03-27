#!/usr/bin/python 
#-*-coding:utf-8-*- 


import threading
import time 
import Queue 

class controler(threading.Thread):
    def __init__(self,father=None,lock=None):
        threading.Thread.__init__(self)
        self.father=father
        self.alive=True
        self.lock=lock
    def run(self):
        i=0
        while self.alive:
            for thread in self.father.threads:
                self.lock.acquire()           #读取子进程获取的url到父进程中来
                while  len(thread.pages)>0:   #如果pages中有数据
                    page=thread.pages.pop(0)  #从最前面开始删除
                    if page in self.father.pages:
                        continue
                    self.father.pages.add(page)
                    self.father.wait_queue.put(page)                       
                self.lock.release()
                
            if len(self.father.visited)==len(self.father.pages):
                if self.father.task_queue.qsize()==0 and self.father.wait_queue.qsize()==0:
                    i+=1
                    if i==3:
                        self.father.dead_all=True
                continue 
            i=0
                            
    def stop(self):
        if self.alive!=False:
            self.alive=False
            

        
        
        

