#!/usr/bin/env python
# See the README.txt for install
import os
import json
import csv
import datetime
from pprint import pprint
import sys
import time
import platform
#import opentimelineio as otio

from multiprocessing.shared_memory import ShareableList,SharedMemory
from multiprocessing import resource_tracker
#sys.path.append('/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules')
#import DaVinciResolveScript as dvr

class MyMpClip():
    
    def __init__(self,
                 file_name:str,
                 video_codec:str,
                 name:str,
                 recordFrame:int, # timeline clip position frame 
                 sourceIn:int, # clip cut in frame
                 sourceOut:int, # clip cut ou frame
                 startTC:str, # clip start tc
                 endTC:str, # clip end tc
                 track:int) -> None:
        
        self._properties = {
            "File Name":file_name,
            "Video Codec":video_codec,
            "Reel Name":file_name,
            "Clip Name":name,
            "Clip Color":"Apricot",
            "Start TC":startTC,
            "End TC":endTC
            
        }
        self._recordFrame = recordFrame
        self._sourceIn = sourceIn
        self._sourceOut = sourceOut
        self._track = track
        self._mpClip = self
        self._timelineClip = None
    
    def setTimelineClip(self,clip):
        self._timelineClip = clip
    
    def GetClipProperty(self,key:str=None):
        if isinstance(self._mpClip,MyMpClip):
            if key:
                return self._properties.get(key,"")
            else:
                return self._properties
        else:
            return self._mpClip.GetClipProperty(key)
        
    def SetClipProperty(self,key:str,value:any):
        if isinstance(self._mpClip,MyMpClip):
            self._properties[key] = value
        else:
            self._mpClip.SetClipProperty(key,value)
            
    def SetClipColor(self,colorName):
        colorName = "Apricot"
        if isinstance(self._mpClip,MyMpClip):
            self._properties["Clip Color"] = colorName
        else:
            if len(self._mpClip.GetClipColor()) == 0:
                self._mpClip.SetClipColor(colorName)
    
    def LinkProxyMedia(self,proxyMediaFilePath):
        if not isinstance(self._mpClip,MyMpClip):
            self._mpClip.LinkProxyMedia(proxyMediaFilePath)
    
    def GetName(self):
        return self._properties["Clip Name"]
    
    def ReplaceClip(self,filename:str):
        ret = True
        currentFolder = getMediaFolder(currentTimeline.GetName())
        binFolder = getMediaFolder("media",parent = currentFolder)
        mediaPool.SetCurrentFolder(binFolder)
        mpClips = binFolder.GetClipList() # try if clip alread exists
        clipFound = False
        try:
            if mpClips:
                for mpClip in mpClips:
                    if mpClip and mpClip.GetClipProperty("File Path") == filename:
                        mpClips = [mpClip]
                        clipFound = True
                        print_info("Clip",mpClip.GetName(),"already exists in the media folder.")
                        break
            if not clipFound:
                mpClips = mediaPool.ImportMedia([filename])
            if len(mpClips) > 0 and mpClips[0]:
                self._mpClip = mpClips[0]
                if self._timelineClip:
                    print_info("Trying to create timeline clip",self._timelineClip.GetName())
                    self._sourceIn = self._timelineClip.GetLeftOffset()
                    self._sourceOut = self._timelineClip.GetRightOffset()
                    self._recordFrame = self._timelineClip.GetStart()
                    currentTimeline.DeleteClips([self._timelineClip])
                ## Appends list of clipInfos specified as dict of "mediaPoolItem", "startFrame" (int), "endFrame" (int), (optional) "mediaType" (int; 1 - Video only, 2 - Audio only), "trackIndex" (int) and "recordFrame" (int). Returns the list of appended timelineItems.
                    clipDict = {
                        "mediaPoolItem":self._mpClip,
                        "startFrame":self._sourceIn,
                        "endFrame":self._sourceOut-1,
                        "mediaType":1,
                        "trackIndex":self._track,
                        "recordFrame":self._recordFrame
                    }
                    #pprint(clipDict)
                    timelineClips = mediaPool.AppendToTimeline([clipDict])
                    if timelineClips:
                        print_info("Timeline item",timelineClips[0].GetName(),"created.")
                    else:
                        print_error("Can't create tileline item!")
                else:
                    print_error("No timeline item!")    

            else:
                print_error("Can't import",filename)
                ret = False
        except Exception as e:
            print_error("An exception accured:",e,"\nstartFrame:",self._sourceIn,"\nendFrame:",self._sourceOut,"\ntrackIndex:",self._track,"\nrecordFrame:",self._recordFrame)
            ret = False
        finally:
            mediaPool.SetCurrentFolder(currentFolder)
        
        return ret
    

def print_error(*args,sep: str = " ", end: str = "\n"):
    print('ERROR:','',end='')
    print(*args,sep=sep,end=end)
    
   
def print_warning(*args,sep: str = " ", end: str = "\n"):
    print('WARNING:','',end='')
    print(*args,sep=sep,end=end)
    
def print_info(*args,sep: str = " ", end: str = "\n"):
    print('INFO:','',end='')
    print(*args,sep=sep,end=end)

#resolve = dvr.scriptapp("Resolve")
print_info("Python version:",sys.version)
#print("Python Path:",sys.path)
CONFORM_ALL_VERSION="2024.1.8"
RESOLVE_VERSION=resolve.GetVersion()
RESOLVE_VERSION_STRING=resolve.GetVersionString()
RESOLVE_VERSION_SUFIX=RESOLVE_VERSION_STRING.replace('.','_')
STOCK_DRB="stock_" + RESOLVE_VERSION_SUFIX + ".drb"
BLACKLIST_FILES="blacklist_files_" + RESOLVE_VERSION_SUFIX + ".json"
print_info("ConformAll version:",CONFORM_ALL_VERSION)
print_info("DaVinci Resolve Version:",RESOLVE_VERSION_STRING)
userPath = os.path.expanduser("~")
if not os.path.exists(userPath):
    print_error("User path does not exist!!!")
    exit(1)
else:
    print_info("User HOME is:",userPath)
    
settingsFile = "ConformAll.json"
settingsPath = os.path.join(userPath,"Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Settings")

settingsJson = {"projects":[{
            "project": "default",
            "mogPath" : "",
            "fieldSep" : "_",
            "fieldCount" : 5,
            "sonyPath" : "",
            "aafPath" : "",
            "avidPath" : "",
            "motionPath" : "",
            "motionFieldSep" : "_",
            "motionFieldCount" : 5,
            "exportStock" : True,
            "importStock" : True,
            "copyMediaPath" : "",
            "autoImportSourceClipsIntoMediaPool":False
            }],
            "currentProject":"default",
            "windowGeometry": { "1": 50, "2": 50, "3": 600, "4": 410 }
            }

settings = {} # project settings
currentHouseProject = ""
stockBinPath = ""

typeColor = {
    'MOG':'Orange',
    'SONY':'Violet',
    'OTHER':'Olive',
    'AUTO':'Yellow', # Media imported using the timeline import function, e.g. Edge proxy 
    'SAME':'Navy', # The High Res codec is the same of Low Res
    'NO_PROXY':'Apricot' # Used when the proxy from AAF is not imported, e.g. error importing, and we load the high resolution instead 
    
}


cancelCopyFiles = False
drScriptsPath="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts"
copyFilesPath = os.path.join(drScriptsPath,"copy_files.py")

def loadSettings():
    global currentHouseProject
    global settingsJson
    path = os.path.join(settingsPath,settingsFile)
    
    #print(path)
    if os.path.exists(path):
        with open(path,'r') as openFile:
            settingsJson = json.load(openFile)
    
    else:    
        with open(path, "w") as outfile:
            json.dump(settingsJson, outfile)
    
def getProjects():
    projects = []
    for obj in settingsJson["projects"]:
        projects.append(obj['project'])
        
    return projects

def getSettings(project):
    global settings
    for obj in settingsJson["projects"]:
        if obj['project'] == project:
            settings = obj
            return True
    
    return False

    
def saveSetting(project = None,rename = False):
    global settingsJson
    settingsJson['currentProject'] = cbProjects.CurrentText 
    settingsJson['windowGeometry'] = win.Geometry
    if project:
        values = getUIValues()
        if not getSettings(project) and not rename: # it's a new project
            settingsJson['projects'].append({'project':project})
            
        for obj in settingsJson["projects"]:
            if obj['project'] == project:
                
                if rename:
                    obj['project'] = cbProjects.CurrentText
                obj['mogPath'] = values[0]
                obj['fieldSep']=values[1]
                obj['fieldCount']=values[2]
                obj['sonyPath']=values[3]
                obj['aafPath']=values[4]
                obj['avidPath']=values[5]
                obj['motionPath']=values[6]
                obj['motionFieldSep']=values[7]
                obj['motionFieldCount']=values[8]
                obj['exportStock']=values[9]
                obj['importStock']=values[10]
                obj['copyMediaPath']=values[11]
                obj['autoImportSourceClipsIntoMediaPool']=values[12]
                break

    path = os.path.join(settingsPath,settingsFile)
    with open(path, "w") as outfile:
        json.dump(settingsJson, outfile)

def getUIValues():
    """
    Get the UI values.
    
    Return (index:value): (
        0:mogPath (string),
        1:fieldSeparator (string),
        2:fieldCount (int), 
        3:sonyPath (string), 
        4:aafPath (string),
        5:avidPath (string),
        6:motionPath (string),
        7:motionFieldSeparator (string),
        8:motionFieldCount (int),
        9:exportStock (bool),
        10:importStock (bool),
        11:copyMediaPath (string)
        12:autoImportSourceClipsIntoMediaPool (bool)
        ) Tuple
    """

    return (win.Find('txtMogPath').Text, 
            win.Find('txtFieldSep').Text, 
            win.Find('spFieldCount').Value,
            win.Find('txtSonyPath').Text,
            win.Find('txtAAFPath').Text,
            win.Find('txtAvidPath').Text,
            "","","", # retirar para usar os campos a seguir
            #win.Find('txtMotionPath').Text,
            #win.Find('txtMotionFieldSep').Text, 
            #win.Find('spMotionFieldCount').Value
            win.Find('ckExportStock').Checked,
            win.Find('ckImportStock').Checked,
            win.Find('txtCopyMediaPath').Text,
            win.Find('ckAutoImportSourceClipsIntoMediaPool').Checked                       
            )

def getEdgeProxyPath():
    avidPath = getUIValues()[5]
    avidPath = os.path.split(avidPath)
    if len(avidPath[1]) == 0: # path have a tail separator
        avidPath=os.path.split(avidPath[0])
    proxyPath = os.path.join(avidPath[0],'Proxy')
    if os.path.isdir(proxyPath):
        return proxyPath
    
    return None

def getUMEPath():
    avidPath = getUIValues()[5]
    avidPath = os.path.split(avidPath)
    if len(avidPath[1]) == 0: # path have a tail separator
        avidPath=os.path.split(avidPath[0])
    umePath = os.path.join(avidPath[0],'UME')
#    if os.path.isdir(umePath):
    return umePath
    
