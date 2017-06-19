# ALYTtool
A tool to extract and repack ALYT files used in Pokémon games to store UI data and images

Usage:

*	to extract an ALYT file:

		python3 ALYTtool.py -x <ALYT file name>

*	to repack a previously extracted ALYT file (extracted with ALYTtool):
		
		python3 ALYTtool.py -p <folder name>

Documentation about ALYT file format can be found in the ALYT_ref.txt file

You can convert between BFLIM and PNG using [ObsidianX's 3dstools](https://www.github.com/ObsidianX/3dstools) (needs Python 2.7, [PyPNG](https://github.com/drj11/pypng), OpenCV for swizzling)
