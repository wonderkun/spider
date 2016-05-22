#!/usr/bin/python 
#-*-coding:utf-8-*-



import threading
import time 
import Queue 
import sys 
import random 
from multiprocessing.managers import BaseManager


try:
    import bsddb
except:
    print "[ERROR] import bsddb error!! Please install ..."
    
import os
import hashlib 
import requests
from  urllib import quote   
import urlparse
import threading
from bs4 import BeautifulSoup 

class worker(threading.Thread):
    '''
     从master中的task_queue中获取任务,
     在本地访问,解析html 
     获取匹配页面中的url,找到合法的,返回给master 
     
    '''
    
    def __init__(self, group=None, target=None, name=None, args=(),kwargs=None, verbose=None, father=None, lock=None):
        #  __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None) #父类的初始化函数 
        threading.Thread.__init__(self)
        self.name=name  #自己的名字 
        self.url=''
        self.father=father  #标记自己的父进程
        self.lock=lock
        self.pages=[]  #解析页面之后,获得的链接 
        self.temp_pages=[] #用来临时保存数据
        #为了让父进程识别自己,设置的一些标志位  
        self.start_flag = False
        self.finished_flag = False
        # self.blocked_flag = False
        self.is_runable=True 
        # self.ignore=['png','jpg','bmp','gif','jpeg','ico','doc','ppt','pdf','xls','avi','flv','mp3','mp4','rmvb','wav','wmv','wav']  #此类文件不进行解析 
        self.ignore=[]
    
    def run(self):
    
        while self.is_runable:
            print "[%s] [INFO] %s is  running ..."%(self.__time(),self.name)
            
            try:
                self.url=self.father.task_queue.get(block=True,timeout=3)
            except Exception as e:
                self.url=""
                                
            if self.url=="":       #如果说自己没有获得url 
                print "\033[49;35m[%s] [WARNING] %s Get url failed!!\033[0m"%(self.__time(),self.name)
                continue 
            else:
                # self.start_flag=True
                # if self.father.in_visited(self.url): #如果自己分配的url已经被其他进程访问过了 
                #     print self.name+" is blocked!"
                #     self.start_flag=False  #把自己阻塞起来
                #     self.blocked_flag=True  #设阻塞的标志位  
                # else:
                # print self.name,"get url:"+self.url
                time1=time.time()
                self.get_url(url=self.url)  #调用函数,把这个页面的数据存储到self.temp_pages中去
                
                print "[%s] [INFO] %s finished url:%s , spend time:%s"%(self.__time(),self.name,self.url,time.time()-time1)
                
                self.pages+=self.temp_pages  #把url放入pages中去,父进程从pages中取走数据                
                print "[%s] [INFO] %s find new page:%s ..."%(self.__time(),self.name,(',').join([x for x in self.temp_pages])[:100])
                self.temp_pages=[]  #清空临时表 
                self.father.add_visited(self.url)
                #每次完成一个任务,这两个标志位置位                    
                self.start_flag=False
                self.finished_flag=True
                
                
    def __time(self):
        return  time.strftime("%H:%M:%S",time.localtime(time.time()))
    
    def get_url(self,url=''):
        if url=='':
            return 
        domain=self.father.domain
        repeat_time=0
        pages=set()  #存储获得的url 
        newpage_flag=False 
        
        data=""
        header={"Referer":domain,"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36",
               "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp","Accept-Encoding":"*"}
        
        while True:
            try:
                response=requests.get(url,headers=header,timeout=5)
            except:
                # print url,"open failed!!"
                repeat_time+=1
                if repeat_time==3:
                    return
            try:
                data=response.text
                break
            except:
                return
                          
        soup=BeautifulSoup(data,'lxml')
        tags=soup.findAll(name='a')
        for tag in tags:
            try:
                ret=tag['href']
            except Exception,e:
                # print self.name+url,"Maybe not have href"
                continue
            
            res=urlparse.urlparse(ret)
            
            try:
                ret=urlparse.urlunparse((res[0],res[1],quote(res[2]),res[3],res[4],'')) #为了删除url中的锚点
            except KeyError,e:
                ret=urlparse.urlunparse((res[0],res[1],quote(res[2].encode('utf-8')),res[3],res[4],''))
                
            res=urlparse.urlparse(ret)
            #修正url
            
            if res[0] is '' and res[1] is '':   #如果没有协议和域名,就是相对于当前目录的相对地址 
                
                
                url_split=urlparse.urlparse(url)
                #url除去文件名,仅仅留下目录名,就ok了 
                
                
                path=url_split[2]
                path=path.split('/')
                
                if path[-1]=="":
                    maybeFile=path[-2]
                    removeNum=-2
                    
                else:
                    maybeFile=path[-1]
                    removeNum=-1
                
                if "." in maybeFile:
                    #说明最后一个是文件名  
                    # print removeNum
                    path[removeNum]=""        
                    path=('/').join(path)
                    
                else:
                    path=('/').join(path)
                
                while "//" in path: 
                    path=path.replace("//",'/')  #把url中的//变为/
                
                path=path.rstrip('/')+'/'  #确保url使用/结尾的  
                
                
                ret=url_split[0]+"://"+url_split[1]+path+ret 
                
                ret=ret[:8]+ret[8:].replace("//",'/')  #把url中的//变为/
                res=urlparse.urlparse(ret)
                
                paths=res[2].split('/')
                
                #防止url出现  http://test.com/./test.html
                for i in range(len(paths)):
                    if '.'==paths[i]:
                        paths[i]=""
                    
                temp_path=''
                
                for path in paths:
                    if path=='':
                        continue
                    temp_path=temp_path+"/"+path
                
                ret=ret.replace(res[2],temp_path)
                res=urlparse.urlparse(ret)  #重新分解
                
                
                #  防止 http://domain/dir/../dir/   出现在url中    
                
                if "../" in res[2]:
                    paths=res[2].split('/')
                    for i in range(len(paths)):
                            
                        if ".."  in  paths[i]:     
                            paths[i]=""
                            t=i
                            while t>-1:
                                if paths[t] =="":
                                    t-=1
                                else:
                                    paths[t]=""    
                                    break                                      
                    temp_path=''
                    
                    for path in paths:
                        if path=='':
                            continue
                        temp_path=temp_path+"/"+path
                    
                    ret=ret.replace(res[2],temp_path)  #替换掉原来中的错误部分 
                res=urlparse.urlparse(ret)  #重新分解            
                
                    #对协议进行过滤　
            
            
            if  'http' not in res[0]:
                # print "bad url "+ret
                continue 
            #对url合理性性进行检测
            
            if res[0] is "" and res[1] is not "":
                # print "bad url "+ret
                continue 
               #对域名进性检查   
            if self.father.domain.rootDomain not in  res[1]:      #没有对子域名进行过滤,过滤放在controller 中进行  
                # print "bad url "+ret
                continue
            #对文件进行过滤,删除 图片 音频 视频 文档 等
            ext=res[2]
            
            if ext[ext.rfind('.')+1:ext.rfind('.')+4] in self.ignore:  #获取扩展名
                continue
                                                                
            newpage=ret
            
            # print "$"*15,newpage
            
            newpage_flag=False 
            
            if (newpage not in self.pages) and (newpage not in self.temp_pages):
                # print "@"*100,"find new page :"+newpage
                
                self.temp_pages.append(newpage)   #子进程把数据放在列表的最后,父进程从列表的最前面开始取走
                newpage_flag=True
            else:                
                pass 
            
            
            
            
            
    def stop(self):
        if self.is_runable!=False:
            self.is_runable=False
            

