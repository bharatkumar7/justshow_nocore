import classes
import datetime, os, sys
from datetime import date, timedelta
import numpy as np
import pyautogui, time, urllib, pywintypes


# header for xlwings
from xlwings import Workbook, Sheet, Range, Chart
import time

os.environ['TZ'] = 'Asia/Kolkata'

def gadi():
   localtime = time.localtime(time.time())
   #print localtime
   if (localtime.tm_min<=9): tm_min="0"+str(localtime.tm_min)
   else: tm_min=localtime.tm_min
    
   if (localtime.tm_sec<=9): tm_sec="0"+str(localtime.tm_sec)
   else: tm_sec=str(localtime.tm_sec)

   abi=int(str(localtime.tm_hour)+str(tm_min)+str(tm_sec))
   start=91600
   eu_start=122500
   eu_end=123500
   end=153000   #first 2 digits hrs, next 2 minutes, last 2 seconds

   if (abi>=start and abi<=eu_start) or (abi>=eu_end and abi<=end): time_ok=1
   else: time_ok=0
   #print abi,time_ok
   return time_ok

# all screenshots are system-to-ssytem dependent --> get your own
#symbol.status = util.eluka(symbol.type, tsym, symbol.lot_size, bprice, 1)
def eluka(otype, fname, lot_size, bsprice, bs):
 dummy = r'D:\stock_market\My_Algo_Code\Live_trading\NIFTY15AUG8700CE.png'
 pyautogui.FAILSAFE = False
 #print dummy
 tloc = pyautogui.locateOnScreen(dummy,grayscale=False)
 if(tloc is None): # check if nest trader is in place
  resp = pyautogui.confirm(text='DUMMY NOT FOUND', title='', buttons=['OK', 'Cancel'])
  if(resp=='OK'): proceed=1
  if(resp=='Cancel'): proceed=0
 else:
  proceed=1
# proceed=1
  x0,y0 = pyautogui.center(tloc)

 ploc = pyautogui.locateOnScreen(fname,grayscale=False)
 #print "here"
 if(ploc is None): # check if nest trader is in place
  resp = pyautogui.confirm(text='MAIN NOT FOUND', title='', buttons=['OK', 'Cancel'])
  if(resp=='OK'):
   #ploc = pyautogui.locateOnScreen(fname,grayscale=False)  # this statement enable
   proceed2=1
  if(resp=='Cancel'):
   proceed2=0
 else: proceed2=1
 #print "Pro2 = ",proceed2
 
 # select the option/equity based on fname (i.e. png)
 if(proceed2==1 and proceed==1):
   # find symbol to trade
   x0,y0 = pyautogui.center(ploc)
   pyautogui.moveTo(x0,y0)
   pyautogui.click(x0,y0) # place order
   
   # (BUY : bs = 1 ) (SELL : bs = 0 )
   if (bs==1): pyautogui.press('f1')
   if (bs==0): pyautogui.press('f2')
   
   # enter qty and price
   if(otype==1): # options
    xqty = str(lot_size)
    pyautogui.typewrite(xqty) # qty
    pyautogui.press('tab')
    xprice = str(bsprice)
    pyautogui.typewrite(xprice) # price
    pyautogui.press('enter') # submit and enter
    pyautogui.press('enter')   
   if(otype==2): # equity
    xqty = str(lot_size)
    pyautogui.typewrite(xqty) # qty
    pyautogui.press('tab')
    xprice = str(bsprice)
    pyautogui.typewrite(xprice) # price
    pyautogui.press('tab')
    pyautogui.press('tab')
    pyautogui.press('down') #MIS
    pyautogui.press('tab')
    pyautogui.press('down')  # IOC
    pyautogui.press('enter') # submit and enter
    pyautogui.press('enter')   
   
   status = 1 # status = 1 (success)
 else:
   status = 0 # status = 0 (failed) 
 
 # (BUY : bs = 1 ) (SELL : bs = 0 )
 if (bs==1 and status ==1): stat = 1
 else: stat = 0
 if (bs==0 and status ==1): stat = 0 
 else: stat = 1
 return stat

 
