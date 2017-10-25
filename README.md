# ALYTtool
A tool to extract and repack ALYT files used in Pokémon games to store UI data and textures

**This repo is dead. Use [3DSkit](https://github.com/Tyulis/3DSkit) instead, which can do anything ALYTtool can do. The only interesting content here is the formats references.**

It also support transparently BL archives, which contain several ALYT and other files.

Usage:

*	to extract an ALYT or BL file:

		python3 ALYTtool.py -x [-c] <file name>

*	to repack a previously extracted ALYT or BL file (extracted with ALYTtool):
		
		python3 ALYTtool.py -p [-c] <folder name>

The -c option converts automatically convertible files (BFLYT and BFLIM) to readable formats (PNG and TFLYT) at extracting. You must precise -c option at repacking if you used it at extracting. 
A little documentation about ALYT file format can be found in the ALYT_ref.txt file

A full description of BL format can be found in the BL_ref.txt file

A list of the files in the RomFS and their description (when I have found it) can be found in the files.txt file.

Each entry is of the form:

	<path in the romfs>: <file name in the extracted GARC (or all)>: <content description>

To convert between BFLIM and PNG, you can use the included scripts. You will need OpenCV. To get it, run:

	pip3 install opencv-python

BFLIM to PNG:

	python3 bflim.py -x <bflim file>

PNG to BFLIM:

	python3 bflim.py -s <swizzling> -c <PNG input file> <BFLIM output file>

To get the original swizzling of the image, look at the console output if you used bflim.py to convert it, swizzling is the "Swizzle" value (normally 4 or 8). If you converted using the following scripts, search your file name in the generated \_extract.log, swizzling is also the 4 or 8 after "Swizzle" value

To convert all BFLIM files contained in a folder:

	python3 folder-bflim.py <folder>

bflim.py is a slightly modified version of the [ObsidianX's original](http://www.github.com/ObsidianX/3dstools) to support python3, with various minor changes like support of other formats at repacking.

The bflyt.py script is a tool to convert between BFLYT files and a homemade readable format (TFLYT for Text caFe LaYouT, opposite of Binary caFe LaYouT), editable in a text editor like Notepad++, Gedit... It is inspirated by [Diddy 81's BenzinU](https://gbatemp.net/threads/benzinu-release.423171), with support of 3DS format and many fixes and optimisations.

	python3 bflyt.py [-x | -p] <input file>

-x: convert from BFLYT to TFLYT
-p: convert from TFLYT to BFLYT

NOTE THAT ACTUALLY, IF YOU REPACK A BFLYT FILE IN AN ALYT FILE, THERE IS SOME ISSUES WITH THE ELEMENT DISPLAYING (or there is not displaying at all...). It seems to be an issues with the ALYT sections, research in progress.
