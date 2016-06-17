from struct import *
from ListRange import *

def readVarInt(stream, offset=0):
	ret = 0
	chr = unpack(">B", stream[offset:offset+1] )[0]
	of = 1
	while(chr & 0x80 and of < 9):
		ret = ret << 7
		ret +=  chr & 0x7F
		chr = unpack(">B", stream[offset+of:offset+of+1] )[0]
		of += 1
	ret = ret << 7
	ret += chr
	return ret, of

def getRecord( payload ):
	(hsize, offset) = readVarInt( payload )
	fields = []
	while offset < hsize:
		(ftype, size) = readVarInt( payload, offset )
		fields.append( { 'type': ftype } )
		offset += size
	for f in fields:
		# Based on http://www.sqlite.org/fileformat2.html#record_format
		t = f['type']
		s = ''
		if t == 0:
			v = 'Nul'
			s = 'NULL'
		elif t == 1:
			v = unpack(">b", payload[offset:offset+1])[0]
			s = 'INTEGER(8)'
			offset += 1 
		elif t == 2:
			v = unpack( ">h", payload[offset:offset+2] )[0]
			s = 'INTEGER(16)'
			offset += 2
		elif t == 3:
			v = 0
			for i in unpack( ">3B", payload[offset:offset+3] ):
				v = v << 8
				v += i
			s = 'INTEGER(24)'
			offset += 3
		elif t == 4:
			v = unpack( ">i", payload[offset:offset+4] )[0]
			s = 'INTEGER(32)'
			offset += 4
		elif t == 5:
			v = 0
			for i in unpack( ">6B", payload[offset:offset+6] ):
				v = v << 8
				v += i
			s = 'INTEGER(48)'
			offset += 6
		elif t == 6:
			v = unpack( ">q", payload[offset:offset+8] )[0]
			s = 'INTEGER(64)'
			offset += 8
		elif t == 7:
			v = unpack( ">d", payload[offset:offset+8] )[0]
			s = 'FLOAT(64)'
			offset += 8
		elif t == 8:
			v = 0
			s = 'CONSTANT'
		elif t == 9:
			v = 1
			s = 'CONSTANT'
		elif t == 10 or t == 11:
			v = 'Unknown value'
			s = 'NOT USED'
		elif t > 11 and t%2 == 0:
			size = (t-12)/2
			if size > len(payload)-offset:
				size = len(payload)-offset
			v = unpack( str(size) + "s", payload[offset:offset+size] )[0]
			s = 'BLOB(' + str(size) + ')'
			offset += size
		elif t > 11 and t%2 == 1:
			size = (t-13)/2
			if size > len(payload)-offset:
				size = len(payload)-offset
			v = unpack( str(size) + "s", payload[offset:offset+size] )[0]
			s = 'STRING(' + str(size) + ')'
			offset += size
		f['strType'] = s
		f['value'] = v
	return fields

def fileHeader(var, headerBytes):
	(var.String, var.pageSize, var.FFWv, var.FFRv, var.reservedSpace, var.maxPayload,
	var.minPayload, var.leafPayload, var.FileChangeCounter, var.DBSize, var.freelistTrunk,
	var.freelistTotal, var.SchemaCookie, var.SchemaFormat, var.PageCacheSize, var.VacuumRootPage,
	var.Encoding, var.UserVersion, var.VacuumMode, var.Reserved, var.VersionValid, var.Version) =  unpack( ">16sH6B11I24s2I", headerBytes )
	if var.Encoding == 1:
		var.EncodingStr = 'UTF-8'
	elif var.Encoding == 2:
		var.EncodingStr = 'UTF-16le'
	elif var.Encoding == 3:
		var.EncodingStr = 'UTF-16be'
	else:
		var.Encoding = 'Unknown'
	if var.pageSize == 1:
		var.pageSize = 65536
	var.usableSize = var.pageSize - var.reservedSpace
	var.maxLocal = (var.usableSize-12)*64/255 - 23
	var.minLocal = (var.usableSize-12)*32/255 - 23
	var.maxLeaf = var.usableSize - 35
	var.minLeaf = (var.usableSize-12)*32/255 - 23

def isBTreePage( f ):
	if f == 0x05 or f == 0x0D or f == 0x02 or f == 0x0A:
		return 1
	return 0

