# -*- coding: UTF-8 -*-
import traceback
from gevent import monkey; monkey.patch_all()
from socketio import SocketIOServer
import sys
import os.path as path

sys.path.append(path.dirname(__file__) + '/.lib')

class Application(object):
    def __init__(self):
        self.buffer = [{'id':'aaron','message':'i am aaron'},
                       {'id':'tei','message':'i am tei'}]
        self.id = ''

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO'].strip('/')
        print '//////////////////////////////'
        print path
        print '//////////////////////////////'
        print start_response
        print '//////////////////////////////'
        #如果在根目錄，就提供超聯結至talk.html
        if not path:
            start_response('200 OK', [('Content-Type', 'text/html')])
            return ['<h1>Welcome. Try the <a href="/talk.html">talk</a> example.</h1>']
        #如果在talk.html，就讀取talk.htm並回應
        if path in ['talk.html']:
            try:
                data = open(path).read()
            except Exception:
                traceback.print_exc()
                return not_found(start_response)
            start_response('200 OK', [('Content-Type', 'text/javascript' if path.endswith('.js') else 'text/html')])
            return [data]
        #如果觸發socket.io事件
        if path.startswith("socket.io"):
            socketio = environ['socketio']
            if socketio.on_connect():
                socketio.send({'buffer': self.buffer})
            while True:
                message = socketio.recv()
                
                if len(message) == 1:
                    message = message[0]
                    if not self.id:
                        self.id = message
                        print 'id:'+self.id
                    else:
                        message = {'id': self.id, 'message': message}
                        self.buffer.append(message)
                        socketio.send({'buffer': [message]})
                        if len(self.buffer) > 15:
                            del self.buffer[0]
            return []
                
def not_found(start_response):
    start_response('404 Not Found', [])
    return ['<h1>Not Found</h1>']
                
if __name__ == '__main__':
    print 'Listening on port 8080 and on port 843 (flash policy server)'
    SocketIOServer(('', 8080), Application(), resource="socket.io").serve_forever()