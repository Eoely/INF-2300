from copy import copy
from threading import Timer

from packet import Packet


class TransportLayer:
    """The transport layer receives chunks of data from the application layer
    and must make sure it arrives on the other side unchanged and in order.
    """

    def __init__(self):
        self.timer = None
        self.timeout = 0.4  # Seconds
        self.send_num = 0
        self.recv_num = 0
        self.prev_packet:Packet = None

    def with_logger(self, logger):
        self.logger = logger
        return self

    def register_above(self, layer):
        self.application_layer = layer

    def register_below(self, layer):
        self.network_layer = layer

    def from_app(self, binary_data, is_ack=False):
        # Implement me!
        if is_ack:
            self.send_num += 1

        packet = Packet(binary_data, is_ack,self.send_num)


        if  self.prev_packet is None or self.prev_packet.seqn == self.send_num - 1: #ACK'd
            self.logger.info(f"if hit")
            self.prev_packet = packet
        else:
            packet = self.prev_packet

        self.logger.info(f"from_app sending {packet.data}{packet.seqn}")
        self.network_layer.send(packet)
        print("\n")


    def from_network(self, packet: Packet):
        self.application_layer.receive_from_transport(packet.data)
        self.logger.info(f"from_network recv {packet.data}{packet.seqn}")

        if packet.is_ack == False:
            self.logger.info(f"expected {self.recv_num} got {packet.seqn}")

        if packet.seqn == self.recv_num and packet.is_ack == False:
            print("why no hit")
            self.recv_num += 1
            self.from_app(b'', True)
            self.send_num += 1
        

        print("\n")

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
