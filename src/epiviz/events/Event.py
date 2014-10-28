'''
Created on Mar 13, 2014

@author: florin
'''

class Event(object):
    '''
    classdocs
    '''


    def __init__(self):
        self._count = 0
        self._listeners = {}
        self._firing = False


    def add_listener(self, listener):
        '''
        :param listener: EventListener
        '''
        if not listener.id() in self._listeners:
            self._count += 1

        self._listeners[listener.id()] = listener


    def remove_listener(self, listener_id):
        if not listener_id in self._listeners:
            return

        del self._listeners[listener_id]
        self._count -= 1


    def notify(self, args):
        if self._firing:
            return

        if self._count == 0:
            return

        self._firing = True

        for _, listener in self._listeners.iteritems():
            listener.update(args)

        self._firing = False