def importIngestSettings(path:str,importToKey:str,importFromKey:str):
    if os.path.exists(path):
        with open(path,'r') as openFile:
            ingestSettings = json.load(openFile)
            
    currentList = [x.upper() for x in settingsJson.get(importToKey,[])]
    for ext in ingestSettings.get(importFromKey,[]):
        if ext.upper() in currentList:
            continue
        currentList.append(ext)
        
    settingsJson[importToKey] = currentList
    saveSetting()


def getAvidMedia(folderPaths : list):
    
    print_info("Getting Media Files (Avid)")
    fileEndings = ["_0.MXF","V.MXF","_CC.MXF","_VFX.MXF",".pmxf"]
    avidFiles = []
    ts = time.time()
    print_info("Avid folders list:",folderPaths)
    for folderPath in folderPaths:
        if not folderPath or not os.path.exists(folderPath):
            print_error("The folder",folderPath,"does not exist. Do you forget to mount any drive?")
            continue
        isUME = os.path.basename(folderPath) == "UME"
        for root, dirs, files in os.walk(folderPath):
            for name in files:
                if not "Quarantine File" in root and not "Creating" in root and not name.startswith("."):
                    endOk = False
                    for end in fileEndings :
                        if name.upper().endswith(end.upper()):
                            endOk=True
                    if not endOk and isUME:
                        ext = os.path.splitext(name)[1]
                        if ext.upper() == ".MXF":
                            endOk = True
                    if endOk:
                        avidFiles.append(os.path.join(root,name))
            now = time.time()
            if ts + 1. < now:
                print(end=".")
                ts = now
            
    #print(amaFiles)
    print()
    print_info(len(avidFiles)," Avid MediaFiles found.")
    return importClips(avidFiles)

def getMediaFiles(folderPath:str, clipDict:dict, folderType:list):
    """
    Get ama files reel names as keys and paths as values.
    all OTHER folderType(s) must exist in the Camera Folders list
    
    Arguments:
    
        folderPath: path to the ama files root
        clipDict: timeline clips
        folderType: list like [ama] for MOG or the Camera Folders from the UI
    
    Return {"reelName":"filename",...}
    """
    print_info("Getting Media Files (AMA)")
    mimes=["." + x.upper() for x in settingsJson.get('fileExtensions',[])]
    amaFiles = {}
    numFiles=0
    uiValues = getUIValues()
    fieldSep = uiValues[1] if "ama" in folderType else None
    fieldCount = uiValues[2] if "ama" in folderType else None
    if not os.path.exists(folderPath):
        print_error("Folder",folderPath,"does not exist. Do you forget to mount any drive?")
        return amaFiles
    ts = time.time()
    for root, dirs, files in os.walk(folderPath):
        cameraFolderExits = False
        for c in folderType:
            rootArray = root.split(os.path.sep) # garante igualdade na palavra e não em parte
            if c in rootArray:
                cameraFolderExits = True
                break
        for name in files:
            filename = os.path.join(root,name)
            _,ext = os.path.splitext(filename)
            if cameraFolderExits and ext.upper() in mimes:
                fileReel = extractReelName(name, fieldSep,fieldCount)
                if clipDict.get(fileReel):
                    amaFiles[fileReel] = filename
                    numFiles+=1

        now = time.time()
        if ts + 1. < now:
            print("",end=".")
            ts = now


    print()                
    print_info(numFiles,"files found in",folderPath,"...")
        
    return amaFiles

def getMediaFolder(name, parent = None):
    """
    Get media folder with "name" from the media pool root, or from parent, if given.
    """
    mpRoot = mediaPool.GetRootFolder()
    if parent:
        mpRoot = parent
    for folder in mpRoot.GetSubFolderList():
        if folder.GetName() == name:
            return folder
    
    return None    

def getHostName():
    hostName = None
    if platform.system() == "Windows":
        hostName = platform.uname().node
    else:
        hostName = os.uname()[1]
        
    return hostName

def lockBinFile(binFilePath: str):
    print_info("Locking stock bin.")
    folder = os.path.dirname(binFilePath)
    if not os.path.exists(folder):
        print_error(f"Cant create lock file. Folder {folder} does not exist. Do you forget to mount some drive?")
        return False
    fileName = os.path.basename(binFilePath).removesuffix(".drb")
    lockFile = os.path.join(folder,fileName+".lock")
    lockDic = {}
    hostName = None
    if os.path.exists(lockFile):
        with open(lockFile,'r') as openFile:
            lockDic = json.load(openFile)
        hostName = lockDic['hostName']
        if hostName != getHostName():
            errorPopupDialog("The bin file is locked by the workstation named \"" + hostName + "\".\n" \
                "Try again later ...")
            return False
        else:
            # it's the same machine
            print_info("The stock bin it's locked but this machine is the owner of the lock.")
            return True
    
    #if not os.path.exists(binFilePath):
    #    print("Stock bin file noes not exist.")
    #    return True

    lockDic['hostName'] = getHostName()
    with open(lockFile,'x') as outfile:
        json.dump(lockDic, outfile)
    return True  
                
def unlockBinFile(binFilePath: str):
    folder = os.path.dirname(binFilePath)
    fileName = os.path.basename(binFilePath).removesuffix(".drb")
    lockFile = os.path.join(folder,fileName + ".lock")
    hostName = getHostName()
    if os.path.exists(lockFile):
        with open(lockFile,'r') as openFile:
            lockDic = json.load(openFile)
        if hostName == lockDic['hostName']:
            try:
                os.remove(lockFile)
                print_info("Stock bin lock removed.")
            except Exception as e:
                print_error(f"Some error ocurred: {e}")
                return False
        else:
            print_error("Can't unlock stock bin file! This machine is not the owner of the lock!")
            return False
    else:
        print_warning("Stock bin lock does not exist!")
    
    return True
                

def importClips(files):
    global stockBinPath
    
    print_info("Importing clips to stock...")
    uiValues = getUIValues()
    localTs = datetime.datetime.now()
    currentFolder = mediaPool.GetCurrentFolder()
    mpRoot = mediaPool.GetRootFolder()
    stock = getMediaFolder("stock")
    
    #if not stock:
    mediaPool.SetCurrentFolder(mpRoot)
    createEmptryStock = True
    if uiValues[10] and isImportExportDrbPossible():
        print_info("Trying to import stock folder...")
        mediaPool.DeleteFolders([stock])
        if os.path.exists(stockBinPath):

            try:
                if mediaPool.ImportFolderFromFile(stockBinPath):
                    stock = getMediaFolder("stock")
                    if stock:
                        print_info("Stock folder imported.")
                        createEmptryStock = False
                    else:
                        print_error("Can not create the stock folder object!")
                else:
                    print_error("Failed to import stock folder!")
            except:
                 print_error("This DaVinci Resolve version can't import the bin folder.")
        else:
            print_warning("Stock folder bin file does not exist!")
    else:
        if stock:
            print_info("Stock bin already exists...")
            createEmptryStock = False
                          
    if createEmptryStock:
        accepted,_,_ = genericPopupDialog("Do you want to import all Avid media files? This may take a while.","Yes","No",haveRejectButton=True)
        if accepted:
            print_info("Creating empty stock folder...")
            stock = mediaPool.AddSubFolder(mpRoot,"stock")
        else:
            print_error("Stock folder creation canceled.")
            return stock
    
    print_info("Getting filenames from stock folder clips...") 
    currentClipsFileNames = []
    ts = time.time()
    for clip in stock.GetClipList():
        if clip:
            currentClipsFileNames.append(clip.GetClipProperty("File Name"))
        now = time.time()
        if ts + 1. < now:
            print("",end=".")
            ts = now
    print()
        
    clipsInMP = len(currentClipsFileNames)
    filesNumber = len(files)
    if filesNumber == 0:
        print_warning("There is no files to import!")
        return stock
    
    #clipsToImport=filesNumber - clipsInMP
    print_info(clipsInMP,"clips already in media pool..")
    print_info("Preparing list of files to import.")
    bmd.wait(0.2)
    #print(files[0] if len(files) > 0  else "None")
        
    files2Process=[]
    blacklist = loadBlacklistFiles(os.path.join(getUIValues()[5],BLACKLIST_FILES))
    print_info(len(blacklist),"files in blacklist.")
    ts = time.time()
    for file in files:
        basename = os.path.basename(file)
        if not basename in currentClipsFileNames:
            if file not in blacklist:
                files2Process.append(file)
        now = time.time()
        if ts + 1. < now:
            print("",end=".")
            ts = now
    print()
    print_info(len(files2Process), "files to import...")
    clips2ImportCounter = len(files2Process)
    
    mediaPool.SetCurrentFolder(stock)
    l_pointer=0
    r_pointer=0
    importedClips=[]
    step=1000
    print_info("Importing media (",step," files each step)...",sep="")
    for l_pointer in range(0,clips2ImportCounter,step):
        r_pointer = l_pointer + step
        if r_pointer > clips2ImportCounter:
           r_pointer = clips2ImportCounter 
        print_info("Importing from index ",l_pointer," to index ",r_pointer-1,".\t",clips2ImportCounter - l_pointer," files remaining...",sep="")
        bmd.wait(0.2)
        importedClips += mediaPool.ImportMedia(files2Process[l_pointer:r_pointer])

    mediaPool.RefreshFolders()
    print_info("Creating blacklist...")
    blacklist = createBlackListFiles(importedClips,files2Process,blacklist)
    print_info(len(blacklist),"files in blacklist.")
    
    if not isImportExportDrbPossible():
        genericPopupDialog("This DaVinci Resolve version ("+ RESOLVE_VERSION_STRING + "), can not export the stock bin folder.\nPlease, do it manualy if you want to.",
            "Ok")


    if (uiValues[9] or isDrbTodayFirstExport()) and isImportExportDrbPossible():
        print_info("Trying to export stock bin...")
        try:
            if stock.Export(stockBinPath):
                print_info("Stock bin exported...")
            else:
                print_error("Failed to export stock bin!")
        except:
            print_error("This DaVinci Resolve version can't export the bin folder.")
        
    mediaPool.SetCurrentFolder(currentFolder)
    if not importedClips:
        return stock
    print_info(len(importedClips),"clips imported of",clips2ImportCounter)   
    dt = datetime.datetime.now() - localTs
    print_info("Processed in",str(dt))
    return stock

def createBlackListFiles(importedClips:list,files2Process:list,blacklist_par:list=None):
    """
    Create a json file with a list of filenames that can not be imported to the media pool.
    
    Arguments:
        importedClips: A list of imported MediaPoolItems.
        files2Process: A list of filenames to import to the media pool.
        blacklist_par: A list of already loaded existing blacklist
        
    Returns:
        The blacklist.
    """
    localFiles2Process = files2Process.copy()
    blacklist = blacklist_par
    blackListFileName = os.path.join(getUIValues()[5],BLACKLIST_FILES)
    if not blacklist:
        blacklist = loadBlacklistFiles(blackListFileName)
    
    # remove processed files from localFiles2Process
    # remaining files are the import errors
    for clip in importedClips:
        clipFilename = clip.GetClipProperty("File Path")
        if clipFilename in localFiles2Process:
            localFiles2Process.remove(clipFilename)
            
    for file in localFiles2Process:
        if file not in blacklist:
            blacklist.append(file)
            
    blacklistJson = {
        'files': blacklist
    }    
    with open(blackListFileName,'w') as f:
        json.dump(blacklistJson,f)
        
    return blacklist
        
