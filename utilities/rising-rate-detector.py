#!/usr/bin/env python3

"""
for a series of data, determine if the average value is rising

the first argument is the window period

for instance, sar data is samples 144 times a day

./rising-rate-detector.py 144 ldavg-15 < sar-load.csv
"""


import sys
from sys import stdin, stderr
import os
import numpy as np
#import csv
import bottleneck as bn
from math import nan
import math


def getLines():
  lines=[]
  for line in stdin:
    lines.append(line.strip())

  return lines


def getHdr(lines):
  hdrLine=lines.pop(0)
  return hdrLine.strip().split(',')


def getColRefs(hdrLine):
  i = 0
  colRefs={}
  for col in hdrLine:
    colRefs[col] = i
    i += 1

  return colRefs


def validateWorkingColumns(hdr,workingColumns):

  for colName in workingColumns:
    if colName not in hdr:
      print('{} is in invalid column name'.format(colName),file=sys.stderr)
      sys.exit(1)

# get a dict of arrays for the data
# used as source to detect outliers per column
def getDataSet(columnRef,workingColumns,lines):
  colVals={}
  #print('column#: {}'.format(columnRef))
  for line in lines:
    a = line.split(',')
    for colName in workingColumns:
      #print('colName: {}'.format(colName))
      colNum = columnRef[colName]
      #print('colNum: {}'.format(colNum))
      #print('{} val {}'.format(colName,a[colNum]))
      if not colNum in colVals.keys():
        colVals[colNum] = []

      # remove values that cause an error
      # most sar files have non-metric values for the first 3 columns
      # date, time , name
      # some may have another non metric value, which is usually the cause of errors here
      try:
        colVals[colNum].append(float(a[colNum]))
      except:
        workingColumns.remove(colName)
        columnRef.pop(colName)

  return colVals

def average(lst):
  return sum(lst) / len(lst)

def main():

  lines = getLines()

  hdr = getHdr(lines) # array

  if sys.argv[1] == 'hdrs':
    hdrList='\n'.join(hdr)
    print(hdrList)
    sys.exit(0)

  colRefs = getColRefs(hdr)
  #print('colRefs: {}'.format(colRefs))

  windowPeriod = int(sys.argv[1])

  workingColumns = []
  for column in sys.argv[2:]:
    workingColumns.append(column)

  validateWorkingColumns(hdr,workingColumns)

  #print('working columns: {}'.format(' - '.join(workingColumns)))
  #print('first line: {}'.format(lines[0]))


  # get the position in the data array for each column to check
  colNums = [ colRefs[i] for i in workingColumns ]
  #print('colNums: {}'.format(colNums))

  #sys.exit(0)

  # this is a dict of lists, where each list is all values for the column
  #colValues = getDataSet(colRefs[workingColumns[0]],lines)
  colValues = getDataSet(colRefs,workingColumns,lines)

  #print('{}'.format(colValues))


  ratesRising=False

  for colName in workingColumns:
    colNum = colRefs[colName]
    ma = bn.move_rank(colValues[colNum], window=windowPeriod)

    #print('len(ma): {}'.format(len(ma)))
    #for i in range(0,len(ma)):

      #if math.isnan(ma[i]):
        #continue

      #if i%72 == 0:
        #print('{:0.2f}'.format(ma[i]))

    # skip the first windowPeriod of values, as they are 'nan'
    avgFirstPeriod = average(ma[windowPeriod:windowPeriod*2])

    midStart=int(len(ma) - (windowPeriod/2))

    avgMiddlePeriod = average(ma[midStart:midStart + windowPeriod])
    avgLastPeriod = average(ma[len(ma)-windowPeriod:])

    if (avgMiddlePeriod > avgFirstPeriod > 0) and ( avgLastPeriod > avgMiddlePeriod > 0):
    #if True:
      ratesRising=True
      #print('{} is rising: {} {} {}'.format(colName,avgFirstPeriod,avgMiddlePeriod,avgLastPeriod))
      print('{} is rising'.format(colName))
      print(' avgFirstPeriod: {:0.6f}'.format(avgFirstPeriod))
      print('avgMiddlePeriod: {:0.6f}'.format(avgMiddlePeriod))
      print('  avgLastPeriod: {:0.6f}'.format(avgLastPeriod))
      print('     %increased: {:5.0f}'.format( (( avgLastPeriod / avgFirstPeriod ) -1) * 100))

      #print('{}'.format(ma))

  if ratesRising:
    sys.exit(1)

if __name__ == '__main__':
  main()


