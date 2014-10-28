'''
Created on Mar 14, 2014

@author: florin
'''

import simplejson

class Response(object):
    '''
    classdocs
    '''


    def __init__(self, request_id, data):
        '''
        
        :param request_id: number, the id of the request whose response this is
        :param data: the contents of the response
        '''
        self._request_id = request_id
        self._data = data

    def request_id(self):
        return self._request_id

    def data(self):
        return self._data

    def to_json(self):
        raw = {'requestId': self._request_id, 'type': 'response', 'data': self._data}
        return simplejson.dumps(raw)
