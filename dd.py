import threading
import time
lock = threading.Lock()

a = range(100)

t1 = time.clock()


def kk():
    while True:
        lock.acquire()
        global a
        if a:
            print a.pop(0)
            lock.release()
            time.sleep(0.5)
        else:
            lock.release()
            break

m = []

for i in range(100):
    t = threading.Thread(target=kk)
    m.append(t)

for j in m:
    j.start()

for k in m:
    k.join()

print 'total time2:', time.clock() - t1