class domainRecorder():

    '''
        用来记录域名,判断子域名的可用性,
        记录在同一个域名下的路径 
        记录子域名的个数 
        
    '''
    def __time(self):
        return time.strftime("%H:%M:%S",time.localtime(time.time())) 
        
    def __init__(self,scheme="http",rootDomain='',domain='',path='/',isSubDomain=False):
        
        
        self.rootDomain=rootDomain.strip()
        self.domain=domain.strip() if domain else rootDomain.strip()
        self.path=path.strip()
        self.scheme=scheme.strip()
        self.count=0
        self.isSubDomain=isSubDomain
        
        self.url=self.path    #self.url 跟self.path是不一样的,
            
        if self.isSubDomain:
            self.__GetStatus()
        
        
    def __GetStatus(self):
           
        url=self.getUrl()
        
        try:
            response=requests.get(url)
        except requests.exceptions.ConnectionError,e:       #说明这是一个顶级域名
                                
            self.domain="www."+self.domain

    def printSelf(self):
    
        if self.isSubDomain:  #获取了subdomain 
            print "[%s] [INFO] Get  subdomain:[%s],RootDomain:[%s],Num:[%d]"%(self.__time(),self.domain,self.rootDomain,self.count)
        else:
            print "[%s] [INFO] Get path:[%s],in subdomain:[%s],in RootDomain:[%s],Num:[%d]"%(self.__time(),self.path,self.domain,self.rootDomain,self.count)
            
    def judgeDomain(self):  #判断是否是一个子域名 
        
        domain_list=self.domain.split('.')
        rootDomain_list=self.rootDomain.split('.')
        # print domain_list
        domain_len=len(domain_list)
        rootDomain_len=len(rootDomain_list)
        
        if domain_len>rootDomain_len:  #判断是否是一个子域名
            domain='.'.join([domain_list[i] for i in range(domain_len-rootDomain_len,domain_len)])
            if domain!=self.rootDomain:
                return False        
        if domain_len==rootDomain_len:
            if self.domain!=self.rootDomain:
                return False
        return True


    def __eq__(self,other):    #重载== 号运算符,判断两个url是否是在同一个目录下,简单的,就判定了一级目录  
        
        if (self.path=='/') or (other.path=='/'):      # 如果任意一个url是根目录,就返回false
            if (self.path!="/") or (other.path!='/'):
                
                return False
                        
        if self.domain==other.domain:
            path1=[]
            path2=[] 
            
            path_tmp1=self.path.split('/')
            
            for i in path_tmp1:
                if 1!='':
                    path1.append(i)
            path_tmp2=other.path.split('/')
            
            for i in path_tmp2:
                if 1!='':
                    path2.append(i)
            if path1[0]==path2[0]:
                return True     
        return False
        
    
    def getPath(self):
        
        path=urlparse.urljoin(self.scheme+"://"+self.domain,self.path)
        
        return path.rstrip('/')+'/'
        
        
    def  getUrl(self):  #返回此条记录的url
         
        url=urlparse.urljoin(self.scheme+"://"+self.domain,self.url)
        
        #如果是路径,就要保证最后一定是用/ 结尾 
        
        path=self.url.split('/')
        
        if path[-1]=="":
            maybeFile=path[-2]
        else:
            maybeFile=path[-1]
                
        if "." not in maybeFile:  #表明是一个路径
            #说明最后一个是文件名  
        #     # print removeNum
              
            url=url.rstrip('/')+"/"  #必须用/结尾  
        else:
            url=url.rstrip('/')
            
        return url  
        
    # def getPath
    
    
    def reInit(self,url): #用一个url来重新初始化此类  
        
        self.url=url
        
        url=urlparse.urlparse(url)
        removeNum=-1 
        self.scheme=url.scheme
        self.domain=url.netloc 
        
        # if self.rootDomain!=self.domain:
            
        #     self.isSubDomain=True  
        
        path=url.path
        if path=="":
            path="/"
        path=path.split('/')
        
        if path[-1]=="":
            maybeFile=path[-2]
            removeNum=-2
        else:
            maybeFile=path[-1]
            removeNum=-1
            
        if "." in maybeFile:
            #说明最后一个是文件名  
            # print removeNum
            path[removeNum]=""        
            self.path=('/').join(path)
            
        else:
            self.path=('/').join(path)
            
        while "//" in self.path: 
            self.path=self.path.replace("//",'/')  #把url中的//变为/

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
            
            print "[%s] [INFO] visited:%d,all:%s ..."%(self.__time(),len(self.father.visited),len(self.father.pages))
            
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
                        
                        
                        domainTmp=domainRecorder(rootDomain=self.father.rootDomain,isSubDomain=False)
                        domainTmp.reInit(page)
                        
                        
                        if self.__judgePath(page):
                            #如果是在同一域名下且是同一目录下 
                            
                            if  self.father.in_pages(page):  #如果已经添加了
                                continue
                            
                            self.father.add_pages(page)
                            self.father.wait_queue.put(page) 
                        
                        else: 
                            
                            
                           #如果没有在当前目录下
                            if domainTmp.getPath()   in   self.father.paths:  #如果获得过这个任务  
                               
                               if self.father.in_pages(page):
                                    continue
                               
                               self.father.add_pages(page)
                               self.father.wait_queue.put(page)
                               
                            else:  #如果不是,就添加到server的等待队列中去
                                
                                print "[%s] [INFO] %s is not in same directory or domain with master ..." %(self.__time(),page)
                                
                                try:    
                                    
                                    # print "$"*100
                                    # domainTmp.printSelf()
                                    self.father.server_response_queue.put(domainTmp)
                                    
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
            

