#!/usr/bin/python 
#-*-coding:utf-8-*-
import  time

# from selenium import webdriver

# # webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.Referer'] = 'http://www.baidu.com/'
# webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36'

# driver = webdriver.PhantomJS('./phantomjs')
# driver.get('http://jszy.nwpu.edu.cn/')

# print(driver.page_source)
# class student(object):
#     def __init__(self,name="",age=""):
#         self.name=name
#         self.age=age
#         self.printf()
#     def printf(self):
#         print self.name,self.age

import requests 
import urllib
import urllib2

from bs4 import BeautifulSoup
begin_time=time.time()
url="http://range.pw/wp-content/uploads/2015/10/QQ图片20150516164635.jpg"
response=urllib2.urlopen(url)
data=response.read()

soup=BeautifulSoup(data,'lxml')
tags=soup.findAll(name='a')


print tags

print time.time()-begin_time

        
        
      