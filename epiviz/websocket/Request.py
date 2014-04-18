'''
Created on Mar 14, 2014

@author: florin
'''

from enum import Enum

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
    def from_raw_object(o):
        return Request(o['requestId'], o['data'])
