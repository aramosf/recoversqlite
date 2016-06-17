#!/usr/bin/python
# -*- coding: utf-8 -*-
# Sat Jul 28 00:57:02 CEST 2012 <aramosf@gmail.com>

import sys
import os 
import struct
import getopt

def usage ( ):
    print ('Usage: %s [options] -f <file>\n' % sys.argv[0])
    print ('Options:')
    print ('    -h            this help')
    print ('    -v            verbose')
    print ('    -f <file>     sqlite file')
    print ('    -o [h|a|n]    output as hex (default), ascii, or nothing')
    
    sys.exit(1)


ftype = "h"
pages = "all"
file = ""
verbose = "0"

try:                                
 opts, args = getopt.getopt(sys.argv[1:], "vho:f:")
except getopt.GetoptError:          
 usage()                         
 sys.exit(2)                     
for opt, arg in opts:                
  if opt in ('-h'):
      usage()                     
  elif opt == '-o':                
     ftype = arg
     if ftype != "a" and ftype != "h" and ftype != "n":
       usage()                     
  elif opt == '-f':                
     file = arg
  elif opt == '-v':                
     verbose = 1

if file == "":
  usage ()

if not os.path.exists(file):
  print 'error: file %s not found!' % file
  usage ()


if len(sys.argv) < 2:
   usage()
   sys.exit()                  

filesize = os.path.getsize(file)
with open(file, 'rb') as f:
    s = f.read()


# The header string: "SQLite format 3\000"
hs=s[:16].rstrip(' \t\r\n\0')
if hs == "SQLite format 3":
 r = " (correct)"
else:
 r = " (incorrect)"
print '%-45s %-20s' % ("Header String:", hs + r)

# The database page size in bytes. Must be a power of two between 512 
# and 32768 inclusive, or the value 1 representing a page size of 65536
pagesize = struct.unpack(">H", s[16:18])[0]
if pagesize == 1:
 pagesize == 65536
print '%-45s %-20s'  % ("Page Size bytes:", pagesize)

# File format write version. 1 for legacy; 2 for WAL
wver = ord(s[18:19])
if wver == 2:
  wrel = str(wver) + " - WAL: yes"
else:
  wrel = str(wver) + " - WAL: no"
print '%-45s %-20s' % ("File format write version:", wrel)

# File format read version. 1 for legacy; 2 for WAL.
rver = ord(s[19:20])
if rver == 2:
  rrel = str(rver) + " - WAL: yes"
else:
  rrel = str(rver) + " - WAL: no"
print '%-45s %-20s' % ("File format read version:", rrel)

# Bytes of unused "reserved" space at the end of each page. Usually 0.
if verbose == 1: print '%-45s %-20s' % ('Bytes of unused reserved space:', ord(s[20]))

# Maximum embedded payload fraction. Must be 64.
if ord(s[21]) == 64:
 r = " (correct)"
else:
 r = " (incorrect)"
if verbose == 1: print '%-45s %-20s' % ('Maximum embedded payload fraction:', str(ord(s[21])) + r)

# Minimum embedded payload fraction. Must be 32.
if ord(s[22]) == 32:
 r = " (correct)"
else:
 r = " (incorrect)"
if verbose == 1: print '%-45s %-20s' % ('Minimum embedded payload fraction:', str(ord(s[22])) + r)

# Leaf payload fraction. Must be 32.
if ord(s[23]) == 32:
 r = " (correct)"
else:
 r = " (incorrect)"
if verbose == 1: print '%-45s %-20s' % ('Leaf payload fraction:', str(ord(s[23])) + r)

# File change counter.
count = struct.unpack(">i", s[24:28])[0]
print '%-45s %-20s' % ('File change counter:', count)

# Size of the database file in pages. The "in-header database size".
sizepag = struct.unpack(">i", s[28:32])[0]
print '%-45s %-20s' % ('Size of the database file in pages:', sizepag)

