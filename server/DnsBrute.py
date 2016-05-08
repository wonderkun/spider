#!/usr/bin/python
#-*-coding:utf-8-*-  

'''
  爆破子域名,根据大牛lijieji的那个DNSBrute写的  
  用了他的字典   
  也是多线程的,默认是10个线程  
    
'''

import  dns.resolver
import time 
import threading 
import Queue
import os
from domainRecorder import *

class DnsBrute(object):
    def __init__(self,father=None,rootDomain=None, names_file=None,threads_num=1):
        self.rootDomain = rootDomain.strip()  #目标
        self.names_file = "subnames.txt" if names_file==None else names_file  #子域名来源
        self.thread_count = self.threads_num = int(threads_num)  #线程数目   
        self.lock = threading.RLock()
        self.resolvers = [dns.resolver.Resolver() for _ in range(threads_num)]  #产生多个dns.resolver.Resolver() 存起来  
        self._load_dns_servers()  #存储dnsserver  
        self._load_sub_names()    #载入子域名字典,存在self.queue中
        self._load_next_sub()  #载入三级域名  
        self.ip_dict = {}
        self.STOP_ME=False
        self.father=father
        
        
        
    def _load_dns_servers(self):
        dns_servers = []
        with open('./dict/dns_servers.txt') as f:
            for line in f:
                server = line.strip()
                if server.count('.') == 3 and server not in dns_servers:
                    dns_servers.append(server)
        self.dns_servers = dns_servers
        self.dns_count = len(dns_servers)
    def _load_sub_names(self):
        self.queue = Queue.Queue()
        file = 'dict/' + self.names_file if not os.path.exists(self.names_file) else self.names_file
        with open(file) as f:
            for line in f:
                sub = line.strip()
                if sub: self.queue.put(sub)
                
    def _load_next_sub(self):            
        next_subs = []
        with open('./dict/next_sub.txt') as f:
            for line in f:
                sub = line.strip()
                if sub and sub not in next_subs:
                    next_subs.append(sub)
        self.next_subs = next_subs   

           
    @staticmethod
    def is_intranet(ip):  #ip规则性检测和内网检测,是内网就返回 True 
        ret = ip.split('.')
        if not len(ret) == 4:
            return True
        if ret[0] == '10':
            return True
        if ret[0] == '172' and 16 <= int(ret[1]) <= 32:
            return True
        if ret[0] == '192' and ret[1] == '168':
            return True
        return False
        
    def _scan(self):
        # self._print_progress()
        thread_id = int( threading.currentThread().getName())  #获取当前线程的名字
        self.resolvers[thread_id].nameservers.insert(0, self.dns_servers[thread_id % self.dns_count])   #随机设定一个dns_server
        self.resolvers[thread_id].lifetime = self.resolvers[thread_id].timeout = 3.0  #设定超时时间
        while self.queue.qsize() > 0 and not self.STOP_ME:     
            sub = self.queue.get(timeout=1.0)
            # self._print_progress()
            cur_sub_domain = sub + '.' + self.rootDomain           
            for _ in range(3):   #每一个域名请求3次 
                try:
                    answers = self.resolvers[thread_id].query(cur_sub_domain)
                    is_wildcard_record = False
                    if answers:
                        
                        # print   self.ip_dict,cur_sub_domain
                        
                        for answer in answers:
                            self.lock.acquire()
                            if answer.address not in self.ip_dict:
                                self.ip_dict[answer.address] = 1
                            else:       
                                self.ip_dict[answer.address] += 1
                                if self.ip_dict[answer.address] > 2:    # a wildcard DNS record
                                    is_wildcard_record = True
                            self.lock.release()
                            
                        if is_wildcard_record:
                            #get a wildcard record   
                            print "[WARNING] Thread-%d Get a wildcard record ..."%(thread_id)
                            continue
                                 
                        ips = ', '.join([answer.address for answer in answers]) #获取响应的地址
                                             
                        if (not self.is_intranet(answers[0].address)): #如果不是内网地址
                            #说明获得了一个子域名  
                            print "[INFO] Thread-%d Get a subdomain:"%(thread_id),cur_sub_domain,ips
                            # self.father.response_queue.put()
                            #把子域名压入到父队列中去  
                            
                            try:
                                
                                subdomain=domainRecorder(rootDomain=self.rootDomain,domain=cur_sub_domain,isSubDomain=True)
                                subdomain.printSelf()                                 
                            except Exception,e:
                                print e
                                
                            if subdomain.judgeDomain():  #如果是子域名
                                self.father.response_queue.put(subdomain)
                            else:
                                
                                print "[Error] %s isn't a subdomain of %s"%(cur_sub_domain,self.rootDomain)
                                
                                
                            for i in self.next_subs:   
                                self.queue.put(i + '.' + sub)
                        break    
                except dns.resolver.NoNameservers, e:
                    break
                except Exception, e:
                    pass
                    
                    
        self.thread_count-=1                     
    def run(self):
    
        for i in range(self.threads_num):
            t = threading.Thread(target=self._scan, name=str(i))  #名字就是自己的id
            t.setDaemon(True)
            t.start()
        while self.thread_count > 0:
        
            try:
                time.sleep(1.0)
            except KeyboardInterrupt,e:
                self.STOP_ME=True
                msg = '[WARNING] User aborted, wait all slave threads to exit...'
                print msg



        
if __name__=="__main__":

    a=DnsBrute(rootDomain="baidu.com")
    a.run()
    