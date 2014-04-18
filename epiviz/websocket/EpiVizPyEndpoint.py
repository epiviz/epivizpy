'''
Created on Mar 12, 2014

@author: florin
'''

import simplejson
import math
import random

import tornado.websocket

from epiviz.websocket.Request import Request
from epiviz.websocket.Response import Response


class EpiVizPyEndpoint(tornado.websocket.WebSocketHandler):

    def __init__(self, *args, **kwargs):
        super(EpiVizPyEndpoint, self).__init__(*args, **kwargs)
        
        self._mock_measurement = {
          'id': 'py_column',
          'name': 'Python Measurement',
          'type': 'feature',
          'datasourceId': 'py_datasource',
          'datasourceGroup': 'py_datasourcegroup',
          'defaultChartType': 'Line Track',
          'annotation': None,
          'minValue': -5,
          'maxValue': 25,
          'metadata': ['py_metadata']
        }

    def open(self):
        print 'new connection'
        # self.write_message('hello')

    def on_message(self, json_message):
        print 'message received %s' % json_message
        message = simplejson.loads(json_message)

        # print message

        if message['type'] == 'request':
            request = Request.from_raw_object(message)
            self._handle_request(request)

    def on_close(self):
        print 'connection closed'


    def send_request(self, request):
        '''
        :param request: Request
        '''

    def _handle_request(self, request):
        action = request.get('action')

        # switch(action)
        response = {
            Request.Action.GET_MEASUREMENTS: lambda: self._get_measurements(request.id()),
            Request.Action.GET_ROWS: lambda: self._get_rows(request.id(), request.get('datasource'), request.get('chr'), request.get('start'), request.get('end'), request.get('metadata')),
            Request.Action.GET_VALUES: lambda: self._get_values(request.id(), request.get('measurement'), request.get('datasource'), request.get('chr'), request.get('start'), request.get('end')),
            Request.Action.GET_SEQINFOS: lambda: self._get_seqinfos(request.id()),
            Request.Action.SEARCH: lambda: self._search(request.id(), request.get('q'), request.get('maxResults'))
        }[action]()


        message = response.to_json()
        print 'response %s' % message
        self.write_message(message)

    # Request handlers

    def _get_measurements(self, request_id):
        '''
        Returns Response
        '''
        return Response(request_id, {
          'id': [self._mock_measurement['id']],
          'name': [self._mock_measurement['name']],
          'type': [self._mock_measurement['type']],
          'datasourceId': [self._mock_measurement['datasourceId']],
          'datasourceGroup': [self._mock_measurement['datasourceGroup']],
          'defaultChartType': [self._mock_measurement['defaultChartType']],
          'annotation': [self._mock_measurement['annotation']],
          'minValue': [self._mock_measurement['minValue']],
          'maxValue': [self._mock_measurement['maxValue']],
          'metadata': [self._mock_measurement['metadata']]
        })

    def _get_rows(self, request_id, datasource, seq_name, start, end, metadata):
        '''
        :param datasource: string
        :param seq_name: string
        :param start: number
        :param end: number
        :param metadata: string[] A list of column names for which to retrieve the values
        Returns response
        '''
        # Return a genomic range of 100 base pairs every 1000 base pairs
        step, width = 1000, 100
        
        globalStartIndex = math.floor((start - 1) / step) + 1
        firstStart = globalStartIndex * step + 1
        firstEnd = firstStart + width

        if firstEnd < start:
            firstStart += step
            firstEnd += step
            
        if firstStart >= end:
            # Nothing to return
            return Response(request_id, { 
              'values': { 'id': [], 'start': [], 'end': [], 'strand': [], 'metadata': { 'py_metadata': [] } },
              'globalStartIndex': None,
              'useOffset': False
            })

        ids = []
        starts = []
        ends = []
        strands = '*'
        py_metadata = []
        
        globalIndex = globalStartIndex
        s = firstStart
        
        while s < end:
            ids.append(globalIndex)
            starts.append(s)
            ends.append(s + width)
            py_metadata.append(self._random_str(5)) # Random string
            globalIndex += 1
            s += step

        return Response(request_id, {
          'values': { 'id': ids, 'start': starts, 'end': ends, 'strand': strands, 'metadata':{ 'py_metadata': py_metadata } },
          'globalStartIndex': globalStartIndex,
          'useOffset': False
        })

    def _get_values(self, request_id, measurement, datasource, seq_name, start, end):
        '''
        :param measurement: string, column name in the datasource that contains requested values
        :param datasource: string
        :param seq_name: string
        :param start: number
        :param end: number
        Returns response
        '''
        # Return a genomic range of 100 base pairs every 1000 base pairs
        step, width = 1000, 100
        
        globalStartIndex = math.floor((start - 1) / step) + 1
        firstStart = globalStartIndex * step + 1
        firstEnd = firstStart + width

        if firstEnd < start:
            firstStart += step
            firstEnd += step
            
        if firstStart >= end:
            # Nothing to return
            return Response(request_id, { 
              'values': [],
              'globalStartIndex': None,
            })
        
        values = []
        globalIndex = globalStartIndex
        s = firstStart
        m = self._mock_measurement
        while s < end:
            v = random.random() * (m['maxValue'] - m['minValue']) + m['minValue']
            values.append(v)
            globalIndex += 1
            s += step

        return Response(request_id, {
          'values': values,
          'globalStartIndex': globalStartIndex
        })

    def _get_seqinfos(self, request_id):
        '''
        Returns response
        '''
        return Response(request_id, [['chr1', 1, 248956422], ['pyChr', 1, 1000000000]])

    def _search(self, request_id, query, max_results):
        '''
        :param query: string
        :param max_results: number
        Returns response
        '''
        return Response(request_id, [])


    def _random_str(self, size):
        chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        result = ''

        for _ in range(size):
            result += chars[random.randint(0, len(chars) - 1)]

        return result

