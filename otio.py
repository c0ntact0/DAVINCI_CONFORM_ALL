import opentimelineio as otio
import os
from pprint import pprint

#print(otio.adapters.available_adapter_names())
#print(otio.adapters.from_filepath(path))
def itioTransform(path,transform=True):
    timeline = otio.adapters.read_from_file(path)
    print("Reading timeline")
    if timeline:
        for clip in timeline.each_clip():
            print(clip.name)
            for fx in clip.effects:
                if fx.metadata:
                    if fx.metadata['Resolve_OTIO']['Effect Name'] == 'Retime and Scaling':
                        if transform:
                            print(fx.metadata)
                            fx.metadata['Resolve_OTIO']['Enabled'] = False
                        print(fx.metadata)

    return timeline
path="/Volumes/21-FF/AAF Files/COLOR/FF_950_CARNAVAL/marco_Export/FF_T9_950_CARNAVAL_V2.otio"
timeline = itioTransform(path)
aafFile,_ = os.path.splitext(path)    
aafFile += "_otio.otio"      
otio.adapters.write_to_file(timeline,aafFile)

#itioTransform(aafFile,False)
                    
                
                        
