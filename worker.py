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
    def __init__(self, group=None, target=None, name=None, args=(),kwargs=None, verbose=None, father=None, lock=None, url=''):
        #  __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None) #父类的初始化函数 
        threading.Thread.__init__(self)
        self.name=name  #自己的名字 
        
        self.url=url
        self.father=father  #标记自己的父进程
        self.lock=lock
        
        self.pages=[]  #解析页面之后,获得的链接  
        
        #为了让父进程识别自己,设置的一些标志位  
        self.start_flag = False
        self.finished_flag = False
        self.blocked_flag = False
        self.is_runable=True 
    def run(self):
        while self.is_runable:
            self.start_flag=True
            if self.url="":             #如果说自己没有获得url 
                self.start_flag=False
                continue 
            else:
                if self.url in self.father.visited: #如果自己分配的url已经被其他进程访问过了 
                    print self.name+"is blocked!"
                     
                    self.start_flag=False  #把自己阻塞起来
                    self.blocked_flag=True  #设阻塞的标志位  
                else:
                    print self.name + "get url:"+self.url 
                    self.blocked_flag=False
                    self.pages=self.get_url(url=self.url)
                    self.father.visited.add(self.url)
                    self.start_flag=False
                    self.finished_flag=True
                    
    def get_url(self,url=''):
        if　 url='':
            return []
        domain=self.father.domain
        repeat_time=0
        pages=set()  #存储获得的url 
        newpage_flag=False 
        
        data=""
        header={"Referer":url,"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36"}
        while True:
            try:
                response=requests.get(url,headers=header,timeout=3)
            except:
                repeat_time+=1
                if repeat_time=3:
                    return []
       
            try:
                data=response.text
                break
            except:
                return []
                          
        soup=BeautifulSoup(data,'lxml')
        tags=soup.findAll(name='a')
        for tag in tags:
            try:
                ret=tag['href']
            except:
                print "Maybe not have href"
                continue 
            res=urlparse.urlparse(ret)
            
            #修正url 
            if res[0] is '' and res[1] is '':   #如果没有协议和域名,就是相对于当前目录的相对地址 
                url_split=urlparse.urlparse(url)
                ret=url_split[0]+"://"+url_split[1]+url_split[2]+reｔ 
                ret=ret[:8]+ret[8:].replace("//",'/')  #把url中的//变为/
                res=urlparse.urlparse(ret)
                
                #  防止 http://domain/dir/../dir/   出现在url中 
                if "../" in res[2]:
                    paths=res[2].split('/')
                    for i in range(len(paths)):
                        if paths[i] == ".."
                            paths[i]==''
                            if paths[i-1]:
                                paths[i-1]=''
                    
                    temp_path=''
                    for path in paths:
                        if path=='':
                            continue
                        temp_path=temp_path+"/"+path
                    
                    ret=ret.replace(res[2],temp_path)  #替换掉原来中的错误部分 
               
               res=urlparse.urlparse(ret)  #重新分解             
                
            #对协议进行过滤　
            
            
            if  'http' not in res[0]:
                print "bad url "+ret
                continue 
            #对url合理性性进行检测
            
            if res[0] is "" and res[1] is not "":
                print "bad url "+ret
                continue 
               
               #对域名进性检查   
            if self.domain not in  res[1]:
                print "bad url"+ret 
                continue
                                           
            newpage=ret
            newpage_flag=False
            self.clok.acquire()
            
            if newpage not in self.father.pages:
                print "find new page :"+newpage
                self.pages.append(newpage)
                newpage_flag=True
            else:
                pass 
            self.lock.release()
            
        return self.pages
    
    def stop(self):
        if self.is_runable!=False:
            self.is_runable=False
            
            
            
            
            
                   
        
        
        
                       
                    
        
        
        
        
        
  
        
 