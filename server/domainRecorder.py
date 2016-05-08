#!/usr/bin/python
#-*-coding:utf-8-*-  

import urlparse 
import requests as req



class domainRecorder():

    '''
        用来记录域名,判断子域名的可用性,
        记录在同一个域名下的路径 
        记录记录的个数 
        
    '''
    
    COUNT=0
    def __init__(self,schema="http",rootDomain=None,domain=None,path='/',isSubDomain=False):
        
        domainRecorder.COUNT+=1
        
        self.rootDomain=rootDomain.strip()
        self.domain=domain.strip()
        self.path=path.strip()
        self.schema=schema.strip()
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
            print "[INFO] Get  subdomain:[%s],RootDomain:[%s],Num:[%d]"%(self.domain,self.rootDomain,self.count)
        else:
            print "[INFO] Get path:[%s],in subdomain:[%s],in RootDomain:[%s],Num:[%d]"(self.path,self.subdomain,self.rootDomain,self.count)

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
        
        
    def  getUrl(self):  #返回此条记录的url
    
        return   urlparse.urljoin(self.schema+"://"+self.domain,self.path)
        
    
    