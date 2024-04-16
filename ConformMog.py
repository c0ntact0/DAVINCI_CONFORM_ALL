import os
import json

settingsFile = "ConformMog.json"


def getSettings():
    jsonObj = {
            "amaPath" : "",
            "fieldSep" : "_",
            "fieldCount" : 5,
            "aafPath" : "",
            "avidPath" : ""
    }
    # normaly defaults to /Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion
    path = os.path.join(os.getcwd(),settingsFile)
    print(path)
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
    
    Return: (amaPath (string), fieldSeparator (string), fieldCount (int), aafPath (string)) Tuple
    """
    return (win.Find('txtAmaPath').Text, 
            win.Find('txtFieldSep').Text, 
            win.Find('spFieldCount').Value,
            win.Find('txtAAFPath').Text)


def getAvidMedia(folderPath):
    print("Getting Media Files (Avid)")
    avidFiles = []
    for root, dirs, files in os.walk(folderPath):
        for name in files:
            if name.endswith(".mxf") or name.endswith(".MXF"):
                avidFiles.append(os.path.join(root,name))
                    
    #print(amaFiles)
    
    return importClips(avidFiles)
    
def getMediaFiles(folderPath, clipDict,allMedia = False):
    """
    Get ama files reel names as keys and paths as values.
    
    Return {"reelName:"filename",...]
    """
    print("Getting Media Files (AMA)")
    amaFiles = {}
    numFiles=0
    for root, dirs, files in os.walk(folderPath):
        for name in files:
            if "ama" in root and (name.endswith(".mxf") or name.endswith(".MXF")):
                fileReel = extractReelName(name)
                if allMedia:
                    amaFiles[fileReel] = os.path.join(root,name)
                    #print(os.path.join(root,name))
                    numFiles+=1
                    continue
                if clipDict.get(fileReel):
                    amaFiles[fileReel] = os.path.join(root,name)
                    numFiles+=1

                    
    print(numFiles,"files found in",folderPath,"...")
    
    if allMedia:
        return importClips(amaFiles)
        
        
    return amaFiles

def getStockFolder():
    mpRoot = mediaPool.GetRootFolder()
    stock = None
    for folder in mpRoot.GetSubFolderList():
        if folder.GetName() == "stock":
            stock = folder
            break
    
    return stock

def importClips(files):
    print("Importing clips to stock...")
    mpRoot = mediaPool.GetRootFolder()
    stock = getStockFolder()

    if not stock:
        print("Creating stock folder...")
        stock = mediaPool.AddSubFolder(mpRoot,"stock")
        
    currentClipsPaths = []
    for clip in stock.GetClipList():
        currentClipsPaths.append(clip.GetClipProperty("File Path"))
    
    clipsInMD = len(currentClipsPaths)
    #files = list(files.values())
    filesNumber = len(files)
    clipsToImport=filesNumber - clipsInMD
    print(clipsInMD,"clips already in media pool..")
    print(clipsToImport, "files to import...")
    print(files[0] if len(files) > 0  else "None")
    
    
    clipsImported=0
    
    '''
    
    for file in files:
        if not file in currentClipsPaths:
            mediaPool.ImportMedia([file])
            clipsImported+=1
            print(clipsImported,"/",clipsToImport)
            
    '''
    files2Process=[]
    for file in files:
        if not file in currentClipsPaths:
            files2Process.append(file)
    
    print("Importing media...")
    
    mediaPool.ImportMedia(files2Process)
    
    print(clipsImported,"imported")
    
    return stock

def getClips(clipsList):
    print("Getting Clips (Media Pool)")
    clipDict = {}
    for clip in clipsList:
        clipName = clip.GetName()
        clipReel = extractReelName(clipName)
        clipDict[clipReel] = clip
    
    return clipDict

def getTimelineClips(clipsList):
    print("Getting Clips (Timeline)")
    clipDict = {}
    numClips=0
    for clip in clipsList:
        mpClip = clip.GetMediaPoolItem()
        if mpClip:
            clipName = mpClip.GetName()
            clipReel = extractReelName(clipName)
            if clipReel:
                clipDict[clipReel] = mpClip
                numClips+=1
    
    print(numClips,"clips found in timeline...")        
    return clipDict

def extractReelName(value: str):
    uiValues = getUIValues()
    
    fieldSep = uiValues[1]
    fieldCount = uiValues[2]

    # remove extension
    valueParts = value.split(".")
    if len(valueParts) > 1:
        valueParts = valueParts[0:len(valueParts)-1]
    clipName = ".".join(valueParts)
    fields = clipName.split(fieldSep)[0:fieldCount]
    if len(fields) != fieldCount:
        return None
    #print(fields)
    return fieldSep.join(fields)
    

def replaceClips(clips,files):
    print("Conforming clips...")
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
    
def buttonsEnabled(state):
    btConformMP = win.Find('btConformMP')
    btConformMP.Enabled = state
    btConformTL = win.Find('btConformTL')
    btConformTL.Enabled = state

##### EVENT HANDLERS #####
def OnClose(ev):
    print("Exit")
    dispatcher.ExitLoop()

def BtConformMP(ev):
    print("Processing Media Pool...")
    buttonsEnabled(False)
    clipDict = getClips(currentFolder.GetClipList())
    uiValues = getUIValues()
    amaPath = uiValues[0]
    amaDic = getMediaFiles(amaPath, clipDict)
    replaceClips(clipDict,amaDic)
    buttonsEnabled(True)
    print("Finished...")

def BtConformTL(ev):
    global currentTimeline
    print("Processing Timeline...")
    buttonsEnabled(False)
    uiValues = getUIValues()
    amaPath = uiValues[0]
    currentTimeline = currentProject.GetCurrentTimeline()
    clipDict = getTimelineClips(currentTimeline.GetItemListInTrack('video', 1))
    amaDic = getMediaFiles(amaPath,clipDict)
    replaceClips(clipDict,amaDic)
    buttonsEnabled(True)
    print("Finished...")
    
def BtImportAAF(ev):
    global currentTimeline
    buttonsEnabled(False)
    values = getUIValues()
    amaPath = values[0]
    path = values[3]
    #stock = getMediaFiles(amaPath,None,True)
    stock = getAvidMedia(settings["avidPath"])
    timelineName = ".".join(os.path.basename(path).split(".")[0:-1])
    print("Creating timeline",timelineName)
    if currentProject.SetCurrentTimeline(mediaPool.CreateEmptyTimeline(timelineName)):
        print("Importing AAF to",timelineName)
        currentTimeline = currentProject.GetCurrentTimeline()

        currentTimeline.ImportIntoTimeline(path, {
            "autoImportSourceClipsIntoMediaPool": False,
            "insertAdditionalTracks": False,
            "ignoreFileExtensionsWhenMatching": False,
            "sourceClipsFolders":[stock]})
            #"sourceClipsPath": amaPath})
    else:
        print("Failed to create the timeline",timelineName)
    buttonsEnabled(True)
    
def BtSaveSettings(ev):
    global settings
    print("Saving settings")
    values = getUIValues()
    saveSetting('amaPath',values[0])
    saveSetting('fieldSep',values[1])
    saveSetting('fieldCount',values[2])
    saveSetting('aafPath',values[3])
    settings = getSettings()


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

    importAAFLayout = ui.HGroup([
        ui.LineEdit({'ID':'txtAAFPath','Text':settings['aafPath']}),
        ui.Button({'ID':'btImportAAF','Text':'Import AAF','FixedSize':[100,30]}),
    ])
    
    extractionLayout = ui.HGroup(
        [   ui.Label({'Text':'Field Separator','FixedSize':[100,30]}),
            ui.LineEdit({'ID':'txtFieldSep','Text':settings['fieldSep']}),
            ui.HGap(5),
            ui.Label({'Text':'Field Count','FixedSize':[100,30]}),
            ui.SpinBox({'ID':'spFieldCount','Value':settings['fieldCount'],'Minimum':1,'Maximum':32,'SingleStep':1}),
        ]
    )

    vLayout = ui.VGroup(
        [ui.Label({'Text':'If you need output, goto the menu Workspace and open the Console.','Alignment':{'AlignTop' : True}}),
         ui.VGap(2),
         amaPathLayout,
         ui.VGap(2),
         extractionLayout,
         ui.VGap(2),
         ui.Button({'ID':'btSaveSettings','Text':'Save Settings'}),
         importAAFLayout,
         ui.Button({'ID':'btConformTL','Text':'Conform From Timeline'}),
         ui.Button({'ID':'btConformMP','Text':'Conform From Media Pool'})
         ]
    )

    win = dispatcher.AddWindow({'WindowTitle':'ConformMog (Rui Loureiro 2023)','ID':'testeWindow', 'MinimumSize':[600,250],'MaximumSize':[600,250]},vLayout)
    win.On.btSaveSettings.Clicked = BtSaveSettings
    win.On.btConformMP.Clicked = BtConformMP
    win.On.btConformTL.Clicked = BtConformTL
    win.On.btImportAAF.Clicked = BtImportAAF
    
    win.On.testeWindow.Close = OnClose
    
    win.Show()
    dispatcher.RunLoop()
    win.Hide()


