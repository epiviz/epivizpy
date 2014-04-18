'''
Created on Apr 18, 2014

@author: florin
'''

from sys import stdin

from epiviz.websocket.EpiVizPy import EpiVizPy

if __name__ == '__main__':
    epivizpy = EpiVizPy()
    epivizpy.start()

    print 'press enter to stop'
    userinput = stdin.readline()
    epivizpy.stop()
    print 'stopped'