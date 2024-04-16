from multiprocessing import shared_memory
from multiprocessing.shared_memory import ShareableList
import os

path = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/test_sub.py"

def OnClose(ev):
    dispatcher.ExitLoop()

def OnGo(ev):
    dest_path="This is some path"
    path_bytes = len(dest_path.encode('utf-8'))
    print(path_bytes)
    """
    shm_size = 2+path_bytes
    try:
        shm = shared_memory.SharedMemory(name="ConformAll",create=True, size=shm_size)
    except FileExistsError:
        print('Shared Memory File Already Exists')
        shm = shared_memory.SharedMemory(name="ConformAll",create=False, size=shm_size)

    print(len(shm.buf))
    shm.buf[0]=False
    shm.buf[1]=True
    shm.buf[2:4]= path_bytes.to_bytes(2,'big')
    shm.buf[4:4+path_bytes]= bytes(dest_path,'utf-8')[:]
    """
    sl = ShareableList([False,True,dest_path],'ConformAll')
    
    bmd.wait(0.1)

    fu.RunScript(path)
    win.Find('btGo').Enabled = False
    bmd.wait(0.5)
    while True:
        #finished=shm.buf[1]
        finished=sl[1]
        if finished:
            break
        if win.Find('btCancel').Down:
            #shm.buf[0]=True
            sl[0]=True
            print('Cancel')
            
        bmd.wait(0.1)
    #shm.close()
    #shm.unlink()
    sl.shm.close()
    sl.shm.unlink()
    print('Finished')
    win.Find('btGo').Enabled = True
    
if __name__ == "__main__":

    fu.ShowConsole(True)
    ui = fu.UIManager
    dispatcher = bmd.UIDispatcher(ui)
    vLayout = ui.VGroup([ui.Button({'ID':'btGo','Text':'Go','Weight': 0.0}),
                         ui.Button({'ID':'btCancel','Text':'Cancel','Weight': 0.0})])
    win = dispatcher.AddWindow({'WindowTitle':'Test','ID':'mainWindow'},vLayout)
    
    win.On.mainWindow.Close = OnClose
    win.On.btGo.Clicked = OnGo
    
    win.Show()
    dispatcher.RunLoop()
    win.Hide()
