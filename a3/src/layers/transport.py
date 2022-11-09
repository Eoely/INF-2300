from copy import copy
from threading import Timer
from config import PACKET_NUM, PACKET_SIZE

from packet import Packet


class TransportLayer:
    """The transport layer receives chunks of data from the application layer
    and must make sure it arrives on the other side unchanged and in order.
    """

    def __init__(self):
        self.timer = None
        self.timeout = 0.4  # Seconds
        self.num_outstanding = 0
        self.remainding_packets = PACKET_NUM


    def with_logger(self, logger):
        self.logger = logger
        return self

    def register_above(self, layer):
        self.application_layer = layer

    def register_below(self, layer):
        self.network_layer = layer

    def from_app(self, binary_data): #Sender
        # if self.num_outstanding < PACKET_SIZE:
        if True:
            print(self.num_outstanding, binary_data)
            packet = Packet(binary_data) #add rn to packet
            self.remainding_packets -= 1
            self.num_outstanding += 1
            self.network_layer.send(packet)
        else:
            raise(Exception)

        # Implement me!


    def from_network(self, packet): #Receiver
        print('network',packet.data)
        self.application_layer.receive_from_transport(packet.data)
        # Implement me!

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
