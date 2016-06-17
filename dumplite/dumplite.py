#! /usr/bin/python
# -*- encoding: utf-8 -*-
# Marcos Aguero - WiredRat with aramosf :D

import getopt, sys
import ListRange
from SQLiteFormat import *
from struct import unpack

def usage():
	print  """
Uso: ./dumplite -f FICHERO [ OPCIONES ]
Parametros:
  -f filename        Fichero a leer
  -F                 Imprime las cabeceras del fichero
  -l                 Imprime registros en paginas freelist leaf
  -h                 Esta ayuda
  -u		     Imprime los rangos libres
  -d		     Imprime los datos de los rangos libres
"""

def all_same(items):
    return all(x == items[0] for x in items)

def hexdump(src, rel_pos=0, length=16):
    if all_same(src):
        strzero = "%04X   00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00    ................\n" % rel_pos
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
       result.append( b"%04X   %-*s   |%s|" % (i+rel_pos, length*(digits + 1),
hexa, text) )
    return b'\n'.join(result)


def printFreelistLeaf():
	print "\nRecuperando registros de paginas Freelist:"
	for i, p in db.Pages.iteritems():
		if p.type == 'Freelist Leaf' and p.isSubType.type != 'Unknown'  and p.isSubType.numCells:
			print "Página numero: " + str(p.pageNum)
			for c in p.isSubType.cells:
				payload = db.getCellPayload( c )
				r = getRecord( db.getCellPayload( c ) )
				print ", ".join(["%s:%s" % (f['strType'], f['value']) for f in r])
			print ""

def printUnallocatedRanges():
  print "\nImprimiendo rangos:"
  for i, p in db.Pages.iteritems():
    print str(p.pageNum) + " (" + p.type + "): ",
    for r in p.unallocated:
      print "[" + str(r[0]+db.pageSize*(p.pageNum-1)) + ", " + str(r[1]+db.pageSize*(p.pageNum-1)) + ']',
    print ""
    if dump_unallocated:
      for r in p.unallocated:
	string = p.stream[r[0]:r[1]]
	print hexdump(string, db.pageSize*(p.pageNum-1)+r[0])
    if p.isSubType:
      print "\t(" + p.isSubType.type + "): ",
      for r in p.isSubType.unallocated:
	print "[" + str(r[0]+db.pageSize*(p.pageNum-1)) + ", " + str(r[1]+db.pageSize*(p.pageNum-1)) + ']',
      print ""




try:
	opts, args = getopt.getopt( sys.argv[1:], 'hf:Flud' );
except getopt.GetoptError, err:
	print str(err)
	usage()
	sys.exit(1)

filename = ''
print_file_headers = 0
print_freelist_leaf_records = 0
print_unallocated_ranges = 0
dump_unallocated = 0

for o, a in opts:
	if o == "-h":
		usage()
		sys.exit(0)
	if o == "-f":
		filename = a
	if o == '-F':
		print_file_headers = 1
	if o == '-l':
		print_freelist_leaf_records = 1
	if o == '-u':
		print_unallocated_ranges = 1
	if o == '-d':
		print_unallocated_ranges = 1
		dump_unallocated = 1


if filename == '':
	print "el parametro -f es obligatorio"
	sys.exit(2)

f = open(filename, 'r')
stream = f.read()
db = SQLiteRaw(stream)

if print_file_headers:
	db.dumpHeader()

if print_freelist_leaf_records:
	printFreelistLeaf()
if print_unallocated_ranges:
	printUnallocatedRanges();
