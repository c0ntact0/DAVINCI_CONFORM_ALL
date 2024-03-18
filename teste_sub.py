from multiprocessing import shared_memory
shm = shared_memory.SharedMemory(name="ConformAll",create=False, size=2)

def doSomething():
    shm.buf[1]=False
    for i in range(5):
        cancel=shm.buf[0]
        if cancel:
            break
        print(i,cancel)
        bmd.wait(1)
    shm.buf[0]=False
    shm.buf[1]=True
    
        
doSomething()
shm.close()
