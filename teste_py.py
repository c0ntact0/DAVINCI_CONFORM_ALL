from multiprocessing.shared_memory import ShareableList
import os

path = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/test_sub.py"

def OnClose(ev):
    dispatcher.ExitLoop()

def OnGo(ev):
    dest_path="This is some path"
    sl = ShareableList([False,True,dest_path],name='ConformAll')
    
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
            bmd.wait(0.5)
            print('Cancel')
            
        bmd.wait(0.1)

    bmd.wait(1)
    sl.shm.close()
    sl.shm.unlink()
    print('Finished')
    win.Find('btGo').Enabled = True

def OnTabChanged(ev):
    print(ev['Index'])
    items['MyStack'].CurrentIndex  = ev['Index']

if __name__ == "__main__":
    fu.ShowConsole(True)
    ui = fu.UIManager
    dispatcher = bmd.UIDispatcher(ui)
    #print(app.GetHelp('UITabBar:AddTab'))
    
    hLayoutButtons = ui.HGroup([
                    
                ui.Button({'ID':'btGo','Text':'Go','Weight': 0.0}),
                ui.Button({'ID':'btCancel','Text':'Cancel','Weight': 0.0})
                ])
    
    vLayout = ui.VGroup(
        [
        ui.TabBar({'Weight':0.0,'ID':'MyTabs'}),
        ui.VGap(10),
        ui.Stack({'Weight':1.0,'ID':'MyStack'},[
                hLayoutButtons,
                ui.Label({'Text':'Outra tab','ID':'label1'})]
                )
            ])
    
    
    win = dispatcher.AddWindow({'WindowTitle':'Test','ID':'mainWindow'},vLayout)
    
    items = win.GetItems()
    
    items['MyStack'].CurrentIndex = 0
    
    items['MyTabs'].AddTab("One")
    items['MyTabs'].AddTab("Two")
    
    win.On.mainWindow.Close = OnClose
    #win.On.btGo.Clicked = OnGo
    win.On.MyTabs.CurrentChanged = OnTabChanged
    
    win.Show()
    dispatcher.RunLoop()
    win.Hide()
