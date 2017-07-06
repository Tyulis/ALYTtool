#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import re
import sys
import shutil
import struct
import argparse

import bflim
import bflyt
from txtree import dump, load

GET_SWIZZLE_FROM_LOG = re.compile(r'.*?\(0x(\d)\)')


#to avoid always repeating this...
def fwrite(content, filename, mode='w'):
	if mode == 'w':
		f = open(filename, mode, encoding='utf-8')
	else:
		f = open(filename, mode)
	f.write(content)
	f.close()


def fread(filename, mode='r'):
	if mode == 'r':
		f = open(filename, mode, encoding='utf-8')
	else:
		f = open(filename, mode)
	content = f.read()
	f.close()
	return content


def ls(path='.'):
	for path, folders, files in os.walk(path):  #to get the content of the folder
		break
	return path, folders, files


#only for debugging purposes
def hexdump(b):
	for i in range(0, len(b), 4):
		s = b[i:i + 4]
		h = s.hex().encode('ascii')
		print(h+b'       '+s)


#found on 3dbrew.org
def calc_hash(name, hash_multiplier):
	result = 0
	for c in name:
		result = c + (result * hash_multiplier)
		# ensure the result is a 32-bit value
		result &= 0xFFFFFFFF
	return result


def extract_convert(name):
	if '.' in name:  #ugly. But it permits to avoid problems with BL files.
		folder = '_' + '.'.join(name.replace('/', '-').split('.')[0:-1]) + '/'
	else:
		folder = '_' + name + '/'
	if os.path.exists(folder+'_alyt.repack.meta'):
		extract_convert_ALYT(folder)
	else:
		extract_convert_BL(folder)
	

def extract_convert_BL(folder):
	os.chdir(folder)
	path, folders, files = ls()
	for alyt in folders:
		extract_convert_ALYT(alyt)
	os.chdir('..')


def extract_convert_ALYT(folder):
	os.chdir(folder+'timg')
	path, folders, files = ls()
	log = open('_extract.log', 'w')
	sys.stdout = log
	for filename in files:
		if not filename.endswith('.bflim'):
			continue
		sys.__stdout__.write(filename + '\n')
		print(filename)
		img = bflim.Bflim(verbose=False, debug=True, big_endian=False, swizzle=0)
		img.read(filename, parse_image=True)
		if img.invalid:
			sys.stdout = sys.__stdout__
			print('%s is not a valid BFLIM file' % filename)
			sys.exit(13)
		img.extract()
		os.remove(filename)
		print('')
	sys.stdout = sys.__stdout__
	print('Extracted BFLIM files')
	os.chdir('../blyt')
	path, folders, files = ls()
	for filename in files:
		if not filename.endswith('.bflyt'):
			continue
		print(filename)
		outname = filename.replace('.bflyt',  '.tflyt')
		tree = bflyt.frombflyt(fread(filename,  'rb'))
		fwrite(dump(tree, [bflyt.OrderedDict]), outname, 'w')
		os.remove(filename)
	print('Extracted BFLYT files')
	os.chdir('..')
	print('Finished!')


def repack_convert(folder):
	if not folder.endswith('/'):  #more practice
		folder += '/'
	if os.path.exists(folder+'_alyt.repack.meta'):
		repack_convert_ALYT(folder)
	else:
		repack_convert_BL(folder)


def repack_convert_BL(folder):
	os.chdir(folder)
	path, folders, files = ls()
	for alyt in folders:
		repack_convert_ALYT(alyt)
	os.chdir('..')


