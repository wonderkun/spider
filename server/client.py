#!/usr/bin/python
#-*-coding:utf-8-*-

import  time
import sys
import Queue
from multiprocessing.managers import BaseManager
import random
from domainRecorder import *

# task_worker.py


# 创建类似的QueueManager:
class QueueManager(BaseManager):
    pass
# 由于这个QueueManager只从网络上获取Queue，所以注册时只提供名字:
QueueManager.register('task_queue_n')
QueueManager.register('response_queue_n')
# 连接到服务器，也就是运行task_master.py的机器:
server_addr = '127.0.0.1'
print('Connect to server %s...' % server_addr)
# 端口和验证码注意保持与task_master.py设置的完全一致:
m = QueueManager(address=(server_addr, 6666), authkey=b'12345')
# 从网络连接:


m.connect()
# 获取Queue的对象:
task = m.task_queue_n()
result = m.response_queue_n()
# 从task队列取任务,并把结果写入result队列:
while True:
    domain=task.get(10)
    print domain.printSelf()
    newdomain=domainRecorder(rootDomain=domain.rootDomain,domain="test.www.baidu.com",path="test")
    result.put(newdomain)
    
# for i in range(10):
#     try:
#         n = task.get(timeout=1)
#         print('run task %d * %d...' % (n, n))
#         r = '%d * %d = %d' % (n, n, n*n)
#         time.sleep(1)
#         result.put(r)
#     except Queue.Empty:
#         print('task queue is empty.')
# 处理结束:
# print('worker exit.')