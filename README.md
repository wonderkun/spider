#spider

-------------
#分布式网络爬虫
--------------------

###server 是服务端 
    ├── bin
    │   ├── pycopile.py                   编译,压缩客户端的的代码 
    │   ├── slave                         编译压缩之后的二进制文件  
    │   └── slave.py                      客户端代码的所有模块代码的合并
    ├── code.py                           客户端运行的代码 
    ├── dict                              字典目录
    │   ├── dns_servers.txt               
    │   ├── next_sub.txt
    │   ├── subnames_largest.txt
    │   └── subnames.txt
    ├── DnsBrute.py                       子域名爆破模块,用的是dict中的字典 
    ├── domainRecorder.py                 path url domain 的统一分类,记录模块 
    ├── HttpServer.py                     HTTP 服务模块
    └── server.py                         服务端的入口文件 
    
###slave  是客户端 

    ├── client.py                   客户端入口,主线程 
    ├── controler.py                控制线程,(1)控制主线程的退出,(2)和server进行数据交换
    ├── domainRecorder.py           path url domain 的统一分类,记录模块                  
    ├── pages.db                    数据库
    ├── visited.db                  
    ├── worker.py                   爬虫模块
 

###comm   服务端和客户端的公用模块 
    ├── domainRecorder.py
    └── __init__.py

# 用法  

```bash
   cd ./server
   #修改 ./server/server.py   的address 参数为自己服务器的ip  
   
   cd ./server/bin
   
   #修改./server/bin/slave.py 的参数 server_addr 为自己的服务器的ip
   
     
   > python pycopile.py   #运行次文件,编译客户端代码 
   > cd ../
     
   > python server.py  domain  [-i]  [-T num]   #运行server   -i 指定是否进行子域名爆破,-T 指定线程 
   > python -c "exec(__import__('urllib2').urlopen('http://server_addr:8000/').read())"   # server_addr 换为自己的ip,然后运行起来客户端 
          
```


