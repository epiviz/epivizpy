'''
Created on Mar 13, 2014

@author: florin
'''

class EventListener(object):
    '''
    classdocs
    '''
    next_id = 0

    def __init__(self, callback):
        '''
        :param callback:
        '''
        self._id = EventListener._create_id()
        self._callback = callback

    def id(self):
        return self._id

    def update(self, args):
        self._callback(args)

    @staticmethod
    def _create_id():
        result = EventListener.next_id
        EventListener.next_id += 1
        return result
