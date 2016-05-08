#!/bin/bash
 
# 递归搜索目录,获取路径
 
names=`find | grep 'py$' | grep -v 'multipro'`   #只找py文件
 
line=0
 
for name in  ${names}
do
 
linetmp=`cat ${name} | wc -l`   #统计每个文件的行数
echo ${name} : ${linetmp}
line=$((line+linetmp))


done
 
echo "总行数:" ${line}
