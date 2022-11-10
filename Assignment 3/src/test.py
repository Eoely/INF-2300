from threading import Timer

def callback_func():
    print("hello timer")

test = [1,2,3,4,5]
for i in range(0,10):
    try:
        print(test[i])
    except IndexError:
        print(i)