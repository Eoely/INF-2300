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
        self.seqn = 0
        self.num_acks = 0
        self.prev_packet:Packet = None

    def with_logger(self, logger):
        self.logger = logger
        return self

    def register_above(self, layer):
        self.application_layer = layer

    def register_below(self, layer):
        self.network_layer = layer

    def from_app(self, binary_data, is_ack=False):#Send
        # Alice sends data packets
        # Bob sends ACKS
        if is_ack:
            packet = Packet(binary_data, is_ack, self.seqn)
        else:
            if self.prev_packet == None or self.seqn > self.prev_packet.seqn: #Prev packet ACK'd
                packet = Packet(binary_data, is_ack, self.seqn)
                self.prev_packet = packet
            else:
                packet = self.prev_packet

        self.logger.info(f"from_app sending {packet.data}{packet.seqn}")
        self.network_layer.send(packet)
        print("eskettit\n") #TODO: try to send packet after sending prev_packet


    def from_network(self, packet: Packet):#Recv

        #ALICE receives ACK
        if packet.is_ack:
            if packet.seqn == self.seqn:
                self.seqn += 1
                # self.logger.info(f"Alice received ack {packet.data}{packet.seqn}")
                return
            else:
                self.logger.error(f"wtf happened??")
                raise Exception("lolzzz")

        #BOB recieve message
        if self.prev_packet == None or packet.seqn - self.prev_packet.seqn == 1:
            self.logger.info(f"Bob recieved message {packet.data}{packet.seqn}")
            self.seqn = packet.seqn
            self.application_layer.receive_from_transport(packet.data)
            self.prev_packet = packet
            self.from_app(b'',True)
            return
        elif packet.seqn - self.prev_packet.seqn == 0:
            self.logger.info(f"Bob2 recieved message {packet.data}{packet.seqn}")
            self.from_app(b'',True)
        else:
            self.logger.info(f"Should never hittt{packet.data}{packet.seqn}")


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
