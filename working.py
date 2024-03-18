# See the README.txt for install

# ShareableList values (index: (type) meaning)
# 0: (boolean) stop flag, changed by the main processed when the user stop the operation.

from multiprocessing.shared_memory import ShareableList
import time

try:
    sl = ShareableList(name='ConformAllWorking')
    #sl[0]=False
    stoped = False
    while not stoped:
        print("",end=".")
        time.sleep(1)
        stoped=sl[0]
    
except Exception as e:
    print(e)
    
finally:
    sl[0]=False
    sl.shm.close()
    

