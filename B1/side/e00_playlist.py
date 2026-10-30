                                                                
                                                                  

import json

                                                                        
with open("B1/side/playlist.json", encoding="utf-8") as file:
    playlist = json.load(file)

print(type(playlist))                                         
print(playlist["name"])                             
print(f"By {playlist['owner']}")                                    

songs = playlist["songs"]                   
print(f"{len(songs)} songs")
print(f"First: {songs[0]['title']}")                               
print(f"Last: {songs[-1]['title']} by {songs[-1]['artist']}")
