#!/usr/bin/env python2
import os
import sys
import shutil
import struct

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
		result = c + (result * hash_multiplier)
		# ensure the result is a 32-bit value
		result &= 0xFFFFFFFF
	return result

def extractALYT(alyt,name):
	if '.' in name: #ugly. But it permit to avoid problems with BL files.
		folder='_'+'.'.join(name.replace('/','-').split('.')[0:-1])
	else:
		folder='_'+name
	try:
		os.mkdir(folder)
	except OSError:
		pass
	os.chdir(folder)
	try:
		os.mkdir('_alyt.repack.meta')
	except:
		pass
	fwrite(name,'_alyt.repack.meta/alyt.bsname')
	log=open('_alyt.repack.meta/extract.log','w')
	
	print('Reading data...')
	alytheader=alyt[0:0x28]
	log.write('Header data:\n')
	try:
		alythdata=struct.unpack('<4sIIIIIIIII',alytheader)
	except struct.error: #for too short files
		print('Not a valid ALYT file')
		os.chdir('..')
		shutil.rmtree(folder)
		return 17 #Don't ask, it's random
	if alythdata[0]!=b'ALYT':
		print('Not a valid ALYT file')
		os.chdir('..')
		shutil.rmtree(folder)
		return 17
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
	log.write('LTBL Chunk (%d;0x%x) lenght -> %d without header)\n'%(len(ltbl),len(ltbl),len(ltbl)-8))
	fwrite(ltbl,'_alyt.repack.meta/alyt.ltbl','wb')
	log.write('\n')
	i+=alythdata[3]
	lmtl=alyt[i:i+alythdata[5]]
	log.write('LMTL Chunk (%d;0x%x) lenght -> %d without header)\n'%(len(lmtl),len(lmtl),len(lmtl)-8))
	fwrite(lmtl,'_alyt.repack.meta/alyt.lmtl','wb')
	log.write('\n')
	i+=alythdata[5]
	lfnl=alyt[i:i+alythdata[7]]
	log.write('LFNL Chunk (%d;0x%x) lenght -> %d without header)\n'%(len(lfnl),len(lfnl),len(lfnl)-8))
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
	log.write('\nSymbol names? (number: %d)\n'%len(symtable))
	log.write('\n'.join(symtable))
	i=alyt[i:-1].index(b'SARC')+i
	fwrite(alyt[bs:i],"_alyt.repack.meta/alyt.symtbl","wb")
	sarchdata=struct.unpack('<4sHHIII',alyt[i:i+0x14])
	log.write('\n')
	log.write('\nSARC Header Data:\n')
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
	padinfo=bytes(padinfo)
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
			name+=bytes((char,))
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
	os.chdir('..')

def extract(filename):
	data=fread(filename,'rb')
	if data.startswith(b'ALYT'):
		print('ALYT file found')
		extractALYT(data,filename)
	elif data.startswith(b'BL'):
		print('BL file found')
		table=data[4:0x80]
		folder='BL-'+'.'.join(filename.replace('/','-').split('.')[0:-1])+'/'
		try:
			os.mkdir(folder)
		except:
			shutil.rmtree(folder)
			os.mkdir(folder)
		fwrite(filename,folder+'.BL_name')
		offsets=[struct.unpack('<I',table[i:i+4])[0] for i in range(0,len(table),4)]
		offsets=[offset for offset in offsets if offset!=0] #remove the 00000000 offsets which are after the table end
		del offsets[-1] #because the last offset is the file end, not a subfile offset
		index=0
		for i,fileoffset in enumerate(offsets):
			if i!=len(offsets)-1: #for the normal files
				filedata=data[fileoffset:offsets[i+1]]
			else: #and for the last in the archive
				filedata=data[fileoffset:]
			res=extractALYT(filedata,str(index))
			if res!=17:
				alytfolder='_'+str(index)
				os.rename(alytfolder, folder+str(index))
			else:
				fwrite(filedata, folder+str(index)+'.bin', 'wb')
			index+=1
	else:
		print('Unrecognized file.')
		return 11
		

