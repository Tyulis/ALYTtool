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

To convert between BFLIM and PNG, you can use the included scripts. You will need OpenCV. To get it, run:

	pip3 install opencv-python

BFLIM to PNG:

	python3 bflim.py -x <bflim file>

PNG to BFLIM:

	python3 bflim.py -s <swizzling> -c <PNG input file> <BFLIM output file>

To get the original swizzling of the image, look at the console output if you used bflim.py to convert it, swizzling is the "Swizzle" value (normally 4 or 8). If you converted using the following scripts, search your file name in the generated \_extract.log, swizzling is also the 4 or 8 after "Swizzle" value

To convert all BFLIM files contained in an extracted ALYT file to PNG:

	python3 alyt-bflim.py <extracted ALYT folder name>

To convert all BFLIM files contained in an extracted BL file to PNG:

	python3 bl-bflim.py <extracted BL folder name>

To convert all BFLIM files contained in a folder:

	python3 folder-bflim.py <folder>

bflim.py is a slightly modified version of the [ObsidianX's original](http://www.github.com/ObsidianX/3dstools) to support python3, with various minor changes.
