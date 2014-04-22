'''
Created on Mar 12, 2014

@author: florin
'''

from threading import Lock
import threading

import tornado.httpserver
import tornado.ioloop
import tornado.web

from epiviz.websocket.EpiVizPyEndpoint import EpiVizPyEndpoint


class EpiVizPy(object):
    '''
    classdocs
    '''

    def __init__(self, console_listener=None, server_path=r'/ws'):
        '''
        Constructor
        '''
        measurements = []
        measurements_lock = Lock()

        # Append a mock measurement
        measurements.append({
          'id': 'py_column',
          'name': 'Python Measurement',
          'type': 'feature',
          'datasourceId': 'py_datasource',
          'datasourceGroup': 'py_datasourcegroup',
          'defaultChartType': 'Line Track',
          'annotation': None,
          'minValue':-5,
          'maxValue': 25,
          'metadata': ['py_metadata']
        })

        self._thread = None
        self._server = None
        self._console_listener = console_listener
        self._application = tornado.web.Application([(server_path, EpiVizPyEndpoint, {
          'console_listener': console_listener,
          'measurements': measurements,
          'measurements_lock': measurements_lock
        })])

    def start(self, port=8888):
        self.stop()
        self._thread = threading.Thread(target=lambda: self._listen(port)).start()
        if not self._console_listener is None:
            self._console_listener.listen()
            self.stop()

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