class SQLitePage(object):
	"""Class to store complete Pages"""
	def __init__(self, pgn, parent, pageBytes):
		self.pageNum = pgn
		self.type = "Unknown"
		self.stream = pageBytes
		self.Flag = 0
		self.BTree = parent
		self.unallocated = ListRange( [0, parent.usableSize] )
		self.cellGap = ListRange()
		self.isSubType = None
	
	def readCellHeader(self, cn):
		if cn < self.numCells:
			c = self.readCellHeaderOff( self.cells[cn]['offset'], cn )
			
	def readCellHeaderOff(self, offset, cn=-1):
		cell = { 
			'pg': self.pageNum,
			'offset': offset,
			'leftChild': 0,
			'payloadLen_v': 0,
			'payloadLen': 0,
			'key_v': 0,
			'key': 0,
			'payloadOffset': 0,
			'localPayloadLen': 0,
			'cellNo': None,
			'cellSize': 0,
			'overflowPage': None,
			'overflowList': None,
			'correct': True
		}
		cell['cellNo'] = cn
		of = 0
		if offset+of >= self.BTree.usableSize or offset+of+4 > self.BTree.usableSize:
			cell['correct'] = False
			return cell
		if not self.Flag & 0x08:
			cell['leftChild'] = unpack(">I", self.stream[offset+of:offset+of+4])
			of += 4
		if self.Flag & 0x8 or self.Flag & 0x7 == 2:
			(cell['payloadLen'], cell['payloadLen_v']) = readVarInt( self.stream, offset+of )
			of += cell['payloadLen_v']
		if self.Flag & 0x1:
			(cell['key'], cell['key_v']) = readVarInt( self.stream, offset+of)
			of += cell['key_v']
		if self.Flag & 0x8 or self.Flag & 0x7 == 2:
			cell['payloadOffset'] = of
			if cell['payloadLen'] > self.maxLocal:
				surplus = self.minLocal + (cell['payloadLen'] - self.minLocal)%(self.BTree.usableSize - 4)
				if surplus <= self.maxLocal:
					cell['localPayloadLen'] = surplus
				else:
					cell['localPayloadLen'] = self.minLocal
				cell['overflowPage'] = int(unpack(">I", self.stream[offset+of+cell['localPayloadLen']:offset+of+cell['localPayloadLen']+4])[0])
				cell['overflowList'] = self.BTree.followOverflow( cell )
				of += 4
			else:
				cell['localPayloadLen'] = cell['payloadLen']
				cell['overflowPage'] = 0
			of += cell['localPayloadLen']
		cell['cellSize'] = of
		return cell
		
	def dump(self):
		print"[+]Page", self.pageNum
		print"\tType:", self.type
		self.__dump__()
	
	def __dump__(self):
		pass


