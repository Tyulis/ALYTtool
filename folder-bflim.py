import os
import sys
from bflim import Bflim

path=sys.argv[1]+"/"

def ls(path):
	for p,d,f in os.walk(path):
		break
	f.sort()
	return f

folder="bflim-%s/"%sys.argv[1]
try:
	os.mkdir(folder)
except:
	pass
log=open(folder+"_extract.log","w")
sys.stdout=log
for fn in ls(path):
	print()
	print()
	print(fn)
	sys.__stdout__.write(fn+'\n')
	bflim = Bflim(verbose=False, debug=True, big_endian=False, swizzle=None)
	bflim.read(path+fn, parse_image=True)
	bflim.extract()
	os.rename(fn.replace(".bin",".png"),folder+fn.replace(".bin",".png"))
sys.stdout=sys.__stdout__
