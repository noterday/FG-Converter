# mugen2rivals
A script to convert Mugen spritesheets and hitboxes into the equivalent Rivals of Aether character files. Spritesheets are converted accurately, but hitbox positions are inacurate and need to be adjusted manually.

[Output Script Example](https://pastebin.com/bpiTrt1X)   
![alt text](https://i.imgur.com/uqQEjjS.png)
  
## How to use
Run mugenrivals.exe and enter the path to the character folder when asked. A new folder containing the converted files will appear at the same location. Copy the spritesheets you want to use along with the matching .gml scripts, and rename them following the [RoA workshop naming convention](https://rivalsofaether.com/workshop/introduction/).
  
To run the source, use python3 and install [Pillow](https://github.com/python-pillow/Pillow) through Pip.

