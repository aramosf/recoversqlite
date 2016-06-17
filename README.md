# recoversqlite
Two different scripts with the same pourpose: recover information from deleted registers in sqlite databases.
  - recoversqlite.py - first version
  - dumplite.py - rewrited, second version

### Version
1.0

### Tech
All of this was part of SecurityByDefault forensics in sqlite articles, you can read more in spanish here:

* http://www.securitybydefault.com/2012/08/forense-de-sqlite-i-recursos.html
* http://www.securitybydefault.com/2012/08/forense-de-sqlite-ii-cabecera.html
* http://www.securitybydefault.com/2012/08/forense-de-sqlite-iii-paginas-libres.html
* http://www.securitybydefault.com/2012/08/forense-de-sqlite-iv-paginas-b-tree-y.html
* http://www.securitybydefault.com/2012/09/forense-de-sqlite-v-celdas.html
* http://www.securitybydefault.com/2012/09/forense-de-sqlite-vi-practica.html
* http://www.securitybydefault.com/2012/09/forense-de-sqlite-vii-ejercicio-resuelto.html


### Installation
just python:

```sh
$ python recoversqlite.py -f personas.sqlite
```

```sh
$ python dumplite.py -f personas.sqlite -l -u -d
```

### References

* http://forensicsfromthesausagefactory.blogspot.com.es/2011/04/carving-sqlite-databases-from.html
* http://forensicsfromthesausagefactory.blogspot.com.es/2011/05/analysis-of-record-structure-within.html
* http://forensicsfromthesausagefactory.blogspot.com.es/2011/05/sqlite-pointer-maps-pages.html 
* http://forensicsfromthesausagefactory.blogspot.com.es/2011/07/sqlite-overflow-pages-and-other-loose.html
* http://mobileforensics.wordpress.com/2011/04/30/sqlite-records/
* http://mobileforensics.wordpress.com/2011/09/17/huffman-coding-in-sqlite-a-primer-for-mobile-forensics/
* http://www.forensicswiki.org/wiki/Mozilla_Firefox_3_History_File_Format
* http://digitalinvestigation.wordpress.com/2012/05/04/the-forensic-implications-of-sqlites-write-ahead-log/
* http://sandbox.dfrws.org/2011/fox-it/DFRWS2011_results/Report/Sqlite_carving_extractAndroidData.pdf
* http://computer-forensics.sans.org/summit-archives/2011/2-taking-it-to-the-next-level.pdf
* http://www.ccl-forensics.com/images/f3%20presentation3.pdf

Official Doc:
* http://www.sqlite.org/fileformat.html 
* http://www.sqlite.org/fileformat2.html
* http://sqlite.org/docs.html
* http://www.sqlite.org/pragma.html#pragma_secure_delete
* http://www.sqlite.org/src/artifact/cce1c3360c

Tools (public and commercial):
* http://www.garykessler.net/software/sqlite_parser_v2.1a.zip
* http://www.crypticbit.com/zen/products/iphoneanalyzer
* http://www.ccl-forensics.com/Software/epilog-from-ccl-forensics.html 
* http://www.filesig.co.uk/sqlite-forensic-reporter.html
* http://www.oxygen-forensic.com/en/features/sqliteviewer/

Studies and publications:
* http://www.springerlink.com/content/n6l6526n16847kh8/
* http://www.sciencedirect.com/science/article/pii/S1742287609000048

Books:
* http://www.amazon.com/Definitive-Guide-SQLite-Mike-Owens/dp/1590596730
* http://books.google.es/books/about/Inside_SQLite.html?id=QoxUx8GOjKMC&redir_esc=y

