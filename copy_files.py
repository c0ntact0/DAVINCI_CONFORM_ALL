# See the README.txt for install

# ShareableList values (index: (type) meaning)
# 0: (boolean) stop flag, changed by the main processed when the user stop the operation.
# 1: (boolean) finish flag, changed by this process when the operation finished. 
# 2: (string) destination path where to copy the media files.
# 3: (string) media pool forder name where to search for files to copy
# 4: (int) number of clips relinked (to send to main process)

from multiprocessing.shared_memory import ShareableList
from multiprocessing import resource_tracker
import os
import shutil
import time
import datetime

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

def inspectSouces(clips:list):
    totalSize= 0
    filesCount=0
    clipsFiles={}
    for clip in clips:
        filesCount+=1
        thisFile = clip.GetClipProperty("File Path")
        totalSize+=os.path.getsize(thisFile)
        clipsFiles[clip.GetClipProperty("File Name")] = clip
        
    return filesCount,totalSize,clipsFiles

def humanReadable(bytesNum,humanReadbleDivider=1024**2,humanReadbleName="MBytes/s"):
    return "{:.3f}".format(bytesNum/humanReadbleDivider) + " " + humanReadbleName

try:
    sl = ShareableList(name='ConformAllCopyMedia')
    sl[0]=False
    sl[4]=0
    mediaPath = sl[2] #folder where to copy the files
    mediaFolderName = sl[3] # bin folder name in the DR from where to read the clips. Current filepath is read from the clip properties.

    print("Media Path:",mediaPath)
    print("DR Media Folder:",mediaFolderName)

    pm = resolve.GetProjectManager()
    currentProject = pm.GetCurrentProject()
    currentTimeline = currentProject.GetCurrentTimeline()
    mediaPool = currentProject.GetMediaPool()

    parentFolder = getMediaFolder(currentTimeline.GetName()) # we assume that the media folder bin is s child of the bin 
    mediaFolder = getMediaFolder(mediaFolderName,parentFolder)

    #print(mediaFolder.GetName())

    cancel = False
    oldFiles = {} # Files already in the folder (recursive). Filename as key and filepath as value
    for root, dirs, files in os.walk(mediaPath):
        for name in files:
            if not name.startswith("."):
                oldFiles[name] = os.path.join(root,name)

    clips = mediaFolder.GetClipList()
    clipsFilesNum,totalSize,clipsFiles = inspectSouces(clips) # clipsFiles is a dicionary with file name as key (not file path) and the clip object as value
    copyCount = 0
    copySize = 0
    relinkedCount = 0
    meanArray = []
    clips2Relink=[]
    for key in clipsFiles.keys():
        cancel=sl[0]
        if cancel:
            print("Copy Media process canceled...")
            break
        
        copyCount+=1
        clip = clipsFiles.get(key)
        filePath = clip.GetClipProperty("File Path")
        fileSize = os.path.getsize(filePath)
        copySize+=fileSize
        print("Copying file",copyCount,"of",clipsFilesNum,end=". ")
        msg = ""
        if key in oldFiles: # test if the filename already exists in the mediaPath
            msg += "File " + key + " already in the media path."
            clips2Relink.append(clip)

        else:
            if os.path.exists(filePath):

                ts = datetime.datetime.timestamp(datetime.datetime.now())        
                # TODO: block copy may be the way if we whant to return the copy progress to the user
                shutil.copyfile(filePath,os.path.join(mediaPath,key),follow_symlinks=False)
                dt = datetime.datetime.timestamp(datetime.datetime.now()) - ts
                bps = fileSize/dt
                copySizeRemaining = totalSize - copySize
                meanArray.append(bps)
                meanBps = sum(meanArray)/len(meanArray)
                timeRemaining = copySizeRemaining/meanBps
                convertedSeconds = str(datetime.timedelta(seconds = int(timeRemaining)))
                msg += "File " + filePath + " copied (" + humanReadable(bps)+ ", " + convertedSeconds + " remaining)."
                clips2Relink.append(clip)
                #else:
                #    msg += "Erro copying the file " + filePath + ". (error: " + str(error) + ")"
            else:
                msg += "The file " + filePath + " does not exists." 

        #if mediaPool.RelinkClips([clip],mediaPath):
        #    relinkedCount+=1
        #    msg += " Clip relinked."
        #else:
        #    msg += " Failed to relink the clip"

        #if not oldFiles.pop(key,False):
        #    msg += " Can't pop media file value from dictionary."

        print(msg)
    """
    if not cancel:
        print("Deleting",len(oldFiles),"unused files")
        for file in oldFiles.values():
            if os.path.exists(file):
                os.remove(file)
    """
    relinkedCount = len(clips2Relink)
    sl[4]=relinkedCount
    if relinkedCount > 0:
        if mediaPool.RelinkClips(clips2Relink,mediaPath):
            print(relinkedCount," of ",clipsFilesNum," relinked.")
        else:
            print("Error relinking clips.")
    else:
        print("There is no clips to relink.")
        
except Exception as e:
    print(e)
finally:
    sl[0]=False
    sl[1]=True
    sl.shm.close()
    