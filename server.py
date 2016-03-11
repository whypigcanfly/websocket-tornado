#!/usr/bin/python
#coding:utf-8
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
import os.path

import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpclient
import tornado.websocket

import json
class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class SocketHandler(tornado.websocket.WebSocketHandler):
    """docstring for SocketHandler"""
    clients = dict()#sender=2
    box = dict()#sender=1

    def check_origin(self, origin):
        return True

    @staticmethod
    def send_to_all(message):
        print 'sys:send_to_all()',message
        #print "Clients:",SocketHandler.clients
        for c in SocketHandler.clients:
            c.write_message(json.dumps(message))

    def open(self):
        code = self.get_argument('code','')
        sender = self.get_argument('sender','1')
        print code
        if int(sender) == 1:
            SocketHandler.box[code] = self
        if int(sender) == 2:
            if code in SocketHandler.clients:
                SocketHandler.clients[code].add(self)
            else:
                SocketHandler.clients[code] = set()
                SocketHandler.clients[code].add(self)

    def on_close(self):
        code = self.get_argument('code','')
        sender = self.get_argument('sender','')
        if int(sender) == 1:
            SocketHandler.clients.pop(code)
            SocketHandler.box.pop(code)
        if int(sender) == 2:
            SocketHandler.clients[code].remove(self)

    def on_message(self, message):
        print 'resv:',message
        code = self.get_argument('code','')
        sender = self.get_argument('sender','')
        if int(sender) == 1:
            self.sendToWeixin(message, code)
        if int(sender) == 2:
            self.sendToBox(message, code)


    def sendToBox(self, message, code):
        if code in SocketHandler.box:
            SocketHandler.box[code].write_message(message)

    def sendToWeixin(self,message, code):
        if code in SocketHandler.clients:
            print 'weixin:%s---%d'%(code,len(SocketHandler.clients[code]))
            for c in SocketHandler.clients[code]:
                c.write_message(message)
##MAIN
if __name__ == '__main__':
    app = tornado.web.Application(
        handlers=[
            (r"/websocket", SocketHandler)
        ],
        debug = True,
        template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__), "static")
    )
    app.listen(9201)
    tornado.ioloop.IOLoop.instance().start()
