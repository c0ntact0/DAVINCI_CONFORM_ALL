import os
import json

settingsFile = "ConformSony.json"

def getSettings():
    jsonObj = {
            "amaPath" : ""
    }
    # normaly defaults to /Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion
    path = os.path.join(os.getcwd(),settingsFile)
    #print(path)
    if os.path.exists(path):
        with open(path,'r') as openFile:
            jsonObj = json.load(openFile)
    
    else:    
        with open(path, "w") as outfile:
            json.dump(jsonObj, outfile)
   
    return jsonObj 
            

def saveSetting(key,value):
    """
    Save just one setting and returns the modified settings object
    """
    # read current settings from file
    jsonObj = getSettings()
    jsonObj[key] = value
    path = os.path.join(os.getcwd(),settingsFile)
    
    with open(path, "w") as outfile:
        json.dump(jsonObj, outfile)
        
    jsonObj

def getUIValues():
    """
    Get the UI values.
    
    Return: amaPath (string)
    """
    return win.Find('txtAmaPath').Text #, win.Find('txtFieldSep').Text, win.Find('spFieldCount').Value)

def getMediaFiles(folderPath, clipDict):
    """
    Get ama files reel names as keys and paths as values.
    
    Return {"reelName:"filename",...]
    """
    print("Getting Media Files (AMA)")
    amaFiles = {}
    for root, dirs, files in os.walk(folderPath):
        for name in files:
            if "Clip" in root and (name.endswith(".MXF") or name.endswith(".mxf")):
                fileReel = extractReelName(name)
                if clipDict.get(fileReel):
                    amaFiles[fileReel] = os.path.join(root,name)
                    print("Reel Name:",fileReel,"\tFilename:",os.path.join(root,name))
    #print(amaFiles)
    return amaFiles

def getClips(clipsList):
    print("Getting Clips (Media Pool)")
    clipDict = {}
    for clip in clipsList:
        clipReel = clip.GetClipProperty("Reel Name") #extractReelName(clipName)
        if len(clipReel) > 0:
            clipDict[clipReel] = clip
            print("Clip name:",clip.GetName(),"\tReel Name:",clipReel)
            
    return clipDict

def getTimelineClips(clipsList):
    print("Getting Clips (Timeline)")
    clipDict = {}
    numClips=0
    for clip in clipsList:
        mpClip = clip.GetMediaPoolItem()
        if mpClip:

            clipReel = mpClip.GetClipProperty("Reel Name") #extractReelName(clipName)
            if clipReel:
                clipDict[clipReel] = mpClip
                numClips+=1
    
    print(numClips,"clips found in timeline...")        
    return clipDict

def extractReelName(value: str):

    # remove extention
    valueParts = value.split(".")
    if len(valueParts) > 1:
        valueParts = valueParts[0:len(valueParts)-1]
    clipName = ".".join(valueParts)

    return clipName
    

def replaceClips(clips,files):
    counter = 0
    for key in clips.keys():
        clip = clips.get(key)
        clipName = clip.GetName()
        file = files.get(key)
        if file:
            if clip.ReplaceClip(file):
                counter+=1
                print("Clip",clipName,"replaced")
            else:
                print("Error replacing",clipName,"with",file)
    print(str(counter)," clips conformed.")

##### EVENT HANDLERS #####
def OnClose(ev):
    print("Exit")
    dispatcher.ExitLoop()
    
def BtSaveSettings(ev):
    global settings
    print("Saving settings")
    saveSetting('amaPath', getUIValues())
    settings = getSettings()


def BtGo(ev):
    global currentTimeline
    print("Processing...")
    btGo = win.Find('btGo')
    btGo.Enabled = False
    currentTimeline = currentProject.GetCurrentTimeline()
    clipDict = getTimelineClips(currentTimeline.GetItemListInTrack('video', 1))
    if len(clipDict.keys()) == 0:
        label = dialog.Find('errorLabel')
        label.Text = "No Reel Names Found.\n" \
        "Please goto File->Project Settings...->General Options\n" \
        "In the Conform Options section select:\n" \
        "- Assist using reel names from the:\n" \
        "-- Embedding in source clip file"
        dialog.Show()
    else:
    
    #clipDict = getTimelineClips(currentTimeline.GetItemListInTrack("video", 1))
        amaPath = getUIValues()
        amaDic = getMediaFiles(amaPath, clipDict)
        replaceClips(clipDict,amaDic)
        print("Finished...")

    btGo.Enabled = True

    
def DialogClose(ev):
    dialog.Hide()

################# MAIN ###################
if __name__ == "__main__":
    settings = getSettings()

    mediaStorage = resolve.GetMediaStorage()
    fusion = resolve.Fusion()
    pm = resolve.GetProjectManager()

    currentProject = pm.GetCurrentProject()
    currentTimeline = currentProject.GetCurrentTimeline()
    mediaPool = currentProject.GetMediaPool()
    currentFolder = mediaPool.GetCurrentFolder()

    ui = fusion.UIManager
    dispatcher = bmd.UIDispatcher(ui)

    amaPathLayout = ui.HGroup(
        [   ui.Label({'Text':'AMA Path','FixedSize':[60,30]}),
            ui.LineEdit({'ID':'txtAmaPath','Text':settings['amaPath'],'MinimumSize':[400,30]}),
        ]
    )

    vLayout = ui.VGroup(
        [ui.Label({'Text':'If you need output, goto the menu Workspace and open the Console.','Alignment':{'AlignTop' : True}}),
         ui.VGap(2),
         amaPathLayout,
         ui.VGap(2),
         #extractionLayout,
         #ui.VGap(2),
         ui.Button({'ID':'btSaveSettings','Text':'Save Settings'}),
         ui.Button({'ID':'btGo','Text':'Go'})
         ]
    )

    win = dispatcher.AddWindow({'WindowTitle':'ConformSony (Rui Loureiro 2023)','ID':'testeWindow', 'MinimumSize':[600,200],'MaximumSize':[600,200]},vLayout)
    win.On.btSaveSettings.Clicked = BtSaveSettings
    win.On.btGo.Clicked = BtGo
    win.On.testeWindow.Close = OnClose

    dialog = dispatcher.AddDialog({'WindowTitle':'Error','ID':'errorDialog','MinimumSize':[400,400],'MaximumSize':[400,400]},
                                  ui.VGroup([ui.Label({'ID':'errorLabel','MinimumSize':[400,350],'MaximumSize':[400,350],'Alignment':{'AlignTop' : True}}),
                                   ui.Button({'ID':'btCloseDialog','Text':'Close'})]))
    dialog.On.btCloseDialog.Clicked = DialogClose
    
    win.Show()
    dispatcher.RunLoop()
    win.Hide()


