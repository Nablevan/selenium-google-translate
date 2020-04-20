import threading
import time


def get_one(nums):
    while True:
        if nums.__len__ == 0:
            break
        time.sleep(1)
        lock.acquire()
        try:
            if nums.__len__() > 0:
                print(threading.current_thread().getName(), nums.pop(0))
        finally:
            lock.release()


if __name__ == '__main__':
    count = [x for x in range(20)]
    lock = threading.Lock()
    t1 = threading.Thread(target=get_one, args=(count,))
    t2 = threading.Thread(target=get_one, args=(count,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
