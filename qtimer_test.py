
def doSomething(ev):
    for i in range(5):
        print(i)
        bmd.wait(1)

def OnClose(ev):
    dispatcher.ExitLoop()
    
def OnGo(ev):
    print(timer.IsActive)
    timer.Start()
    print(timer.IsActive)
    print(timer.ID)
    print(timer.RemainingTime)
        

def OnCancel(ev):
    print("OnCancel")
    if timer.IsActive:
        print("IsActive")
        timer.Stop()
    print(timer.IsActive)

if __name__ == "__main__":

    fu.ShowConsole(True)
    ui = fu.UIManager
    dispatcher = bmd.UIDispatcher(ui)
    timer = ui.Timer({'ID':'timer','Interval':10000,'SingleShot': True})
    btGo = ui.Button({'ID':'btGo','Text':'Go','Weight': 0.0})
    vLayout = ui.VGroup([btGo,
                         ui.Button({'ID':'btCancel','Text':'Cancel','Weight': 0.0}),timer]
                        )
    win = dispatcher.AddWindow({'WindowTitle':'Test','ID':'mainWindow'},vLayout)
    #print(resolve.GetHelp('UITimer'))
    
    win.On.mainWindow.Close = OnClose
    win.On.btGo.Clicked = OnGo
    win.On.btCancel.Clicked = OnCancel
    
    win.Show()
    dispatcher.RunLoop()
    win.Hide()