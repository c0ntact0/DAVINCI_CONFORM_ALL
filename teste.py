
from threading import Thread
import time


def threadTest(name):
    ts = time.time()
    print(ts)
    while True:
        now = time.time()
        if ts + 5. < now:
            print(ts + 5.,now)
            print("Do it")
            ts = time.time()
        time.sleep(0.5)
    
if __name__ == "__main__":
    t = Thread(target=threadTest,args=(1,))
    t.start()
    teste = input()
    print("Teste",teste)