class SQLiteBTreePage(SQLitePage):
	def __init__(self, pgn, parent, pageBytes, root=0):
		super(SQLiteBTreePage, self).__init__(pgn, parent, pageBytes)
		of = 0
		self.isFirstPage = root
		if self.isFirstPage:
			of += 100
		self.Flag = unpack(">B", self.stream[of:of+1])[0]
		of += 1
		if not isBTreePage (self.Flag):
			return
		self.FirstBlock = 0
		self.numnumCells = 0
		self.ContentArea = 0
		self.Fragment = 0
		self.avgCellSize = 0
		self.avgPayloadLen = 0
		self.unallocated = ListRange( )
		self.Pointer = 0
		(self.FirstBlock, self.numCells, self.ContentArea, self.Fragment) = unpack(">3HB", self.stream[of:of+7])
		self.maxLocal = self.BTree.maxLocal
		self.minLocal = self.BTree.minLocal
		of += 7
		if self.Flag & 0x8:
			self.strType = "Leaf" 
		else:
			self.strType = "Interior"
			self.Pointer = unpack(">I", pageBytes[of:of+4])[0]
			of += 4
		if self.Flag & 0x7 == 2:
			self.strType += " Index";
		elif self.Flag & 0x7 == 5:
			self.strType += " Table";
			self.maxLocal = self.BTree.maxLeaf
			self.minLocal = self.BTree.minLeaf
		if self.strType != "Unknown":
			self.type = "BTree"
		if self.numCells:
			self.cells = []
			self.cellGap.addRange( [self.ContentArea, self.BTree.usableSize] )
			avgSize = 0
			avgPayload = 0
			for i in range(0, self.numCells):
				co = unpack( ">H", self.stream[of:of+2] )[0]
				cell = self.readCellHeaderOff(co, i)
				self.cells.append( cell )
				self.cellGap.delRange( [cell['offset'], cell['offset']+cell['cellSize']] )
				avgSize += cell['cellSize']
				if 'payloadLen' in cell:
					avgPayload += cell['payloadLen']
				of += 2
			for r in self.cellGap:
				self.unallocated.addRange( r )
			self.avgCellSize = int(avgSize / self.numCells)
			self.avgPayloadLen = int(avgPayload / self.numCells)
		if self.ContentArea == self.BTree.usableSize:
			self.unallocated.addRange( [of, self.BTree.usableSize] )
		else:
			self.unallocated.addRange( [of, self.ContentArea-1] )
	
	def __dump__(self):
		if self.isFirstPage:
			print "\tFirst Page (with file header)"
		print "\tBTree Page Type", self.Flag, "(" + self.strType + ")"
		print "\tByte offset into First Freeblock:", self.FirstBlock
		print "\tNumber of cells:", self.numCells
		print "\tAvg. cell size:", self.avgCellSize
		if self.avgPayloadLen:
			print "\tAvg. payload size:", self.avgPayloadLen
		print "\tOffset to the first byte of content area:", self.ContentArea
		print "\tFragment:", self.Fragment
		if self.numCells:
			print "\tCell ptrs:", ",".join([ str(i['offset']) for i in self.cells])
		if not(self.Flag & 0x8):
			print "\tThe right-most pointer:", self.Pointer
		print "\tUnallocated space:", ",".join([str(i) for i in self.unallocated])
		print "\tCell gaps:", ",".join([str(i) for i in self.cellGap])
	
class SQLiteFreelistPage(SQLitePage):
	def __init__(self, pgn, parent, pageBytes, trunk=0):
		super(SQLiteFreelistPage, self).__init__(pgn, parent, pageBytes)
		self.isSubType = None
		self.isTrunk = trunk
		self.unallocated = ListRange( )
		if trunk:
			self.type = 'Freelist Trunk'
			(self.nextTrunkPage, self.leafpageCount) =  unpack( '>II', self.stream[0:8] )
			self.leafPages = []
			offset = 8
			for i in range(0, self.leafpageCount):
				self.leafPages.append( unpack( '>I', self.stream[offset:offset+4] )[0] )
				offset += 4
			self.unallocated.addRange( [offset, parent.pageSize] );
		else:
			#if isBTreePage( unpack(">B", pageBytes[0:1] )[0]):
			self.isSubType = SQLiteBTreePage(pgn, self.BTree, pageBytes)
			self.type = 'Freelist Leaf'
			self.unallocated.addRange( [1, parent.pageSize] );
			
	def __dump__(self):
		if self.isTrunk:
			print "\tNext freelist trunk page:", self.nextTrunkPage
			print "\tLeaf pages count:", self.leafpageCount
			print "\tLeaf pages: " + ",".join(["%d" % i for i in  self.leafPages ]) 
		if self.isSubType:
			print "\tSubtype:", self.isSubType.type
			self.isSubType.__dump__( )

class SQLiteOverflowPage(SQLitePage):
	def __init__(self, pgn, parent, pageBytes, page=-1, cell=-1):
		super(SQLiteOverflowPage, self).__init__(pgn, parent, pageBytes)
		self.type = 'Cell Overflow'
		self.parentPage = page
		self.parentCell = cell
		self.nextOverflow = int(unpack(">I", self.stream[0:4])[0])
		self.unallocated = ListRange( )

	def __dump__(self):
		print "\tParent cell:", str(self.parentPage) + "," + str(self.parentCell)
		print "\tContinues on:", self.nextOverflow
		print "\tUnallocated space:", ",".join([str(i) for i in self.unallocated])
		
