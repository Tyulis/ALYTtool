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
BOMS={'<': b'\xff\xfe', '>':b'\xff\xfe'}

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
	
class TypeWriter (object):
	def uint8(self,data):
		return struct.pack('%sB'%self.byteorder,data)
	def uint16(self,data):
		return struct.pack('%sH'%self.byteorder,data)
	def uint32(self,data):
		return struct.pack('%sI'%self.byteorder,data)
	def int8(self,data):
		return struct.pack('%sb'%self.byteorder,data)
	def int16(self,data):
		return struct.pack('%sh'%self.byteorder,data)
	def int32(self,data):
		return struct.pack('%si'%self.byteorder,data)
	def float32(self,data):
		return struct.pack('%sf'%self.byteorder,data)
	def string(self,data,align=0):
		s=data.encode('ascii')+b'\x00'
		pad=self.pad(align-len(s))
		return s+pad
	def string4(self,data):
		s=data.encode('ascii')+b'\x00'
		pad=self.pad(4-(len(s)%4))
		return s+pad
	def pad(self,num):
		return b'\x00'*num
	def sechdr(self,data,magic):
		magic=magic.encode('ascii')
		length=len(data)+8
		return magic+self.uint32(length)
	def color(self,data,format):
		format=format.upper()
		out=b''
		if format in ('RGB8','RGBA8'):
			out+=self.uint8(data['RED'])
			out+=self.uint8(data['BLUE'])
			out+=self.uint8(data['GREEN'])
			if format=='RGBA8':
				out+=self.uint8(data['ALPHA'])
		return out
	def magiccount(self,data,magic):
		count=0
		for key in data.keys():
			if '-'.join(key.split('-')[:-1])==magic:
				count+=1
		return count

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
		self.tree['byte-order']=self.byteorder
		self.tree['version']=self.version
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
		return self.tree
	
	def readlyt1(self,data):
		self.actnode['lyt1']=OrderedDict()
		localnode=self.actnode['lyt1']
		ptr=8
		localnode['drawn-from-middle']=bool(self.uint8(data,ptr)); ptr+=4
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
				mat['false-0x800']=True
			else:
				mat['false-0x800']=False
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
				flagnode['condition']=ALPHA_COMPARE_CONDITIONS[self.uint8(data,ptr)]; ptr+=1
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
		node['position-adjustment']=bool((flags&0b00000100)>>2)
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
			dic=OrderedDict()
			dic['material']=self.materials[self.uint16(data,ptr)]['name']; ptr+=2
			dic['index']=self.uint8(data,ptr); ptr+=1
			wndmat.append(dic)
			pad=self.uint8(data,ptr); ptr+=1
		localnode['wnd4-materials']=wndmat
	
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
		#localnode['text']=text.hex()
		localnode['text']=text.decode('utf-16-%s'%self.endianname[0]+'e')
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
			entry['unknown']=unknown
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