def loadBlacklistFiles(blackListFileName:str):
    blacklist = []
    if os.path.exists(blackListFileName):
        with open(blackListFileName,'r') as f:
            blacklistJson = json.load(f)
            blacklist= blacklistJson.get('files',[])
    return blacklist


def getTimelineClips():
    global currentTimeline    
    clips = []
    currentTimeline = currentProject.GetCurrentTimeline()
    videoTracks = currentTimeline.GetTrackCount('video')
    print_info('Video tracks in timeline:',videoTracks)
    for i in range(1,videoTracks+1):
        print_info("Getting clips from track",i)
        for clip in currentTimeline.GetItemListInTrack('video', i):
            clips.append((clip,i))
            
    return clips

def getTimelineClipFromEditIndex():
    global currentTimeline    
    currentTimeline = currentProject.GetCurrentTimeline()
    csv_path = os.path.join(os.path.expanduser("~"),"timeline.csv")
    if os.path.exists(csv_path):
        os.remove(csv_path) # remove to avoid false readings
    currentTimeline.Export(csv_path, resolve.EXPORT_TEXT_CSV, resolve.EXPORT_MISSING_CLIPS)
    if not os.path.exists(csv_path):
        print_error("Edit Index failed to export!")
        return {}
    with open(csv_path,encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)
                
        data = {}
        for rows in csv_reader:
            track = rows['V']
            if track.startswith("V"):
                rec_in = tc2Frames(rows['Record In'])
                rec_out = tc2Frames(rows['Record Out'])
                source_in = tc2Frames(rows['Source In'])
                source_out = tc2Frames(rows['Source Out'])
                key = (int(track[1:]),rec_in)

                if not data.get(key,False):
                    data[key] = MyMpClip(rows["Reel"],
                                         rows["Codec"],
                                         rows["Name"],
                                         key[1],
                                         source_in, 
                                         source_out,
                                         rows['Source Start'],
                                         rows['Source End'],
                                         key[0])
        print_info(f"Edit index have {len(data)} records.")
        return data

def getMpClipsFromTimeline(resolution:str = 'all'): 
    """
        Return all media pool clips don't matter the media type.
        
        Arguments:
            resolution: one of 'all','high' or 'proxy'
    """
    resolution = 'codecs' if resolution == 'high' else resolution
    resolution = 'codecsProxy' if resolution == 'proxy' else resolution
    
    timelineClips = getTimelineClips()
    clips = []
    currentList = [x.upper() for x in settingsJson.get(resolution,[])]
    for clip in timelineClips:
        mpClip = clip[0].GetMediaPoolItem()
        if mpClip:
            codec = mpClip.GetClipProperty("Video Codec")
            if len(currentList) > 0 and codec.upper() in currentList:
                clips.append(mpClip)
            
    return clips

def getTimelineClipsMog(clipsList, timeline_names_reels):
    """
    Arguments:
        clipsList: timeline clips list
        
    Returns a dict as {"clipReel":(<media pool clip>,'MOG',<timelineClip>),....}
    """
    print_info("Getting MOG Clips...")
    clipDict = {}
    numClips=0
    numClipsEditIndex=0
    uiValues = getUIValues()
    fieldSep = uiValues[1]
    fieldCount = uiValues[2]
    #pprint(timeline_names_reels)
    for clip_tuple in clipsList:
        clip = clip_tuple[0]
        track = clip_tuple[1]
        mpClip = clip.GetMediaPoolItem()
        if mpClip:
            if len(mpClip.GetClipProperty("Clip Color")) == 0:
                # Try to extract the reel name from the clipname
                clipName = mpClip.GetName()
                clipReel = extractReelName(clipName,fieldSep,fieldCount)
                #clipReel = mpClip.GetClipProperty("Reel Name")
                if clipReel:
                    clipDict[clipReel] = (mpClip,'MOG',clip)
                    numClips+=1
                else:
                    # Try to get the reel name insted 
                    clipReel = extractReelName(mpClip.GetClipProperty("Reel Name"),fieldSep,fieldCount)
                    if clipReel:
                        clipDict[clipReel] = (mpClip,'MOG',clip)
                        numClips+=1
        else:
            tcIn = clip.GetStart()
            print_warning("Trying to get the reel name from the edit index with timeline clip name",clip.GetName())
            mpClip = timeline_names_reels.get((track,tcIn),False)
            if mpClip:
                mpClip.setTimelineClip(clip)
                clipReel = extractReelName(mpClip.GetClipProperty("Reel Name"),fieldSep,fieldCount)
                if clipReel:
                    print_info("Adding reel name from edit index:",clipReel)
                    clipDict[clipReel] = (mpClip,'MOG',clip)
                    numClips+=1
                    numClipsEditIndex+=1
            else:
                print_error("No edit index found for that timeline clip!")
    
    print_info(numClips,"not corformed clips found in timeline.",numClipsEditIndex,"clips detected with edit index...")        
    return clipDict if numClips > 0 else None

def getTimelineClipsOthers(clipsList,clipType,timeline_names_reels):
    """
    Arguments:
        clipsList: timeline clips list
        clipType: clipType
        
    Returns a dict as {clipReel: (<media pool clip>,clipType,timelineClip),...}
    """
    mimes=["." + x.upper() for x in settingsJson.get('fileExtensions',[])]
    print_info("Getting " + clipType + " Clips...")
    clipDict = {}
    numClips=0
    numClipsEditIndex=0
    for clip_tuple in clipsList:
        clip = clip_tuple[0]
        track = clip_tuple[1]
        mpClip = clip.GetMediaPoolItem()
        if mpClip:
            if len(mpClip.GetClipProperty("Clip Color")) == 0:

                clipReel = mpClip.GetClipProperty("Reel Name")
                if not clipReel:
                    clipReel = extractReelName(mpClip.GetClipProperty("File Name"))

                if clipReel:
                    # remove extension from the reel name, if exists
                    reelNoExt,reelExt = os.path.splitext(clipReel)
                    if reelExt.upper() in mimes:
                        clipReel = reelNoExt
                    clipDict[clipReel] = (mpClip,clipType,clip)
                    numClips+=1
        else:
            tcIn = clip.GetStart()
            print_warning("Trying to get the reel name from the edit index with timeline clip name",clip.GetName())
            mpClip = timeline_names_reels.get((track,tcIn),False)
            if mpClip:
                mpClip.setTimelineClip(clip)
                clipReel = mpClip.GetClipProperty("Reel Name")
                if not clipReel:
                    clipReel = extractReelName(mpClip.GetClipProperty("File Name"))
                if clipReel:
                    print_info("Adding reel name from edit index:",clipReel)
                    clipDict[clipReel] = (mpClip,clipType,clip)
                    numClips+=1
                    numClipsEditIndex+=1
            else:
                print_error("No edit index found for that timeline clip!")
        
    #if numClips > 0:
    #    pprint(clipDict)
    #print_info(numClips,"not corformed clips found in timeline...")    
    print_info(numClips,"not corformed clips found in timeline.",numClipsEditIndex,"clips detected with edit index...")       
    return clipDict if numClips > 0 else None

def getMpClipFromReelName(reelName:str,stockClipList:list):
    
    for mpClip in stockClipList:
        if mpClip.GetClipProperty("Reel Name") == reelName:
            return mpClip
        
 
def removeExtension(path):
    valueParts = path.split(".")
    if len(valueParts) > 1:
        valueParts = valueParts[0:len(valueParts)-1]
        
    return ".".join(valueParts)

def extractReelName(value: str, fieldSep = None, fieldCount = None):

    # remove extension
    clipName = removeExtension(value)
    if fieldSep == None and fieldCount == None: # is sony
        return clipName
    fields = clipName.split(fieldSep)[0:fieldCount]
    if len(fields) != fieldCount:
        return None
    #print(fields)
    return fieldSep.join(fields)
    
def changeClipsColorOnAutoImportSourceClipsIntoMediaPool():
    timelineClips = getTimelineClips()
    for clip in timelineClips:
        mpClip = clip[0].GetMediaPoolItem()
        if mpClip:
            mpClip.SetClipColor(typeColor['AUTO'])
        
def getTimelineCodecs():
    timelineClips = getTimelineClips()
    codecs=[]
    for clip in timelineClips:

        mpClip = clip[0].GetMediaPoolItem()
        if mpClip:
            codec = mpClip.GetClipProperty("Video Codec")
            if codec not in codecs:
                codecs.append(codec)
            
    return codecs

def replaceClips(timelineClips:dict,files:dict):
    print_info("Conforming clips...")
    currentFolder = getMediaFolder(currentTimeline.GetName())
    binFolder = getMediaFolder("media",parent = currentFolder)
    if not binFolder:
        binFolder = mediaPool.AddSubFolder(currentFolder,"media")
        
    counter = 0
    clips2Move=[]
    clipType = None
    for key in timelineClips.keys():
        c = timelineClips.get(key)
        mpClip = c[0]
        clipType = c[1]
        timelineClip=c[2]
        timelineClipName = timelineClip.GetName()
        proxyClipFileName=mpClip.GetClipProperty("File Name") 
        proxyClipPath=mpClip.GetClipProperty("File Path")
        proxyCodec=mpClip.GetClipProperty("Video Codec")

        clipName = mpClip.GetName()
        file = files.get(key)
        #print(file)
        if file:
            oldStartTc = mpClip.GetClipProperty("Start TC")
            oldStartTCSplit = oldStartTc.split(":")
            if oldStartTCSplit[0] == "24":
                mpClip.SetClipProperty("Start TC","00:" + oldStartTCSplit[1] + ":" + oldStartTCSplit[2] + ":" + oldStartTCSplit[3])
                oldEndTC = mpClip.GetClipProperty("End TC")
                oldEndTCSplit = oldEndTC.split(":")
                oldEndHour = int(oldEndTCSplit[0])
                newEndHour = oldEndHour - 24
                mpClip.SetClipProperty("End TC",str(newEndHour) + ":" + oldEndTCSplit[1]  + ":" + oldEndTCSplit[2] + ":" + oldEndTCSplit[3])
                print_info("TC for",mpClip.GetName(),"is now",mpClip.GetClipProperty("Start TC"),"->",mpClip.GetClipProperty("End TC"))
    
            if mpClip.ReplaceClip(file):
                bmd.wait(0.1)
                if proxyCodec == mpClip.GetClipProperty("Video Codec") and not isinstance(mpClip,MyMpClip):
                    print_warning("New and old files have de same codec.")
                    mpClip.ReplaceClip(proxyClipPath)
                    bmd.wait(0.1)
                    mpClip.SetClipProperty("Scene",timelineClipName)
                    mpClip.SetClipColor(typeColor["SAME"])
                    continue    
                
                counter+=1
                mpClip.LinkProxyMedia(proxyClipPath)
                mpClip.SetClipColor(typeColor[clipType])
                mpClip.SetClipProperty("Scene",timelineClipName) 
                #mpClip.SetClipProperty("Reel",key) 

                clips2Move.append(mpClip)
                
                print_info("Clip",clipName,"replaced")
            else:
                print_error("Error replacing",clipName,"with",file)
    
    
    mediaPool.MoveClips(clips2Move,binFolder)
    mediaPool.SetCurrentFolder(currentFolder)
    print_info(str(counter)," clips conformed.")
        
    return counter

