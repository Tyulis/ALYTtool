# -*- coding:utf-8 -*-
import sys
from txtree import dump,load
import collections
import struct

FILE='_garc-099-11/blyt/TitleMoon_Main_Up_000_de.bflyt'

FLYT_HEADER='%s4sHHHHIHH'
WRAPS=(
	'Near-Clamp',
	'Near-Repeat',
	'Near-Mirror',
	'GX2-Mirror-Once',
	'Clamp',
	'Repeat',
	'Mirror',
	'GX2-Mirror-Once-Border'
)
MAPPING_METHODS=(
	'UV-Mapping',
	'',
	'',
	'Orthogonal-Projection',
	'PaneBasedProjection'
)
BLENDS=(
	'Max',
	'Min'
)

COLOR_BLENDS=(
	'Overwrite',
	'Multiply',
	'Add',
	'Exclude',
	'4',
	'Subtract',
	'Dodge',
	'Burn',
	'Overlay',
	'Indirect',
	'Blend-Indirect',
	'Each-Indirect'
)

ALPHA_COMPARE_CONDITION=(
	'Never',
	'Less',
	'Less-or-Equal',
	'Equal',
	'Not-Equal',
	'Greater-or-Equal',
	'Greater',
	'Always'
)
BLEND_CALC=(
	'0',
	'1',
	'FBColor',
	'1-FBColor',
	'PixelAlpha',
	'1-PixelAlpha',
	'FBAlpha',
	'1-FBAlpha',
	'PixelColor',
	'1-PixelColor'
)

BLEND_CALC_OPS=(
	'0',
	'Add',
	'Subtract',
	'Reverse-Subtract',
	'Min',
	'Max'
)

LOGICAL_CALC_OPS=(
	'None',
	'NoOp',
	'Clear',
	'Set',
	'Copy',
	'InvCopy',
	'Inv',
	'And',
	'Nand',
	'Or',
	'Nor',
	'Xor',
	'Equiv',
	'RevAnd',
	'InvAnd',
	'RevOr',
	'InvOr'
)

PROJECTION_MAPPING_TYPES=(
	'Standard',
	'Entire-Layout',
	'2',
	'3',
	'Pane-RandS-Projection',
	'5',
	'6'
)

TEXT_ALIGNS=(
	'NA',
	'Left',
	'Center',
	'Right'
)
ORIG_X=(
	'Center',
	'Left',
	'Right'
)
ORIG_Y=(
	'Center',
	'Up',
	'Down'
)

def fread(filename,mode='rb'):
	if mode=='r':
		f=open(filename,mode,encoding='utf-8')
	else:
		f=open(filename,mode)
	c=f.read()
	f.close()
	return c
	
def fwrite(content,filename,mode='wb'):
	if mode=='w':
		f=open(filename,mode,encoding='utf-8')
	else:
		f=open(filename,mode)
	f.write(content)
	f.close()

class ClsFunc(object):
	'''A class which emulates a function. Useful to split big functions into small modules which share data'''
	def __new__(cls,*args,**kwargs):
		self=object.__new__(cls)
		return self.main(*args,**kwargs)

class OrderedDict (collections.OrderedDict):
	def __setitem__(self,item,value):
		if item in self.keys():
			if not str(item).startswith('__'):
				raise KeyError('%s already defined'%item)
		collections.OrderedDict.__setitem__(self,item,value)

