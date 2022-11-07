from threading import Timer

def callback_func():
    print("hello timer")

inst = Timer(0.6,callback_func,[])
inst.run()
for i in range(0,1000):
    print(i)