# unit ts to datetime (use for display only)
def ts_conv(ts_date):
  datetime_tick = datetime.datetime.fromtimestamp(int(ts_date)).strftime('%Y-%m-%d %H:%M:%S')
  return datetime_tick

def print_tick(tdata):
 for i in range(0, classes.symbol.ntick):
  for j in range(0,classes.symbol.maxtick):
   print '[ Symbol = ',i, "Datapt. = ",j,']', tdata[i].ticktime[j], tdata[i].ltp[j], tdata[i].vol[j]
  print "----------"
 return

def xl_persist(xwb, xstr):
 val = Range(xstr).value
 while(Range(xstr).value < 0):
  val = Range(xstr).value
 return val
 
def nest_fetcher(symbols, xwb):
 idata = np.zeros((classes.symbol.ntick,6)) # current tick data 
 
 # get data 
 for i in range(0, classes.symbol.ntick):
  if(i<=2):
   xstr3 = 'A'+ str(i+1)
   idata[i][0] = time.time()
   idata[i][1] = Range(xstr3).value #xl_persist(xwb, xstr3)
   idata[i][2] = 0.0
   idata[i][3] = 0.0
   idata[i][4] = 0.0
   idata[i][5] = 0.0
   if(str(idata[i][1]).replace('.','').isdigit() is False):
    print idata[i][1]
    pyautogui.confirm(text='NO VALID DATA FROM EXCEL: INDEX', title='', buttons=['OK', 'Cancel'])
    sys.exit(0)
   if(idata[i][1] <0 ):
    pyautogui.confirm(text='NO VALID DATA FROM EXCEL: INDEX (129)', title='', buttons=['OK', 'Cancel'])
    sys.exit(0) 	
    
  if(i>2):
   xstr3 = chr(67+(i-3))
   idata[i][0] = time.time()
   idata[i][1] = Range(xstr3+str(1)).value
   idata[i][2] = Range(xstr3+str(2)).value
   idata[i][3] = Range(xstr3+str(3)).value
   idata[i][4] = Range(xstr3+str(4)).value
   if(str(idata[i][1]).replace('.','').isdigit() is False or str(idata[i][2]).replace('.','').isdigit() is False or str(idata[i][3]).replace('.','').isdigit() is False):
    pyautogui.confirm(text='NO VALID DATA FROM EXCEL: OPTION', title='', buttons=['OK', 'Cancel'])
    sys.exit(0)   
   if(str(idata[i][4]).replace('.','').isdigit() is False or str(idata[i][5]).replace('.','').isdigit() is False):
    pyautogui.confirm(text='NO VALID DATA FROM EXCEL: OPTION', title='', buttons=['OK', 'Cancel'])
    sys.exit(0)   
 
   if(idata[i][1] <0 or idata[i][2] <0 or idata[i][3] <0):
    pyautogui.confirm(text='NO VALID DATA FROM EXCEL: OPTION', title='', buttons=['OK', 'Cancel'])
    sys.exit(0)   
   if(idata[i][4] <0 or idata[i][5] <0):
    pyautogui.confirm(text='NO VALID DATA FROM EXCEL: OPTION', title='', buttons=['OK', 'Cancel'])
    sys.exit(0)   

 return idata

# insert the current tick into total data
#def insert_tick_old(tdata, idata): # 0 element in array is last updated
# for i in range(0, classes.symbol.ntick):
#  tdata[i].ticktime = np.roll(tdata[i].ticktime,1)
#  tdata[i].ltp = np.roll(tdata[i].ltp,1)
#  tdata[i].vol = np.roll(tdata[i].vol,1)
# 
#  tdata[i].ticktime[0]=idata[i][0]
#  tdata[i].ltp[0]=idata[i][1]
#  tdata[i].vol[0]=idata[i][2]
# return
 
