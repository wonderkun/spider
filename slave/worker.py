#!/usr/bin/python 
#-*-coding:utf-8-*-


import time 
import requests
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
                print "\033[49;35m[{time}] [WARNING] {name} Get url failed!!\033[0m".format(time=self.__time(),name=self.name)
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
                
                print "[%s] [INFO] %s finished url:%s,spend time:%s",(self.__time(),self.name,self.url,time.time()-time1)
                
                self.pages+=self.temp_pages  #把url放入pages中去,父进程从pages中取走数据                
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
                response=requests.get(url,headers=header,timeout=3)
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
            except:
                # print self.name+url,"Maybe not have href"
                continue
            
            res=urlparse.urlparse(ret)
            ret=urlparse.urlunparse((res[0],res[1],res[2],res[3],res[4],'')) #为了删除url中的锚点
            res=urlparse.urlparse(ret)   
            #修正url 
            if res[0] is '' and res[1] is '':   #如果没有协议和域名,就是相对于当前目录的相对地址 
                url_split=urlparse.urlparse(url)
                ret=url_split[0]+"://"+url_split[1]+url_split[2]+ret 
                ret=ret[:8]+ret[8:].replace("//",'/')  #把url中的//变为/
                res=urlparse.urlparse(ret)
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
            if self.father.domain.rootDomain not in  res[1]:  #没有对子域名进行过滤
                # print "bad url "+ret
                continue
            #对文件进行过滤,删除 图片 音频 视频 文档 等
            ext=res[2]
            if ext[ext.rfind('.')+1:ext.rfind('.')+4] in self.ignore:  #获取扩展名
                continue
                                                                
            newpage=ret
            newpage_flag=False
            self.lock.acquire()
            
            if (newpage not in self.pages) and (newpage not in self.temp_pages):
                # print "find new page :"+newpage
                print "[%s] [INFO] %s find new page:%s"%(self.__time(),self.name,newpage)
                
                self.temp_pages.append(newpage)   #子进程把数据放在列表的最后,父进程从列表的最前面开始取走
                newpage_flag=True
            else:
                pass 
                
            self.lock.release()
            
    def stop(self):
        if self.is_runable!=False:
            self.is_runable=False
            
            