# Page number of the first freelist trunk page.
pagenum = struct.unpack(">i", s[32:36])[0]
print '%-45s %-20s' % ('Page number of the first freelist trunk page:', pagenum)

# Total number of freelist pages.
freenum = struct.unpack(">i", s[36:40])[0]
print '%-45s %-20s' % ('Total number of freelist pages:', freenum)

# The schema cookie.
schema = struct.unpack(">i", s[40:44])[0]
if verbose == 1: print '%-45s %-20s' % ('The schema cookie:', schema)

# The schema format number. Supported schema formats are 1, 2, 3, and 4.
schemav = struct.unpack(">i", s[44:48])[0]
if schemav == 1:
 schemavs = " -  back to ver 3.0.0"
elif schemav == 2:
 schemavs = " - >= 3.1.3 on 2005-02-19"
elif schemav == 3:
 schemavs = " - >= 3.1.4 on 2005-03-11"
elif schemav == 4:
 schemavs = " - >= 3.3.0 on 2006-01-10"
else:
 schemavs = " - schema version error"
if verbose == 1: print '%-45s %-20s' % ('The schema format number', str(schemav) + schemavs)

# Default page cache size.
pcachesize = struct.unpack(">i", s[44:48])[0]
if verbose == 1: print '%-45s %-20s' % ('Default page cache size:', pcachesize)

# The page number of the largest root b-tree page when in auto-vacuum or incremental-vacuum modes, or zero otherwise.
vacuum = struct.unpack(">i", s[52:56])[0]
if vacuum == 0:
 vacuums = " - not supported"
else:
 vacuums = " "
if verbose == 1: print '%-45s %-20s' % ('Auto/incremental-vacuum page number:', str(vacuum) + vacuums)

# The database text encoding. A value of 1 means UTF-8. A value of 2 means UTF-16le. A value of 3 means UTF-16be.
encod = struct.unpack(">i", s[56:60])[0]
if encod == 1:
  encods = " - UTF-8"
elif encod == 2:
  encods = " - UTF-16le"
elif encod == 3:
  encods = " - UTF-16be"
else:
 encods = " - error"
print '%-45s %-20s' % ('The database text encoding:', str(encod) + encods)

# The "user version" as read and set by the user_version pragma.
userv = struct.unpack(">i", s[60:64])[0]
if verbose == 1: print '%-45s %-20s' % ('User version number:', userv)

# True (non-zero) for incremental-vacuum mode. False (zero) otherwise.
incvacuum = struct.unpack(">i", s[64:68])[0]
if incvacuum == 0:
  sinc = " - false"
else:
  sinc = " - true"
print '%-45s %-20s' % ('Incremental-vacuum mode:', str(incvacuum) + sinc)

reserv = struct.unpack(">iiiiii", s[68:92])[0]
if reserv == 0:
  strreserv = "0 (correct)"
else:
  strreserv = "!= 0 (incorrect)"
if verbose == 1: print '%-45s %-20s' % ('Reserved for expansion:', strreserv)

# The version-valid-for number.
# The 4-byte big-endian integer at offset 92 is the value of the change counter
# when the version number was stored. The integer at offset 92 indicates which 
# transaction the version number is valid for and is sometimes called the 
# "version-valid-for number".
verval =  struct.unpack(">i", s[92:96])[0]
if verbose == 1: print '%-45s %-20s' % ('The version-valid-for number:', verval)

# SQLITE_VERSION_NUMBER:
# #define SQLITE_VERSION        "3.7.13"
# #define SQLITE_VERSION_NUMBER 3007013
vervalid = struct.unpack(">i", s[96:100])[0]
may = vervalid / 1000000
min = (vervalid - (may * 1000000)) / 1000
rls =  vervalid - (may * 1000000) - (min * 1000) 
verstr = str(vervalid) + " - " + str(may) + "." + str(min) + "." + str(rls)
print '%-45s %-20s' % ('SQLITE_VERSION_NUMBER:', verstr) 

