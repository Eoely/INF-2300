class Packet:
    """Represent a packet of data.
    Note - DO NOT REMOVE or CHANGE the data attribute!
    The simulation assumes this is present!"""

    def __init__(self, binary_data, is_ack, seqn):
        # Add which ever attributes you think you might need
        # to have a functional packet.
        # TIPS: Add a __str__ method to print a packet-object nicely! :)
        self.data = binary_data
        self.is_ack = is_ack
        self.seqn = seqn
        #sequence number

        # Extend me!
