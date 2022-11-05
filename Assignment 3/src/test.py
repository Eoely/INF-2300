from packet import Packet
test = Packet(b'123',False, 5)
print(test.seqn)
test.seqn = 10
print(test.seqn)