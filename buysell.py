import classes, util
import numpy as np
import time, os,talib
import mibian
os.environ['TZ'] = 'Asia/Kolkata'

def buyorder(symbol, idata,logger):
 if (symbol.status == 0): # if only is not bought
  xstr = symbol.tname.replace(chr(124),chr(34)).split(chr(34))
  tsym = xstr[1]+".png"#r"D:\stock_market\My_Algo_Code\Live_trading\NIFTY15JUL8700CE.png" #
  bprice = round(idata.bp[classes.symbol.maxtick-1],2)
  symbol.bprice = bprice
  symbol.btime = time.time()
  #(BUY : bs = 1 ) (SELL : bs = 0 )
  symbol.status = util.eluka(symbol.type, tsym, symbol.lot_size, bprice, 1)
  #(symbol.status = 1 in a trade)
  #if (symbol.status==1): util.update_ledger(symbol)
  logger.info("BOUGHT :: "+symbol.tname+ ' at '+ str(bprice))
  localtime = time.localtime(time.time())
  #bprice = round(idata.ltp[classes.symbol.maxtick-1],2) # Assigning bprice for sell order to be max
  print "Bought ", symbol.tname, ' at ', bprice, str(localtime.tm_hour)+':'+str(localtime.tm_min)+':'+str(localtime.tm_sec)
 return
 
def sellorder(symbol, idata,logger):
 if (symbol.status == 1): # if only bought
  xstr = symbol.tname.replace(chr(124),chr(34)).split(chr(34))
  tsym = xstr[1]+".png"
  sprice = round(idata.ap[classes.symbol.maxtick-1],2)
  symbol.sprice = sprice
  symbol.stime = time.time()
  #(BUY : bs = 1 ) (SELL : bs = 0 )
  symbol.status = util.eluka(symbol.type, tsym, symbol.lot_size, sprice, 0)
  #(symbol.status = 0 out of a trade)
  #if (symbol.status==0): util.update_ledger(symbol)
 
  logger.info("SOLD :: "+symbol.tname+ ' at '+ str(sprice)+ 'Perc = '+str( (symbol.sprice-symbol.bprice)*100/symbol.bprice) )
  localtime = time.localtime(time.time())
  print "Sold ", symbol.tname, ' at ', sprice, 'Perc = ',(symbol.sprice-symbol.bprice)*100/symbol.bprice,str(localtime.tm_hour)+':'+str(localtime.tm_min)+':'+str(localtime.tm_sec)
 return

#-----------------------------------------------------------------------
def hhv(period,tdata):
 latest=classes.symbol.maxtick-1
 #print tdata
 x=np.max(tdata[(latest-period):latest])
 if x==tdata[latest]:hhv_sig=1
 else: hhv_sig=0
 return hhv_sig
 
def llv(period,tdata):
 latest=classes.symbol.maxtick-1
 x=np.min(tdata[(latest-period):latest])
 if x==tdata[latest]:llv_sig=1
 else: llv_sig=0
 return llv_sig
 

#------------------------------------------------------------
def analysis(symbols, pclose, tdata, logger):
 localtime = time.localtime(time.time())
 #print str(localtime.tm_hour)+':'+str(localtime.tm_min)+':'+str(localtime.tm_sec)
 logger.info("WAITING")
 #print classes.symbol.ntick
 

 for i in range (3,classes.symbol.ntick):
  Bk_strategy(pclose[i], tdata[i],symbols[i], logger, tdata[0],symbols[0])
 
 #buyorder(symbols[3], tdata[3], logger)
 #strategy_1m(pclose[4], tdata[4],symbols[4], logger)
 return
#-----------------------------------------------------------------------
#--------------        STRATEGIES     ----------------------------------
#-----------------------------------------------------------------------
def strategy_1(pclose, tdata, symbol, logger):
 latest=classes.symbol.maxtick-1
 # BUY strategy
 if (symbol.status == 0): # if not bought earlier 
  if(tdata.ltp[latest] > tdata.ltp[latest-1] > tdata.ltp[latest-2]): trend = 1
  else: trend = 0 
  if(trend):buyorder(symbol, tdata, logger)
  else:
    logger.info("BUY waiting :-(")
   
 # SELL strategy
 if (symbol.status == 1 and tdata.ltp[latest] >= symbol.bprice*classes.symbol.target_profit): # if only bought
  sellorder(symbol, tdata, logger)
 if (symbol.status == 1 and tdata.ltp[latest] <= symbol.bprice*classes.symbol.stop_loss): # if only bought
  sellorder(symbol, tdata, logger)
 return
 
 
