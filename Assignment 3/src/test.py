import re

def is_corrupted(data):
    return re.match(r'(?:[A-Z]+)$',data) == None

print(is_corrupted('HG^6'))
print(is_corrupted('str'))
print(is_corrupted('STR'))
print(is_corrupted('Q]~U'))
t = 'KQCK'
print(is_corrupted(t))
data = b'KQCK'
str_data = str(data)[2:-1]
print(str_data, t, str_data == t)