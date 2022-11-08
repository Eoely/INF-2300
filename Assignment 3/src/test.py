from threading import Timer

def callback_func():
    print("hello timer")

inst = Timer(0.6,callback_func,[])
inst.run()
test = 10
for i in range(0,test):
    test += 1
    print(i, test)