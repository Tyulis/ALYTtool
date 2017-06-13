#!/usr/bin/env python2
import os
import sys
import struct
from bflim import Bflim

#to avoid always repeating this...
def fwrite(content,filename,mode='w'):
	f=open(filename,mode)
	f.write(content)
	f.close()

def fread(filename,mode='r'):
	f=open(filename,mode)
	content=f.read()
	f.close()
	return content
	
#only for debugging purposes
def hexdump(b):
	for i in range(0,len(b),4):
		s=b[i:i+4]
		h=s.hex().encode('ascii')
		print(h+b'       '+s)

#found on 3dbrew.org
def calc_hash(name, hash_multiplier):
	result = 0
	for c in name:
		result = ord(c) + (result * hash_multiplier)
		# ensure the result is a 32-bit value
		result &= 0xFFFFFFFF
	return result


def convertpng():
	os.chdir('timg')
	print('Converting PNG files to BFLIM')
	for p,d,files in os.walk(os.getcwd()):
		for file in files:
			if not file.endswith('.png'):
				continue
			bflim=Bflim(verbose=False, debug=False, big_endian=False, swizzle=4)
			bflim.load(file)
			bflim.save(file.replace('.png','.bflim'))
	print('Converted.')
	os.chdir('..')

def convertbflim():
	os.chdir('timg')
	print('Converting BFLIM files to PNG')
	for p,d,files in os.walk(os.getcwd()):
		for file in files:
			if not file.endswith('.bflim'):
				continue
			bflim=Bflim(verbose=False, debug=False, big_endian=False, swizzle=4)
			bflim.read(file, parse_image=True)
			if bflim.invalid:
				print('Invalid BFLIM file: %s'%file)
				continue
			bflim.extract()
			os.remove(file)
	print('Converted.')
	os.chdir('..')

