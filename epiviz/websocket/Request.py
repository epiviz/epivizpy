'''
Created on Mar 14, 2014

@author: florin
'''

from enum import Enum
import simplejson

class Request(object):
    '''
    classdocs
    '''

    class Action(Enum):
        # Server actions
        GET_ROWS = 'getRows'
        GET_VALUES = 'getValues'
        GET_MEASUREMENTS = 'getMeasurements'
        SEARCH = 'search'
        GET_SEQINFOS = 'getSeqInfos'
        SAVE_WORKSPACE = 'saveWorkspace'
        GET_WORKSPACES = 'getWorkspaces'

        # UI actions
        ADD_MEASUREMENTS = 'addMeasurements'
        REMOVE_MEASUREMENTS = 'removeMeasurements'
        ADD_SEQINFOS = 'addSeqInfos'
        REMOVE_SEQNAMES = 'removeSeqNames'
        ADD_CHART = 'addChart'
        REMOVE_CHART = 'removeChart'
        CLEAR_DATASOURCE_GROUP_CACHE = 'clearDatasourceGroupCache'
        FLUSH_CACHE = 'flushCache'
        NAVIGATE = 'navigate'
        REDRAW = 'redraw'
        GET_CURRENT_LOCATION = 'getCurrentLocation'

    next_id = 0

    def __init__(self, request_id, args):
        '''

        :param request_id: number
        :param args: map<string, string>
        '''

        self._id = request_id
        self._args = args

    def id(self):
        return self._id

    def get(self, arg):
        if arg in self._args:
            return self._args[arg]

        return None

    @staticmethod
    def generate_id():
        result = Request.next_id
        Request.next_id += 1
        return result

    @staticmethod
    def add_measurements(measurements):
        return Request(Request.generate_id(), {'action': Request.Action.ADD_MEASUREMENTS, 'measurements': simplejson.dumps(measurements)})

    @staticmethod
    def remove_measurements(measurements):
        return Request(Request.generate_id(), {'action': Request.Action.REMOVE_MEASUREMENTS, 'measurements': simplejson.dumps(measurements)})

    @staticmethod
    def add_chart(chart_type, measurements):
        return Request(Request.generate_id(), {'action': Request.Action.ADD_CHART, 'type': chart_type, 'measurements': simplejson.dumps(measurements)})

    @staticmethod
    def remove_chart(chart_id):
        return Request(Request.generate_id(), {'action': Request.Action.REMOVE_CHART, 'chartId': chart_id})

    @staticmethod
    def redraw():
        return Request(Request.generate_id(), {'action': Request.Action.REDRAW})

    @staticmethod
    def flush_cache():
        return Request(Request.generate_id(), {'action': Request.Action.FLUSH_CACHE})

    @staticmethod
    def clear_datasource_group_cache(datasource_group):
        return Request(Request.generate_id(), {'action': Request.Action.CLEAR_DATASOURCE_GROUP_CACHE, 'datasourceGroup': datasource_group})

    @staticmethod
    def get_current_location():
        return Request(Request.generate_id(), {'action': Request.Action.GET_CURRENT_LOCATION})

    @staticmethod
    def navigate(location):
        return Request(Request.generate_id(), {'action': Request.Action.NAVIGATE, 'range': simplejson.dumps(location)})

    def to_json(self):
        raw = {'requestId': self._id, 'type': 'request', 'data': self._args}
        return simplejson.dumps(raw)

    @staticmethod
    def from_raw_object(o):
        return Request(o['requestId'], o['data'])
