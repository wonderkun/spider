#!/usr/bin/python 
#-*-coding:utf-8-*- 





if __name__=="__main__":
    from  argparse import  ArgumentParser
    p=ArgumentParser()
    p.add_argument('--port',default=6666,type=int,action="store",help="The port to start the server")
    p.add_argument('domain',type=str,action="store",help="The domain to crawler")
    p.add_argument('-d',action="store_true",help="Wether to crawler subdomain")
    args=p.parse_args()
    print args
    
    
    
    
    
    
    