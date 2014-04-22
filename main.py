'''
Created on Apr 18, 2014

@author: florin
'''

from epiviz.websocket.ConsoleListener import ConsoleListener
from epiviz.websocket.EpiVizPy import EpiVizPy


if __name__ == '__main__':
    epivizpy = EpiVizPy(ConsoleListener())
    epivizpy.start()
