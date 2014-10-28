'''
Created on Mar 12, 2014

@author: florin
'''

from epiviz.events.EventListener import EventListener
from epiviz.utils.SamFile import SamFile
from epiviz.websocket.ConsoleListener import ConsoleListener
from epiviz.websocket.EpiVizPy import EpiVizPy


epivizpy = None

def handle_command(command):
    if command != 'addData':
        return

    samfile = SamFile.read('../influenza-A.sam')
    # print samfile.coverage('1', 1, 1000)
    # print samfile.base_pair_coverage('1', 1, 1000)

    all_cov = samfile.whole_genome_coverage()
    print all_cov

    epivizpy.add_data(all_cov, 'influenza', None, ['coverage'], ['Influenza read coverage'], [0], [15], None)


if __name__ == "__main__":
    console_listener = ConsoleListener()

    event_listener = EventListener(handle_command)
    console_listener.on_command_received().add_listener(event_listener)

    epivizpy = EpiVizPy(console_listener)
    epivizpy.start()