def getMpClipMyName(name:str,mediaFolder):
    for clip in mediaFolder.GetClipList():
        if name == clip.GetName():
            return clip
        
    return None
    

def insertReferences():
    global currentTimeline
    
    currentTimeline = currentProject.GetCurrentTimeline()
    filename = removeExtension(getUIValues()[4])
    audioFile = filename + ".wav"
    if not os.path.exists(audioFile):
        audioFile = filename + ".WAV"
        if not os.path.exists(audioFile):
            audioFile = None
    
    videoFile = filename + ".mxf"
    if not os.path.exists(videoFile):
        videoFile = filename + ".MXF"
        if not os.path.exists(videoFile):
            videoFile = None
    
    if audioFile:
        print_info("Inserting reference audio...")
        audioClip = mediaPool.ImportMedia([audioFile])[0]
        appendedClips = mediaPool.AppendToTimeline(audioClip)
        if len(appendedClips) == 0:
            print_error("Failed to add reference audio!")
        else:
            print_info("Reference audio added...")    
    else:
        print_warning("Reference audio file does not exist")
        
    if videoFile:
        print_info("Inserting reference video...")
        if currentTimeline.AddTrack('video'):
            trackCount = currentTimeline.GetTrackCount('video')
            videoClip = mediaPool.ImportMedia([videoFile])[0]
            if videoClip:
                clipDic = {
                    "mediaPoolItem":videoClip,
                    "startFrame":0,
                    "endFrame":videoClip.GetClipProperty("End"),
                    "mediaType":1,
                    "trackIndex":trackCount,
                    "recordFrame":currentTimeline.GetStartFrame()
                }
                appendedClips = mediaPool.AppendToTimeline([clipDic])
            if len(appendedClips) == 0:
                print_error("Failed to add reference video!")
            else:
                print_info("Reference video added...")
        else:
            print_error("Failed to create video track!")
    else:
        print_warning("Reference video file does not exist")
        
    currentTimeline.SetCurrentTimecode(currentTimeline.GetStartTimecode())
    
def buttonsEnabled(state,exceptions:list=[]):
    exceptions.append('mainWindow')
    exceptions.append('MyStack')
    if state:
        win.On.mainWindow.Close = OnClose
    else:
        win.On.mainWindow.Close = None
    for obj in win.GetItems().values():
        #if obj.ID in exceptions:
        #    print(obj.ID)
        if obj.ID not in exceptions:
            obj.Enabled = state

def fileExists(filePath, extraText = ""):
    if not os.path.exists(filePath):
        errorPopupDialog("The file " + filePath + " does not exists.")
        return False
    
    return True

def tc2Frames(tc:str):
    
    """
    Returns a timecode string in frames (int)
    """
    tc = tc.replace(".",":")
    tc = tc.replace(";",":")
    tc_list = tc.split(":")
    
    hours = int(tc_list[0])
    minuts = int(tc_list[1])
    seconds = int(tc_list[2])
    frames = int(tc_list[3])
    
    fps = int(currentProject.GetSetting("timelineFrameRate"))
    
    tc_frames = hours * 60 * 60 * fps + minuts * 60 * fps + seconds * fps + frames
    
    return tc_frames
    
    
def isOnStockFolder():
    if mediaPool.GetCurrentFolder().GetName() == "stock":
        errorPopupDialog("You can not do this operation inside the stock folder/bin.\nPlease choose another folder/bin")
        return True
    
    return False

def isNotTimelineSelected():
    if not currentProject.GetCurrentTimeline():
        errorPopupDialog("Please, select a timeline or import a AAF.")
        return True
    
    return False

def isEditPage():
    page = resolve.GetCurrentPage()
    if page != "edit":
        errorPopupDialog("Please go to the Edit page")
        return False
    
    return True

def isCopyMediaOk():
    if isNotTimelineSelected():
        return False,False
    
    mediaPath = getUIValues()[11]
    if not os.path.exists(mediaPath):
        errorPopupDialog("The new media path \"" + mediaPath + "\" does not exist. Please choose a valid path.")
        return False,False
    
    currentFolder = getMediaFolder(currentTimeline.GetName())
    binFolder = getMediaFolder("media",parent = currentFolder)
    if not binFolder:
        errorPopupDialog('The "media" folder (bin) does not exists. Please conform media before copy media.')
        return False,False
    
    return mediaPath,binFolder

def isReelNameSelected(clipDict):
    if len(clipDict.keys()) == 0: # does not matter if does no have clips
        return True
    
    for v in clipDict.values():
        if v[0].GetClipProperty("Reel Name"):
            return True    
    
    errorPopupDialog("No Reel Names Found.\n" \
    "The reel names need to be activated in the Project Settings.\n" \
    "Please goto File->Project Settings...->General Options\n" \
    "In the Conform Options section select:\n" \
    "- Assist using reel names from the:\n" \
    "-- Embedding in source clip file")
    
    return False
    
def isImportExportDrbPossible():
    version = str(RESOLVE_VERSION[0])+str(RESOLVE_VERSION[1])
    #print(version)
    return (int(version) >= 185)

def isDrbTodayFirstExport():

    fileDate = None if not os.path.exists(stockBinPath) else datetime.datetime.fromtimestamp(os.path.getmtime(stockBinPath)).date()
    today = datetime.datetime.now().date()    
    if fileDate != today:
        accept,_,_ = genericPopupDialog("The stock folder has not yet been exported today. Last export date is " + str(fileDate) + ".\nDo you want to export the stock folder?","Yes","No",haveRejectButton=True)
        return accept
        
    return False
    
def areFoldersOk():
    """
    Get the UI values.
    
    Return (index:value): (
        0:mogPath (string),
        1:fieldSeparator (string),
        2:fieldCount (int), 
        3:sonyPath (string), 
        4:aafPath (string),
        5:avidPath (string),
        6:motionPath (string),
        7:motionFieldSeparator (string),
        8:motionFieldCount (int),
        9:exportStock (bool),
        10:importStock (bool),
        11:copyMediaPath (string)
        12:autoImportSourceClipsIntoMediaPool (bool)
        ) Tuple
    """
    
    ui_values = getUIValues()
    msg = ""
    ret = True
    if not os.path.exists(ui_values[0]):
        ret = False
        msg += f"The Mog Path {ui_values[0]} does not exist.\n"
    if not os.path.exists(ui_values[0]):
        ret = False
        msg += f"The Sony Path {ui_values[3]} does not exist.\n"
    if not os.path.exists(ui_values[0]):
        ret = False
        msg += f"The Avid Path {ui_values[5]} does not exist.\n"
    if not os.path.exists(ui_values[0]):
        ret = False
        msg += f"The Edit Storage Path {ui_values[11]} does not exist.\n"
    if not ret:
        msg += "\nDo you forget to mount any drive?"
        accept,_,_ = genericPopupDialog(msg,"Continue","Exit",haveRejectButton=True)
        ret = accept
    
    return ret

    

def timelineExists(timelineName:str):
    for i in range(1,currentProject.GetTimelineCount()+1):
        if currentProject.GetTimelineByIndex(i).GetName() == timelineName:
            return True
    
    return False

def working(command:str="start"):
    """
        Start and stop the working script that prints progress points in the console.
        
        Arguments:
        
            command: String. command to send. May be 'start' (default), 'stop'.
    """
    if command == "start":
        sl = None;
        scriptPath=os.path.join(drScriptsPath,"working.py")
        resource_tracker.ensure_running()
        try:
            SharedMemory(name='ConformAllWorking').unlink()
            print_warning("Shared Memory removed")
        except: 
            print_warning("Shared Memory does not exist")                       
        finally:
            sl = ShareableList([False],name='ConformAllWorking')
        bmd.wait(0.1)
        fu.RunScript(scriptPath)
    elif command == "stop":
        sl = ShareableList(name='ConformAllWorking')
        sl[0] = True
        bmd.wait(0.1)
        sl.shm.close()
        

##### EVENT HANDLERS #####
def OnClose(ev):
    saveSetting(currentHouseProject)
    print_info("Exit")
    fu.ShowConsole(False)
    dispatcher.ExitLoop()

def BtConformMog(ev):
    if not isEditPage():
        return False
    if isNotTimelineSelected() or isOnStockFolder():
        return False
    print_info("Processing MOG...")
    buttonsEnabled(False)
    uiValues = getUIValues()
    mogPath = uiValues[0]
    maxRetries = 30
    retry = 0
    result = True
    mogDic = None
    timeline_names_reels = getTimelineClipFromEditIndex()
    while retry < maxRetries and result:
        retry+=1
        print_info(f"Retry {retry} of {maxRetries}")
        timelineClipDict = getTimelineClipsMog(getTimelineClips(),timeline_names_reels)

        if timelineClipDict and isReelNameSelected(timelineClipDict):
            if not mogDic:
                mogDic = getMediaFiles(mogPath,timelineClipDict,["ama"])
            result = replaceClips(timelineClipDict,mogDic) > 0
        else:
            result = False
        
    buttonsEnabled(True)
    print_info("Finished MOG conforming...")
    return True
    
def BtConformCameras(ev):
    who = ev['who']
    clipType = "SONY"
    folderType = ["CLIP","Clip"]
    if who == 'btConformOthers':
        clipType = "OTHER"
        folderType = settingsJson.get('cameras',[])

    if not isEditPage():
        return False
    if isNotTimelineSelected() or isOnStockFolder():
        return False
    print_info("Processing " + clipType + "...")
    buttonsEnabled(False)
    maxRetries = 30
    retry = 0
    result = True
    sonyDic = None
    sonyPath = getUIValues()[3]
    timeline_names_reels = getTimelineClipFromEditIndex()
    while retry < maxRetries and result:
        retry+=1
        print_info(f"Retry {retry} of {maxRetries}")
        timelineClips = getTimelineClips()
        clipDict = getTimelineClipsOthers(timelineClips,clipType,timeline_names_reels)
        if clipDict and isReelNameSelected(clipDict):
            if not sonyDic:
                sonyDic = getMediaFiles(sonyPath, clipDict,folderType)
            result = replaceClips(clipDict,sonyDic) > 0
        else:
            result = False
        
    buttonsEnabled(True)
    print_info("Finished",clipType,"conforming...")
    return True
    
def BtConformAll(ev):
    if not isEditPage():
        return
    print_info("Conforming all media types...")
    if BtConformCameras({'who':'btConformSony'}):
        if BtConformCameras({'who':'btConformOthers'}):
            BtConformMog(None)
    
