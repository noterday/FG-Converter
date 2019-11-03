# mugen2rivals
This script automatically converts a Mugen character into a set of spritesheets and gml scripts to use in Rivals of Aether mods. The gml scripts contain both animation timing and hitboxes (although hitboxes currently always come out misaligned).

[Example of an output script](https://pastebin.com/bpiTrt1X)   
![alt text](https://i.imgur.com/uqQEjjS.png)
  
## How to use
Run mugenrivals.exe and enter the path to the character folder when asked. A new folder containing the converted files should appear at the same location.
  
To run the source, use python3 and install [Pillow](https://github.com/python-pillow/Pillow) through Pip.
  
## Todo
- [ ] Fix issues with misaligned hitboxes
- [ ] Add the ability to chose which color palette to use
- [ ] Add command line options
- [ ] Something about hitstop???
