#!/usr/bin/python 
#-*-coding:utf-8-*- 

import requests

from bs4 import BeautifulSoup

response=requests.get('http://www.baidu.com/')

soup=BeautifulSoup(response.text,'lxml')
for child in  soup.head.children:
    print child
    
