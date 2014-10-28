'''
Created on Mar 13, 2014

@author: florin
'''

class EpiVizException(Exception):

    def __init__(self, message):
        self._message = message

    def __str__(self):
        return self._message

    def message(self):
        return self._message
