#!/usr/bin/python
#-*-coding:utf-8-*-  

      
        
import urlparse 
import requests
import time 



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
        
        
if  __name__=='__main__':
    while True:
    
        a=domainRecorder(domain='search.nwpu.edu.cn',rootDomain='nwpu.edu.cn')
        
        print a.judgeDomain()
        
        
        