def otioTransform(path):
    filePath,_ = os.path.splitext(path)
    otioPath = filePath + ".otio"
    currentTimeline = currentProject.GetCurrentTimeline()
    currentTimeline.Export(otioPath,resolve.EXPORT_OTIO)
    
    timeline = otio.adapters.read_from_file(otioPath)
    print_info("Reading timeline")
    if timeline:
        for clip in timeline.each_clip():
            print_info('============================================================')
            print_info(clip.name)
            for fx in clip.effects:
                if fx.metadata:
                    if fx.metadata['Resolve_OTIO']['Effect Name'] == 'Retime and Scaling':
                        fx.metadata['Resolve_OTIO']['Enabled'] = False
                        print_info(fx.metadata)
                        
    aafFile,_ = os.path.splitext(path)    
    aafFile += "_otio.otio"      
    otio.adapters.write_to_file(timeline,aafFile)               
    #Export(fileName, resolve.EXPORT_OTIO, exportSubtype)
    #thisClip = currentTimeline.GetCurrentVideoItem()
    #if thisClip.ResetNode(1):
    #    print("Clip reseted")
    #    
    #if thisClip.GetFusionCompCount() > 0:
    #    comp = thisClip.GetFusionCompByIndex(1)
    #    tools = comp.GetToolList()
    #    for tool in tools.values():
    #        pprint(tool.GetData())
    
    return aafFile
def otioExport(path:str):
    pass
def BtImportAAF(ev):
    global currentTimeline,stockBinPath
    values = getUIValues()
    if not isImportExportDrbPossible():
        accept,_,_ = genericPopupDialog("This DaVinci Resolve version (" + RESOLVE_VERSION_STRING + "), can not import the stock bin folder. \
            \nDo you want to cancel the operation and import the stock bin folder manualy?",
            "Yes, cancel the operation","No, continue with the operation",haveRejectButton=True)
        if accept:
            return
    stockBinPath = os.path.join(getUIValues()[5],STOCK_DRB)
    if not isEditPage():
        return
    if isOnStockFolder():
        return
    if not lockBinFile(stockBinPath):
        return
    buttonsEnabled(False)
    
    path = values[4]
    if not os.path.exists(path):
        print_error("AAF file does not exists!")
        buttonsEnabled(True)
        unlockBinFile(stockBinPath)
        return
    timelineName = ".".join(os.path.basename(path).split(".")[0:-1])
    if timelineExists(timelineName):
        print_error("The timeline",timelineName,"already exists!")
        buttonsEnabled(True)
        unlockBinFile(stockBinPath)
        return
    autoImportSourceClipsIntoMediaPool=values[12]
    stock = None
    if not autoImportSourceClipsIntoMediaPool:
        stock = getAvidMedia([values[5],getEdgeProxyPath(),getUMEPath()])
        if not stock:
            return
        clips = stock.GetClipList()
        if len(clips) == 0:
            print_warning("There is no clips in stock folder!")
            if not autoImportSourceClipsIntoMediaPool:
                autoImportSourceClipsIntoMediaPool,_,_ = genericPopupDialog("There is no clips in stock folder!\nDo you want link to source camera files?","Yes","No",haveRejectButton=True)
            if not autoImportSourceClipsIntoMediaPool:
                buttonsEnabled(True)
                unlockBinFile(stockBinPath)
                return
        if not autoImportSourceClipsIntoMediaPool:
            print_info("Stock folder have",len(clips),"clips.")

    binFolder = getMediaFolder(timelineName)
    if not binFolder:
        mpRoot = mediaPool.GetRootFolder()
        binFolder = mediaPool.AddSubFolder(mpRoot,timelineName)
    
    if not mediaPool.SetCurrentFolder(binFolder):
        print_error("Can't select the bin folder")
        buttonsEnabled(True)
        unlockBinFile(stockBinPath)
        return
    
    
    print_info("Creating timeline",timelineName)
    bmd.wait(2)
    timeline = mediaPool.CreateEmptyTimeline(timelineName)
    bmd.wait(2)
    #pprint(timeline.GetSetting())
    sourceClipsFolders = [stock] if stock else []
    importDict={
    "linkToSourceCameraFiles":False,
    "autoImportSourceClipsIntoMediaPool":autoImportSourceClipsIntoMediaPool,
    "insertAdditionalTracks":False,
    "useSizingInfo":True
    }
    if not autoImportSourceClipsIntoMediaPool:
        importDict["sourceClipsFolders"] = [stock]  
    print_info("Importing AAF into timeline...")
    if not timeline.ImportIntoTimeline(path,importDict):
        print_error("Failed to import the timeline",timelineName)
        print_error("Please confirm the timeline creation frame rate in the project settings.")
    
    #timeline = mediaPool.ImportTimelineFromFile(path, {
    #    "timelineName":timelineName,
    #    "importSourceClips":False,
    #    "sourceClipsFolders":[stock]
    #    })
    #if not timeline:
    #    print("Failed to import the timeline",timelineName)
    else:
        if currentProject.SetCurrentTimeline(timeline):
            print_info("Timeline created. Inserting references...")
            insertReferences()
            if autoImportSourceClipsIntoMediaPool:
                changeClipsColorOnAutoImportSourceClipsIntoMediaPool()
                currentFolder = getMediaFolder(currentTimeline.GetName())
                binFolder = getMediaFolder("media",parent = currentFolder)
                if not binFolder:
                    binFolder = mediaPool.AddSubFolder(currentFolder,"media")
                    clips2Move = getMpClipsFromTimeline(resolution='high')
                    
                    mediaPool.MoveClips(clips2Move,binFolder)
                    mediaPool.SetCurrentFolder(currentFolder)
        
            print_info("Trying to change TCs of offline clips, if any...")
            timeline_names_reels = getTimelineClipFromEditIndex()
            #clips_count=0
            stockClipList = None

            for clip_tuple in getTimelineClips():
                #clips_count+=1
                #print("Clips count",clips_count)
                clip = clip_tuple[0]
                track = clip_tuple[1]
                mpClip = clip.GetMediaPoolItem()
                if not mpClip:
                    tcIn = clip.GetStart()
                    mpClip = timeline_names_reels.get((track,tcIn),False)
                    if mpClip:
                        startFrame = mpClip.GetClipProperty("Start TC")
                        if startFrame == "24:00:00:00":
                            #print(startFrame)
                            mpClip.setTimelineClip(clip)
                            clipReel = mpClip.GetClipProperty("Reel Name")
                            #print("mClip")
                            if not clipReel:
                                #print("extractReelName")
                                clipReel = extractReelName(mpClip.GetClipProperty("File Name"))
                            if clipReel:
                                #print("getMpClipFromReelName")
                                print_info("Edit Index clip",clipReel,"have",startFrame,"Start TC. Getting the media pool clip...")
                                if not stockClipList:
                                    stock = getMediaFolder("stock")
                                    stockClipList = stock.GetClipList()
                                mpClip = getMpClipFromReelName(clipReel,stockClipList)
                                if mpClip:
                                    #print("checking TC")
                                    mpClip.SetClipProperty("Start TC","24:00:00:00")
                                    oldEndTC = mpClip.GetClipProperty("End TC")
                                    oldEndTCSplit = oldEndTC.split(":")
                                    oldEndHour = int(oldEndTCSplit[0])
                                    newEndHour = oldEndHour + 24
                                    mpClip.SetClipProperty("End TC",str(newEndHour) + ":" + oldEndTCSplit[1]  + ":" + oldEndTCSplit[2] + ":" + oldEndTCSplit[3])
                                    print_info("TC for",mpClip.GetName(),"is now",mpClip.GetClipProperty("Start TC"),"->",mpClip.GetClipProperty("End TC"))
    
                 
        else:
            print_error("Failed to set ",timelineName," as the current timeline",timelineName)
    
    print_info("AAF import finished...")
    buttonsEnabled(True)
    unlockBinFile(stockBinPath)
    
def ProjectChanged(ev):
    global currentHouseProject
    global win
    saveSetting(currentHouseProject)
    currentHouseProject = cbProjects.CurrentText
    loadSettings()
    getSettings(currentHouseProject)
    print_info("Current project is",currentHouseProject)
    
    #TODO: ver isto melhor, não deviar ter que reconstruir a window
    win.Hide()
    win = MainWindow()
    win.Show()

def DeleteProject(ev):
    global currentHouseProject
    global settingsJson
    
    if cbProjects.CurrentIndex == 0:
        print_error("Default project can not be deleted!")
        return
    print_info("Deleting project",currentHouseProject)
    oldSettings = settings
    idx = cbProjects.CurrentIndex
    currentHouseProject = None
    cbProjects.CurrentIndex = idx-1
    settingsJson['projects'].remove(oldSettings)

    
def AddProject(ev):
    global currentHouseProject
    newName = win.Find("txtNewProject").Text
    projects = getProjects()
    if newName in projects:
        print_error("Project",newName,"already exist!")
        return
    cbProjects.AddItem(newName)
    currentHouseProject = newName
    cbProjects.CurrentText = newName
    
def RenameProject(ev):
    newName = win.Find("txtNewProject").Text
    projects = getProjects()
    if newName in projects:
        print_error("Project",newName,"already exist!")
        return
    oldName = cbProjects.CurrentText
    cbProjects.ItemText[cbProjects.CurrentIndex] = newName
    saveSetting(oldName,rename=True)
    
def OnCopyMedia(ev):
    global currentProject, currentTimeline, mediaPool
    extraText = "\nThis file is needed to perform this operation."
    if not fileExists(copyFilesPath,extraText):
        return
    
    mediaPath, mediaFolder = isCopyMediaOk()

    if mediaPath and mediaFolder:
        mediaFolderName = mediaFolder.GetName()
        bt = win.Find(ev['who'])
        buttonsEnabled(False,[bt.ID])
#        bmd.wait(2)
#       buttonsEnabled(True)
#        return

        sl = None;
        resource_tracker.ensure_running()
        try:
            SharedMemory(name='ConformAllCopyMedia').unlink()
            print_warning("Shared Memory removed")
        except: 
            print_warning("Shared Memory does not exist")                       
        finally:
            sl = ShareableList([False,False,mediaPath,mediaFolderName,0],name='ConformAllCopyMedia')
        bmd.wait(0.1)

        fu.RunScript(copyFilesPath) # run child process
        bt.Text = "Cancel"
        bt.Events = {'Clicked':False}
        bmd.wait(0.5) # wait to child processs updates shm
        ts = datetime.datetime.now()
        while True:
            finished=sl[1]
            if finished:
                break
            if bt.Down:
                sl[0]=True
                bt.Text = "Canceling..."
                bt.Enabled = False
                print_info(' Canceling...\n')
                bmd.wait(0.5) # Wait to write in shm 

            bmd.wait(0.0001)
        #print(sl.shm.name)
        relinkedClips = sl[4]
        sl.shm.close()
        #sl.shm.unlink()
        if relinkedClips > 0:
            pm.SaveProject()
            currentProjectName = currentProject.GetName()
            pm.CloseProject(currentProject)
            currentProject = pm.LoadProject(currentProjectName)
            print_info("Current DaVinci Resolve project:",currentProject.GetName())
            currentTimeline = currentProject.GetCurrentTimeline()
            mediaPool = currentProject.GetMediaPool()
        dt = datetime.datetime.now() - ts
        print_info("Processed in",str(dt))
        print_info('Finished copying files.')
        bt.Text = "Copy Media"
        bt.Events = {'Clicked':True}
        buttonsEnabled(True)
    