class tobflyt(ClsFunc, TypeWriter):
	def main(self, tree):
		if list(tree.keys())[2]!='BFLYT':
			print('This is not a converted BFLYT file')
			sys.exit(3)
		self.version=tree['version']
		self.byteorder=tree['byte-order']
		self.sections=tree['BFLYT']
		self.final=self.repackdata()
		return self.final
	
	def repackdata(self):
		self.secnum=0
		data=self.repacktree(self.sections,True)
		hdr=self.repackhdr(data)
		return hdr+data
	
	def repackhdr(self,data):
		final=b'FLYT'
		final+=BOMS[self.byteorder]
		final+=self.uint16(0x14)
		final+=self.uint16(self.version)
		final+=self.uint16(0x0702)
		final+=self.uint32(len(data)+0x14)
		final+=self.uint16(self.secnum)
		final+=self.uint16(0)
		return final
	
	def repacktree(self,tree,top=False):
		final=b''
		for section in tree.keys():
			magic=section.split('-')[0]
			try:
				method=eval('self.pack%s'%magic)
			except AttributeError:
				print('Invalid section: %s'%magic)
				sys.exit(4)
			if top:
				self.secnum+=1
			final+=method(tree[section])
		return final

	def packlyt1(self,data):
		final=b''
		final+=self.uint8(data['drawn-from-middle'])
		final+=self.pad(3)
		final+=self.float32(data['screen-width'])
		final+=self.float32(data['screen-height'])
		final+=self.float32(data['max-parts-width'])
		final+=self.float32(data['max-parts-height'])
		final+=self.string4(data['name'])
		hdr=self.sechdr(final,'lyt1')
		return hdr+final

	def packtxl1(self,data):
		final=b''
		final+=self.uint16(data['texture-number'])
		final+=self.uint16(0) #data offset. Seems to be always 0
		filetable=b''
		offsets=[]
		self.textures=data['file-names']
		offset_tbl_length=len(self.textures)*4
		for name in self.textures:
			offsets.append(len(filetable)+offset_tbl_length)
			filetable+=self.string(name)
		offsettbl=b''
		for offset in offsets:
			offsettbl+=self.uint32(offset)
		final+=offsettbl
		final+=filetable
		final+=self.pad(4-(len(final)%4))
		hdr=self.sechdr(final,'txl1')
		return hdr+final
	
	def packfnl1(self,data):
		final=b''
		final+=self.uint16(data['fonts-number'])
		final+=self.uint16(0) #data offset. Seems to be always 0
		filetable=b''
		offsets=[]
		filenames=data['file-names']
		self.fontnames=filenames
		offset_tbl_length=len(filenames)*4
		for name in filenames:
			offsets.append(len(filetable)+offset_tbl_length)
			filetable+=self.string(name)
		offsettbl=b''
		for offset in offsets:
			offsettbl+=self.uint32(offset)
		final+=offsettbl
		final+=filetable
		final+=self.pad(4-(len(final)%4))
		hdr=self.sechdr(final,'fnl1')
		return hdr+final
		
	
	def packmat1(self,data):
		final=b''
		final+=self.uint16(data['materials-number'])
		final+=self.uint16(0)
		self.materials=data['materials']
		self.matnames=[el['name'] for el in self.materials]
		offsets=[]
		offset_tbl_length=len(self.materials)*4
		matdata=b''
		for mat in self.materials:
			offsets.append(offset_tbl_length+len(matdata))
			matsec=b''
			matsec+=self.string(mat['name'],0x1C)
			matsec+=self.color(mat['fore-color'],'RGBA8')
			matsec+=self.color(mat['back-color'],'RGBA8')
			flags=0
			flags|=self.magiccount(mat,'texref')
			flags|=self.magiccount(mat,'textureSRT')<<2
			flags|=self.magiccount(mat,'mapping-settings')<<4
			flags|=self.magiccount(mat,'texture-combiner')<<6
			flags|=('alpha-compare' in mat.keys())<<8
			flags|=self.magiccount(mat,'blend-mode')<<9
			flags|=self.magiccount(mat,'blend-alpha')<<11
			flags|=('indirect-adjustment' in mat.keys())<<13
			flags|=self.magiccount(mat,'projection-mapping')<<14
			flags|=('shadow-blending' in mat.keys())
			if mat['false-0x800']:
				flags|=0x800
			matsec+=self.uint32(flags)
			items=list(mat.keys())[3:]
			for item in items:
				itemtype='-'.join(item.split('-')[:-1])
				dic=mat[item]
				if itemtype=='texref':
					matsec+=self.uint16(self.textures.index(dic['file']))
					matsec+=self.uint8(WRAPS.index(dic['wrap-S']))
					matsec+=self.uint8(WRAPS.index(dic['wrap-T']))
				elif itemtype=='textureSRT':
					matsec+=self.float32(dic['X-translate'])
					matsec+=self.float32(dic['Y-translate'])
					matsec+=self.float32(dic['rotate'])
					matsec+=self.float32(dic['X-scale'])
					matsec+=self.float32(dic['Y-scale'])
				elif itemtype=='mapping-settings':
					matsec+=self.uint8(dic['unknown-1'])
					matsec+=self.uint8(MAPPING_METHODS.index(dic['mapping-method']))
					matsec+=self.uint8(dic['unknown-2'])
					matsec+=self.uint8(dic['unknown-3'])
					matsec+=self.uint8(dic['unknown-4'])
					matsec+=self.uint8(dic['unknown-5'])
					matsec+=self.uint8(dic['unknown-6'])
					matsec+=self.uint8(dic['unknown-7'])
				elif itemtype=='texture-combiner':
					matsec+=self.uint8(COLOR_BLENDS.index(dic['color-blend']))
					matsec+=self.uint8(BLENDS.index(dic['alpha-blend']))
					matsec+=self.uint8(dic['unknown-1'])
					matsec+=self.uint8(dic['unknown-2'])
				elif itemtype=='alpha-compare':
					matsec+=self.uint8(ALPHA_COMPARE_CONDITION.index(dic['condition']))
					matsec+=self.uint8(dic['unknown-1'])
					matsec+=self.uint8(dic['unknown-2'])
					matsec+=self.uint8(dic['unknown-3'])
					matsec+=self.uint32(dic['value'])
				elif itemtype=='blend-mode':
					matsec+=self.uint8(BLEND_CALC_OPS.index(dic['blend-operation']))
					matsec+=self.uint8(BLEND_CALC.index(dic['source']))
					matsec+=self.uint8(BLEND_CALC.index(dic['destination']))
					matsec+=self.uint8(LOGICAL_CALC_OPS.index(dic['logical-operation']))
				elif itemtype=='blend-alpha':
					matsec+=self.uint8(BLEND_CALC_OPS.index(dic['blend-operation']))
					matsec+=self.uint8(BLEND_CALC.index(dic['source']))
					matsec+=self.uint8(BLEND_CALC.index(dic['destination']))
					matsec+=self.uint8(dic['unknown'])
				elif itemtype=='indirect-adjustment':
					matsec+=self.float32(dic['rotate'])
					matsec+=self.float32(dic['X-warp'])
					matsec+=self.float32(dic['Y-warp'])
				elif itemtype=='projection-mapping':
					matsec+=self.float32(dic['X-translate'])
					matsec+=self.float32(dic['Y-translate'])
					matsec+=self.float32(dic['X-scale'])
					matsec+=self.float32(dic['Y-scale'])
					matsec+=self.uint8(PROJECTION_MAPPING_TYPES.index(dic['option']))
					matsec+=self.uint8(dic['unknown-1'])
					matsec+=self.uint16(dic['unknown-2'])
				elif itemtype=='shadow-blending':
					matsec+=self.color(dic['black-blending'],'RGB8')
					matsec+=self.color(dic['white-blending'],'RGBA8')
					matsec+=self.pad(1)
			matdata+=matsec
		offsettbl=b''
		for offset in offsets:
			offsettbl+=self.uint32(offset)
		final+=offsettbl
		final+=matdata
		if 'extra' in data.keys():
			final+=bytes.fromhex(data['extra'])
		hdr=self.sechdr(final,'mat1')
		return hdr+final
	
	def packpane(self,data):
		panesec=b''
		flags=0
		flags|=data['visible']
		flags|=data['transmit-alpha-to-children']<<1
		flags|=data['position-adjustment']<<2
		panesec+=self.uint8(flags)
		origin_x=ORIG_X.index(data['origin']['x'])
		origin_y=ORIG_Y.index(data['origin']['y'])
		parent_origin_x=ORIG_X.index(data['parent-origin']['x'])
		parent_origin_y=ORIG_Y.index(data['parent-origin']['y'])
		main_origin=(origin_y*4)+origin_x
		parent_origin=(parent_origin_y*4)+parent_origin_x
		origin=(parent_origin*16)+main_origin
		panesec+=self.uint8(origin)
		panesec+=self.uint8(data['alpha'])
		panesec+=self.uint8(data['part-scale'])
		panesec+=self.string(data['name'],32)
		panesec+=self.float32(data['X-translation'])
		panesec+=self.float32(data['Y-translation'])
		panesec+=self.float32(data['Z-translation'])
		panesec+=self.float32(data['X-rotation'])
		panesec+=self.float32(data['Y-rotation'])
		panesec+=self.float32(data['Z-rotation'])
		panesec+=self.float32(data['X-scale'])
		panesec+=self.float32(data['Y-scale'])
		panesec+=self.float32(data['width'])
		panesec+=self.float32(data['height'])
		return panesec

	def packpan1(self,data):
		final=self.packpane(data)
		hdr=self.sechdr(final,'pan1')
		return final+hdr

	def packpas1(self,data):
		tree=self.repacktree(data,True)
		pas1=self.sechdr(b'','pas1')
		return pas1+tree

	def packpae1(self,data):
		return self.sechdr(b'','pae1')

	def packwnd1(self,data):
		final=self.packpane(data)
		final+=self.uint16(data['stretch-left'])
		final+=self.uint16(data['stretch-right'])
		final+=self.uint16(data['stretch-up'])
		final+=self.uint16(data['stretch-down'])
		final+=self.uint16(data['custom-left'])
		final+=self.uint16(data['custom-right'])
		final+=self.uint16(data['custom-up'])
		final+=self.uint16(data['custom-down'])
		final+=self.uint8(data['frame-count'])
		final+=self.uint8(data['flags'])
		final+=self.pad(2)
		final+=self.uint32(0x70) #the offset1. Always 0x70
		final+=self.uint32(132+(32*data['coordinates-count'])) #the offset2
		final+=self.color(data['color-1'],'RGBA8')
		final+=self.color(data['color-2'],'RGBA8')
		final+=self.color(data['color-3'],'RGBA8')
		final+=self.color(data['color-4'],'RGBA8')
		final+=self.uint16(self.matnames.index(data['material']))
		final+=self.uint8(data['coordinates-count'])
		final+=self.pad(1)
		for i in range(0,data['coordinates-count']):
			dic=data['coords-%d'%i]
			for texcoord in dic.values():
				final+=self.float32(texcoord)
		part1len=len(final)
		for i in range(0, len(data['wnd4-materials'])):
			offset=part1len+4*(len(data['wnd4-materials']))+(4*i)+8
			final+=self.uint32(offset)
		for mat in data['wnd4-materials']:
			final+=self.uint16(self.matnames.index(mat['material']))
			final+=self.uint8(mat['index'])
			final+=self.pad(1)
		hdr=self.sechdr(final,'wnd1')
		return hdr+final

	def packtxt1(self,data):
		final=self.packpane(data)
		final+=self.uint16(data['restrict-length'])
		final+=self.uint16(data['length'])
		final+=self.uint16(self.matnames.index(data['material']))
		final+=self.uint16(self.fontnames.index(data['font']))
		align=(ORIG_Y.index(data['alignment']['y'])*4)+ORIG_X.index(data['alignment']['x'])
		final+=self.uint8(align)
		final+=self.uint8(TEXT_ALIGNS.index(data['line-alignment']))
		final+=self.uint8(data['active-shadows'])
		final+=self.uint8(data['unknown-1'])
		final+=self.float32(data['italic-tilt'])
		final+=self.uint32(164) #the start offset. Always 164
		final+=self.color(data['top-color'],'RGBA8')
		final+=self.color(data['bottom-color'],'RGBA8')
		final+=self.float32(data['font-size-x'])
		final+=self.float32(data['font-size-y'])
		final+=self.float32(data['char-space'])
		final+=self.float32(data['line-space'])
		final+=self.uint32(0)
		shadow=data['shadow']
		final+=self.float32(shadow['offset-X'])
		final+=self.float32(shadow['offset-Y'])
		final+=self.float32(shadow['scale-X'])
		final+=self.float32(shadow['scale-Y'])
		final+=self.color(shadow['top-color'],'RGBA8')
		final+=self.color(shadow['bottom-color'],'RGBA8')
		final+=self.uint32(shadow['unknown-2'])
		text=data['text'].encode('utf-16-%se'%('l' if self.byteorder=='<' else 'b'))
		final+=text
		final+=self.pad(4-(len(text)%4))
		final+=self.string4(data['call-name'])
		hdr=self.sechdr(final,'txt1')
		return hdr+final

	def packusd1(self,data):
		final=b''
		entrynum=data['entry-number']
		final+=self.uint16(data['entry-number'])
		final+=self.uint16(data['unknown'])
		nametbl=b''
		datatbl=b''
		entries=b''
		nameoffsets=[]
		dataoffsets=[]
		for entry in data['entries']:
			nameoffsets.append(len(nametbl))
			nametbl+=self.string(entry['name'])
			dataoffsets.append(len(datatbl))
			typename=entry['data'][0].__class__.__qualname__
			if typename=='float':
				datatype=2
			elif typename=='int':
				datatype=1
			elif typename in ('str','unicode','bytes'): #...
				datatype=0
			for el in entry['data']:
				if datatype==0:
					datatbl+=self.string(el)
				elif datatype==1:
					datatbl+=self.int32(el)
				elif datatype==2:
					datatbl+=self.float32(el)
		datatbl+=self.pad(4-(len(datatbl)%4))
		nametbl+=self.pad(4-(len(nametbl)%4))
		i=0
		entryoffset=len(final)
		for entry in data['entries']: #1 entry in the table = 12B
			entryrest=entrynum-(i+1)
			final+=self.uint32((12*entryrest)+len(datatbl)+nameoffsets[i])
			final+=self.uint32((12*entryrest)+dataoffsets[i])
			final+=self.uint16(len(entry['data']))
			typename=entry['data'][0].__class__.__qualname__
			if typename=='float':
				datatype=2
			elif typename=='int':
				datatype=1
			elif typename in ('str','unicode','bytes'): #...
				datatype=0
			final+=self.uint8(datatype)
			final+=self.uint8(entry['unknown'])
		final+=datatbl
		final+=nametbl
		hdr=self.sechdr(final,'usd1')
		return hdr+final

	def packpic1(self,data):
		final=self.packpane(data)
		final+=self.color(data['top-left-vtx-color'],'RGBA8')
		final+=self.color(data['top-right-vtx-color'],'RGBA8')
		final+=self.color(data['bottom-left-vtx-color'],'RGBA8')
		final+=self.color(data['bottom-right-vtx-color'],'RGBA8')
		final+=self.uint16(self.matnames.index(data['material']))
		texcoordnum=data['tex-coords-number']
		final+=self.uint8(texcoordnum)
		final+=self.pad(1)
		for texcoord in data['tex-coords']:
			final+=self.float32(texcoord['top-left']['s'])
			final+=self.float32(texcoord['top-left']['t'])
			final+=self.float32(texcoord['top-right']['s'])
			final+=self.float32(texcoord['top-right']['t'])
			final+=self.float32(texcoord['bottom-left']['s'])
			final+=self.float32(texcoord['bottom-left']['t'])
			final+=self.float32(texcoord['bottom-right']['s'])
			final+=self.float32(texcoord['bottom-right']['t'])
		hdr=self.sechdr(final,'pic1')
		return hdr+final

	def packbnd1(self,data):
		final=self.packpane(data)
		hdr=self.sechdr(final,'bnd1')
		return hdr+final

	def packprt1(self,data):
		final=self.packpane(data)
		
		hdr=self.sechdr(final,'prt1')
		return hdr+final

	def packgrp1(self,data):
		final=b''
		
		hdr=self.sechdr(final,'grp1')
		return hdr+final

	def packgrs1(self,data):
		final=b''
		
		hdr=self.sechdr(final,'grs1')
		return hdr+final

	def packgre1(self,data):
		final=b''
		
		hdr=self.sechdr(final,'gre1')
		return hdr+final

	def packcnt1(self,data):
		final=b''
		
		hdr=self.sechdr(final,'cnt1')
		return hdr+final

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
		fwrite(dump(tree,[OrderedDict]), outname, 'w')
	elif '-p' in args:
		outname=args[-1].split('/')[-1].replace('.tflyt', '.bflyt')
		tree=load(fread(args[-1],'r'))
		bflyt=tobflyt(tree)
		fwrite(bflyt, outname)
	else:
		print('No option specified')