def hexdump(src, length=16):
    if all_same(src):
	strzero = "0000   00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00    ................\n"
	strzero += "..."
	return strzero
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in xrange(0, len(src), length):
       s = src[i:i+length]
       hexa = b' '.join(["%0*X" % (digits, ord(x))  for x in s])
       text = b''
       for x in s:
         if(ord(x) < 0x20 or ord(x) == 0x7F or 0x81 <= ord(x) < 0xA0):
           text += b'.'
         else:
           text += x
       result.append( b"%04X   %-*s   |%s|" % (i, length*(digits + 1),
hexa, text) )
    return b'\n'.join(result)


def asciidump(src, length=80):
    if all_same(src):
      strzero = "................................................................................"
      return strzero
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in xrange(0, len(src), length):
       s = src[i:i+length]
       text = b''
       for x in s:
         if(ord(x) < 0x20 or ord(x) == 0x7F or 0x81 <= ord(x) < 0xA0):
           text += b'.'
         else:
           text += x
       result.append( b"%s" % (text) )
    return b'\n'.join(result)

def all_same(items):
    return all(x == items[0] for x in items)

def formatlist(list):
 i=0
 for el in list:
    i+=1
    if i == 10:
       if verbose == 1: print
       i=0
    else:
       if verbose == 1: print '%5d' % el,
 if verbose == 1: print



def locatetrunk ( offset ):
 nextrunk =  struct.unpack(">i", s[offset:offset+4])[0]
 if nextrunk != 0:
   return nextrunk
 else:
   return 0

def locatefreeleafs ( offset ):
  numleafpag = struct.unpack(">i", s[offset+4:offset+8])[0]
  # -24 -> bug in sqlite avoids writing in last 6 entries
  freepage = s[offset+8:offset+pagesize-24]  
  fmt = ">" + "i" * (len(freepage)/4)
  # return only numleafpag
  return struct.unpack(fmt, freepage)[0:numleafpag]


def freepages( ):
  offset = (pagenum - 1)*pagesize
  freeleaftpages=locatefreeleafs( offset )
  nextrunk = 1
  freetrunk.append(pagenum)
  while ( nextrunk != 0 ):
    nextrunk = locatetrunk( offset )
    if nextrunk != 0:
        freetrunk.append(nextrunk)
        offset = (nextrunk - 1)*pagesize
        freeleaftpages += locatefreeleafs( offset )
    
  freeleaf = list(set(freeleaftpages))

  return freeleaf, freetrunk

def locatebtree( ):
  offset = 100
  page = 1
  while ( offset < filesize ):
	byte = ord(s[offset])
  	if byte == 13 and page not in freeleaf:
	   leafpages.append(page)
        elif byte == 2 and page not in freeleaf:
	   interindex.append(page)
        elif byte == 5 and page not in freeleaf:
	   intertable.append(page)
        elif byte == 10 and page not in freeleaf:
           leafindex.append(page)
	if offset == 100:
	    offset = 0
        offset += pagesize
        page += 1

