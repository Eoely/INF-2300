from packet import Packet
from secrets import token_bytes

for i in range(0,5):
    s = token_bytes(4)
    print(s)
    if b'x' in s:
        print("lol")
