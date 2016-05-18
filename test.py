#!/usr/bin/env python
#-*-coding:utf-８-*-  

import urlparse



def test(url,ret):

    res=urlparse.urlparse(ret)
    ret=urlparse.urlunparse((res[0],res[1],res[2],res[3],res[4],'')) #为了删除url中的锚点
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
        return 
    #对url合理性性进行检测
    
    if res[0] is "" and res[1] is not "":
        # print "bad url "+ret
        return  
    
    
    print ret



if __name__=='__main__':
    url=raw_input("URL:")
    while 1:
        ret=raw_input("TEST:")
        test(url,ret)
        
