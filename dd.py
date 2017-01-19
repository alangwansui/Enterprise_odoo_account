import threading
import time
from multiprocessing import Process, Lock
#lock = threading.Lock()

# a = range(100)
# b = [range(1,10),range(10, 20), range(20,30),range(30, 40),range(40, 50),
#      range(50,60),range(60,70),range(70,80),range(80,90),range(90,101)]
#
# t1 = time.clock()
#
#
# def kk(c):
#     while True:
#         lock.acquire()
#         #global a
#         if c:
#             print c.pop(0)
#             lock.release()
#             time.sleep(0.1)
#         else:
#             lock.release()
#             break
#
# m = []
#
# for i in range(10):
#     t = threading.Thread(target=kk, args=(b[i],))
#     m.append(t)
#
# for j in m:
#     j.start()
#
# for k in m:
#     k.join()
#
# print 'total time2:', time.clock() - t1

# assets = range(67)
# assets_part = [[] for i in range(10)]
# count = 0
# for asset in assets:
#     assets_part[count].append(asset)
#     if count == 9:
#         count = 0
#     else:
#         count += 1
#
# print assets_part


# =========================================
import os
a = range(10)
b = [range(1, 10), range(10, 20), range(20, 30), range(30, 40), range(40, 50),
     range(50, 60), range(60, 70), range(70, 80), range(80, 90), range(90, 101)]


def kk(lock):
    while True:
        lock.acquire()
        if a:
            print '%s:' % os.getpid(), a.pop(0)
            lock.release()
            time.sleep(1)
        else:
            lock.release()
            break

if __name__ == "__main__":
    lock = Lock()
    t1 = time.clock()
    m = []

    for i in range(2):
        t = Process(target=kk, name='process_%s' % i, args=(lock,))
        m.append(t)

    for j in m:
        j.start()

    for k in m:
        k.join()

    print 'total time2:', time.clock() - t1