class SQLiteRaw:
	def __init__(self, stream):
		fileHeader(self, stream[0:100] )
		self.stream = stream
		page1 = stream[:self.pageSize]
		pages = stream[self.pageSize:]
		self.Pages = { 1: SQLiteBTreePage(1, self, page1, 1) }
		if self.freelistTrunk:
			tp = self.freelistTrunk
			while tp:
				pgOffset = (tp-1)*self.pageSize
				freelistTP = SQLiteFreelistPage( tp, self, stream[pgOffset:pgOffset+self.pageSize], 1 )
				self.Pages[tp] = freelistTP
				for pl in freelistTP.leafPages:
					plof = (pl-1)*self.pageSize
					self.Pages[pl] = SQLiteFreelistPage( pl, self, stream[plof:plof+self.pageSize] )
				tp = freelistTP.nextTrunkPage

		self.pageCount = 1
		while len(pages) >= self.pageSize:
			self.pageCount += 1
			if not self.pageCount in self.Pages:
				try:
					self.Pages[self.pageCount] = SQLiteBTreePage( self.pageCount, self, pages[:self.pageSize] )
				except:
					self.Pages[self.pageCount] = SQLitePage( self.pageCount, self, pages[:self.pageSize] )
			pages = pages[self.pageSize:]
	def followOverflow(self, cell):
		if not cell['overflowPage']:
			return []
		ret = []
		overflow = cell['overflowPage']
		size = cell['localPayloadLen']
		while overflow:
			ret.append( overflow )
			if not overflow in self.Pages:
				ovpg = SQLiteOverflowPage( overflow, self, self.stream[(overflow-1)*self.pageSize:overflow*self.pageSize], cell['pg'], cell['cellNo'] )
				self.Pages[overflow] = ovpg
			else:
				ovpg = self.Pages[overflow]
			if ovpg.type == 'Overflow':
				overflow = ovpg.nextOverflow
				if overflow:
					size += self.usableSize-4
				else:
					ovpg.unallocated.addRange( [cell['payloadLen']-size+4, self.usableSize] )
			else:
				break
				

		return ret

	def getCellPayload(self, cell):
		of = cell['offset'] + cell['payloadOffset']
		read_len = l = cell['localPayloadLen']
		stream = self.Pages[cell['pg']].stream
		payload = unpack( str(l) + "s", stream[of:of+l] )[0]
		if cell['overflowPage']:
			for ovpg in cell['overflowList']:
				stream = self.Pages[ovpg].stream
				l = min(self.usableSize-4, cell['payloadLen'] - read_len)
				payload += unpack( str(l) + "s", stream[4:4+l] )[0]
		return payload

	def dumpHeader(self):
		print "[+] Dumping SQLite Header"
		print "Header String:", self.String
		print "Page Size:",self.pageSize
		print "FFW, FFR:", self.FFWv, ",", self.FFRv
		print "Bytes of unused 'reserved' space:", self.reservedSpace
		print "Maximum embedded payload fraction (64):", self.maxPayload
		print "Minimun embedded payload fraction (32):", self.minPayload
		print "\tMaximum embedded payload:", self.maxLocal
		print "\tMinimun embedded payload:", self.minLocal
		print "Minimun Leaf payload (32):", self.leafPayload
		print "\tMaximum embedded Leaf payload:", self.maxLeaf
		print "\tMinumun embedded Leaf payload:", self.minLeaf
		print "File change counter:", self.FileChangeCounter
		print "Size of the database file in pages:", self.DBSize
		print "Page number of the first freelist trunk page:", self.freelistTrunk
		print "Total number of freelist pages:", self.freelistTotal
		print "The schema cookie:", self.SchemaCookie
		print "The schema format number (1, 2, 3 or 4):", self.SchemaFormat
		print "Default page cache size:",  self.PageCacheSize
		print "Largest root b-tree page (Vacuum):", self.VacuumRootPage
		print "The database text encoding:", self.Encoding, "(" + self.EncodingStr +")"
		print "User Version:", self.UserVersion
		print "Incremental-Vacuum mode:", self.VacuumMode
		print "Reserved:", str(self.Reserved)
		print "Version valid for:", self.VersionValid
		print "SQLite Version:", self.Version

	def dump(self):
		self.dumpHeader()
		print "Real Page Count:", self.pageCount
		print ""
	def dump_pages(self):
		print "[+]Pages"
		for index, page in self.Pages.iteritems():
			page.dump()

