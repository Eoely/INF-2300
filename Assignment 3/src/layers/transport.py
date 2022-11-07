from copy import copy
import re
from threading import Timer
import time

from packet import Packet

class TransportLayer:
    """The transport layer receives chunks of data from the application layer
    and must make sure it arrives on the other side unchanged and in order.
    """

    def __init__(self):
        self.timer = None
        self.timeout = 0.4  # Seconds
        self.base = 1
        self.nextseqnum = 1
        self.expectedseqnum = 1
        self.ack_data = b''
        self.window = list() #TODO: Create class with own functions for easy pop append

    def with_logger(self, logger):
        self.logger = logger
        return self

    def register_above(self, layer):
        self.application_layer = layer

    def register_below(self, layer):
        self.network_layer = layer

    def from_app(self, binary_data):
        # Alice sends data packets
        packet = Packet(binary_data, False, self.nextseqnum)
        
        self.logger.info(f"Alice sending {packet.data}{packet.seqn}")
        if self.base == self.nextseqnum:
            print("reset timer -- sending")
            self.reset_timer(self.packet_timeout,[])

        self.network_layer.send(packet)
        self.nextseqnum += 1
        time.sleep(0.2)


    def from_network(self, packet: Packet):#Recv
        #ALICE receives ACK
        if packet.is_ack:
            self.logger.info(f"Alice recieving ACK {packet.seqn}")
            self.base = packet.seqn + 1
            if self.base == self.nextseqnum:
                print("cancel timer -- receiving ACK")
                self.timer.cancel()
            else:
                print("reset timer -- recieving ACK")
                self.reset_timer(self.packet_timeout)
            return

        #BOB recieve packet
        self.logger.info(f"Bob recieving {packet.data}{packet.seqn}")
        self.application_layer.receive_from_transport(packet.data)
        ack_packet = Packet(self.ack_data, True, self.expectedseqnum)
        self.logger.info(f"Bob sending ACK {ack_packet.seqn}")
        self.network_layer.send(ack_packet)
        self.expectedseqnum = self.expectedseqnum + 1

    def reset_timer(self, callback, *args):
        # This is a safety-wrapper around the Timer-objects, which are
        # separate threads. If we have a timer-object already,
        # stop it before making a new one so we don't flood
        # the system with threads!
        if self.timer:
            if self.timer.is_alive():
                self.timer.cancel()
        # callback(a function) is called with *args as arguments
        # after self.timeout seconds.
        self.timer = Timer(self.timeout, callback, *args)
        self.timer.start()

    def is_corrupted(self, data):
        return re.match(r'(?:[A-Z]+)$' ,str(data)[2:-1]) == None
    
    def packet_timeout(self):
        # self.ex = self.nextseqnum
        # quit()
        # self.timeout = 23
        print("hva skjer nåå")

