#!/usr/bin/python 
#-*-coding:utf-8-*-  


import os
import posixpath
import BaseHTTPServer
import urllib
import urlparse
import cgi
import sys
import shutil
import mimetypes
import time  

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class HttpServer(BaseHTTPServer.HTTPServer):

    def  Time(self):   #格式化输出时间 
        return time.strftime("%H:%M:%S",time.localtime(time.time())) 
        
    
class HttpServerHandle(BaseHTTPServer.BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Serve a GET request."""
        # print self.headers
        # # print help(self.headers)
        # print self.headers.get('User-Agent')
        
        f = self.send_head()
        if f:
            try:
                self.copyfile(f, self.wfile)
            finally:
                f.close()
                
    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
                
        f = None
        
        codePath=os.getcwd()+"/bin/slave"
        userAgent=self.headers.get('User-Agent')
        
        if("Python-urllib/2.7" not in userAgent):
            f = StringIO()
            f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Spider使用说明(wonderkun)</title>
</head>
<body>
    关于Spider的使用说明,仅仅需要两步,就可以了</br>
    一.在服务器端运行main.y</br>
    二.在客户端运行 python -c "exec(__import__('urllib2').urlopen('http://127.0.0.1:8000/').read())",就可以了</br>
    三.然后就没有然后了</br>
</body>
</html>''')
            length = f.tell()
            f.seek(0)
            self.send_response(200)
            encoding = sys.getfilesystemencoding()
            self.send_header("Content-type", "text/html; charset=%s" % encoding)
            self.send_header("Content-Length", str(length))
            self.end_headers()
            return f
                #输出index.html
        elif path!=codePath:
        
            try:        
                f=open('code.py','rb')
            except IOError:
                self.send_error(404, "File not found")
                return None
            try:
                self.send_response(200)
                fs = os.fstat(f.fileno())
                encoding = sys.getfilesystemencoding()
                self.send_header("Content-type", "gzip; charset=%s" % encoding)
                self.send_header("Content-Length",str(fs[6]))
                self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
                self.end_headers()
                return f
            except :
                f.close()
                raise
        else:
            #show codeObject 
            try:        
                print codePath
                
                f=open(codePath,'rb')
                
            except IOError:
                self.send_error(404, "File not found")
                return None
            try:
                self.send_response(200)
                fs = os.fstat(f.fileno())
                encoding = sys.getfilesystemencoding()
                self.send_header("Content-type", "gzip; charset=%s" % encoding)
                self.send_header("Content-Length",str(fs[6]))
                self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
                self.end_headers()
                return f
            except :
                f.close()
                raise
                
    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        shutil.copyfileobj(source, outputfile)
        
    def translate_path(self, path):
    
    
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path  
          
        
        
def HttpServer(HandlerClass = HttpServerHandle,ServerClass = HttpServer):
    
    server_address=('',8000)
    httpd=ServerClass(server_address,HandlerClass)
    
    sa = httpd.socket.getsockname()
    print "[%s] [INFO] Serving HTTP on %s port %d  ..."%(httpd.Time(),sa[0],sa[1])
    
    httpd.serve_forever()
    
    # httpd.stop_server()
    
    
    
if __name__ == '__main__':
    HttpServer()
    
