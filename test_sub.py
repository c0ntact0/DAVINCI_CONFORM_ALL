from multiprocessing.shared_memory import ShareableList

sl=ShareableList(name='ConformAll')
sl[1]=False
text=sl[2]
print(text)
for i in range(5):
    cancel=sl[0]
    if cancel:
        break
    print(i)
    bmd.wait(1)
    
sl[0] = False
sl[1] = True
sl.shm.close()
    