# insert the current tick into total data
def insert_tick(tdata, idata):  # Last element in array is last updated
 for i in range(0, classes.symbol.ntick):
  tdata[i].ticktime = np.roll(tdata[i].ticktime,-1)
  tdata[i].ltp = np.roll(tdata[i].ltp,-1)
  tdata[i].vol = np.roll(tdata[i].vol,-1)
  tdata[i].bp = np.roll(tdata[i].bp,-1)
  tdata[i].ap = np.roll(tdata[i].ap,-1)
 
  tdata[i].ticktime[classes.symbol.maxtick-1]=idata[i][0]
  tdata[i].ltp[classes.symbol.maxtick-1]=idata[i][1]
  tdata[i].vol[classes.symbol.maxtick-1]=idata[i][2]
  tdata[i].bp[classes.symbol.maxtick-1]=idata[i][3]
  tdata[i].ap[classes.symbol.maxtick-1]=idata[i][4]
 return 

# set working directory - get previous working date
def set_workdir():
  dayy = datetime.date.today() # myday
  #print dayy
  dayx = dayy
  if(dayy.weekday() == 0): # if monday then friday
    dayx -= timedelta(days=3)
  elif(dayy.weekday() == 5): # if saturday then friday
    dayx -= timedelta(days=1)
  elif(dayy.weekday() == 6): # if sunday then friday
    dayx -= timedelta(days=2)
  else: # if not monday then yesterday
    dayx -= timedelta(days=1)
  
  tmp = str(dayx).replace('-','')[2:]
  tmp1 = str(tmp[0:2])
  tmp2 = str(tmp[2:4])
  tmp3 = str(tmp[4:6])
  myday = tmp3+"-"+tmp2+"-"+tmp1
  classes.symbol.work_dir = myday
  
  # dump data and day analysis
  work_dir = myday
  if not os.path.exists(work_dir): os.makedirs(work_dir)
  print 'Working Directory = ',work_dir
  return

# previous close function
def pclose_topen(name, xchange):
 base_url = "http://www.google.com/finance/getprices?q="+name+"&x="+xchange+"&i=0&p=2d"
 response=urllib.urlopen(base_url).readlines()
 print response
 j=0
 p_close = 0.0
 for row in reversed(response):
  # todays open
  #if j==0:
   #gt=row.split(',')
   #print j, gt
   #topen=float(gt[4])	  
   #j=j+1
  # yesterdays close
  if j==0:
   gt=row.split(',')
   #print j, row, gt
   p_close=float(gt[1])
  j=j+1
 return p_close

  
