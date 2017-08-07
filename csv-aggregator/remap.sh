#!/bin/bash

originalFile=sar-disk-original.csv
newFile=sar-disk.csv

: <<'JKS-DOC'

remap drive names to ASM names
this query used to get names and numbers



select
	'dm-name-' || substr(d.path,instr(d.path,'/',-1)+1,length(d.path) - instr(d.path,'/',-1)) path
	, g.name || lpad(d.disk_number,2,'0') name
from v$asm_disk d
join v$asm_diskgroup g on g.group_number = d.group_number
order by 2

15:10:17 SYSDBA> /

PATH			                   NAME
------------------------------ --------------------
dm-name-mpathmp1	             DATA00
dm-name-mpathnp1	             DATA01
dm-name-mpathop1	             DATA02
dm-name-mpathqp1	             DATA03
dm-name-mpathrp1	             DATA04
dm-name-mpathsp1	             DATA05
dm-name-mpathtp1	             DATA06
dm-name-mpathvp1	             DATA07
dm-name-mpathwp1	             DATA08
dm-name-mpathcp1	             FRA00

10 rows selected.

JKS-DOC

sed \
	-e 's/dm-name-mpathmp1/DATA00/g' \
	-e 's/dm-name-mpathnp1/DATA01/g' \
	-e 's/dm-name-mpathop1/DATA02/g' \
	-e 's/dm-name-mpathqp1/DATA03/g' \
	-e 's/dm-name-mpathrp1/DATA04/g' \
	-e 's/dm-name-mpathsp1/DATA05/g' \
	-e 's/dm-name-mpathtp1/DATA06/g' \
	-e 's/dm-name-mpathvp1/DATA07/g' \
	-e 's/dm-name-mpathwp1/DATA08/g' \
	-e 's/dm-name-mpathcp1/FRA00/g' \
< $originalFile > $newFile


