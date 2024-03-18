#!/bin/bash
# tail -f /Library/Application\ Support/Blackmagic\ Design/DaVinci\ Resolve/logs/davinci_resolve.log
# copy to oneDrive
rsync -ruv "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/"*.py "/Users/rui/Library/CloudStorage/OneDrive-GrupoMediaCapital/PLURAL_OFFLINE/PP/DAVINCI_CONFORM_MOG/."
rsync -ruv "/Users/rui/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Settings/"*.json "/Users/rui/Library/CloudStorage/OneDrive-GrupoMediaCapital/PLURAL_OFFLINE/PP/DAVINCI_CONFORM_MOG/."
rsync -ruv "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/"*.py "/Users/rui/Library/CloudStorage/OneDrive-GrupoMediaCapital/PLURAL_OFFLINE/PP/DAVINCI_CONFORM_MOG/."

# copy to INSTALL
echo "Copy to install"
open smb://rui.loureiro@ppadmin.pluralpp.plr/TECNICA
sleep 5
if test -d "/Volumes/TECNICA"
then
rsync -ruv "/Users/rui/Library/CloudStorage/OneDrive-GrupoMediaCapital/PLURAL_OFFLINE/PP/DAVINCI_CONFORM_MOG/"ConformAll.py "/Volumes/TECNICA/install/DAVINCI/rl_Conform/."
rsync -ruv "/Users/rui/Library/CloudStorage/OneDrive-GrupoMediaCapital/PLURAL_OFFLINE/PP/DAVINCI_CONFORM_MOG/"copy_files.py "/Volumes/TECNICA/install/DAVINCI/rl_Conform/."
rsync -ruv "/Users/rui/Library/CloudStorage/OneDrive-GrupoMediaCapital/PLURAL_OFFLINE/PP/DAVINCI_CONFORM_MOG/"working.py "/Volumes/TECNICA/install/DAVINCI/rl_Conform/."
rsync -ruv "/Users/rui/Library/CloudStorage/OneDrive-GrupoMediaCapital/PLURAL_OFFLINE/PP/DAVINCI_CONFORM_MOG/"README.txt "/Volumes/TECNICA/install/DAVINCI/rl_Conform/."
fi
open /Users/rui/Library/CloudStorage/OneDrive-GrupoMediaCapital/PLURAL_OFFLINE/PP/DAVINCI_CONFORM_MOG/DAVINCI_CONFORM_MOG.code-workspace
open "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/"ConformAll.py
open "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/"copy_files.py
#open "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/"working.py

open "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/README.txt"
open "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Workflow Integrations/README.txt"

# open https://resolvedevdoc.readthedocs.io/en/latest/
# open https://www.steakunderwater.com/wesuckless/viewtopic.php?t=1411&start=120
# open https://gitlab.com/WeSuckLess/Reactor/-/tree/master
# open "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Reactor/Deploy"

echo "Copy to davinci1"
open smb://admin:sEgUrOIT@davinci1/macSSD
sleep 5
if test -d "/Volumes/macSSD"
then
rsync -ruv "/Users/rui/Library/CloudStorage/OneDrive-GrupoMediaCapital/PLURAL_OFFLINE/PP/DAVINCI_CONFORM_MOG/"ConformAll.py \
"/Volumes/macSSD/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/".
rsync -ruv "/Users/rui/Library/CloudStorage/OneDrive-GrupoMediaCapital/PLURAL_OFFLINE/PP/DAVINCI_CONFORM_MOG/"copy_files.py \
"/Volumes/macSSD/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/".
umount /Volumes/macSSD
fi

echo "Copy to davinci1"
open smb://admin:sEgUrOIT@davinci1/macSSD
sleep 5
if test -d "/Volumes/macSSD"
then
rsync -ruv "/Users/rui/Library/CloudStorage/OneDrive-GrupoMediaCapital/PLURAL_OFFLINE/PP/DAVINCI_CONFORM_MOG/"ConformAll.py \
"/Volumes/macSSD/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/".
rsync -ruv "/Users/rui/Library/CloudStorage/OneDrive-GrupoMediaCapital/PLURAL_OFFLINE/PP/DAVINCI_CONFORM_MOG/"copy_files.py \
"/Volumes/macSSD/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/".
umount /Volumes/macSSD
fi

for i in 1 3 4
do
echo "Copy to davinci0$i"
open smb://admin:sEgUrOIT@davinci0$i/"Macintosh HD"
sleep 5
if test -d "/Volumes/Macintosh HD-1"
then
rsync -ruv "/Users/rui/Library/CloudStorage/OneDrive-GrupoMediaCapital/PLURAL_OFFLINE/PP/DAVINCI_CONFORM_MOG/"ConformAll.py \
"/Volumes/Macintosh HD-1/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/".
rsync -ruv "/Users/rui/Library/CloudStorage/OneDrive-GrupoMediaCapital/PLURAL_OFFLINE/PP/DAVINCI_CONFORM_MOG/"copy_files.py \
"/Volumes/Macintosh HD-1/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/".
umount "/Volumes/Macintosh HD-1"
fi
done