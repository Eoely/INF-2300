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
        self.base = 0
        self.nextseqnum = 0
        self.expectedseqnum = 0
        self.ack_data = b''
        self.window_size = 4 #N
        self.window = list() #Window array to contain packets. Tracks all packets, use indexes to find window

    def with_logger(self, logger):
        self.logger = logger
        return self

    def register_above(self, layer):
        self.application_layer = layer

    def register_below(self, layer):
        self.network_layer = layer

    def from_app(self, binary_data):
        #Alice sends data packets
        #Append all incoming data to array
        packet = Packet(binary_data, False, self.nextseqnum)
        self.window.append(packet)
        #If the window is not full, send packet
        if self.nextseqnum < self.base + self.window_size:
            self.network_layer.send(packet)
            #If there is no outstanding packets, start timer.
            if self.base == self.nextseqnum:
                self.reset_timer(self.packet_timeout)

        self.nextseqnum += 1



    def from_network(self, packet: Packet):#Recv
        #ALICE receives ACK
        #Shift base of window to packet after last acknowledged packet
        if packet.is_ack:
            self.base = packet.seqn + 1
            #If there are no packets being sent, stop timer.
            if self.base == self.nextseqnum:
                self.timer.cancel()
            else:#Outstanding packets, reset timer for timeout if lost/corrupted/delayed
                self.reset_timer(self.packet_timeout)
            return

        #BOB recieve packet
        #Packet is corrupted or out of order => Return out, same as packet got dropped
        if self.is_corrupted(packet) or packet.seqn != self.expectedseqnum:
            return
        
        #Acknowledge recieved pack
        #If new packet, update values and send ack
        self.application_layer.receive_from_transport(packet.data)
        ack_packet = Packet(self.ack_data, True, self.expectedseqnum)
        self.network_layer.send(ack_packet)
        self.expectedseqnum += 1

    

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
        self.timer.daemon = True #Makes the sim quit after finishing
        self.timer.start()

    def is_corrupted(self, packet):
        '''Returns True for corrupts packets, uses Regex to detect all caps all chars string'''
        return re.match(r'(?:[A-Z]+)$' ,str(packet.data)[2:-1]) == None
    
    def packet_timeout(self):
        '''Callback function for timer, send all packets in window: [base : nextseqnum - 1]'''
        self.reset_timer(self.packet_timeout)
        for i in range(self.base, self.base + self.window_size + 1):
            try:
                self.network_layer.send(self.window[i])
            except IndexError:
                return
        
            