#!/usr/bin/python
#-*-coding:utf-8-*-  

import urlparse 
import requests as req
import time 


class domainRecorder():

    '''
        用来记录域名,判断子域名的可用性,
        记录在同一个域名下的路径 
        记录子域名的个数 
        
    '''
    
    COUNT=0
    def __time(self):
        return time.strftime("%H:%M:%S",time.localtime(time.time())) 
        
    def __init__(self,scheme="http",rootDomain=None,domain='',path='/',isSubDomain=False):
        
        domainRecorder.COUNT+=1
        
        self.rootDomain=rootDomain.strip()
        self.domain=domain.strip()
        self.path=path.strip()
        self.scheme=scheme.strip()
        self.count=domainRecorder.COUNT
        self.isSubDomain=isSubDomain
            
        if self.isSubDomain:
            self.__GetStatus()
        
    def __GetStatus(self):
           
        url=self.getUrl()
        
        try:
            response=req.get(url)
        except req.exceptions.ConnectionError,e:    #说明这是一个顶级域名            
            self.domain="www."+self.domain


    def printSelf(self):
        if self.isSubDomain:  #获取了subdomain 
            print "[%s] [INFO] Get  subdomain:[%s],RootDomain:[%s],Num:[%d]"%(self.__time(),self.domain,self.rootDomain,self.count)
        else:
            print "[%s] [INFO] Get path:[%s],in subdomain:[%s],in RootDomain:[%s],Num:[%d]"(self.__time(),self.path,self.subdomain,self.rootDomain,self.count)

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
    
        if self.path=='/' or other.path=='/':   # 如果任意一个url是根目录,就返回false
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
        
                     
    def  getUrl(self):  #返回此条记录的url
    
        url=urlparse.urljoin(self.scheme+"://"+self.domain,self.path)
        url=url.rstrip('/')+"/"  #必须用/结尾  
        return url  
    
    def reInit(self,url): #用一个url来重新初始化此类  
        url=urlparse.urlparse(url)
        
        self.scheme=url.scheme
        self.domain=url.netloc 
        if (self.rootDomain!=self.domain) and (self.judgeDomain):
            self.isSubDomain=True  
        
        path=url.path.split('/')
        
        for i in path:
            if '.' in i: #说明包含了文件   
                path.remove(i)
                
        self.path=('/').join(path)
        
        
if  __name__=='__main__':
    a=domainRecorder(rootDomain='baidu.com')
    url=raw_input(":")
    a.reInit(url)
    print a.getUrl()
    
    
    