def extract(alytfile):
	alyt=bytearray(fread(alytfile,'rb'))
	
	try:
		os.mkdir('_'+alytfile.split('.')[0])
	except OSError:
		pass
	os.chdir('_'+alytfile.split('.')[0])
	try:
		os.mkdir('_alyt.repack.meta')
	except:
		pass
	fwrite(alytfile,'_alyt.repack.meta/alyt.bsname')
	log=open('_alyt.repack.meta/extract.log','w')
	
	print('Reading data...')
	alytheader=alyt[0:0x28]
	log.write('Header data:\n')
	alythdata=struct.unpack('<4sIIIIIIIII',alytheader)
	log.write('Magic: %s\n'%alythdata[0])
	fwrite(str(alythdata[1]),'_alyt.repack.meta/alyt.flags')#undetermined, but don't take risk
	log.write('Header length: %d\n'%alythdata[2])
	log.write('LTBL length: %d\n'%alythdata[3])
	log.write('End of LTBL: 0x%x\n'%alythdata[4])
	log.write('LMTL length: %d\n'%alythdata[5])
	log.write('End of LMTL: 0x%x\n'%alythdata[6])
	log.write('LFNL length: %d\n'%alythdata[7])
	log.write('End of LFNL: 0x%x\n'%alythdata[8])
	log.write('File length: %d\n'%alythdata[9])
	log.write('\n')
	i=alythdata[2]
	ltbl=alyt[i:i+alythdata[3]]
	log.write('LTBL Chunk (%d;0x%x) lenght)\n'%(len(ltbl),len(ltbl)))
	fwrite(ltbl,'_alyt.repack.meta/alyt.ltbl','wb')
	log.write('\n')
	i+=alythdata[3]
	lmtl=alyt[i:i+alythdata[5]]
	log.write('LMTL Chunk (%d;0x%x) lenght)\n'%(len(lmtl),len(lmtl)))
	fwrite(lmtl,'_alyt.repack.meta/alyt.lmtl','wb')
	log.write('\n')
	i+=alythdata[5]
	lfnl=alyt[i:i+alythdata[7]]
	log.write('LFNL Chunk (%d;0x%x) lenght)\n'%(len(lfnl),len(lfnl)))
	fwrite(lfnl,'_alyt.repack.meta/alyt.lfnl','wb')
	i+=alythdata[7]
	
	i=alythdata[8]
	fwrite(str(i),'_alyt.repack.meta/alyt.elfnl')
	log.write('\n')
	filenumber=struct.unpack('<I',alyt[i:i+4])[0]
	log.write('Number of files: %d:\n'%filenumber)
	i+=4
	nametable=[]
	bs=i
	for j in range(0,filenumber):
		nametable.append(alyt[i:i+64].rstrip(b'\x00').decode('utf-8'))
		i+=64
	log.write('\n'.join(nametable))
	fwrite(alyt[bs:i],'_alyt.repack.meta/alyt.nmtb','wb')
	
	bs=i
	symnumber=struct.unpack('<I',alyt[i:i+4])[0]
	i+=4
	symtable=[]
	for j in range(0,symnumber):
		symtable.append(alyt[i:i+32].rstrip(b'\x00').decode('utf-8'))
		i+=32
	log.write('\n')
	log.write('Symbol names? (number: %d)\n'%len(symtable))
	log.write('\n'.join(symtable))
	#i+=88
	i=alyt[i:-1].index(b'SARC')+i
	fwrite(alyt[bs:i],"_alyt.repack.meta/alyt.symtbl")
	sarchdata=struct.unpack('<4sHHIII',alyt[i:i+0x14])
	log.write('\n')
	log.write('SARC Header Data:\n')
	log.write('Magic: %s\n'%sarchdata[0])
	log.write('Header Length: %d\n'%sarchdata[1])
	log.write('Byte order: %s Endian\n'%('Big' if sarchdata[2]==0xfffe else 'Little'))#read little endian, so reversed
	log.write('File Length: %d\n'%sarchdata[3])
	dataoffset=sarchdata[4]+i
	log.write('Data Offset: %x\n'%dataoffset)
	i+=0x14
	
	log.write('\n')
	log.write('SFAT Header Data:')
	sfathdata=struct.unpack('<4sHHI',alyt[i:i+0x0c])
	log.write('Magic: %s'%sfathdata[0])
	log.write('Header Length: %d\n'%sfathdata[1])
	nodenum=sfathdata[2]
	log.write('Node number: %d\n'%sfathdata[2])
	log.write('Hash Multiplier: %d\n'%sfathdata[3])
	fwrite(str(sfathdata[3]),'_alyt.repack.meta/sfat.hashmul')
	i+=0x0c
	sfatnodes=[]
	log.write('\n')
	padinfo=[]
	prevfileend=-1
	for j in range(0,nodenum):
		nodedata=list(struct.unpack('<IIII',alyt[i:i+0x10]))
		namehash=nodedata[0]
		nameoffset=nodedata[1]
		if prevfileend!=-1: #=not the first
			padinfo.append(nodedata[2]-prevfileend)
		nodedata[2]+=dataoffset
		filebegin=nodedata[2]
		prevfileend=nodedata[3]
		nodedata[3]+=dataoffset
		fileend=nodedata[3]+dataoffset
		log.write('SFAT Node %x\n:'%namehash)
		log.write('File Name Offset: %x\n'%nameoffset)
		log.write('File Start Offset: %x\n'%filebegin)
		log.write('File End Offset: %x\n'%fileend)
		i+=0x10
		sfatnodes.append(nodedata)
	padinfo=''.join([chr(c) for c in padinfo])
	fwrite(padinfo,'_alyt.repack.meta/sarc.pad','wb')
	log.write('\n')
	log.write('SFNT Header Data:\n')
	sfnthdata=struct.unpack('<4sHH',alyt[i:i+8])
	log.write('Magic: %s\n'%sfnthdata[0])
	log.write('Header Length: %d\n'%sfnthdata[1])
	log.write('Padding?: %x\n'%sfnthdata[2])
	i+=8
	sfntdata={}
	name=b''
	zero=0
	bs=i
	for char in alyt[i:]:
		i+=1
		if char==0:
			zero+=1
			if name!=b'':
				sfntdata[(i-len(name)-bs)//4]=name
				name=b''
			if zero>4:
				break
		else:
			zero=0
			name+=chr(char)
	sfnt=alyt[bs:sfatnodes[0][2]]
	fwrite(sfnt,'_alyt.repack.meta/alyt.sfnt','wb')
	log.write('SFNT Data:\n')
	for k in sfntdata.keys():
		log.write('%x: %s\n'%(k,sfntdata[k]))
	log.write('\n')
	
	print('Extracting...')
	for filedata in sfatnodes:
		filename=sfntdata[filedata[1]&0xffffff]
		filename=filename.decode('utf-8')
		if '/' in filename:
			dir=filename.split('/')[0]
			if not os.path.exists(dir):
				os.mkdir(dir)
		data=alyt[filedata[2]:filedata[3]]
		fwrite(data,filename,'wb')
		log.write('Extracted %s\n'%filename)
	log.close()
	print('Finished extracting.')

def repacksarc():
	print('Repacking SARC section...')
	sfnt=bytearray(fread('_alyt.repack.meta/alyt.sfnt','rb'))
	hashmul=int(fread('_alyt.repack.meta/sfat.hashmul'))
	sfntdata=[]
	name=b''
	zero=0
	i=0
	for char in sfnt:
		i+=1
		if char==0:
			zero+=1
			if name!=b'':
				sfntdata.append((calc_hash(name,hashmul),(i-len(name))//4,name))
				name=b''
			if zero>4:
				break
		else:
			zero=0
			name+=chr(char)
	sfntdata.sort()
	sfntheader=struct.pack('<4sHH','SFNT',0x08,0x00)
	sfatnodes=[]
	filedata=''
	pointer=0
	padinfo=fread('_alyt.repack.meta/sarc.pad','rb')
	for i,info in enumerate(sfntdata):
		content=fread(info[2],'rb')
		filestart=pointer
		fileend=filestart+len(content)
		try:
			padding=ord(padinfo[i])
		except IndexError:
			padding=0
		filedata+=content+(padding*b'\x00')
		pointer+=len(content)+padding
		node=[info[0],(info[1]|0x01000000),filestart,fileend]
		sfatnodes.append(node)
	sfattable=''.join([struct.pack('<IIII',*node) for node in sfatnodes])
	sfatheader=struct.pack('<4sHHI','SFAT',0x0c,len(sfatnodes),hashmul)
	
	headdata=sfatheader+sfattable+sfntheader+sfnt
	sarcdata=headdata+filedata
	sarcheader=struct.pack('<4sHHIII','SARC',0x14,0xfeff,len(sarcdata)+0x14,len(headdata)+0x14,0x00000100)
	sarc=sarcheader+sarcdata
	return sarc,[el[2] for el in sfntdata]

def repack(folder):
	os.chdir(folder)
	sarc,filenames=repacksarc()
	print('Repacking ALYT file...')
	ltbl=fread('_alyt.repack.meta/alyt.ltbl','rb')
	lmtl=fread('_alyt.repack.meta/alyt.lmtl','rb')
	lfnl=fread('_alyt.repack.meta/alyt.lfnl','rb')
	#but is it a symbol table? That's the question.
	symtable=fread('_alyt.repack.meta/alyt.symtbl','rb')
	nametable=fread('_alyt.repack.meta/alyt.nmtb','rb')
	nametable=struct.pack('<I',len(filenames))+nametable
	datastart=int(fread('_alyt.repack.meta/alyt.elfnl'))
	hdrdata=ltbl+lmtl+lfnl
	padding=(datastart-(len(hdrdata)+0x28))*'\x00'
	hdrdata+=padding+nametable+symtable
	data=hdrdata+sarc
	lmtloffset=0x28+len(ltbl)
	lfnloffset=lmtloffset+len(lmtl)
	hdrflag=int(fread('_alyt.repack.meta/alyt.flags'))
	alytheader=struct.pack('<4sIIIIIIIII','ALYT',hdrflag,0x28,len(ltbl),lmtloffset,len(lmtl),lfnloffset,len(lfnl),datastart,len(data)+0x28-datastart)
	alyt=alytheader+data
	finalname=fread('_alyt.repack.meta/alyt.bsname')+'.repacked'
	os.chdir('..')
	fwrite(alyt,finalname,'wb')
	print('Finished!')
	return 0
	
if __name__=='__main__':
	args=sys.argv[1:-1]
	filename=sys.argv[-1]
	script=sys.argv[0].split('/')[-1]
	if len(args)==0 or '-h' in args or filename=='-h':
		print('ALYTtool.py')
		print('An ALYT files extractor written by Tyulis')
		print('Use:')
		print('	%s [-h] [-x | -p] [-c] file_name'%script)
		print()
		print('	-h : Shows this help')
		print('	-x : Extracts an ALYT file in a folder')
		print('	-p : Repack a previously extracted ALYT file from a folder')
		print('	-c : Convert directly BFLIM files to PNG when extracting and PNG to BFLIM when repacking, using bflim.py from ObsidianX\'s 3dstools')
		print('	file_name : ALYT file name when extracting and folder name when repacking')
	if '-x' in args:
		extract(filename)
		if '-c' in args:
			convertbflim()
		os.chdir('..')
	elif '-p' in args:
		os.chdir(filename)
		if '-c' in args:
			convertpng()
		os.chdir('..')
		repack(filename)
