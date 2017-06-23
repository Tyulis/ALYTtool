import os
import sys
from bflim import Bflim

path=sys.argv[1]+"/"

def ls(path):
	for p,d,f in os.walk(path):
		break
	f.sort()
	return f

def dls(path):
	for p,d,f in os.walk(path):
		break
	d.sort()
	return d

folder="timg-bl-%s/"%sys.argv[1]
try:
	os.mkdir(folder)
except:
	pass
for dr in dls(path):
	dr+='/'
	try:
		os.mkdir(folder+dr)
	except:
		pass
	log=open(folder+dr+"_extract.log","w")
	sys.stdout=log
	for fn in ls(path+dr+'timg/'):
		print()
		print()
		print(fn)
		sys.__stdout__.write(dr+fn+'\n')
		bflim = Bflim(verbose=False, debug=True, big_endian=False, swizzle=None)
		bflim.read(path+dr+'timg/'+fn, parse_image=True)
		bflim.extract()
		os.rename(fn.replace(".bflim",".png"),folder+dr+fn.replace(".bflim",".png"))
	log.close()
sys.stdout=sys.__stdout__