def ST_macd_hhvllv(pclose, tdata, symbol, logger, tdata_n, symbol_n):
  
 float_data = [float(x) for x in tdata.ltp]
 tdata.ltp = np.array(float_data)
 float_data = [float(x) for x in tdata_n.ltp]
 tdata_n.ltp = np.array(float_data)
  
 latest=classes.symbol.maxtick-1
 # Analysis of the NIFTY data 
 upordown_n = talib.EMA(tdata_n.ltp, 5)
 # Analysis of the symbol data 
 macd, macdsignal, macdhist = talib.MACD(tdata.ltp, fastperiod=13, slowperiod=14, signalperiod=3)
 upordown = talib.EMA(tdata.ltp, 5)
 #print round(tdata.ltp[latest],2), round(tdata_n.ltp[latest],2), round(upordown[latest],2), round(upordown_n[latest],2)
 # CALL  
 
 # BUY strategy -------------#and \  (upordown_n[latest]>upordown_n[latest-1]
 if (symbol.status == 0): # if not bought earlier 
  if((upordown_n[latest]>upordown_n[latest-1])): trend = 1
  else: trend = 0 
  
  if(trend==1): buyorder(symbol, tdata, logger) # print "BUY - %.2f",(tdata.bp[latest]-0.1)
  else: pass #logger.info("BUY waiting")
   
 # SELL PROFIT strategy
 if (symbol.status == 1 and tdata.ltp[latest] >= symbol.bprice*classes.symbol.target_profit): # if only bought
  symbol.bprice=tdata.ltp[latest]
  classes.symbol.stop_loss=0.9975
  
  #sellorder(symbol, tdata, logger)
  #print "SOLD PROFIT- %.2f", tdata.ltp[latest]
 
 # SELL STOP LOSS strategy 
 if (symbol.status == 1 and (tdata.ltp[latest] <= symbol.bprice*classes.symbol.stop_loss)): # if only bought (upordown_n[latest]<upordown_n[latest-1])
  sellorder(symbol, tdata, logger)
  classes.symbol.stop_loss=0.99
 #print "SOLD SL - %.2f", tdata.ltp[latest]
  
 return
 
 
 
 
def Bk_strategy(pclose, tdata, symbol, logger, tdata_n, symbol_n):
  
 float_data = [float(x) for x in tdata.ltp]
 tdata.ltp = np.array(float_data)
 float_data = [float(x) for x in tdata_n.ltp]
 tdata_n.ltp = np.array(float_data)
 
 latest=classes.symbol.maxtick-1
 upordown_n = talib.EMA(tdata_n.ltp, 5) # Nifty EMA 
 upordown_ltp = talib.EMA(tdata.ltp, 5)   # Symbol EMA
 rsiv=talib.RSI(tdata.ltp, 14)
 tanv = talib.TAN(tdata.ltp)
 rocv = talib.ROC(tdata.ltp,5)
 hhvv=hhv(2,tdata.ltp)
 llvv=hhv(2,tdata.ltp)
 #------------Garman-Kohlhagen Model for premium prie-----------
 #if symbol.optype!=0:
  #GK([underlyingPrice, strikePrice, domesticRate, foreignRate,
  # daysToExpiration], volatility=x, callPrice=y, putPrice=z)
  #c = mibian.GK([tdata_n.ltp[latest], self.stkprice, 8, 0, 10], volatility=20)
  #if symbol.optype==1: print c.callPrice
  #if symbol.optype==2: print c.putPrice
 

 # -----------Strategy Removed

 # -------------------------BUY strategy-------------------------
 if (symbol.status == 0 and swingv==120):
  trend=0
  if hhvv==1:trend += 1
  if(trend>=1): 
   print "  BUY - %.2f, Investment - %.2f"%(tdata.ltp[latest],(symbol.lot_size*tdata.ltp[latest]))
   #buyorder(symbol, tdata, logger)
   symbol.bprice=tdata.ltp[latest]
   symbol.bd=120
   symbol.status = 1
 #---------------flat---------------------------------
 if (symbol.status == 0 and swingv==110):
  trend=0
  if rsiv[latest]<30:trend += 1	 
  if(trend>=1): 
   print "  BUY - %.2f, Investment - %.2f"%(tdata.ltp[latest],(symbol.lot_size*tdata.ltp[latest]))
   #buyorder(symbol, tdata, logger)
   symbol.bprice=tdata.ltp[latest]
   symbol.bd=110
   symbol.status = 1
 #---------------Remaining trend minus downtrend---------------------------------
 if (symbol.status == 0 and (swingv==110 or swingv==120)):
  trend=0
  if tanv[latest]<0:trend += 1
  if (upordown_ltp[latest]>upordown_ltp[latest-1]):trend += 1
  if rocv[latest]<0:trend += 1	 
  if(trend>=3): 
   print "  BUY - %.2f, Investment - %.2f"%(tdata.ltp[latest],(symbol.lot_size*tdata.ltp[latest]))
   #buyorder(symbol, tdata, logger)
   symbol.bprice=tdata.ltp[latest]
   symbol.bd=110
   symbol.status = 1
 
# ------------------------ SELL -----------------------------------------   
 #------------------------  Trailing Stop Loss --------------------------- 
 # SELL trailing for uptrend buy strategy
 if (symbol.status == 1 and symbol.bd==120 and \
 ((tdata.ltp[latest] > symbol.bprice*classes.symbol.target_profit))): # if only bought
  symbol.bprice=tdata.ltp[latest]
  symbol.stop_loss=0.995


 # SELL trailing for flatrend buy strategy
 if (symbol.status == 1 and symbol.bd==110 and \
 ((tdata.ltp[latest] > symbol.bprice*classes.symbol.target_profit))): # if only bought
  #sellorder(symbol, tdata, logger)
  print "  SELL - %.2f"%(tdata.ltp[latest])
  #symbol.stop_loss=classes.symbol.stop_loss
  symbol.status = 0
 
 # SELL STOP LOSS strategy 
 if (symbol.status == 1 and ((tdata.ltp[latest] < symbol.bprice*classes.symbol.stop_loss) or \
 (tdata.ltp[latest] < symbol.bprice*symbol.stop_loss))):# or swingv==100)): # if only bought (upordown_n[latest]<upordown_n[latest-1])
  #sellorder(symbol, tdata, logger)
  print "  SELL - %.2f"%(tdata.ltp[latest])
  #symbol.stop_loss=classes.symbol.stop_loss
  symbol.status = 0
  
 return
 

 
 