def repackSARC():
	print('Repacking SARC section...')
	sfnt=fread('_alyt.repack.meta/alyt.sfnt','rb')
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
			name+=bytes((char,))
	sfntdata.sort()
	sfntheader=struct.pack('<4sHH',b'SFNT',0x08,0x00)
	sfatnodes=[]
	filedata=b''
	pointer=0
	padinfo=fread('_alyt.repack.meta/sarc.pad','rb')
	for i,info in enumerate(sfntdata):
		content=fread(info[2],'rb')
		filestart=pointer
		fileend=filestart+len(content)
		try:
			padding=padinfo[i]
		except IndexError:
			padding=0
		filedata+=content+(padding*b'\x00')
		pointer+=len(content)+padding
		node=[info[0],(info[1]|0x01000000),filestart,fileend]
		sfatnodes.append(node)
	sfattable=b''.join([struct.pack('<IIII',*node) for node in sfatnodes])
	sfatheader=struct.pack('<4sHHI',b'SFAT',0x0c,len(sfatnodes),hashmul)
	
	headdata=sfatheader+sfattable+sfntheader+sfnt
	sarcdata=headdata+filedata
	sarcheader=struct.pack('<4sHHIII',b'SARC',0x14,0xfeff,len(sarcdata)+0x14,len(headdata)+0x14,0x00000100)
	sarc=sarcheader+sarcdata
	return sarc,[el[2] for el in sfntdata]

def repackALYT(folder):
	os.chdir(folder)
	sarc,filenames=repackSARC()
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
	padding=(datastart-(len(hdrdata)+0x28))*b'\x00'
	hdrdata+=padding+nametable+symtable
	data=hdrdata+sarc
	lmtloffset=0x28+len(ltbl)
	lfnloffset=lmtloffset+len(lmtl)
	hdrflag=int(fread('_alyt.repack.meta/alyt.flags'))
	alytheader=struct.pack('<4sIIIIIIIII',b'ALYT',hdrflag,0x28,len(ltbl),lmtloffset,len(lmtl),lfnloffset,len(lfnl),datastart,len(data)+0x28-datastart)
	alyt=alytheader+data
	finalname=fread('_alyt.repack.meta/alyt.bsname')+'.repacked'
	os.chdir('..')
	fwrite(alyt,finalname,'wb')
	print('Finished!')
	return 0

def repackBL(folder):
	print('Repacking the BL archive...')
	for path, folders, files in os.walk(folder): #to get the content of the folder
		break
	os.chdir(folder)
	files=[f for f in files if f.endswith('.bin')]
	filesnumber=len(files)+len(folders)
	subfiles=[None]*filesnumber
	print('Repacking ALYT files...')
	for alytfolder in folders:
		repackALYT(alytfolder)
		subfiles[int(alytfolder.lstrip('_'))]=fread(alytfolder.lstrip('_')+'.repacked','rb')
	for otherfile in files:
		subfiles[int(otherfile.split('.')[0])]=fread(otherfile.split('.')[0])
	#now repacking.
	print('Repacking the BL file...')
	magic=struct.pack('<2sH',b'BL',filesnumber) #magic+files number
	table=b''
	data=b''
	for filedata in subfiles:
		padding=0x80-(len(filedata)%0x80)
		filedata+=b'\x00'*padding
		table+=struct.pack('<I',0x80+len(data))
		data+=filedata
	table+=struct.pack('<I',0x80+len(data)) #the last offset is the BL file's end
	header=magic+table
	hdrpadding=0x80-(len(header)%0x80)
	header+=b'\x00'*hdrpadding
	final=header+data
	finalname=fread('.BL_name')+'.repacked'
	os.chdir('..')
	fwrite(final,finalname,'wb')
	print('Finished!')
		

def repack(folder):
	if not folder.endswith('/'): #more practical.
		folder+='/'
	if os.path.exists(folder+'.BL_name'):
		repackBL(folder)
	else:
		repackALYT(folder)
	
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
		print('	file_name : ALYT file name when extracting and folder name when repacking')
	if '-x' in args:
		extract(filename)
	elif '-p' in args:
		repack(filename)