class TypeReader (object):
	def bit(self,n,bit,length=1):
		bit=32-bit
		mask=((2**length)-1)<<(bit-(length))
		return (n&mask)>>(bit-length)
	def uint8(self,data,ptr):
		return struct.unpack_from('%sB'%self.byteorder,data,ptr)[0]
	def uint16(self,data,ptr):
		return struct.unpack_from('%sH'%self.byteorder,data,ptr)[0]
	def uint32(self,data,ptr):
		return struct.unpack_from('%sI'%self.byteorder,data,ptr)[0]
	def int8(self,data,ptr):
		return struct.unpack_from('%sb'%self.byteorder,data,ptr)[0]
	def int16(self,data,ptr):
		return struct.unpack_from('%sh'%self.byteorder,data,ptr)[0]
	def int32(self,data,ptr):
		return struct.unpack_from('%si'%self.byteorder,data,ptr)[0]
	def float32(self,data,ptr):
		return struct.unpack_from('%sf'%self.byteorder,data,ptr)[0]
	def string(self,data,ptr):
		subdata=data[ptr:]
		try:
			end=subdata.index(0)
		except:
			end=-1
		if end==-1:
			return subdata.decode('ascii')
		else:
			return subdata[:end].decode('ascii')
	def color(self,data,offset,format):
		format=format.upper().strip()
		if format in ('RGBA8','RGB8'):
			r=data[offset]
			g=data[offset+1]
			b=data[offset+2]
			if format=='RGBA8':
				a=data[offset+3]
			final=OrderedDict()
			final['RED']=r
			final['GREEN']=g
			final['BLUE']=b
			if format=='RGBA8':
				final['ALPHA']=a
		return final

