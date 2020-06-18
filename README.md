# mugen2rivals
This script converts the spritesheet and hitbox data of a Mugen character into the equivalent Rivals of Aether character files. It is currently incomplete, and it's translation of hitboxes is slightly inacurate.

[Example of an output script](https://pastebin.com/bpiTrt1X)   
![alt text](https://i.imgur.com/uqQEjjS.png)
  
## How to use
Run mugenrivals.exe and enter the path to the character folder when asked. A new folder containing the converted files should appear at the same location. Select the spritesheets you want to use and their equivalent gml scripts, and rename them following the [RoA workshop naming convention](https://rivalsofaether.com/workshop/introduction/).
  
To run the source, use python3 and install [Pillow](https://github.com/python-pillow/Pillow) through Pip.

