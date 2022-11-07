from copy import copy
import re
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
        self.ack_data = b''

    def with_logger(self, logger):
        self.logger = logger
        return self

    def register_above(self, layer):
        self.application_layer = layer

    def register_below(self, layer):
        self.network_layer = layer

    def from_app(self, binary_data):
        # Alice sends data packets
        packet = Packet(binary_data, False, self.seqn)
        
        #If the previous packet was ACK'd, send the new data.
        if self.prev_packet == None or self.seqn > self.prev_packet.seqn: #Prev packet ACK'd
            self.prev_packet = packet
        #Otherwise send the old packet
        else:
            packet = self.prev_packet

        #Send the packet until ACK'd
        old_seqn = packet.seqn
        while self.seqn == old_seqn:
            self.logger.info(f"Alice sending {packet.data}{packet.seqn}")
            self.network_layer.send(packet)


    def from_network(self, packet: Packet):#Recv
        #ALICE receives ACK
        if packet.is_ack:
            if packet.seqn == self.seqn:
                self.seqn += 1
                self.logger.info(f"Alice received ack {packet.data}{packet.seqn}")
            return
            # else:
            #     self.logger.error(f"ACK FAULT expected {self.seqn} got {packet.seqn}")
            #     raise Exception("Receive ACK exception")

        #BOB recieve message - NOT ACK
        #Message is not corrupted, dont ACK => Alice will send packet again
        if self.is_corrupted(packet.data):
            return
        
        #If this message is new: recieve data and send ack
        if self.prev_packet == None or packet.seqn - self.prev_packet.seqn == 1:
            self.logger.info(f"Bob recieved message {packet.data}{packet.seqn}")
            self.seqn = packet.seqn
            self.application_layer.receive_from_transport(packet.data)
            self.prev_packet = packet

        #Not expected or previous packet => Message got skipped, raise exception 
        elif packet.seqn != self.prev_packet.seqn:
            return
        
        ack_packet = Packet(self.ack_data, True, self.seqn)
        self.network_layer.send(ack_packet)

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
        self.timer.daemon = True
        self.timer.start()

    def is_corrupted(self, data):
        res = re.match(r'(?:[A-Z]+)$' ,str(data)[2:-1]) == None
        # print(data, res)
        return res