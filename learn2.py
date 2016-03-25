#!/usr/bin/python 
#-*-coding:utf-8-*-
import  time

# from selenium import webdriver

# # webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.Referer'] = 'http://www.baidu.com/'
# webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36'

# driver = webdriver.PhantomJS('./phantomjs')
# driver.get('http://jszy.nwpu.edu.cn/')

# print(driver.page_source)

class student(object):
    def __init__(self,name="",age=""):
        self.name=name
        self.age=age
    def printf(self):
        print self.name,self.age
        