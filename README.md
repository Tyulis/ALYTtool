# ALYTtool
A tool to extract and repack ALYT files used in Pokémon games to store UI data and images

It also support transparently BL archives, which contain several ALYT and other files.

Usage:

*	to extract an ALYT or BL file:

		python3 ALYTtool.py -x <file name>

*	to repack a previously extracted ALYT or BL file (extracted with ALYTtool):
		
		python3 ALYTtool.py -p <folder name>

A little documentation about ALYT file format can be found in the ALYT_ref.txt file

A full description of BL format can be found in the BL_ref.txt file

A list of the files in the RomFS and their description (when I have found it) can be found in the files.txt file.

Each entry is of the form:

	<path in the romfs>: <file name in the extracted GARC (or all)>: <content description>

You can convert between BFLIM and PNG using [ObsidianX's 3dstools](https://www.github.com/ObsidianX/3dstools) (needs Python 2.7, [PyPNG](https://github.com/drj11/pypng), OpenCV for swizzling)
