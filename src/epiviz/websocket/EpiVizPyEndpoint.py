'''
Created on Mar 12, 2014

@author: florin
'''

import random

import simplejson
import tornado.websocket

from epiviz.events.EventListener import EventListener
from epiviz.websocket.Request import Request
from epiviz.websocket.Response import Response


class EpiVizPyEndpoint(tornado.websocket.WebSocketHandler):

    def __init__(self, *args, **kwargs):
        self._console_listener = kwargs.pop('console_listener')
        self._datastore = kwargs.pop('datastore')
        self._measurements = kwargs.pop('measurements')
        self._measurements_lock = kwargs.pop('measurements_lock')
        self._event_listener = EventListener(lambda command: self._handle_command(command))
        if not self._console_listener is None:
            self._console_listener.on_command_received().add_listener(self._event_listener)

        # Used to keep track of callbacks for responses
        self._callback_map = {}

        self._charts = []
        self._current_location = None

        self._datastore.on_data_added().add_listener(EventListener(lambda data_tuple: self._data_added(data_tuple)))

        super(EpiVizPyEndpoint, self).__init__(*args, **kwargs)

    def check_origin(self, origin):
        return True

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
            Request.Action.GET_ROWS: lambda: self._get_rows(request.id(), request.get('datasource'), request.get('seqName'), request.get('start'), request.get('end'), request.get('metadata')),
            Request.Action.GET_VALUES: lambda: self._get_values(request.id(), request.get('measurement'), request.get('datasource'), request.get('seqName'), request.get('start'), request.get('end')),
            Request.Action.GET_SEQINFOS: lambda: self._get_seqinfos(request.id()),
            Request.Action.SEARCH: lambda: self._search(request.id(), request.get('q'), request.get('maxResults'))
        }[action]()

        message = response.to_json()
        self.write_message(message)

        print 'response: %s' % message

    # Request handlers

    def _get_measurements(self, request_id):
        '''
        Returns Response
        '''
        return Response(request_id, self._datastore.measurements())

    def _get_rows(self, request_id, datasource, seq_name, start, end, metadata):
        '''
        :param datasource: string
        :param seq_name: string
        :param start: number
        :param end: number
        :param metadata: string[] A list of column names for which to retrieve the values
        Returns response
        '''
        return Response(request_id, self._datastore.rows(datasource, seq_name, start, end, metadata))

    def _get_values(self, request_id, measurement, datasource, seq_name, start, end):
        '''
        :param measurement: string, column name in the datasource that contains requested values
        :param datasource: string
        :param seq_name: string
        :param start: number
        :param end: number
        Returns response
        '''
        return Response(request_id, self._datastore.values(measurement, datasource, seq_name, start, end))

    def _get_seqinfos(self, request_id):
        '''
        Returns response
        TODO: Come back here!
        '''
        return Response(request_id, self._datastore.seq_infos())

    def _search(self, request_id, query, max_results):
        '''
        :param query: string
        :param max_results: number
        Returns response
        '''
        return Response(request_id, [])

    def _handle_command(self, command):
        # switch(action)
        command_handlers = {
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
        }

        if command not in command_handlers:
            return

        request = command_handlers[command]()

        if request is None:
            print '**unable to make request**'
            return

        message = request.to_json()
        self.write_message(message)

    def _add_measurements(self):
        return None

    def _remove_measurements(self):
        return None

    def _add_chart(self):
        return None

    def _chart_added(self, data):
        if not data['success']:
            print '**Adding chart failed: %s**' % data['errorMessage']
            return

        self._charts.append(data['value']['id'])
        print 'Added chart successfully: %s' % data['value']['id']

    def _remove_chart(self):
        return None

    def _redraw(self):
        return Request.redraw()

    def _flush_cache(self):
        return Request.flush_cache()

    def _clear_datasource_group_cache(self):
        return None

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
        return None

    def _random_str(self, size):
        chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        result = ''

        for _ in range(size):
            result += chars[random.randint(0, len(chars) - 1)]

        return result

    def _data_added(self, data_tuple):
        '''
        :param data_tuple:
        '''
        ms = []
        for i in range(len(data_tuple['measurements'])):
            m = {
              'id': data_tuple['measurements'][i],
              'name': data_tuple['names'][i],
              'type': 'feature',
              'datasourceId': data_tuple['datasource_id'],
              'datasourceGroup': data_tuple['datasource_group'],
              'defaultChartType': 'any',
              'annotation': None,
              'minValue': data_tuple['minVals'][i],
              'maxValue': data_tuple['maxVals'][i],
              'metadata': data_tuple['metadata']
            }
            ms.append(m)
        request = Request.add_measurements(ms)
        message = request.to_json()
        self.write_message(message)

        request = Request.add_seqinfos(data_tuple['seqInfos'])
        message = request.to_json()
        self.write_message(message)



