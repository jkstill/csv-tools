#!/usr/bin/env python3

"""
for a series of data, get moving average for windowPeriod samples
iterarting through the data 1 row at a time

the first argument is the window period

for instance, sar data is sampled 144 times a day

mvavg-max-detector.py window-size maxvalue threshold-count COL1 COL2 ... <  file

to find if either reads or writes are found to average > 0.5 seconds in a window sizes of 10 samples, at least 5 times

./mvavg-max-detector.py 10 0.5 5 AVG_READ_TIME AVG_WRITE_TIME < diskgroup-breakout/FRA.csv

If you want to get a count of all occurrences, make the threshold count larger than the number of rows in the file
Number of times MAX AVG_READ_TIME IO time of 0.5 in Window of 10 Exceeded: 11
Number of times MAX AVG_WRITE_TIME IO time of 0.5 in Window of 10 Exceeded: 10

./mvavg-max-detector.py 10 0.5 $(wc -l diskgroup-breakout/FRA.csv | awk '{ print $1}' )  AVG_READ_TIME AVG_WRITE_TIME < diskgroup-breakout/FRA.csv
Number of times MAX AVG_READ_TIME IO time of 0.5 in Window of 10 Exceeded: 146
Number of times MAX AVG_WRITE_TIME IO time of 0.5 in Window of 10 Exceeded: 10


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
  maxIOTime=float(sys.argv[2])
  maxIOThresholdCount=int(sys.argv[3])

  workingColumns = []
  for column in sys.argv[4:]:
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

  maxIOTimeExceededCount={}

  for colName in workingColumns:
    colNum = colRefs[colName]
    ma = bn.move_mean(colValues[colNum], window=windowPeriod)

    maxIOTimeExceededCount[colName] = 0

    #print('len(ma): {}'.format(len(ma)))
    #for i in range(0,len(ma)):

      #if math.isnan(ma[i]):
        #continue

      #if i%72 == 0:
        #print('{:0.2f}'.format(ma[i]))

    # skip the first windowPeriod of values, as they are 'nan'
    for windowStart in range(windowPeriod, int(len(ma)) - windowPeriod, windowPeriod):
      try:
        periodMA = average(ma[windowStart:windowStart + windowPeriod])
      except ZeroDivisionError:
        continue

      if periodMA > maxIOTime:
        maxIOTimeExceededCount[colName] += 1
        if maxIOTimeExceededCount[colName] > maxIOThresholdCount:
          break


  failureFound = False
  for colName in workingColumns:
    print('Number of times MAX {} IO time of {} in Window of {} Exceeded: {}'.format(colName,maxIOTime,windowPeriod,  maxIOTimeExceededCount[colName]))
    if maxIOTimeExceededCount[colName] > maxIOThresholdCount:
      failureFound = True

  if failureFound:
    sys.exit(1)


if __name__ == '__main__':
  main()


