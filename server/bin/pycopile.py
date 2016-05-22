#!/usr/bin/env python   
#-*-coding:utf-8-*-  




import zlib,marshal


if __name__=="__main__":

    try:
        file=open('slave.py','rb')
        content=file.read()
        
    except IOError,e:
        print "Read file Error ..."
        exit()
    else:
        file.close()
        
    try:
        co=compile(content,'slave','exec')
    except:
        print "Compile file Error ..."
        exit()
        
        
    with open('slave','wb') as file:
        marshal.dump(co,file)
        
    try:
        file=open('slave','rb')
        content=zlib.compress(file.read())
        file.close()
        file=open('slave','wb')
        file.write(content)
    except:
        print "Compress Error ..."
        raise  
    else:
        file.close()
        
        