class master(threading.Thread,BaseManager):  #多重继承  
    '''
      连接服务器模块 
      
      当url在同一目录下的时候客户端用url的hash来去重,
      如果url没在同一目录下,就发送到server,server来重新发布任务  
      如果发现了子域名,也会交给server 处理  
      
      
    
    这是clinet端的多线程任务管理类,负责多线程任务的分发和回收 
         1.控制线程队列
         2.控制任务队列
         3.线程任务的分发和回收
         4.控制线程的个数
         
    '''
    
    def __init__(self,thread_size=0,server_addr='127.0.0.1',server_port=6666,authkey=b'123456',lock=None,count=10):
        threading.Thread.__init__(self)  #初始化父类
        BaseManager.__init__(self,address=(server_addr,server_port), authkey=authkey)
        
        self.visited=None    #访问过的集合
        self.pages=None     #采集到的页面
        self.threads=[]  #存储每个线程
        self.wait_queue=Queue.Queue()  #正在等待的任务组成的队列
        self.lock=lock #设置线程锁
        
        # 为实现任务管理设置的标志位 
        
        self.start_flag = False
        self.is_running = False  
        self.finished_all = False
        self.dead_all = False
        
        self.Runable=True  # 
        
        self.thread_size=thread_size  #设置线程的个数 
        self.task_num=self.thread_size*2     # 设置任务队列的大小
        
        
        '''
        初始化服务器连接模块  
        
        '''
        self.server_addr=server_addr
        self.server_port=server_port
        self.authkey=authkey
        self.register('task_queue_n')
        self.register('response_queue_n')
        self.__count=count #尝试连接服务器的次数  
        
        print'[%s] [INFO] Connect to server %s...' %(self.__time(),server_addr)
        
        try:
            self.connect()
        except Exception,e:
            print "[%s] [ERROR] Connect to server error , please confirm ip,port and authkey ..."%(self.__time())
            exit(0)
        
        self.server_task_queue=self.task_queue_n()  #server 的任务队列 
        self.server_response_queue=self.response_queue_n()  #server 的返回队列 
        
        
        
        self.controler=controler(father=self,lock=self.lock)
        self.task_queue=Queue.Queue(self.task_num)
        self.__init_threads__()
        self.__init__bsddb__()
        self.begin_time=time.time()
        self.times=0
        
        # 本地需要记录自己的获得过的任务  
        
        self.paths=[]
        
        
    def __printResult(self):
     
        print "result".center(160,'+')
        for i in self.pages:
            print "URL:%s"%(self.pages[i])
        
        print "[%s] [INFO] Spend time %d ..."%(self.__time(),time.time()-self.begin_time)
        print  "[%s] [INFO] Get count:%s ..."%(self.__time(),len(self.pages))
        
        #关闭数据库对象 
        
        self.pages.close()
        self.visited.close()
        
            
    def __init__bsddb__(self):
        print "[%s] [INFO] Create the bsddb ..."%(self.__time())
        print "[%s] [WARNING] Checking if the bsddb is exist"%(self.__time())
        if os.path.exists("pages.db"):
            # print "[%s] [INFO] Delete the exist  db ..."%(self.__time())
            os.remove("pages.db")
        if os.path.exists("visited.db"):
            # print "[%s] [INFO] Delete the visited.db ..."%(self.__time())
            os.remove("visited.db")
        try:
            
            self.pages=bsddb.btopen(file="pages.db",flag='c')
            self.visited=bsddb.btopen(file="visited.db",flag='c')
            
            print "[%s] [INFO] Create db success ..."%(self.__time())
        except:
            print "[%s] [ERROR] Create db error ..."%(self.__time())
                   
                   
    def  __init_threads__(self):   #初始化线程,调用worker类,创建工作线程
        for i in range(self.thread_size):
            name="Thread %d"%(i)
            print "[%s] [INFO] %s is start"%(self.__time(),name)
            
            substread=worker(father=self,lock=self.lock,name=name)
            substread.setDaemon(True)  #设置为伴随进程
            substread.start()
            
             
            self.threads.append(substread)
    
    def __time(self):
        return  time.strftime("%H:%M:%S",time.localtime(time.time()))
    
    def begin(self):
        # for task in self.tasks:
            
        if self.is_running!=True:
            #启动标志位置位 
            self.start_flag=True
            self.is_running=True  
            self.start()
            self.controler.setDaemon(True)
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
        # print url
          
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
        
        while self.Runable:
            
            try:
                
                if self.server_task_queue.empty()==False:
                    
                    self.times=0
                    self.domain=self.server_task_queue.get()
                    self.domain.printSelf()
                    self.rootDomain=self.domain.rootDomain
                    self.paths.append(self.domain.getPath())    #把得到的任务,做一个记录
                    
                    
                    #domainRecorder 的 url 需要保存到任务队列,当path和url不一样的时候,也需要保存到任务队列中去
                    
                    if self.domain.getUrl()!=self.domain.getPath():
                        self.task=self.domain.getPath()
                        self.wait_queue.put(self.task)
                        self.add_pages(self.task)                                                                      
                                            
                    self.task=self.domain.getUrl()  #
                    self.wait_queue.put(self.task)
                    self.add_pages(self.task)
                    
                    # if self.domain.getPath()!=self.domain.getUrl():
                    #     self.task=self.domain.getPath()
                    #     self.wait_queue.put(self.task)
                    
                    self.start_flag=True 
                
                else:
                     print  "[%s] [INFO] I am waiting for task ..."%(self.__time())
                     self.times+=1
                     time.sleep(2)
                     self.start_flag=False
                     if(self.times==self.__count):
                        self.Runable=False  
                           
                           
                           
            except KeyboardInterrupt,e:
                print "[%s] [WARNING] User aborted, wait all slave threads to exit..."%(self.__time())
                self.Runable=False 
                
                     
            while self.start_flag:
                
                print "[%s] [INFO] I am master , I am running .... "%(self.__time())
                
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
                        print "[%s] [INFO] Wait_queue is empty ..."%(self.__time())
                        time.sleep(0.8)       
                        break
                    url_tmp=self.wait_queue.get()
                    self.task_queue.put(url_tmp)
                else:
                    print "[%s] [INFO] Task_queue is full,I am waiting ..."%(self.__time())
                    time.sleep(0.8)
                if (self.finished_all==True) and (self.dead_all==True):                  
                    if self.start_flag!=False:
                        self.start_flag=False
        
        
        self.__stop()
        
        # time.sleep(5)
       
        time.sleep(2)
        # if (self.finished_all==True) and (self.dead_all==True):
        self.__printResult()
        
        
    def __stop(self):  #结束所有的子线程
        
        for thread in self.threads:
            thread.stop()
            thread.join()
            
        self.controler.stop()          
        self.controler.join()
        
        if self.start_flag!=False:
            self.start_flag=False
        
        
if __name__=="__main__":
    
    a=master(thread_size=10,count=10,server_addr='192.168.191.2')
    a.begin()
    
    