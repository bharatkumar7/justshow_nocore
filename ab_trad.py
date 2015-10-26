# Last Update : 10/7/2015
# 
# 
import classes , util, buysell
import os
import numpy as np
# header for xlwings
from xlwings import Workbook, Sheet, Range, Chart
import time, logging
os.environ['TZ'] = 'Asia/Kolkata'

# logger
logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('today.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

# load symbols and set working directory, open xls file
symbols, tdata, xwb, pclose = util.reader()

#initial run (set maxticks)
time.sleep(classes.symbol.sleeptime) #wait
print "Initial data", classes.symbol.maxtick, '::', 
for i in range(0,classes.symbol.maxtick):
 idata = util.nest_fetcher(xwb, symbols) # fetch ticker
 util.insert_tick(tdata, idata) # insert the present tick into full data
 #util.print_tick(tdata)
 print i
 time.sleep(classes.symbol.sleeptime) #wait
print " Done"

# analysis will start from here
while 1:
 #print "------------------------------------------"
 timeOK = util.gadi() #check if its good time to trade
 idata = util.nest_fetcher(xwb, symbols) # fetch ticker
 util.insert_tick(tdata, idata) # insert the present tick into full data  
 #util.print_tick(tdata)
 if(timeOK): buysell.analysis(symbols, pclose, tdata,logger)
 time.sleep(classes.symbol.sleeptime) #wait
 
#util.eluka()


