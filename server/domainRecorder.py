#!/usr/bin/python
#-*-coding:utf-8-*-  

import urlparse 

class domainRecorder():
    COUNT=0
    def __init__(self,schema="http",rootDomain=None,domain=None,path=None):
        domainRecorder.COUNT+=1
        self.rootDomain=rootDomain
        self.domain=domain
        self.path=path
        self.schema=schema
        self.count=domainRecorder.COUNT
        
    def printSelf(self):
        print "#"*50
        print "[*] I am a domainRecorder"
        print "## My num is: {}".format(self.count)
        print "## rootDomain: {}".format(self.rootDomain)
        print "## domain: {}".format(self.domain)
        print "## path: {}".format(self.path)
        print "#"*50 
        
    def judgeDomain(self):  #判断是否是一个子域名 
    
        domain_list=self.domain.split('.')
        rootDomain_list=self.rootDomain.split('.')
        print domain_list
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
    
    

        