# init everything
def reader():
 fname = r"D:\stock_market\My_Algo_Code\Live_trading\input.txt"
 tfile = open(fname,"r")
 
 i=0
 nt = 0
 symbols = []
 for line in tfile.readlines():
  i=i+1
  print line
  if (line[0]!='#' and len(line)>5): # not comment line and non-empty line
    print i, line[0], line
    nt = nt + 1
    print nt
    xstr = line.split(',')
    
    # TYPE(index-0, option-1, equity-2)
    # Reference name (No spaces)
    # Trading symbol (in quotes)
    # LotQty/No. of shares (0 for  default)
    # strategy type (unused- can be for specifiying strategy)
    xstr2 = xstr[2].split(chr(34))
    tname = xstr2[1]
    rname = xstr[1]
    type = int(xstr[0])
    strategy = int(xstr[4])
    status = 0
    bprice = 0
    sprice = 0
    bd = 0
    stop_loss=0
    perc = 0
    btime = 0
    stime = 0
    nsells = 0
    nbuys = 0
    investment = 0
    lot_size = int(xstr[3]) 
    optype = int(xstr[5])
    stkprice = int(xstr[6])
    if(lot_size==0): lot_size  =  classes.symbol.lot_size
    symbols.append(classes.symbol(tname,  rname,  type,  strategy,  status,  bprice,  sprice,  bd, stop_loss, perc,  btime,  stime,\
                                        nsells,  nbuys,  investment,  lot_size, optype, stkprice))
  
 classes.symbol.ntick = nt
 set_workdir()
 print "No. of symbols = ", nt
 print "---------------------------------"
 for i in range(0,classes.symbol.ntick):
  print symbols[i].tname, symbols[i].rname, symbols[i].type  
 print "---------------------------------"
 
 # init tick data
 tdata=[]
 for i in range(0, classes.symbol.ntick): tdata.append(classes.tickdata())
 print "Max ticks = ", classes.symbol.maxtick, " NSymbols = ",classes.symbol.ntick
 #idata = np.random.randint(10, size=(classes.symbol.ntick,7)) # current tick data 
 
 # open xls
 ifile = r'D:\stock_market\My_Algo_Code\Live_trading\tmp_2.xls'
 print "xl file = ", ifile
 wb = Workbook(ifile)  # Creates a connection with a new workbook 
 pclose = np.zeros(classes.symbol.ntick,'f')
 
 #names of the indexes
 xstr1 = []
 xstr1.append("NIFTY")
 xstr1.append("NSE")
 
 xstr1.append("SENSEX")
 xstr1.append("INDEXBOM")

 xstr1.append("BANKNIFTY")
 xstr1.append("NSE")
 
 #print xstr1
 
 # get previous close of all symbols
 rtd_str = "=RTD("+chr(34)+"Nest.ScripRTD"+chr(34)+",,"+chr(34)+"XXX"+chr(34)+","+chr(34)+"YYY"+chr(34)+")"
 for i in range(0,classes.symbol.ntick):
  #indexes
  if (i<=2):
   pclose[i] = pclose_topen(xstr1[2*i],xstr1[2*i+1])
   
  # options
  if (i>2):
   xstr = 'A'+ str(i+10)
   xrtd = rtd_str.replace('XXX',symbols[i].tname).replace('YYY','Prev Close')
   #print xrtd
   Range(xstr).value = xrtd
   pclose[i] = Range(xstr).value
 
 print "Pclose = ",pclose
 
 
 # fill excel sheet with neccesary commands for logging data
 for i in range(0,classes.symbol.ntick):
  #indexes
  if (i<=2):
   xstr3 = 'A'+ str(i+1)
   print i, xstr3, symbols[i].tname
   xrtd = rtd_str.replace('XXX',symbols[i].tname).replace('YYY','Index Value')
   Range(xstr3).value = xrtd
  #options
  if (i>2):
   xstr3 = chr(67+(i-3))
   print i, symbols[i].tname, xstr3+str(1), xstr3+str(2) #, xstr3+str(3), xstr3+str(4), xstr3+str(5)
   Range(xstr3+str(1)).value = rtd_str.replace('XXX',symbols[i].tname).replace('YYY','LTP')
   Range(xstr3+str(2)).value = rtd_str.replace('XXX',symbols[i].tname).replace('YYY','Volume Traded Today')
   Range(xstr3+str(3)).value = rtd_str.replace('XXX',symbols[i].tname).replace('YYY','Bid Rate')
   Range(xstr3+str(4)).value = rtd_str.replace('XXX',symbols[i].tname).replace('YYY','Ask Rate')
   
   #Range(xstr3+str(3)).value = rtd_str.replace('XXX',symbols[i].tname).replace('YYY','Open')
   #Range(xstr3+str(4)).value = rtd_str.replace('XXX',symbols[i].tname).replace('YYY','High')
   #Range(xstr3+str(5)).value = rtd_str.replace('XXX',symbols[i].tname).replace('YYY','Low ')
   
 
 return symbols, tdata, wb, pclose
 
 
 
