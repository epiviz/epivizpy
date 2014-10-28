'''
Created on Mar 12, 2014

@author: florin
'''

from threading import Lock
import threading

import tornado.httpserver
import tornado.ioloop
import tornado.web

from epiviz.exceptions.EpiVizException import EpiVizException
from epiviz.websocket.DataStore import DataStore
from epiviz.websocket.EpiVizPyEndpoint import EpiVizPyEndpoint


class EpiVizPy(object):
    '''
    classdocs
    '''

    def __init__(self, console_listener, server_path=r'/ws'):
        '''
        Constructor
        '''
        measurements = []
        measurements_lock = Lock()
        self._thread = None
        self._server = None
        self._data_store = DataStore()
        self._console_listener = console_listener
        self._application = tornado.web.Application([(server_path, EpiVizPyEndpoint, {
          'console_listener': self._console_listener,
          'measurements': measurements,
          'measurements_lock': measurements_lock,
          'datastore': self._data_store
        })])

    def start(self, port=8888):
        self.stop()
        self._thread = threading.Thread(target=lambda: self._listen(port)).start()
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

    def add_data(self, data, datasource_id, datasource_group=None, measurements=None, names=None, minVals=None, maxVals=None, metadata=None):
        '''
        :param data: DataFrame
        :param datasource_id: the name of the datasource
        :param datasource_group: optional, identifies multiple data sources with the same start, end and index
        :param measurements: a list of columns from the data frame that will be treated as measurements
        :param names: a list of human readable names for the measurements
        :param minVals: optional, a list of min values for the given list of columns
        :param maxVals: optional, a list of max values for the given list of columns
        '''
        if data is None:
            raise EpiVizException('data argument undefined')

        if not datasource_id:
            raise EpiVizException('datasource_id argument undefined')

        datasource_group = datasource_group or datasource_id

        if measurements:
            minVals = [minVals[i] if minVals and minVals[i] != None else min(data[measurements[i]]) for i in range(len(measurements))]
            maxVals = [maxVals[i] if maxVals and maxVals[i] != None else max(data[measurements[i]]) for i in range(len(measurements))]
            names = [names[i] if names and names[i] else measurements[i] for i in range(len(measurements))]

        self._data_store.add_data(data, datasource_id, datasource_group, measurements, names, minVals, maxVals, metadata)


