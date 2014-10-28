'''
Created on Apr 22, 2014

@author: florin
'''

from sys import stdin

from epiviz.events.Event import Event


class ConsoleListener(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self._command_received = Event();


    def on_command_received(self):
        return self._command_received

    def listen(self):
        stop = False
        print 'ConsoleListener: listening... [type "stop" + Enter to stop]'
        while not stop:
            userinput = stdin.readline().strip()
            print 'user input: "%s"' % userinput
            if userinput == 'stop':
                stop = True
                break

            self._command_received.notify(userinput)
        print 'ConsoleListener: stopped.'