def OnDeleteMedia(ev):
    parentFolder = getMediaFolder(currentTimeline.GetName())
    mediaFolder = getMediaFolder("media",parentFolder)
    if not mediaFolder:
        errorPopupDialog('The "media" folder (bin) does not exists. You must conform and copy files before delete files.')
        return
    
    accepted,_,_ = genericPopupDialog("Do you want to delete the media files in the edit storage folder?","Yes","No",haveRejectButton=True)
    if not accepted:
        return
    mpClips = mediaFolder.GetClipList()
    copyMediaPath = getUIValues()[11]
    clips2Move=[]
    deleteUnrelinked = False
    deleteUnrelinkedAsked = False
    for clip in mpClips:
        filePath = clip.GetClipProperty('File Path')
        if filePath.startswith(copyMediaPath):
            if os.path.exists(filePath):
                proxy = clip.GetClipProperty("Proxy Media Path")
                if clip.ReplaceClip(proxy):
                    clip.UnlinkProxyMedia()
                    clip.SetClipColor("Blue")
                    print_info('Deleting file',filePath)
                    os.remove(filePath)
                    clips2Move.append(clip)
                else:
                    if not deleteUnrelinkedAsked:
                        deleteUnrelinked,_,_ = genericPopupDialog("Some chips do not have an associated proxy and will be offline. Do you want to remove these files anyway?",
                                                                  "Yes","No",haveRejectButton=True)
                        deleteUnrelinkedAsked = True
                    if deleteUnrelinked:
                        print_info('Deleting file',filePath)
                        os.remove(filePath)
                    else:
                        print_warning("Can not delete the file ", filePath,".",sep='')
                        
            else:
                print_error(filePath,"does not exists!")
        else:
            print_error(filePath,'can not be deleted')
            
    stock = getMediaFolder("stock")
    if stock:
        mediaPool.MoveClips(clips2Move,stock)
            
            
def OnBrowse(ev):
    buttonsEnabled(False)
    who = ev['who']
    if who == "btBrowseMog":
        txt = win.Find('txtMogPath')
        txt.Text = fu.RequestDir(txt.Text)
    elif who == "btBrowseSony":
        txt = win.Find('txtSonyPath')
        txt.Text = fu.RequestDir(txt.Text)
    elif who == "btBrowseAvid":
        txt = win.Find('txtAvidPath')
        newPath = fu.RequestDir(txt.Text)
        if newPath:
            if newPath.endswith(os.sep + 'Avid MediaFiles' + os.sep + 'MXF' + os.sep):
                txt.Text = newPath
            else:
                print_error('Wrong path')
                errorPopupDialog(newPath + " is a wrong Path.\nThe path must be in the format <Volume>" + os.sep + 'Avid MediaFiles' + os.sep + 'MXF' + os.sep)
            
    elif who == "btBrowseAAF":
        txt = win.Find('txtAAFPath')
        txt.Text = fu.RequestFile(os.path.dirname(txt.Text),'',{"FReqB_SeqGather" : True, "FReqS_Filter" : "Open AAF Files (*.aaf)|*.aaf", "FReqS_Title" : "Choose AAF file"}) #filedialog.askopenfilename(defaultextension='aaf', initialdir=os.path.dirname(txt.Text))
    elif who == "btBrowseCopyMedia":
        txt = win.Find('txtCopyMediaPath')
        txt.Text = fu.RequestDir(txt.Text)
    elif who == "btImportExtensions":
        ingestSettingsFile = fu.RequestFile(userPath,'',{"FReqB_SeqGather" : True, "FReqS_Filter" : "Open JSON Files (*.json)|*.json", "FReqS_Title" : "Choose ReelMyFiles Ingest Settings file"})
        if ingestSettingsFile:
            importIngestSettings(ingestSettingsFile,'fileExtensions','fileExtensions')
            treeExtensionsConfig(win)
    elif who == "btImportCameraFolder":
        ingestSettingsFile = fu.RequestFile(userPath,'',{"FReqB_SeqGather" : True, "FReqS_Filter" : "Open JSON Files (*.json)|*.json", "FReqS_Title" : "Choose ReelMyFiles Ingest Settings file"})
        if ingestSettingsFile:
            importIngestSettings(ingestSettingsFile,'cameras','cameras')
            treeCameraFoldersConfig(win)
        
    buttonsEnabled(True)

def OnTabChanged(ev):
    items = win.GetItems()
    items['MyStack'].CurrentIndex  = ev['Index']

def OnExtensionsList(ev):
    items = win.GetItems()
    who = ev['who']
    if who == 'btAddExtension':
        _,_,items = genericPopupDialog("Enter a extension name",haveInput=True,haveRejectButton=True)
        ext = items['LineEdit'].Text
        currentList = [x.upper() for x in settingsJson.get('fileExtensions',[])]
        if len(currentList) == 0:
            settingsJson['fileExtensions'] = []
        if ext and not ext.upper() in currentList:
            settingsJson['fileExtensions'].append(ext)
            treeExtensionsConfig(win)
            saveSetting()
    elif who == 'btRemoveExtension':
        tree = items['treeExtensions']
        haveSelecteds = False
        for it in tree.SelectedItems().values():
            haveSelecteds=True
            ext = it.Text[0]
            settingsJson['fileExtensions'].remove(ext)
        
        if haveSelecteds:
            treeExtensionsConfig(win)
            saveSetting()

def OnCamerasList(ev):
    items = win.GetItems()
    who = ev['who']
    if who == 'btAddCameraFolder':
        _,_,items = genericPopupDialog("Enter a camera folder",haveInput=True,haveRejectButton=True)
        ext = items['LineEdit'].Text
        currentList = [x.upper() for x in settingsJson.get('cameras',[])]
        if len(currentList) == 0:
            settingsJson['cameras'] = []
        if ext and not ext.upper() in currentList:
            settingsJson['cameras'].append(ext)
            treeCameraFoldersConfig(win)
            saveSetting()
    elif who == 'btRemoveCameraFolder':
        tree = items['treeCameraFolders']
        haveSelecteds = False
        for it in tree.SelectedItems().values():
            haveSelecteds=True
            ext = it.Text[0]
            settingsJson['cameras'].remove(ext)
        
        if haveSelecteds:
            treeCameraFoldersConfig(win)
            saveSetting()

def OnCodecsList(ev):
    items = win.GetItems()
    who = ev['who']
    if who == 'btAddCodec':
        _,_,items = genericPopupDialog("Enter a codec",haveInput=True,haveRejectButton=True)
        codec = items['LineEdit'].Text
        addCodecsToList([codec],'codecs',treeCodecsConfig,['codecsProxy'])

    elif who in ['btRemoveCodec','btSendToProxy']:
        #print(who)
        tree = items['treeCodecs']
        haveSelecteds = False
        for it in tree.SelectedItems().values():
            haveSelecteds=True
            codec = it.Text[0]
            settingsJson['codecs'].remove(codec)
            if who == 'btSendToProxy':
                addCodecsToList([codec],'codecsProxy',treeProxyCodecsConfig)     
        
        if haveSelecteds:
            treeCodecsConfig(win)
            saveSetting()
    elif who == 'btImportFromTimeline':
        timelineCodecs = getTimelineCodecs()
        addCodecsToList(timelineCodecs,'codecs',treeCodecsConfig,['codecsProxy'])
                        
def OnProxyCodecsList(ev):
    items = win.GetItems()
    who = ev['who']
    if who == 'btAddProxyCodec':
        _,_,items = genericPopupDialog("Enter a codec",haveInput=True,haveRejectButton=True)
        codec = items['LineEdit'].Text
        addCodecsToList([codec],'codecsProxy',treeProxyCodecsConfig,['codecs'])
            
    elif who in ['btRemoveProxyCodec','btSendToHigh']:
        tree = items['treeProxyCodecs']
        haveSelecteds = False
        for it in tree.SelectedItems().values():
            haveSelecteds=True
            codec = it.Text[0]
            settingsJson['codecsProxy'].remove(codec)
            if who == 'btSendToHigh':
                pass
        
        if haveSelecteds:
            treeProxyCodecsConfig(win)
            saveSetting()


            
def OnTeste(ev):
    timeline_names_reels = getTimelineClipFromEditIndex()
    for clip_tuple in getTimelineClips():
        clip = clip_tuple[0]
        track = clip_tuple[1]
        mpClip = clip.GetMediaPoolItem()
        if not mpClip:
            tcIn = clip.GetStart()
            mpClip = timeline_names_reels.get((track,tcIn),False)
            if mpClip:
                mpClip.setTimelineClip(clip)
                clipReel = mpClip.GetClipProperty("Reel Name")
                if not clipReel:
                    clipReel = extractReelName(mpClip.GetClipProperty("File Name"))
                if clipReel:
                    mpClip = getMpClipFromReelName(clipReel)
                    if mpClip:
                        oldStartTC = mpClip.GetClipProperty("Start TC")
                        if oldStartTC == "00:00:00:00":
                            mpClip.SetClipProperty("Start TC","24:00:00:00")
                            oldEndTC = mpClip.GetClipProperty("End TC")
                            oldEndTCSplit = oldEndTC.split(":")
                            oldEndHour = int(oldEndTCSplit[0])
                            newEndHour = oldEndHour + 24
                            mpClip.SetClipProperty("End TC",str(newEndHour) + ":" + oldEndTCSplit[1]  + ":" + oldEndTCSplit[2] + ":" + oldEndTCSplit[3])
                            print("TC for",mpClip.GetName(),"is now",mpClip.GetClipProperty("Start TC"),"->",mpClip.GetClipProperty("End TC"))
                                          
    
    #currentFolder = mediaPool.GetCurrentFolder()
    #stock = getMediaFolder("stock")
    #for mpClip in stock.GetClipList():
    #    oldStartTC = mpClip.GetClipProperty("Start TC")
    #    if oldStartTC == "00:00:00:00":
    #        mpClip.SetClipProperty("Start TC","24:00:00:00")
    #        oldEndTC = mpClip.GetClipProperty("End TC")
    #        oldEndTCSplit = oldEndTC.split(":")
    #        oldEndHour = int(oldEndTCSplit[0])
    #        newEndHour = oldEndHour + 24
    #        mpClip.SetClipProperty("End TC",str(newEndHour) + ":" + oldEndTCSplit[1]  + ":" + oldEndTCSplit[2] + ":" + oldEndTCSplit[3])
    #        print("TC for",mpClip.GetName(),"is now",mpClip.GetClipProperty("Start TC"),"->",mpClip.GetClipProperty("End TC"))
    #    else:
    #        continue
        
    
                    
        
    
# =============== UI CONFIGURATION =============

def tabsConfig(win):
    items = win.GetItems()
    
    items['MyStack'].CurrentIndex = 0
    items['MyTabs'].AddTab("General")
    items['MyTabs'].AddTab("Settings")

