import time 
import requets
import urlparse
import Queue
import threading
from bs4 import BeautifulSoup 

class worker(threading.Thread):
    '''
     从master中的task_queue中获取任务,
     在本地访问,解析html 
     获取匹配页面中的url,找到合法的,返回给master 
     
    '''
    def __init__(self, group=None, target=None, name=None, args=(),kwargs=None, verbose=None, father=None, lock=None, url=''):
        #  __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None) #父类的初始化函数 
        threading.Thread.__init__(self)
        self.name=name
        self.url=url
        self.father=father  #标记自己的父进程
        
        
        
  
        
 