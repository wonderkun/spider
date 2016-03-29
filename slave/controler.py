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
        count=0
        while self.alive:
            print len(self.father.visited),len(self.father.pages)
            if len(self.father.visited)==len(self.father.pages):
                if self.father.task_queue.qsize()==0 and self.father.wait_queue.qsize()==0:
                    i+=1
                    if i==3:
                        self.father.dead_all=True
                else:
                    i=0
                        
            print "[*] I am controler!!"
            
            for thread in self.father.threads:
                # self.lock.acquire()           #读取子进程获取的url到父进程中来
                while  len(thread.pages)>0:   #如果pages中有数据
                    page=thread.pages.pop(0)  #从最前面开始删除
                    if  self.father.in_pages(page):  #
                        continue
                    self.father.add_pages(page)
                    self.father.wait_queue.put(page)                       
                else:
                    count=count+1
                    if count==len(self.father.threads): #说明所有的页面都没有返回 pages
                        time.sleep(3)
                        count=0
                    print "[*] "+thread.name+ " not return pages"
                # self.lock.release()
                                     
    def stop(self):
        if self.alive!=False:
            self.alive=False
            