class frombflyt(ClsFunc, TypeReader):
	def main(self,data):
		self.bflyt=data
		self.readheader()
		return self.parsedata()
	def readheader(self):
		header=self.bflyt[:0x14]
		self.data=self.bflyt[0x14:]
		if header[0:4]!=b'FLYT':
			print('Not a valid BFLYT file.')
			sys.exit(1)
		self.byteorder='<' if header[4:6]==b'\xff\xfe' else '>'
		self.endianname='little' if self.byteorder=='<' else 'big'
		hdata=struct.unpack(FLYT_HEADER%self.byteorder,header)
		#some unused data
		#magic, endianness,
		#headerlength=hdata[2]
		self.version=hdata[3]
		#padding=hdata[4]
		#filesize=hdata[5]
		self.secnum=hdata[6]
		#padding=hdata[7]
	
	def parsedata(self):
		ptr=0
		self.tree=OrderedDict()
		self.tree['BFLYT']=OrderedDict()
		self.actnode=self.tree['BFLYT']# creates a pointer in the tree, which can change later
		self.actnode['__pan1idx']=0
		self.actnode['__pas1idx']=0
		for i in range(0,self.secnum):
			magic=self.data[ptr:ptr+4].decode('ascii')
			size=int.from_bytes(self.data[ptr+4:ptr+8],self.endianname)
			chunk=self.data[ptr:ptr+size]
			try:
				method=eval('self.read'+magic)# quicker to code than if magic=='lyt1':...
			except AttributeError:
				print('Invalid section magic: %s'%magic)
			method(chunk)
			ptr+=size
		return dump(self.tree,[OrderedDict])
	
	def readlyt1(self,data):
		self.actnode['lyt1']=OrderedDict()
		localnode=self.actnode['lyt1']
		ptr=8
		localnode['drawn-from-middle']=bool(data[ptr]); ptr+=4
		localnode['screen-width']=self.float32(data,ptr); ptr+=4
		localnode['screen-height']=self.float32(data,ptr); ptr+=4
		localnode['max-parts-width']=self.float32(data,ptr); ptr+=4
		localnode['max-parts-height']=self.float32(data,ptr); ptr+=4
		localnode['name']=self.string(data,ptr)
	
	def readtxl1(self,data):
		self.actnode['txl1']=OrderedDict()
		localnode=self.actnode['txl1']
		ptr=8
		texnum=self.uint16(data,ptr); ptr+=2
		localnode['texture-number']=texnum
		#localnode['data-start-offset']=self.uint16(data,ptr)
		ptr+=2
		offsets=[]
		startentries=ptr
		for i in range(0,texnum):
			offsets.append(self.uint32(data,ptr)); ptr+=4
		#localnode['filenames-offsets']=offsets
		filenames=[]
		for offset in offsets:
			absoffset=startentries+offset
			filenames.append(self.string(data,absoffset))
		localnode['file-names']=filenames
		self.texturenames=filenames
	
	def readfnl1(self,data):
		self.actnode['fnl1']=OrderedDict()
		localnode=self.actnode['fnl1']
		localnode['comment']='List of the used fonts files names'
		ptr=8
		fontnum=self.uint16(data,ptr); ptr+=2
		localnode['fonts-number']=fontnum
		#localnode['data-start-offset']=self.uint16(data,ptr);
		ptr+=2
		offsets=[]
		startentries=ptr
		for i in range(0,fontnum):
			offsets.append(self.uint32(data,ptr)); ptr+=4
		#localnode['file-names-offsets']=offsets
		filenames=[]
		for offset in offsets:
			absoffset=startentries+offset
			filenames.append(self.string(data,absoffset))
		localnode['file-names']=filenames
		self.fontnames=filenames
	
	def readmat1(self,data):
		self.actnode['mat1']=OrderedDict()
		localnode=self.actnode['mat1']
		ptr=8
		matnum=self.uint16(data,ptr); ptr+=2
		localnode['materials-number']=matnum
		#localnode['data-start-offset']=self.uint16(data,ptr)
		ptr+=2
		offsets=[]
		startentries=ptr
		for i in range(0,matnum):
			offsets.append(self.uint32(data,ptr)); ptr+=4
		#localnode['materials-offsets']=offsets
		self.materials=[]
		for offset in offsets:
			ptr=offset
			mat=OrderedDict()
			mat['name']=self.string(data,ptr); ptr+=0x1c
			mat['fore-color']=self.color(data,ptr,'RGBA8'); ptr+=4
			mat['back-color']=self.color(data,ptr,'RGBA8'); ptr+=4
			
			flags=self.uint32(data,ptr); ptr+=4
			if flags in (2069,2154): #to avoid many problems
				flags^=0x0800
			texref=self.bit(flags,30,2)
			textureSRT=self.bit(flags,28,2)
			mappingSettings=self.bit(flags,26,2)
			textureCombiners=self.bit(flags,24,2)
			alphaCompare=self.bit(flags,22,1)
			blendMode=self.bit(flags,20,2)
			blendAlpha=self.bit(flags,18,2)
			indirect=self.bit(17,1)
			projectionMapping=self.bit(flags,15,2)
			shadowBlending=self.bit(flags,14,1)
			
			for i in range(0,texref):
				mat['texref-%d'%i]=OrderedDict()
				flagnode=mat['texref-%d'%i]
				flagnode['file']=self.texturenames[self.uint16(data,ptr)]; ptr+=2
				flagnode['wrap-S']=WRAPS[self.uint8(data,ptr)]; ptr+=1
				flagnode['wrap-T']=WRAPS[self.uint8(data,ptr)]; ptr+=1
			for i in range(0,textureSRT):
				mat['textureSRT-%d'%i]=OrderedDict()
				flagnode=mat['textureSRT-%d'%i]
				flagnode['X-translate']=self.float32(data,ptr); ptr+=4
				flagnode['Y-translate']=self.float32(data,ptr); ptr+=4
				flagnode['rotate']=self.float32(data,ptr); ptr+=4
				flagnode['X-scale']=self.float32(data,ptr); ptr+=4
				flagnode['Y-scale']=self.float32(data,ptr); ptr+=4
			for i in range(0,mappingSettings):
				mat['mapping-settings-%d'%i]=OrderedDict()
				flagnode=mat['mapping-settings-%d'%i]
				flagnode['unknown-1']=self.uint8(data,ptr); ptr+=1
				flagnode['mapping-method']=MAPPING_METHODS[self.uint8(data,ptr)]; ptr+=1
				flagnode['unknown-2']=self.uint8(data,ptr); ptr+=1
				flagnode['unknown-3']=self.uint8(data,ptr); ptr+=1
				flagnode['unknown-4']=self.uint8(data,ptr); ptr+=1
				flagnode['unknown-5']=self.uint8(data,ptr); ptr+=1
				flagnode['unknown-6']=self.uint8(data,ptr); ptr+=1
				flagnode['unknown-7']=self.uint8(data,ptr); ptr+=1
			
			for i in range(0,textureCombiners):
				mat['texture-combiner-%d'%i]=OrderedDict()
				flagnode=mat['texture-combiner-%d'%i]
				flagnode['color-blend']=COLOR_BLENDS[self.uint8(data,ptr)]; ptr+=1
				flagnode['alpha-blend']=BLENDS[self.uint8(data,ptr)]; ptr+=1
				flagnode['unknown-1']=self.uint8(data,ptr); ptr+=1
				flagnode['unknown-2']=self.uint8(data,ptr); ptr+=1
			if alphaCompare:
				mat['alpha-compare']=OrderedDict()
				flagnode=mat['alpha-compare']
				flagnode['condition']=ALPHA_COMP_CONDITIONS[self.uint8(data,ptr)]; ptr+=1
				flagnode['unknown-1']=self.uint8(data,ptr); ptr+=1
				flagnode['unknown-2']=self.uint8(data,ptr); ptr+=1
				flagnode['unknown-3']=self.uint8(data,ptr); ptr+=1
				flagnode['value']=self.float32(data,ptr); ptr+=4
			for i in range(0,blendMode):
				mat['blend-mode-%d'%i]=OrderedDict()
				flagnode=mat['blend-mode-%d'%i]
				flagnode['blend-operation']=BLEND_CALC_OPS[self.uint8(data,ptr)]; ptr+=1
				flagnode['source']=BLEND_CALC[self.uint8(data,ptr)]; ptr+=1
				flagnode['destination']=BLEND_CALC[self.uint8(data,ptr)]; ptr+=1
				flagnode['logical-operation']=LOGICAL_CALC_OPS[self.uint8(data,ptr)]; ptr+=1
			for i in range(0,blendAlpha):
				mat['blend-alpha-%d'%i]=OrderedDict()
				flagnode=mat['blend-alpha']
				flagnode['blend-operation']=BLEND_CALC_OPS[self.uint8(data,ptr)]; ptr+=1
				flagnode['source']=BLEND_CALC[self.uint8(data,ptr)]; ptr+=1
				flagnode['destination']=BLEND_CALC[self.uint8(data,ptr)]; ptr+=1
				flagnode['unknown']=self.uint8(data,ptr); ptr+=1
			if indirect:
				mat['indirect-adjustment']=OrderedDict()
				flagnode=mat['indirect-adjustment']
				flagnode['rotate']=self.float32(data,ptr); ptr+=4
				flagnode['X-warp']=self.float32(data,ptr); ptr+=4
				flagnode['Y-warp']=self.float32(data,ptr); ptr+=4
			for i in range(0,projectionMapping):
				mat['projection-mapping-%d'%i]=OrderedDict()
				flagnode=mat['projection-mapping-%d'%i]
				flagnode['X-translate']=self.float32(data,ptr); ptr+=4
				flagnode['Y-translate']=self.float32(data,ptr); ptr+=4
				flagnode['X-scale']=self.float32(data,ptr); ptr+=4
				flagnode['Y-scale']=self.float32(data,ptr); ptr+=4
				flagnode['option']=PROJECTION_MAPPING_TYPES[self.uint8(data,ptr)]; ptr+=1
				flagnode['unknown-1']=self.uint8(data,ptr); ptr+=1
				flagnode['unknown-2']=self.uint16(data,ptr); ptr+=2
			if shadowBlending:
				mat['shadow-blending']=OrderedDict()
				flagnode=mat['shadow-blending']
				flagnode['black-blending']=self.color(data,ptr,'RGB8'); ptr+=3
				flagnode['white-blending']=self.color(data,ptr,'RGBA8'); ptr+=4
				pad=self.uint8(data,ptr); ptr+=1
			self.materials.append(mat)
		if ptr<len(data):
				extra=data[ptr:]
				localnode['extra']=extra.hex()
		localnode['materials']=self.materials
	
	def readpane(self,data,ptr):
		node=OrderedDict()
		flags=self.uint8(data,ptr); ptr+=1
		node['visible']=bool(flags&0b00000001)
		node['transmit-alpha-to-children']=bool((flags&0b00000010)>>1)
		origin=self.uint8(data,ptr); ptr+=1
		mainorigin=origin%16
		parentorigin=origin//16
		node['origin']=OrderedDict()
		node['parent-origin']=OrderedDict()
		orignode=node['origin']
		orignode['x']=ORIG_X[mainorigin%4]
		orignode['y']=ORIG_Y[mainorigin//4]
		orignode=node['parent-origin']
		orignode['x']=ORIG_X[parentorigin%4]
		orignode['y']=ORIG_Y[parentorigin//4]
		node['alpha']=self.uint8(data,ptr); ptr+=1
		node['part-scale']=self.uint8(data,ptr); ptr+=1
		node['name']=self.string(data,ptr); ptr+=32
		self.actnode['__prevname']=node['name']
		node['X-translation']=self.float32(data,ptr); ptr+=4
		node['Y-translation']=self.float32(data,ptr); ptr+=4
		node['Z-translation']=self.float32(data,ptr); ptr+=4
		node['X-rotation']=self.float32(data,ptr); ptr+=4
		node['Y-rotation']=self.float32(data,ptr); ptr+=4
		node['Z-rotation']=self.float32(data,ptr); ptr+=4
		node['X-scale']=self.float32(data,ptr); ptr+=4
		node['Y-scale']=self.float32(data,ptr); ptr+=4
		node['width']=self.float32(data,ptr); ptr+=4
		node['height']=self.float32(data,ptr); ptr+=4
		return node,ptr
	
	def readpan1(self,data):
		ptr=8
		info,ptr=self.readpane(data,ptr)
		secname='pan1-%s'%self.actnode['__prevname']
		self.actnode[secname]=OrderedDict()
		self.actnode[secname].update(info)
		
	def readpas1(self,data):
		secname='pas1-%s'%self.actnode['__prevname']
		self.actnode[secname]=OrderedDict()
		parentnode=self.actnode
		self.actnode=self.actnode[secname]
		self.actnode['__parentnode']=parentnode
	
	def readwnd1(self,data):
		ptr=8
		info,ptr=self.readpane(data,ptr)
		secname='wnd1-%s'%self.actnode['__prevname']
		self.actnode[secname]=OrderedDict()
		localnode=self.actnode[secname]
		localnode.update(info)
		localnode['stretch-left']=self.uint16(data,ptr); ptr+=2
		localnode['stretch-right']=self.uint16(data,ptr); ptr+=2
		localnode['stretch-up']=self.uint16(data,ptr); ptr+=2
		localnode['stretch-down']=self.uint16(data,ptr); ptr+=2
		localnode['custom-left']=self.uint16(data,ptr); ptr+=2
		localnode['custom-right']=self.uint16(data,ptr); ptr+=2
		localnode['custom-up']=self.uint16(data,ptr); ptr+=2
		localnode['custom-down']=self.uint16(data,ptr); ptr+=2
		framenum=self.uint8(data,ptr); ptr+=1
		localnode['frame-count']=framenum
		localnode['flags']=self.uint8(data,ptr); ptr+=1
		pad=self.uint16(data,ptr); ptr+=2
		offset1=self.uint32(data,ptr); ptr+=4
		offset2=self.uint32(data,ptr); ptr+=4
		localnode['color-1']=self.color(data,ptr,'RGBA8'); ptr+=4
		localnode['color-2']=self.color(data,ptr,'RGBA8'); ptr+=4
		localnode['color-3']=self.color(data,ptr,'RGBA8'); ptr+=4
		localnode['color-4']=self.color(data,ptr,'RGBA8'); ptr+=4
		matnum=self.uint16(data,ptr); ptr+=2
		localnode['material']=self.materials[matnum]['name']
		coordsnum=self.uint8(data,ptr); ptr+=1
		localnode['coordinates-count']=coordsnum
		pad=self.uint8(data,ptr); ptr+=1
		for i in range(0,coordsnum):
			localnode['coords-%d'%i]=OrderedDict()
			coordnode=localnode['coords-%d'%i]
			for j in range(0,8):
				coordnode['texcoord-%d'%j]=self.float32(data,ptr); ptr+=4
		wnd4offsets=[]
		for i in range(0,framenum):
			wnd4offsets.append(self.uint32(data,ptr)); ptr+=4
		wndmat=[]
		for i in range(0,framenum):
			wndmat.append(self.materials[self.uint16(data,ptr)]['name']); ptr+=2
		localnode['wnd4-materials']=wndmat
		localnode['wnd4-materials-index']=self.uint8(data,ptr); ptr+=1
	
	def readtxt1(self,data):
		ptr=8
		info,ptr=self.readpane(data,ptr)
		secname='txt1-%s'%self.actnode['__prevname']
		self.actnode[secname]=OrderedDict()
		localnode=self.actnode[secname]
		localnode.update(info)
		localnode['restrict-length']=self.uint16(data,ptr); ptr+=2
		localnode['length']=self.uint16(data,ptr); ptr+=2
		localnode['material']=self.materials[self.uint16(data,ptr)]['name']; ptr+=2
		localnode['font']=self.fontnames[self.uint16(data,ptr)]; ptr+=2
		align=self.uint8(data,ptr); ptr+=1
		localnode['alignment']=OrderedDict()
		localnode['alignment']['x']=ORIG_X[align%4]
		localnode['alignment']['y']=ORIG_Y[align//4]
		localnode['line-alignment']=TEXT_ALIGNS[self.uint8(data,ptr)]; ptr+=1
		localnode['active-shadows']=self.uint8(data,ptr); ptr+=1
		localnode['unknown-1']=self.uint8(data,ptr); ptr+=1
		localnode['italic-tilt']=self.float32(data,ptr); ptr+=4
		startoffset=self.uint32(data,ptr); ptr+=4
		localnode['top-color']=self.color(data,ptr,'RGBA8'); ptr+=4
		localnode['bottom-color']=self.color(data,ptr,'RGBA8'); ptr+=4
		localnode['font-size-x']=self.float32(data,ptr); ptr+=4
		localnode['font-size-y']=self.float32(data,ptr); ptr+=4
		localnode['char-space']=self.float32(data,ptr); ptr+=4
		localnode['line-space']=self.float32(data,ptr); ptr+=4
		callnameoffset=self.uint32(data,ptr); ptr+=4
		localnode['shadow']=OrderedDict()
		shadownode=localnode['shadow']
		shadownode['offset-X']=self.float32(data,ptr); ptr+=4
		shadownode['offset-Y']=self.float32(data,ptr); ptr+=4
		shadownode['scale-X']=self.float32(data,ptr); ptr+=4
		shadownode['scale-Y']=self.float32(data,ptr); ptr+=4
		shadownode['top-color']=self.color(data,ptr,'RGBA8'); ptr+=4
		shadownode['bottom-color']=self.color(data,ptr,'RGBA8'); ptr+=4
		shadownode['unknown-2']=self.uint32(data,ptr); ptr+=4
		text=data[ptr:ptr+localnode['restrict-length']]
		localnode['text']=text.hex()
		ptr+=len(text)
		ptr+=4-(ptr%4)
		callname=self.string(data,ptr)
		localnode['call-name']=callname
	
	def readusd1(self,data):
		ptr=8
		secname='usd1-%s'%self.actnode['__prevname']
		self.actnode[secname]=OrderedDict()
		localnode=self.actnode[secname]
		entrynum=self.uint16(data,ptr); ptr+=2
		localnode['entry-number']=entrynum
		localnode['unknown']=self.uint16(data,ptr); ptr+=2
		entries=[]
		for i in range(0,entrynum):
			entry=OrderedDict()
			entryoffset=ptr
			nameoffset=self.uint32(data,ptr)+entryoffset; ptr+=4
			dataoffset=self.uint32(data,ptr)+entryoffset; ptr+=4
			datanum=self.uint16(data,ptr); ptr+=2
			datatype=self.uint8(data,ptr); ptr+=1
			unknown=self.uint8(data,ptr); ptr+=1
			if datatype==0:
				entrydata=data[dataoffset:dataoffset+datanum].decode('ascii')
			elif datatype==1:
				entrydata=[]
				for j in range(0,datanum):
					entrydata.append(self.int32(data,dataoffset+(j*4)))
			elif datatype==2:
				entrydata=[]
				for j in range(0,datanum):
					entrydata.append(self.float32(data,dataoffset+(j*4)))
			entry['name']=self.string(data,nameoffset)
			entry['data']=entrydata
			entries.append(entry)
		localnode['entries']=entries
	
	def readpae1(self,data):
		self.actnode=self.actnode['__parentnode']
		secname='pae1-%s'%self.actnode['__prevname']
		self.actnode[secname]='End of %s'%self.actnode['__prevname']
	
	def readbnd1(self,data):
		ptr=8
		info,ptr=self.readpane(data,ptr)
		secname='bnd1-%s'%self.actnode['__prevname']
		self.actnode[secname]=OrderedDict()
		localnode=self.actnode[secname]
		localnode.update(info)
	
	def readpic1(self,data):
		ptr=8
		info,ptr=self.readpane(data,ptr)
		secname='pic1-%s'%self.actnode['__prevname']
		self.actnode[secname]=OrderedDict()
		localnode=self.actnode[secname]
		localnode.update(info)
		localnode['top-left-vtx-color']=self.color(data,ptr,'RGBA8'); ptr+=4
		localnode['top-right-vtx-color']=self.color(data,ptr,'RGBA8'); ptr+=4
		localnode['bottom-left-vtx-color']=self.color(data,ptr,'RGBA8'); ptr+=4
		localnode['bottom-right-vtx-color']=self.color(data,ptr,'RGBA8'); ptr+=4
		localnode['material']=self.materials[self.uint16(data,ptr)]['name']; ptr+=2
		localnode['tex-coords-number']=self.uint8(data,ptr); ptr+=1
		pad=self.uint8(data,ptr); ptr+=1
		coords=[]
		for i in range(0,localnode['tex-coords-number']):
			entry=OrderedDict()
			entry['top-left']={'s':self.float32(data,ptr), 't':self.float32(data,ptr+4)}; ptr+=8
			entry['top-right']={'s':self.float32(data,ptr), 't':self.float32(data,ptr+4)}; ptr+=8
			entry['bottom-left']={'s':self.float32(data,ptr), 't':self.float32(data,ptr+4)}; ptr+=8
			entry['bottom-right']={'s':self.float32(data,ptr), 't':self.float32(data,ptr+4)}; ptr+=8
			coords.append(entry)
		localnode['tex-coords']=coords
	
	def readprt1(self,data):
		ptr=8
		info,ptr=self.readpane(data,ptr)
		secname='prt1-%s'%self.actnode['__prevname']
		self.actnode[secname]=OrderedDict()
		localnode=self.actnode[secname]
		localnode.update(info)
		count=self.uint32(data,ptr)-1; ptr+=4
		localnode['section-count']=count
		localnode['section-scale-X']=self.float32(data,ptr); ptr+=4
		localnode['section-scale-Y']=self.float32(data,ptr); ptr+=4
		entries=[]
		for i in range(0,count):
			entry=OrderedDict()
			parentnode=self.actnode
			self.actnode=entry
			self.actnode['__parentnode']=parentnode
			entry['name']=self.string(data,ptr); ptr+=24
			entry['unknown-1']=self.uint8(data,ptr); ptr+=1
			entry['flags']=self.uint8(data,ptr); ptr+=1
			pad=self.uint16(data,ptr); ptr+=2
			entryoffset=self.uint32(data,ptr); ptr+=4
			extraoffset=self.uint32(data,ptr); ptr+=4
			pad=self.uint32(data,ptr); ptr+=4
			if entryoffset!=0:
				length=self.uint32(data,entryoffset+4);
				entrydata=data[entryoffset:entryoffset+length]
				magic=entrydata[0:4].decode('ascii')
				try:
					method=eval('self.read'+magic)# quicker to code than if magic=='txt1':...
				except AttributeError:
					print('Invalid section magic: %s'%magic)
				method(entrydata)
			if extraoffset!=0:
				extra=data[extraoffset:extraoffset+48].hex()
				key=list(entry.keys())[-1]
				entry['extra']=extra
			self.actnode=self.actnode['__parentnode']
			entries.append(entry)
		localnode['entries']=entries
	
	def readgrp1(self,data):
		ptr=8
		name=self.string(data,ptr); ptr+=34
		secname='grp1-%s'%name
		self.actnode[secname]=OrderedDict()
		localnode=self.actnode[secname]
		localnode['name']=name
		subnum=self.uint16(data,ptr); ptr+=2
		subs=[]
		for i in range(0,subnum):
			subs.append(self.string(data,ptr)); ptr+=24
		localnode['subs']=subs
		
	
	def readgrs1(self,data):
		if '__grsnum' not in self.actnode.keys():
			self.actnode['__grsnum']=0
		secname='grs1-%d'%self.actnode['__grsnum']
		self.actnode['__grsnum']+=1
		self.actnode[secname]=OrderedDict()
		parentnode=self.actnode
		self.actnode=self.actnode[secname]
		self.actnode['__parentnode']=parentnode
	
	def readgre1(self,data):
		self.actnode=self.actnode['__parentnode']
		secname='gre1-%d'%(self.actnode['__grsnum']-1)
		self.actnode[secname]='End of grs1-%d'%(self.actnode['__grsnum']-1)
	
	def readcnt1(self,data):
		ptr=8
		self.actnode['cnt1']=OrderedDict()
		localnode=self.actnode['cnt1']
		offset1=self.uint32(data,ptr); ptr+=4
		offset2=self.uint32(data,ptr); ptr+=4
		partnum=self.uint16(data,ptr); ptr+=2
		animnum=self.uint16(data,ptr); ptr+=2
		offset3=self.uint32(data,ptr); ptr+=4
		offset4=self.uint32(data,ptr); ptr+=4
		localnode['part-number']=partnum
		localnode['anim-number']=animnum
		name=self.string(data,ptr)
		ptr+=len(name)
		ptr+=4-(ptr%4)
		localnode['name']=name
		if partnum!=0:
			ptr=offset2
			parts=[]
			for i in range(0,partnum):
				parts.append(self.string(data,ptr)); ptr+=24
			localnode['parts']=parts
		if animnum!=0:
			startpos=ptr
			animpartnum=self.uint32(data,ptr); ptr+=4
			animname=self.string(data,ptr);
			ptr+=len(animname)
			ptr+=4-(ptr%4)
			offsets=[]
			localnode['anim-part']=OrderedDict()
			localnode['anim-part']['name']=animname
			localnode['anim-part']['anim-part-number']=animpartnum
			for i in range(0, animpartnum):
				offsets.append(self.uint32(data,ptr)); ptr+=4
			anims=[]
			for offset in offsets:
				ptr=startpos+offset
				anims.append(self.string(data,ptr));
			ptr+=len(anims[-1])
			ptr+=4-(ptr%4)
			localnode['anim-part']['anims']=anims
		if ptr<len(data):
			dump=data[ptr:]
			localnode['dump']=dump

class tobflyt(ClsFunc):
	def main(self, tree):
		if list(tree.keys())[0]!='BFLYT':
			print('This is not a converted BFLYT file')
			sys.exit(3)
		self.sections=tree['BFLYT']
		self.final=b''
		self.repackdata()
		return self.final
	
	def repackdata(self):
		for section in self.sections.keys():
			magic=section.split('-')[0]
			try:
				method=eval('self.pack%s'%magic)
			except AttributeError:
				print('Invalid section: %s'%magic)
				sys.exit(4)
			self.final+=method(self.sections[section])

	def packlyt1(self,data):
		return b''

	def packtxl1(self,data):
		return b''

	def packmat1(self,data):
		return b''

	def packpan1(self,data):
		return b''

	def packpas1(self,data):
		return b''

	def packpae1(self,data):
		return b''

	def packwnd1(self,data):
		return b''

	def packtxt1(self,data):
		return b''

	def packpic1(self,data):
		return b''

	def packbnd1(self,data):
		return b''

	def packgrp1(self,data):
		return b''

	def packgrs1(self,data):
		return b''

	def packgre1(self,data):
		return b''

	def packcnt1(self,data):
		return b''

if __name__=='__main__':
	args=sys.argv[1:]
	if '-h' in args or len(args)==0:
		print('A tool to convert BFLYT files to a readable format')
		print('by Tyulis')
		print('Inspirated from BenzinU by Diddy81')
		print('Using:')
		print('\tbflyt.py [-x | -p] <file>')
		print('')
		print('-x: convert from BFLYT to TFLYT')
		print('-p: convert from TFLYT to BFLYT')
	elif '-x' in args:
		outname=args[-1].split('/')[-1].replace('.bflyt', '.tflyt')
		tree=frombflyt(fread(args[-1]))
		fwrite(dump(tree), outname, 'w')
	elif '-p' in args:
		outname=args[-1].split('/')[-1].replace('.tflyt', '.bflyt')
		tree=load(fread(args[-1],'r'))
		bflyt=tobflyt(tree)
		fwrite(bflyt, outname)
	else:
		print('No option specified')