def treeExtensionsConfig(win):
    items = win.GetItems()
    tree = items['treeExtensions']
    tree.Clear()
    hdr = tree.NewItem()
    hdr.Text[0] = "Extensions"
    tree.SetHeaderItem(hdr)
    tree.ColumnCount = 1
    extensions = settingsJson.get('fileExtensions',[])
    for ext in extensions:
        row = tree.NewItem()
        row.Text[0] = ext
        tree.AddTopLevelItem(row)
        
def treeCameraFoldersConfig(win):
    items = win.GetItems()
    tree = items['treeCameraFolders']
    tree.Clear()
    hdr = tree.NewItem()
    hdr.Text[0] = "Camera Folders"
    tree.SetHeaderItem(hdr)
    tree.ColumnCount = 1
    extensions = settingsJson.get('cameras',[])
    for ext in extensions:
        row = tree.NewItem()
        row.Text[0] = ext
        tree.AddTopLevelItem(row)

def addCodecsToList(codecs:list,settingsKey:str,treeConfigFunction,settingsKeysToCheck:list = []):
    """
        Arguments:
            codecs: list of codecs to add
            settingsKey: key of the settings value for the list of codecs
            treeConfigFunction: function that configure the UI list
            settingsKeysToCheck: other settings key values to check if the codec already exists
    """
    currentList = [x.upper() for x in settingsJson.get(settingsKey,[])]
    for key in settingsKeysToCheck:
        currentList += [x.upper() for x in settingsJson.get(key,[])]
    if len(currentList) == 0:
        settingsJson[settingsKey] = []
    for codec in codecs:
        if codec and not codec.upper() in currentList:
            settingsJson[settingsKey].append(codec)
            treeConfigFunction(win)
            saveSetting()
  
def treeCodecsConfig(win):
    items = win.GetItems()
    tree = items['treeCodecs']
    tree.Clear()
    hdr = tree.NewItem()
    hdr.Text[0] = "High Resolution Codecs"
    tree.SetHeaderItem(hdr)
    tree.ColumnCount = 1
    extensions = settingsJson.get('codecs',[])
    for ext in extensions:
        row = tree.NewItem()
        row.Text[0] = ext
        tree.AddTopLevelItem(row)

def treeProxyCodecsConfig(win):
    items = win.GetItems()
    tree = items['treeProxyCodecs']
    tree.Clear()
    hdr = tree.NewItem()
    hdr.Text[0] = "Proxy Codecs"
    tree.SetHeaderItem(hdr)
    tree.ColumnCount = 1
    extensions = settingsJson.get('codecsProxy',[])
    for ext in extensions:
        row = tree.NewItem()
        row.Text[0] = ext
        tree.AddTopLevelItem(row)
    
# =============== UI WINDOW =============
def MainWindow():
    global cbProjects

    cbProjects = ui.ComboBox({'ID':'cbProjects'})
    cbProjects.AddItems(getProjects())
    cbProjects.CurrentText = currentHouseProject
    
    houseProjectLayout = ui.VGroup({'ID':'houseProjectLayout','Weight': 0.0},[
        ui.Label({'Text':'House Project','Alignment':{'AlignTop' : True,'AlignCenter' : True},'StyleSheet':'border: 1px white;border-style: solid none none none'}),
        ui.HGroup({'Weight': 0.0},[cbProjects,
                                 ui.Button({'ID':'btDeleteProject','Text':'Delete Current','Weight': 0.0})
                                   ]),
        ui.HGroup({'Weight': 0.0},[ui.LineEdit({'ID':'txtNewProject','Text':currentHouseProject}),
                                 ui.Button({'ID':'btAddProject','Text':'Add New','Weight': 0.0}),
                                 ui.Button({'ID':'btRenameProject','Text':'Rename Current','Weight': 0.0})                            
                                   ])
        ])
    
    mogPathLayout = ui.HGroup({'Weight': 0.0},
        [   ui.Label({'Text':'MOG Path','FixedSize':[70,30]}),
            ui.LineEdit({'ID':'txtMogPath','Text':settings['mogPath'],'MinimumSize':[400,30]}),
            ui.Button({'ID':'btBrowseMog','Text':'Browse','Weight': 0.0})         
        ]
    )

    extractionLayout = ui.HGroup(
        [   ui.Label({'Text':'Field Separator','FixedSize':[100,30]}),
            ui.LineEdit({'ID':'txtFieldSep','Text':settings['fieldSep']}),
            ui.HGap(5),
            ui.Label({'Text':'Field Count','FixedSize':[100,30]}),
            ui.SpinBox({'ID':'spFieldCount','Value':settings['fieldCount'],'Minimum':1,'Maximum':32,'SingleStep':1}),
        ]
    )
    
    sonyPathLayout = ui.HGroup({'Weight': 0.0},
        [   ui.Label({'Text':'SONY/OTHER Path','FixedSize':[75,30]}),
            ui.LineEdit({'ID':'txtSonyPath','Text':settings['sonyPath'],'MinimumSize':[400,30]}),
            ui.Button({'ID':'btBrowseSony','Text':'Browse','Weight': 0.0})
        ]
    )
    
    avidPathLayout = ui.HGroup({'Weight': 0.0},
        [   ui.Label({'Text':'AVID Path','FixedSize':[60,30]}),
            ui.LineEdit({'ID':'txtAvidPath','Text':settings['avidPath'],'MinimumSize':[400,30]}),
            ui.Button({'ID':'btBrowseAvid','Text':'Browse','Weight': 0.0})
        ]
    )
    
    """
    motionPathLayout = ui.HGroup(
        [   ui.Label({'Text':'MOTION Path','FixedSize':[60,30]}),
            ui.LineEdit({'ID':'txtMotionPath','Text':settings['motionPath'],'MinimumSize':[400,30]}),
        ]
    )
    """
    
    importAAFLayout = ui.VGroup({'Weight': 0.0,'StyleSheet':'QGroupBox {border: 1px solid white}'},[
        ui.HGroup({'Weight': 0.0},[
        ui.LineEdit({'ID':'txtAAFPath','Text':settings['aafPath']}),
        ui.Button({'ID':'btBrowseAAF','Text':'Browse','Weight': 0.0}),
        ui.Button({'ID':'btImportAAF','Text':'Import AAF','Weight': 0.0}),
    ]),
        ui.HGroup({'Weight': 0.0},[
            ui.CheckBox({'ID':'ckExportStock','Text':'Export Stock Bin','Checked':settings['exportStock'],'ToolTip':"Export the stock bin to " + settings['avidPath'] + " after importing the media"}),
            ui.CheckBox({'ID':'ckImportStock','Text':'Import Stock Bin','Checked':settings['importStock'],'ToolTip':"Import the saved stock bin from disk if the stock folder does not exist"}),
            ui.CheckBox({'ID':'ckAutoImportSourceClipsIntoMediaPool','Text':'Auto Import Source Clips Into MediaPool','Checked':settings.get("autoImportSourceClipsIntoMediaPool",False),
                         'ToolTip':"Use if you want to import and link the timeline to the source clips. Use this with a Avid Edge workflow.",'StyleSheet':'color: ' + typeColor['AUTO']}),
            #autoImportSourceClipsIntoMediaPool       
                   ])
        ])  
    
    copyMediaLayout = ui.VGroup({'Weight': 0.0},[
        ui.HGroup({'Weight': 0.0},[
        ui.Label({'Text':'Destination','FixedSize':[70,30]}),
        ui.LineEdit({'ID':'txtCopyMediaPath','Text':settings.get('copyMediaPath',"")}),
        ui.Button({'ID':'btBrowseCopyMedia','Text':'Browse','Weight': 0.0}),
        ui.Button({'ID':'btCopyMedia','Text':'Copy Media','Weight': 0.0}),
    ])
        ,ui.Button({'ID':'btDeleteMedia','Text':'Delete files from edit storage','ToolTip':'Delete files from "' + settings.get('copyMediaPath','None') + '" that exists in the media folder (High Res Files)'})
        ]
        
    )
    
    vLayoutGeneral = ui.VGroup({'Weight': 0.0},
        [ui.Label({'Text':'<p><a href="https://github.com/c0ntact0/DAVINCI_CONFORM_MOG/blob/main/README.md#versions" target="_blank">Versions</a></p>','OpenExternalLinks':True}),
        houseProjectLayout,
         ui.VGap(0.2),
         ui.Label({'Text':'Mog Settings','Alignment':{'AlignTop' : True,'AlignCenter' : True},'StyleSheet':'border: 1px white;border-style: solid none none none'}),
         ui.VGap(0.2),
         mogPathLayout,
         ui.VGap(2),
         extractionLayout,
         ui.VGap(5),
         ui.Label({'Text':'Sony and Other Cameras Settings','Alignment':{'AlignTop' : True,'AlignCenter' : True},'StyleSheet':'border: 1px white;border-style: solid none none none'}),
         ui.VGap(0.2),
         sonyPathLayout,
         ui.VGap(0.2),
         ui.Label({'Text':'Avid','Alignment':{'AlignTop' : True,'AlignCenter' : True},'StyleSheet':'border: 1px white;border-style: solid none none none'}),
         ui.VGap(2),
         avidPathLayout,
         ui.VGap(0.2),
         ui.Label({'Text':'Import AFF','Alignment':{'AlignTop' : True,'AlignCenter' : True},'StyleSheet':'border: 1px white;border-style: solid none none none'}),
         ui.VGap(2),
         importAAFLayout,
         ui.VGap(0.2),
         ui.Label({'Text':'Conforming','Alignment':{'AlignTop' : True,'AlignCenter' : True},'StyleSheet':'border: 1px white;border-style: solid none none none'}),
         ui.VGap(0.2),
         ui.VGroup({'Weight': 0.0},[
         ui.Button({'ID':'btConformSony','Text':'Conform SONY','Weight': 0.0,'StyleSheet':'color: ' + typeColor['SONY']}),
         ui.Button({'ID':'btConformOthers','Text':'Conform OTHER cameras','Weight': 0.0,'StyleSheet':'color: ' + typeColor['OTHER'] }),
         ui.Button({'ID':'btConformMog','Text':'Conform MOG','Weight': 0.0,'StyleSheet':'color:' + typeColor['MOG']}),
         ui.Button({'ID':'btConformAll','Text':'Conform ALL media types','Weight': 0.0})]),
         ui.VGap(0.2),
         ui.Label({'Text':'Copy files to edit storage and relink','Alignment':{'AlignTop' : True,'AlignCenter' : True},'StyleSheet':'border: 1px white;border-style: solid none none none'}),
         ui.VGap(2),
         copyMediaLayout
         #,ui.Button({'ID':'btTeste','Text':'Teste'})
         ]
        
    )
    
    vLayoutSettings =  ui.HGroup({'Weight': 0.0},[
            ui.VGroup({'Weight': 2.0},[
            ui.HGroup({'Weight': 10.0},[
            ui.Tree({
			"ID": "treeExtensions",
			"SortingEnabled": True,'SelectionMode':'ExtendedSelection','Weight': 1.0})
            ,
            ui.VGroup({'Weight': 0.0},[
                ui.Button({'ID':'btAddExtension','Text':'Add','Weight': 0.0}),
                ui.Button({'ID':'btRemoveExtension','Text':'Remove','Weight': 0.0}),
                ui.Button({'ID':'btImportExtensions','Text':'Import','Weight': 0.0}),
            ])
            ]),
            ui.HGroup({'Weight': 10.0},[
            ui.Tree({
			"ID": "treeCodecs",
			"SortingEnabled": True,'SelectionMode':'ExtendedSelection','Weight': 3.0})
            ,
            ui.VGroup({'Weight': 0.0},[
                ui.Button({'ID':'btAddCodec','Text':'Add','Weight': 0.0}),
                ui.Button({'ID':'btRemoveCodec','Text':'Remove','Weight': 0.0}),
                ui.Button({'ID':'btSendToProxy','Text':'Send To\nProxy','Weight': 0.0}),
                ui.Button({'ID':'btImportFromTimeline','Text':'Import From\nTimeline','Weight': 0.0}),
            ])
            ]),
            ui.HGroup({'Weight': 10.0},[
            ui.Tree({
			"ID": "treeProxyCodecs",
			"SortingEnabled": True,'SelectionMode':'ExtendedSelection','Weight': 3.0})
            ,
            ui.VGroup({'Weight': 0.0},[
                ui.Button({'ID':'btAddProxyCodec','Text':'Add','Weight': 0.0}),
                ui.Button({'ID':'btRemoveProxyCodec','Text':'Remove','Weight': 0.0}),
            ])
            ])
            ]),
            
            ui.HGap(20),
             
            ui.VGroup({'Weight': 2.0},[
                ui.Label({'Text':'Sony cameras with the \"Clip\" folder are already included in the \"Conform SONY\" process.','WordWrap':True,
                          'Alignment':{'AlignTop' : True},'Weight': 1.0}),
                ui.VGap(4),
                ui.HGroup({'Weight': 20.0},[
                    ui.Tree({
			            "ID": "treeCameraFolders",
			            "SortingEnabled": True,'SelectionMode':'ExtendedSelection','Weight': 2.0}),
            ui.VGroup({'Weight': 0.0},[
                ui.Button({'ID':'btAddCameraFolder','Text':'Add','Weight': 0.0}),
                ui.Button({'ID':'btRemoveCameraFolder','Text':'Remove','Weight': 0.0}),
                ui.Button({'ID':'btImportCameraFolder','Text':'Import','Weight': 0.0}),
            ])
            ])
            ])
        ])
    
    
    vLayoutMainWindow = ui.VGroup({'Weight': 0.0},[
        ui.TabBar({'Weight':0.0,'ID':'MyTabs'}),
        ui.Stack({'Weight':1.0,'ID':'MyStack'},[
            vLayoutGeneral,
            vLayoutSettings            
        ])
    ])
        
    geoDic = settingsJson['windowGeometry']
    geometry = [geoDic['1'],geoDic['2'],geoDic['3'],geoDic['4']]
    win = dispatcher.AddWindow({'WindowTitle':'ConformAll (Rui Loureiro 2024)','ID':'mainWindow','Geometry':geometry},vLayoutMainWindow)
    #pprint(win.GetItems())
    
    tabsConfig(win)
    treeExtensionsConfig(win)
    treeCameraFoldersConfig(win)
    treeCodecsConfig(win)
    treeProxyCodecsConfig(win)
    win.On.btConformMog.Clicked = BtConformMog
    win.On.btConformSony.Clicked = BtConformCameras
    win.On.btConformOthers.Clicked = BtConformCameras
    
    win.On.btConformAll.Clicked = BtConformAll
    win.On.btImportAAF.Clicked = BtImportAAF
    win.On.cbProjects.CurrentIndexChanged = ProjectChanged
    win.On.btDeleteProject.Clicked = DeleteProject
    win.On.btAddProject.Clicked = AddProject
    win.On.btRenameProject.Clicked = RenameProject
    win.On.btCopyMedia.Clicked = OnCopyMedia
    win.On.btDeleteMedia.Clicked = OnDeleteMedia
    
    win.On.btBrowseMog.Clicked = OnBrowse
    win.On.btBrowseSony.Clicked = OnBrowse
    win.On.btBrowseAvid.Clicked = OnBrowse
    win.On.btBrowseAAF.Clicked = OnBrowse
    win.On.btBrowseCopyMedia.Clicked = OnBrowse
    win.On.btImportExtensions.Clicked = OnBrowse
    win.On.btImportCameraFolder.Clicked = OnBrowse
    win.On.MyTabs.CurrentChanged = OnTabChanged
    win.On.btAddExtension.Clicked = OnExtensionsList
    win.On.btRemoveExtension.Clicked = OnExtensionsList
    win.On.btAddCameraFolder.Clicked = OnCamerasList
    win.On.btRemoveCameraFolder.Clicked = OnCamerasList
    win.On.btAddCodec.Clicked = OnCodecsList
    win.On.btRemoveCodec.Clicked = OnCodecsList
    win.On.btSendToProxy.Clicked = OnCodecsList
    win.On.btImportFromTimeline.Clicked = OnCodecsList
    win.On.btAddProxyCodec.Clicked = OnProxyCodecsList
    win.On.btRemoveProxyCodec.Clicked = OnProxyCodecsList
    win.On.btSendToHigh.Clicked = OnProxyCodecsList
    
    win.On.mainWindow.Close = OnClose
   
    win.On.btTeste.Clicked = OnTeste

    return win