def repack_convert_ALYT(folder):
	os.chdir(folder+'timg')
	logbs = fread('_extract.log', 'r').splitlines()
	log = [[]]
	for line in logbs:
		if line == '':
			log.append([])
		elif line.endswith('.bflim') or line.startswith('imag Swizzle:') or line.startswith('imag Format'):
			log[-1].append(line)
	if log[-1] == []:
		del log[-1]
	for info in log:
		print(info[0])
		format = info[1].split(': ')[1]
		swizzle = int(re.sub(GET_SWIZZLE_FROM_LOG, r'\1', info[2]))
		img = bflim.Bflim(verbose=False, debug=True, big_endian=False, swizzle=swizzle, format=format)
		img.load(info[0].replace('.bflim', '.png'))
		img.save(info[0])
	os.chdir('../blyt')
	path, folders, files = ls()
	for filename in files:
		if not filename.endswith('.tflyt'):
			continue
		outname = filename.replace('.tflyt', '.bflyt')
		tree = load(fread(filename, 'r'))
		final = bflyt.tobflyt(tree)
		fwrite(final, outname, 'wb')
	os.chdir('../..')


def extractALYT(alyt, name):
	if '.' in name:  #ugly. But it permits to avoid problems with BL files.
		folder = '_' + '.'.join(name.replace('/', '-').split('.')[0:-1])
	else:
		folder = '_' + name
	try:
		os.mkdir(folder)
	except OSError:
		pass
	os.chdir(folder)
	try:
		os.mkdir('_alyt.repack.meta')
	except:
		pass
	fwrite(name, '_alyt.repack.meta/alyt.bsname')
	log = open('_alyt.repack.meta/extract.log', 'w')
	
	print('Reading data...')
	alytheader = alyt[0:0x28]
	log.write('Header data:\n')
	try:
		alythdata = struct.unpack('<4sIIIIIIIII', alytheader)
	except struct.error:  #for too short files
		print('Not a valid ALYT file')
		os.chdir('..')
		shutil.rmtree(folder)
		return 17  #Don't ask, it's random
	if alythdata[0] != b'ALYT':
		print('Not a valid ALYT file')
		os.chdir('..')
		shutil.rmtree(folder)
		return 17
	#purpose undetermined, but don't take risk
	log.write('Magic: %s\n' % alythdata[0])
	fwrite(str(alythdata[1]), '_alyt.repack.meta/alyt.flags')
	log.write('Header length: %d\n' % alythdata[2])
	log.write('LTBL length: %d\n' % alythdata[3])
	log.write('End of LTBL: 0x%x\n' % alythdata[4])
	log.write('LMTL length: %d\n' % alythdata[5])
	log.write('End of LMTL: 0x%x\n' % alythdata[6])
	log.write('LFNL length: %d\n' % alythdata[7])
	log.write('End of LFNL: 0x%x\n' % alythdata[8])
	log.write('File length: %d\n' % alythdata[9])
	log.write('\n')
	i = alythdata[2]
	ltbl = alyt[i:i+alythdata[3]]
	log.write('LTBL Chunk (%d;0x%x) lenght -> %d without header)\n' % (len(ltbl), len(ltbl), len(ltbl)-8))
	fwrite(ltbl, '_alyt.repack.meta/alyt.ltbl', 'wb')
	log.write('\n')
	i += alythdata[3]
	lmtl = alyt[i:i + alythdata[5]]
	log.write('LMTL Chunk (%d;0x%x) lenght -> %d without header)\n' % (len(lmtl), len(lmtl), len(lmtl)-8))
	fwrite(lmtl, '_alyt.repack.meta/alyt.lmtl', 'wb')
	log.write('\n')
	i += alythdata[5]
	lfnl = alyt[i:i + alythdata[7]]
	log.write('LFNL Chunk (%d;0x%x) lenght -> %d without header)\n' % (len(lfnl), len(lfnl), len(lfnl)-8))
	fwrite(lfnl, '_alyt.repack.meta/alyt.lfnl', 'wb')
	i += alythdata[7]
	
	i = alythdata[8]
	fwrite(str(i), '_alyt.repack.meta/alyt.elfnl')
	log.write('\n')
	filenumber = struct.unpack('<I', alyt[i:i + 4])[0]
	log.write('Number of files: %d:\n' % filenumber)
	i += 4
	nametable = []
	bs = i
	for j in range(0, filenumber):
		nametable.append(alyt[i:i + 64].rstrip(b'\x00').decode('utf-8'))
		i += 64
	j = 0
	for nm in nametable:
		log.write('%d: %s\n' % (j, nm))
		j += 1
		
	fwrite(alyt[bs:i], '_alyt.repack.meta/alyt.nmtb', 'wb')
	
	bs = i
	symnumber = struct.unpack('<I', alyt[i:i + 4])[0]
	i += 4
	symtable = []
	for j in range(0, symnumber):
		symtable.append(alyt[i:i + 32].rstrip(b'\x00').decode('utf-8'))
		i += 32
	log.write('\n')
	log.write('\nSymbols (number: %d)\n' % len(symtable))
	j = 0
	for sym in symtable:
		log.write('%d: %s\n' % (j, sym))
		j += 1
	i = alyt[i:-1].index(b'SARC') + i
	fwrite(alyt[bs:i], '_alyt.repack.meta/alyt.symtbl', 'wb')
	sarchdata = struct.unpack('<4sHHIII', alyt[i:i + 0x14])
	log.write('\n')
	log.write('\nSARC Header Data:\n')
	log.write('Magic: %s\n' % sarchdata[0])
	log.write('Header Length: %d\n' % sarchdata[1])
	log.write('Byte order: %s Endian\n' % ('Big' if sarchdata[2] == 0xfffe else 'Little'))  #read little endian, so reversed
	log.write('File Length: %d\n' % sarchdata[3])
	dataoffset = sarchdata[4] + i
	log.write('Data Offset: %x\n' % dataoffset)
	i += 0x14
	
	log.write('\n')
	log.write('SFAT Header Data:')
	sfathdata = struct.unpack('<4sHHI', alyt[i:i + 0x0c])
	log.write('Magic: %s' % sfathdata[0])
	log.write('Header Length: %d\n' % sfathdata[1])
	nodenum = sfathdata[2]
	log.write('Node number: %d\n' % sfathdata[2])
	log.write('Hash Multiplier: %d\n' % sfathdata[3])
	fwrite(str(sfathdata[3]), '_alyt.repack.meta/sfat.hashmul')
	i += 0x0c
	sfatnodes = []
	log.write('\n')
	padinfo = []
	prevfileend = -1
	for j in range(0, nodenum):
		nodedata = list(struct.unpack('<IIII', alyt[i:i + 0x10]))
		namehash = nodedata[0]
		nameoffset = nodedata[1]
		if prevfileend != -1:  #=not the first
			padinfo.append(nodedata[2] - prevfileend)
		nodedata[2] += dataoffset
		filebegin = nodedata[2]
		prevfileend = nodedata[3]
		nodedata[3] += dataoffset
		fileend = nodedata[3] + dataoffset
		log.write('SFAT Node %x\n:' % namehash)
		log.write('File Name Offset: %x\n' % nameoffset)
		log.write('File Start Offset: %x\n' % filebegin)
		log.write('File End Offset: %x\n' % fileend)
		i += 0x10
		sfatnodes.append(nodedata)
	padinfo = bytes(padinfo)
	fwrite(padinfo, '_alyt.repack.meta/sarc.pad', 'wb')
	log.write('\n')
	log.write('SFNT Header Data:\n')
	sfnthdata = struct.unpack('<4sHH', alyt[i:i + 8])
	log.write('Magic: %s\n' % sfnthdata[0])
	log.write('Header Length: %d\n' % sfnthdata[1])
	log.write('Padding?: %x\n' % sfnthdata[2])
	i += 8
	sfntdata = {}
	name = b''
	zero = 0
	bs = i
	for char in alyt[i:]:
		i += 1
		if char == 0:
			zero += 1
			if name != b'':
				sfntdata[(i - len(name) - bs) // 4] = name
				name = b''
			if zero > 4:
				break
		else:
			zero = 0
			name += bytes((char, ))
	sfnt = alyt[bs:sfatnodes[0][2]]
	fwrite(sfnt, '_alyt.repack.meta/alyt.sfnt', 'wb')
	log.write('SFNT Data:\n')
	for k in sfntdata.keys():
		log.write('%x: %s\n' % (k, sfntdata[k]))
	log.write('\n')
	
	print('Extracting...')
	for filedata in sfatnodes:
		filename = sfntdata[filedata[1] & 0xffffff]
		filename = filename.decode('utf-8')
		if '/' in filename:
			dir = filename.split('/')[0]
			if not os.path.exists(dir):
				os.mkdir(dir)
		data = alyt[filedata[2]:filedata[3]]
		fwrite(data, filename, 'wb')
		log.write('Extracted %s\n' % filename)
	log.close()
	print('Finished extracting.')
	os.chdir('..')


def extract(filename):
	data = fread(filename, 'rb')
	if data.startswith(b'ALYT'):
		print('ALYT file found')
		extractALYT(data, filename)
	elif data.startswith(b'BL'):
		print('BL file found')
		table = data[4:0x80]
		folder = 'BL-' + '.'.join(filename.replace('/', '-').split('.')[0:-1]) + '/'
		try:
			os.mkdir(folder)
		except:
			shutil.rmtree(folder)
			os.mkdir(folder)
		fwrite(filename, folder + '.BL_name')
		offsets = [struct.unpack('<I', table[i:i + 4])[0] for i in range(0, len(table), 4)]
		offsets = [offset for offset in offsets if offset != 0]  #remove the 00000000 offsets which are after the table end
		del offsets[-1]  #because the last offset is the file end, not a subfile offset
		index = 0
		for i, fileoffset in enumerate(offsets):
			if i != len(offsets) - 1:  #for the normal files
				filedata = data[fileoffset:offsets[i + 1]]
			else:  #and for the last in the archive
				filedata = data[fileoffset:]
			res = extractALYT(filedata, str(index))
			if res != 17:
				alytfolder = '_' + str(index)
				os.rename(alytfolder, folder + str(index))
			else:
				fwrite(filedata, folder+str(index)+'.bin', 'wb')
			index += 1
	else:
		print('Unrecognized file.')
		return 11
		

def repackSARC():
	print('Repacking SARC section...')
	sfnt = fread('_alyt.repack.meta/alyt.sfnt', 'rb')
	hashmul = int(fread('_alyt.repack.meta/sfat.hashmul'))
	sfntdata = []
	name = b''
	zero = 0
	i = 0
	for char in sfnt:
		i += 1
		if char == 0:
			zero += 1
			if name != b'':
				sfntdata.append((calc_hash(name, hashmul), (i - len(name)) // 4, name))
				name = b''
			if zero > 4:
				break
		else:
			zero = 0
			name += bytes((char, ))
	sfntdata.sort()
	sfntheader = struct.pack('<4sHH', b'SFNT', 0x08, 0x00)
	sfatnodes = []
	filedata = b''
	pointer = 0
	padinfo = fread('_alyt.repack.meta/sarc.pad', 'rb')
	for i, info in enumerate(sfntdata):
		content = fread(info[2], 'rb')
		filestart = pointer
		fileend = filestart + len(content)
		try:
			padding = padinfo[i]
		except IndexError:
			padding = 0
		filedata += content + (padding * b'\x00')
		pointer += len(content) + padding
		node = [info[0], (info[1] | 0x01000000), filestart, fileend]
		sfatnodes.append(node)
	sfattable = b''.join([struct.pack('<IIII', *node) for node in sfatnodes])
	sfatheader = struct.pack('<4sHHI', b'SFAT', 0x0c, len(sfatnodes), hashmul)
	
	headdata = sfatheader + sfattable + sfntheader + sfnt
	sarcdata = headdata + filedata
	sarcheader = struct.pack('<4sHHIII', b'SARC', 0x14, 0xfeff, len(sarcdata) + 0x14, len(headdata) + 0x14, 0x00000100)
	sarc = sarcheader + sarcdata
	return sarc, [el[2] for el in sfntdata]


def repackALYT(folder):
	os.chdir(folder)
	sarc, filenames = repackSARC()
	print('Repacking ALYT file...')
	ltbl = fread('_alyt.repack.meta/alyt.ltbl', 'rb')
	lmtl = fread('_alyt.repack.meta/alyt.lmtl', 'rb')
	lfnl = fread('_alyt.repack.meta/alyt.lfnl', 'rb')
	#but is it a symbol table? That's the question.
	symtable = fread('_alyt.repack.meta/alyt.symtbl', 'rb')
	nametable = fread('_alyt.repack.meta/alyt.nmtb', 'rb')
	nametable = struct.pack('<I', len(filenames)) + nametable
	datastart = int(fread('_alyt.repack.meta/alyt.elfnl'))
	hdrdata = ltbl + lmtl + lfnl
	padding = (datastart - (len(hdrdata) + 0x28)) * b'\x00'
	hdrdata += padding + nametable + symtable
	data = hdrdata + sarc
	lmtloffset = 0x28 + len(ltbl)
	lfnloffset = lmtloffset + len(lmtl)
	hdrflag = int(fread('_alyt.repack.meta/alyt.flags'))
	alytheader = struct.pack('<4sIIIIIIIII', b'ALYT', hdrflag, 0x28, len(ltbl), lmtloffset, len(lmtl), lfnloffset, len(lfnl), datastart, len(data) + 0x28 - datastart)
	alyt = alytheader + data
	finalname = fread('_alyt.repack.meta/alyt.bsname') + '.repacked'
	os.chdir('..')
	fwrite(alyt, finalname, 'wb')
	print('Finished!')
	return 0


def repackBL(folder):
	print('Repacking the BL archive...')
	path, folders, files = ls(folder)
	os.chdir(folder)
	files = [f for f in files if f.endswith('.bin')]
	filesnumber = len(files) + len(folders)
	subfiles = [None] * filesnumber
	print('Repacking ALYT files...')
	for alytfolder in folders:
		repackALYT(alytfolder)
		subfiles[int(alytfolder.lstrip('_'))] = fread(alytfolder.lstrip('_') + '.repacked', 'rb')
	for otherfile in files:
		subfiles[int(otherfile.split('.')[0])] = fread(otherfile.split('.')[0])
	#now repacking.
	print('Repacking the BL file...')
	magic = struct.pack('<2sH', b'BL', filesnumber)  #magic+files number
	table = b''
	data = b''
	for filedata in subfiles:
		padding = 0x80 - (len(filedata) % 0x80)
		filedata += b'\x00' * padding
		table += struct.pack('<I', 0x80 + len(data))
		data += filedata
	table += struct.pack('<I', 0x80 + len(data))  #the last offset is the BL file's end
	header = magic+table
	hdrpadding = 0x80 - (len(header) % 0x80)
	header += b'\x00' * hdrpadding
	final = header + data
	finalname = fread('.BL_name')+'.repacked'
	os.chdir('..')
	fwrite(final, finalname, 'wb')
	print('Finished!')
		

def repack(folder):
	if not folder.endswith('/'):  #more practice.
		folder += '/'
	if os.path.exists(folder+'.BL_name'):
		repackBL(folder)
	else:
		repackALYT(folder)
	
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='A tool to extract and repack ALYT files found in 3DS games')
	mode = parser.add_mutually_exclusive_group()
	mode.add_argument('-x', '--extract', help='Extract files from an ALYT or BL file', action='store_true')
	mode.add_argument('-p', '--pack', help='Repack a previously extracted ALYT or BL file', action='store_true')
	parser.add_argument('-c', '--convert', help='Automatically convert BFLYT files to TFLYT and BFLIM files to PNG at extract, and re-convert them in their original format at repacking', action='store_true')
	parser.add_argument('input_name', help='ALYT, BL file or folder')
	args = parser.parse_args()
	if args.extract:
		extract(args.input_name)
		if args.convert:
			extract_convert(args.input_name)
	elif args.pack:
		if args.convert:
			repack_convert(args.input_name)
		repack(args.input_name)