def pagedump(pages):
 for page in pages:
    offset = (page-1  )*pagesize
    end = 0
    if page == 0 or offset == 0: 
       offset += 100
       end = 100
    if page not in freeleaf and page not in freetrunk:
	# B-Tree header
	#
	# Number of cells on this page
	numcells = struct.unpack(">H", s[offset+3:offset+5])[0]
	# Offset to the first byte of the cell content area. 
	# A zero value is used to represent an offset of 65536,
	# which occurs on an empty root page when using a 65536-byte page size.
	offcells = struct.unpack(">H", s[offset+5:offset+7])[0]
	osfree = struct.unpack(">H", s[offset+1:offset+3])[0]
	fragmented = struct.unpack(">b", s[offset+7])[0]
	nextfb = osfree
	fbsize = 0
	if offcells == 0:
        	offcells = 65536
	# interior btree header = 12 bytes, leaf btree = 8 bytes
	head = 8
	if ord(s[offset]) == 2 or 5: head = 12
	# unallocated start and end
	unstart = offset + head + ( numcells * 2 )
	unend = offset + offcells  - end
	freestr = s[unstart:unend]  
	if ftype != "n":
		print '%-25s page: %s offset: %10s-%-10s' % ('Unallocated space: ', page, unstart,unend)
	if ftype == "a":
       		print asciidump(freestr)
    	elif ftype == "h":
       		print hexdump(freestr)
    
	while ( nextfb != 0 ):
      	# freeblock  1,2 bytes next block or 0 if none
      	# freeblock  3,4 size of freeblock
      		fbsize = struct.unpack(">H", s[offset+nextfb+2:offset+nextfb+4])[0]
      		fbstart = offset+nextfb+4
		fbend = offset+nextfb+fbsize
      		fbstr = s[fbstart:fbend]
     		if ftype != "n":
         		print '%-25s page: %s offset: %10s-%-10s' % ('Freeblock space: ', page, fbstart,fbend)
         	if ftype == "a":
    	      		print asciidump(fbstr)
         	elif ftype == "h":
              		print hexdump(fbstr)
 		nextfb = struct.unpack(">H", s[offset+nextfb:offset+nextfb+2])[0]
    elif page in freeleaf:
	freestr = s[offset:offset+pagesize]  
	if ftype != "n":
          print '%-25s page: %s offset: %10s' % ('Freelist leaf page: ',page, offset)
	if ftype == "a":
	        print asciidump(freestr)
     	elif ftype == "h":
       		print hexdump(freestr)

    elif page in freetrunk:
	ftstart = offset+8+(4*len(freeleaf))
	ftend = offset+pagesize
	freestr = s[ftstart:ftend]  
	if ftype != "n":
	  print '%-25s page: %s offset: %10s-%-10s' % ('Freelist trunk space: ', page, ftstart,ftend)
	if ftype == "a":
	        print asciidump(freestr)
     	elif ftype == "h":
       		print hexdump(freestr)





# Freepages
freeleaf = [ ]
freetrunk = [ ]

if freenum > 0: freeleaf,  freetrunk = freepages( )
if verbose == 1 and freenum >0: 
  print "Freelist leaf pages:"
  formatlist(freeleaf)
print '%-45s %-20s' % ('Number of freelist leaf pages:', len(sorted(set(freeleaf))))

## B-tree pages unallocated + freeblocks
btreepages = [ ]
leafpages = [ ]
interindex = [ ]
intertable = [ ]
leafindex = [ ]


locatebtree()


if verbose == 1 and len(freetrunk) >0: 
  print "Freelist trunk pages:"
  formatlist(freetrunk)
print '%-45s %-20s' % ('Number of freelist trunk pages:', len(freetrunk))

if verbose == 1 and len(leafpages) > 0: 
  print "B-Tree leaf pages:"
  formatlist(leafpages)
print '%-45s %-20s' % ('Number of b-tree leaf pages:', len(leafpages))
if verbose == 1 and len(leafindex) >0: 
  print "B-Tree leaf index pages:"
  formatlist(leafindex)
print '%-45s %-20s' % ('Number of b-tree leaf index pages:', len(leafindex))
if verbose == 1 and len(interindex) >0: 
  print "B-Tree interior index pages:"
  formatlist(interindex)
print '%-45s %-20s' % ('Number of b-tree interior index pages:', len(interindex))
if verbose == 1 and len(intertable) >0: 
  print "B-Tree interior table pages:"
  formatlist(intertable)
print '%-45s %-20s' % ('Number of b-tree interior table pages:', len(intertable))


btreepages = sorted(leafpages + leafindex + interindex + intertable)
allpag = sorted(btreepages + freeleaf + freetrunk)

pagedump(allpag)


if verbose == 1:
  print '%-45s %-20s' % ('Number of detected pages:', len(allpag))
  print '%-45s %-20s' % ('Missing:', sizepag - len(allpag))