def errorPopupDialog(label=""):
    
    def OnErrorDialogClose(ev):
        dispatcher.ExitLoop()
    
    fontSize = ui.Font().PixelSize
    labelLines = len(label)*fontSize/580
    arrLabel = label.split('\n')
    labelLines+=len(arrLabel)
    labelH = labelLines*fontSize if len(label)*fontSize > 580 else 30
    
    windowH = 50+labelH
   
    errorDialog = dispatcher.AddDialog({'WindowTitle':'Error','ID':'errorDialog','MinimumSize':[600,windowH],'MaximumSize':[600,windowH],'Weight': 0.0},
                                  ui.VGroup({'Weight': 0.0,'Width':0.0},[
                                      ui.Label({'ID':'Label','Text':label,'WordWrap': True,'Alignment':{'AlignTop' : True},'MinimumSize':[580,labelH],'MaximumSize':[580,labelH]}),
                                   ui.Button({'ID':'btCloseDialog','Text':'Close','Weight': 0.0})]))
    errorDialog.On.btCloseDialog.Clicked = OnErrorDialogClose
    items = errorDialog.GetItems()
    
    buttonsEnabled(False)
    errorDialog.Show()
    dispatcher.RunLoop()
    errorDialog.Hide()
    buttonsEnabled(True)
    return errorDialog,items

def genericPopupDialog(label="",acceptButtonText="OK",rejectButtonText="Cancel",haveInput=False,haveRejectButton=False):
    
    """
        Return: (accepted (boolean),dialog object,dialog items objects)
    """
      
    def OnGenericPopupDialog(ev):
        
        who = ev['who']
        if who == "btCancelInputDialog":
            if haveInput:
                items['LineEdit'].Clear()
        elif who == "btOkInputDialog":
            bt = items['btOkInputDialog']
            bt.Checked = True    
        dispatcher.ExitLoop()
    
    fontSize = ui.Font().PixelSize
    labelLines = len(label)*fontSize/580
    arrLabel = label.split('\n')
    labelLines+=len(arrLabel)
    labelH = labelLines*fontSize if len(label)*fontSize > 580 else 30
    
    textEditGap = 5 if haveInput else 0
    windowH = 133+labelH
    windowH = windowH - 30 if not haveInput else windowH
    inputDialog = dispatcher.AddDialog({'WindowTitle':'Input Dialog','ID':'inputDialog','MinimumSize':[600,windowH],'MaximumSize':[600,windowH],'Weight': 5},
                                        ui.VGroup({'Weight': 0},[
                                        ui.Label({'Text':label,'ID':'Label','WordWrap': True,'Alignment':{'AlignTop' : True},'MinimumSize':[580,labelH],'MaximumSize':[580,labelH]}),#,'FrameStyle': 20 | 6}),
                                        ui.VGap(textEditGap),
                                        ui.VGap(0) if not haveInput else ui.LineEdit({'ID':'LineEdit','MinimumSize':[580,30],'MaximumSize':[580,30],'Visible':haveInput}),
                                        ui.VGap(5),
                                           ui.HGroup({'Weight': 0},[
                                               ui.Button({'Text':acceptButtonText,'ID':'btOkInputDialog','Checkable':True}),
                                               ui.VGap(0) if not haveRejectButton else ui.Button({'Text':rejectButtonText,'ID':'btCancelInputDialog'}),
                                               ])
                                       ]))
    items = inputDialog.GetItems()
    inputDialog.On.btOkInputDialog.Clicked = OnGenericPopupDialog
    inputDialog.On.btCancelInputDialog.Clicked = OnGenericPopupDialog
    
    buttonsEnabled(False)
    inputDialog.Show()
    dispatcher.RunLoop()
    inputDialog.Hide()
    buttonsEnabled(True)
    return items['btOkInputDialog'].Checked,inputDialog,items

def copyFilesDialog():
    canceled = False
    
    def run(ev):
        for i in range(10):
            if canceled:
                break
            bmd.wait(1)
            print(i)
        
        dispatcher.ExitLoop()
        
    def OnCancel(ev):
        global canceled
        
        print("Canceled")
        canceled = True
    
    copyDialog = dispatcher.AddDialog({'WindowTitle':'Input Dialog','ID':'inputDialog','FixedSize':[420,133]},
                                      ui.VGroup([
                                          
                                        ui.Button({'Text':'Cancel','ID':'btCancel'})  
                                      ]))
    
    timer = ui.Timer({'ID':'Timer','SingleShot':True,'Interval':1000})
    ui.QueueEvent('Timer', 'Timeout', {})
    copyDialog.On.btCancel.Clicked = OnCancel
    dispatcher.On.Timer.Timeout = run
    
    items = copyDialog.GetItems()
    pprint(items)
    copyDialog.Show()
    timer.Start()
    
    print(timer.SingleShot,timer.Interval,timer.GetTimerID(),timer.IsActive,timer.RemainingTime)
    dispatcher.RunLoop()

    copyDialog.Hide()
    
################# MAIN ###################
if __name__ == "__main__":


    loadSettings()
    currentHouseProject = settingsJson['currentProject']
    getSettings(currentHouseProject)
    
    mediaStorage = resolve.GetMediaStorage()
    #fusion = resolve.Fusion()
    fu.ShowConsole(True)
    
    pm = resolve.GetProjectManager()
    ui = fu.UIManager
    dispatcher = bmd.UIDispatcher(ui)

    currentProject = pm.GetCurrentProject()
    #pprint(currentProject.GetSetting())
    print_info("Current DaVinci Resolve project:",currentProject.GetName())
    #pprint(currentProject.GetSetting())
    currentTimeline = currentProject.GetCurrentTimeline()
    mediaPool = currentProject.GetMediaPool()
    win = MainWindow()
    if areFoldersOk():
        win.Show()
        dispatcher.RunLoop()
    win.Hide()