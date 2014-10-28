'''
Created on Mar 12, 2014

@author: florin
'''

import math
import random

import simplejson
import tornado.websocket

from epiviz.events.EventListener import EventListener
from epiviz.websocket.Request import Request
from epiviz.websocket.Response import Response


class EpiVizPyEndpoint(tornado.websocket.WebSocketHandler):

    def __init__(self, *args, **kwargs):
        self._console_listener = kwargs.pop('console_listener')
        self._measurements = kwargs.pop('measurements')
        self._measurements_lock = kwargs.pop('measurements_lock')

        self._event_listener = EventListener(lambda command: self._handle_command(command))
        if not self._console_listener is None:

            self._console_listener.on_command_received().add_listener(self._event_listener)

        # Used to keep track of callbacks for responses
        self._callback_map = {}

        self._charts = []
        self._current_location = None

        super(EpiVizPyEndpoint, self).__init__(*args, **kwargs)

    def open(self):
        print 'new connection'

    def on_message(self, json_message):
        print 'message received %s' % json_message
        message = simplejson.loads(json_message)

        if message['type'] == 'request':
            request = Request.from_raw_object(message)
            self._handle_request(request)

        if message['type'] == 'response':
            if message['requestId'] in self._callback_map:
                callback = self._callback_map[message['requestId']]
                self._callback_map.pop(message['requestId'])
                callback(message['data'])

    def on_close(self):
        if not self._console_listener is None:
            self._console_listener.on_command_received().remove_listener(self._event_listener.id())
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
        self.write_message(message)

    # Request handlers

    def _get_measurements(self, request_id):
        '''
        Returns Response
        '''
        self._measurements_lock.acquire()
        data = {'id': [], 'name': [], 'type': [], 'datasourceId': [], 'datasourceGroup': [],
                'defaultChartType': [], 'annotation': [], 'minValue': [], 'maxValue': [], 'metadata': [] }
        for i in range(len(self._measurements)):
            for key, value in self._measurements[i].iteritems():
                data[key].append(value)
        self._measurements_lock.release()

        return Response(request_id, data)

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
            py_metadata.append(self._random_str(5))  # Random string
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
        while s < end:
            v = random.random() * 30 - 5
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


    def _handle_command(self, command):
        # switch(action)
        request = {
            Request.Action.ADD_MEASUREMENTS: lambda: self._add_measurements(),
            Request.Action.REMOVE_MEASUREMENTS: lambda: self._remove_measurements(),
            Request.Action.ADD_SEQINFOS: lambda: self._add_seqinfos(),
            Request.Action.REMOVE_SEQNAMES: lambda: self._remove_seqnames(),
            Request.Action.ADD_CHART: lambda: self._add_chart(),
            Request.Action.REMOVE_CHART: lambda: self._remove_chart(),
            Request.Action.CLEAR_DATASOURCE_GROUP_CACHE: lambda: self._clear_datasource_group_cache(),
            Request.Action.FLUSH_CACHE: lambda: self._flush_cache(),
            Request.Action.NAVIGATE: lambda: self._navigate(),
            Request.Action.REDRAW: lambda: self._redraw(),
            Request.Action.GET_CURRENT_LOCATION: lambda: self._get_current_location()
        }[command]()

        if request is None:
            print '**unable to make request**'
            return

        message = request.to_json()
        self.write_message(message)

    def _add_measurements(self):
        mid = self._random_str(5)
        m = {
          'id': 'python_ms_%s' % mid,
          'name': 'Python Measurement %s' % mid,
          'type': 'feature',
          'datasourceId': 'py_datasource',
          'datasourceGroup': 'py_datasourcegroup',
          'defaultChartType': 'Line Track',
          'annotation': None,
          'minValue':-5,
          'maxValue': 25,
          'metadata': ['py_metadata']
        }

        self._measurements_lock.acquire()
        self._measurements.append(m)
        self._measurements_lock.release()

        return Request.add_measurements([m])

    def _remove_measurements(self):
        if len(self._measurements) == 0:
            return None

        self._measurements_lock.acquire()
        m = self._measurements.pop()
        self._measurements_lock.release()

        return Request.remove_measurements([m])

    def _add_seqinfos(self):
        return None

    def _add_chart(self):
        if len(self._measurements) == 0:
            return None

        ms = [self._measurements[0]]
        if (len(self._measurements) > 1):
            ms.append(self._measurements[1])

        request = Request.add_chart('epiviz.plugins.charts.LineTrack', ms)
        self._callback_map[request.id()] = lambda data: self._chart_added(data)

        return request

    def _chart_added(self, data):
        if not data['success']:
            print '**Adding chart failed: %s**' % data['errorMessage']
            return

        self._charts.append(data['value']['id'])
        print 'Added chart successfully: %s' % data['value']['id']

    def _remove_chart(self):
        if len(self._charts) == 0:
            return None

        chart_id = self._charts.pop()
        return Request.remove_chart(chart_id)

    def _redraw(self):
        return Request.redraw()

    def _flush_cache(self):
        return Request.flush_cache()

    def _clear_datasource_group_cache(self):
        return Request.clear_datasource_group_cache('py_datasourcegroup')

    def _get_current_location(self):
        request = Request.get_current_location()
        self._callback_map[request.id()] = lambda data: self._current_location_retrieved(data)

        return request

    def _current_location_retrieved(self, data):
        if not data['success']:
            print '**Current location retrieval failed: %s**' % data['errorMessage']
            return

        self._current_location = data['value']
        print 'Current location: %s:%s-%s' % (data['value']['seqName'], data['value']['start'], data['value']['end'])

    def _navigate(self):
        if self._current_location is None:
            return None

        width = self._current_location['end'] - self._current_location['start']
        start = self._current_location['start'] + width * 0.2
        end = start + width

        self._current_location = { 'seqName': self._current_location['seqName'], 'start': start, 'end': end }

        return Request.navigate(self._current_location)

    def _random_str(self, size):
        chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        result = ''

        for _ in range(size):
            result += chars[random.randint(0, len(chars) - 1)]

        return result

