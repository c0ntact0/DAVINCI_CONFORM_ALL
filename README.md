
Please read the ConformAllManual.pdf to more info about the script.

# Install

**Put the ConformAll.py script in one of the following locations**:

- Mac OS X:
```
/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility
```
- Windows:
```
%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Utility
```
- Linux:

```
/opt/resolve/Fusion/Scripts
```
or
```
/home/resolve/Fusion/Scripts/Utility
```
depending on installation.

 
**Put the copy_files.py script in:**

- Mac OS X:
```
/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts
```
- Windows:
```
%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts
```
- Linux:
```
/opt/resolve/Fusion/Scripts
```
or
```
/home/resolve/Fusion/Scripts/
```
depending on installation.


**The settings file location:**

- Mac OS X:
```
/Users/<USER>/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Settings
```
- Windows:
```
%APPDATA%\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Settings
```
- Linux:
```
$HOME/.local/share/DaVinciResolve/Fusion/Scripts/Settings
```
  
The settings file is a json file named ConformAll.json.
The settings file is created by the ConformAll.py script.

# Versions
2025.0.1
  - Solved a problem introduced by the DaVinci Resolve version >= 19.1. The problem is related with the modification made in the ConformAll version 2024.1.7. Blackmagic solved the problem with the timeline clip offset, and now the frame is not removed if the DaVinci Resolve version is >= 19.1.

2024.1.8
  - Solved bug when checking if Resolve version can import/export bins for major versions greater than 18.
  - MyMpClip class have now the correct Source In and Source Out frame fields from the Edit Index (previously it was using the Record In and Record Out)
  - Fixed an issue with the routine implemented in version 2024.1.5. Previously, it was getting the Start TC for comparing media pool clips using the reel name from the Edit Index to get the media pool clip. This takes time, and because clips with the correct TC were also being searched unnecessarily, on very large timelines it seemed to the user that the system had crashed. Now, only clips that have the TC at 24:00:00:00 in the Edit Index are searched in the media pool.
  - Fixed bug in the conform routines retry loop. 

2024.1.7
  - Solved bug when conforming MOG media with corrupted MPEG50 proxies. When adding a high definition (AMA) clip to the timeline, one frame must be removed from the original timeline clip Right Offset.

2024.1.6
  - Solved problem with the starting TC when conforming clips that have the start and end TCs modified with the rotine implemented in version 2024.1.5.

2024.1.5
  - Solved the DaVinci Resolve bug when importing clips with start TC at 00:00:00:00 from Avid AAFs. If any timeline clips don't have a corresponding media pool clip, the script will try to get the media pool clip using the Edit Index and change the start TC from 00:00:00:00 to 24:00:00:00 and the end TC adding 24 hours to the original end TC.

2024.1.4
  - All media types can now be conformed using the Edit Index information if the link to the AAF media failed.

2024.1.3
  - Solved bug when the proxies folder does not exit
  
2024.1.2
  - Solved bug when the UME folder does not exit
  - Solved bug when the stock bin creation was canceled.

2024.1.1
  - Solved problem with the edit index timecode frame separator ("." or ";" are converted to ":").

2024.1.0
  - Solved bug when browsing for Avid Path and cancel the choose folder dialog.
  - New check runs at startup that verify if all folders exit. Useful if the user forget to mount any drive.
  - Solved bug when trying to create lock file and the folder does not exist (e.g. drive not mounted).
  - Solved problem with MOG corrupted MPEG50 proxies.

2024.0.8
  - Stock bin lock is ignored if the machine trying to access the stock bin is the owner of the lock.

2024.0.7
  - Extension is removed from reel names than have it.
  - Versions hyperlink added.

2024.0.6
  - A new file blacklist_files.json is created in the Avid Path containing a list of files that the DR does not import into the Media Pool. This avoids consecutives tries to import this files.
  - Try to import MOG files with the clip Reel Name (e.g. Avid consolidation of MOG MPEG50 proxy files) if the clip that does not have the MOG filename template in the clipname.    

2024.0.5
- Bug solved: fail to delete files from edit storage if the clip does not have the proxy association.

2024.0.4
- Console messages prefix (INFO, WARNING, ERROR)
- When the import of the stock file fail,the user is asked if he want prossed with the import of the clips.

2024.0.3
- If "Export Stock Bin" it's not selected and is the first AAF import of the current day, is asked to the user if he wants to export the stock bin.
- Clips that not have the "Clip Color" property empty are not included in the timeline clips dictionary for conforming.
- If the timeline clips dictionary is empty, the test for "reel name option is selected" returns true (the alert dialog is not shown). Only returns false if the dictionary is not empty and
  all of the media pool clips have the "Reel Name" property empty.

2024.0.2
- Original AAF clip Descript is copied to the Scene field when conforming.
- New "Delete files from edit storage" function. This avoid deleting files that are not in the edit storage folder.
- When copy files to edit storage, the relink is now made after all files are copied. This avoid Nexis "delayed write" errors.
  To avoid media offline because of the delayed write errors, the project is saved and reloaded at the end of the copy.
- Avid MediaFiles/UME folder included in the Avid media import process. AAFs from Avid MC can now be exported linked to the UME workflow.
- Clips that have the same High Res and Low Res codecs, like the UME clips, are given the "Navy" color. This clips stay linked to the Low Res file (avid media)

2024.0.1
- Import timewarps solution removed. All media FX must be rendered in Avid MC before the AAF export.
- Resolved bug in the conforming video channel count.
- Avid Media Path must be in the format <Volume>/Avid MediaFiles/MXF/
- It's now possible to import Edge proxy when Blackmagic implements this codec (someday in the future)
- Added "autoImportSourceClipsIntoMediaPool" option in AAF Import. Links AAF to high resolution media and import the media to the media pool
- New High Resolution Codecs and Proxy Codecs lists, to distinguish between high resolution and proxy clips

2023.0.5
- Importing timewarps solved for no MOG media. MOG media FX must be rendered in Avid MC before the AAF export.
- Solved crash bug with the AAF import when the timeline already exists.

2023.0.4
- Timeline import is now done with the Timeline.ImportIntoTimeline() function instead of MediaPool.ImportTimelineFromFile().
  This way the "useSizingInfo" option is turned on.
  
2023.0.3
- OTHER camera type
- Extension list
- Camera folders list
- Copy files speed and time remaning (during copying)
- Copy files time duration (on the end)
- Popups re-styling
- Bug solved: Copy files button blocked during copying does not allowing to cancel the copy operation

2023.0.2
- Stock bin file it's always imported.
- Lock file implemented for the import AAF process.

2023.0.1
- Inicial version