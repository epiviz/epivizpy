'''
Created on Mar 12, 2014

@author: florin
'''

import threading

import tornado.httpserver
import tornado.ioloop
import tornado.web

from epiviz.websocket.EpiVizPyEndpoint import EpiVizPyEndpoint


class EpiVizPy(object):
    '''
    classdocs
    '''

    def __init__(self, server_path=r'/ws'):
        '''
        Constructor
        '''
        self._thread = None
        self._server = None
        self._application = tornado.web.Application([(server_path, EpiVizPyEndpoint)])

    def start(self, port=8888):
        self.stop()
        self._thread = threading.Thread(target=lambda: self._listen(port)).start()

    def stop(self):
        if self._server != None:
            # self._server.stop()
            tornado.ioloop.IOLoop.instance().stop()
            self._server = None
            self._thread = None

    def _listen(self, port):
        self._server = tornado.httpserver.HTTPServer(self._application)
        self._server.listen(port)
        tornado.ioloop.IOLoop.instance().start()


