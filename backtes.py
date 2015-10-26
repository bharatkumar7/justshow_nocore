'''# -*- coding: utf-8 -*-           If you are just trying to use UTF-8 characters or don't care if they are in your code, add this line''' 
import numpy as np
import time,os,talib
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick, candlestick2
from matplotlib import gridspec,colors
from math import pi
import funct
import mibian
import pandas as pd
from pandas import *

#import matplotlib.dates as mdates



stock_data=1  # 1 - Streamline data, 2 - OHLC data
tickskip=1 #1 denotes every tick
colm=0

for k in range(0,10):
	if k==0:fname="1sec_close.txt"
	if k==1:fname="NIFTY_AUG_8700C.txt"
	
	status = 0
	AccountSize=100000
	maxtick=40
	target_profit=1.02  #Risk to Reward ratio 3:1
	stop_loss=0.97 #stop loss when entering a position
	tpf=target_profit
	tsl=stop_loss
	graph=0#1 - Yes, 0 - None
	tick_analysis_display=0 #1 - Yes , 0 - No
	pruy=0
	file_format=3 # 1- OHLC format, 2 - Live ticker format(Time OHLC), 3 - Live ticker format(Range OHLC)
	initcap=AccountSize
	
	
	#----------------------- File reader ------------------------------------------------------------------------------------------------------
	if file_format==1:
	 tedhi,price_open,price_high,price_low,price_close, vol=(np.loadtxt(fname, dtype=float, delimiter=',', usecols=(1,3,4,5,6,7), skiprows=1,unpack=True))
	 numb=len(price_open)
	 xoi=np.min(price_low)
	 yoi=np.max(price_high)
	 xoi=xoi-(xoi*0.05)
	 yoi=yoi+(yoi*0.05)
	 
	elif file_format==2:
	 tedhi,dummy=(np.loadtxt(fname, dtype=str, delimiter=',', usecols=(0,1),skiprows=1,unpack=True))
	 cl_price, vol=(np.loadtxt(fname, dtype=float, delimiter=',', usecols=(1,2), skiprows=1,unpack=True))
	 #---------------------- DataFrame using pandas  as pd--------------------------------------------------------------------
	 d={'Datetime': Series(to_datetime(tedhi)),
	       'price': Series((cl_price)),
	       'volume':Series((vol))}
	 df=DataFrame(d)
	
	 #print price
	 df.set_index('Datetime', inplace=True)
	 vol_sum = (df['volume'].resample('30s', how='sum',fill_method='backfill',limit=0)).dropna(how='any', axis=0)
	 price_ohlc = (df['price'].resample('30s', how='ohlc',fill_method='backfill',limit=0)).dropna(how='any', axis=0)
	 #print pd.concat([vol_sum, price_ohlc], 1, keys=['volume', 'price'])

	 #print price_ohlc.open.isnull().sum()
	 #print price_ohlc.dropna(thresh=None, how='any', axis=0)
	 numb=len(price_ohlc)
	 xoi=np.min(price_ohlc.low)
	 yoi=np.max(price_ohlc.high)
	 xoi=xoi-(xoi*0.05)
	 yoi=yoi+(yoi*0.05)
	 
	 
	elif file_format==3:
	 cl_price, vol=(np.loadtxt(fname, dtype=float, delimiter=',', usecols=(1,2), skiprows=1,unpack=True))
	 if cl_price[0]<=25:rangeper=0.03  #constant range percent "0.01" represents 1%
	 elif cl_price[0]<=50:rangeper=0.02  
	 else: rangeper=0.01  
	 price_open,price_high,price_low,price_close=funct.range_bar(cl_price,vol,rangeper)
	 numb=len(price_close)
	 #print numb
	 #for i in range(0,numb):
	  #print price_open[i],price_high[i],price_low[i],price_close[i]
	 #print "Back to Main"
	 xoi=np.min(price_low)
	 yoi=np.max(price_high)
	 xoi=xoi-(xoi*0.05)
	 yoi=yoi+(yoi*0.05) 
	 
	#----------------------- END OF FILE READER ------------------------------------------------------------------------------------------------------
	

	buy=np.full(numb-maxtick,-10)  #full  fills all the array with the defned number "-10" this case
	bstime=np.arange(0,numb-maxtick)  #arange puts all real numbers in order 1,2,3
	sell=np.full(numb-maxtick,-10)
	short=np.full(numb-maxtick,-10)
	cover=np.full(numb-maxtick,-10)
	alltrades=np.zeros(numb-maxtick)
	PLP=np.zeros(numb-maxtick)

	# ---------------------- Analysis -----------------------------------
	for i in range(0,numb-maxtick):      
	 bstime[i]=i-1+maxtick
	 
	 if file_format==1 or file_format==3:
	  for j in range(i,maxtick+i):
	   tdata_ltp[j-i]=price_close[j]
	   tdata_vol[j-i]=vol[j]
	   tdata_op[j-i]=price_open[j]
	   tdata_hi[j-i]=price_high[j]
	   tdata_lo[j-i]=price_low[j]
	   
	 #time.sleep(2)
	 if file_format==2:
	  for j in range(i,maxtick+i):
	   tdata_ltp[j-i]=price_ohlc.close[j]
	   tdata_vol[j-i]=vol_sum[j]
	   tdata_op[j-i]=price_ohlc.open[j]
	   tdata_hi[j-i]=price_ohlc.high[j]
	   tdata_lo[j-i]=price_ohlc.low[j]
	 
	 # --------------------Technical Indicators Calclations---------------------------------

	 upordown_ltp = talib.EMA(tdata_ltp,5)
	 upordown_ltpl = talib.EMA(tdata_ltp,15)
	 upordown_ltplong = talib.EMA(upordown_ltpl,10)
	 kmav = talib.KAMA(tdata_ltp,10)
	 upordown_kmav = talib.EMA(kmav,10)
	 atrv = talib.ATR(tdata_hi, tdata_lo, tdata_ltp,timeperiod=14)
	 adxv=talib.ADX(tdata_hi, tdata_lo, tdata_ltp, timeperiod=14)

	 hhv=np.max(tdata_hi[maxtick-14:maxtick-1])
	 llv=np.min(tdata_lo[maxtick-14:maxtick-1])
	 latest=maxtick-1
	 
	 #--------------------- Black-Scholes Model for Option pricing------------------------
	 BS([underlyingPrice, strikePrice, interestRate, daysToExpiration], volatility=x, callPrice=y, putPrice=z)
	 c = mibian.BS([tdata_ltp_nifty[latest], 8800,8, 5], callPrice=tdata_ltp[latest])
	 c.impliedVolatility
	 c = mibian.BS([tdata_ltp_nifty[latest], 8700,8, 5], volatility=30)
	 c.callPrice
	 print round(c.impliedVolatility,2)
	# -------------------------Trend Detection---------------------------------------
	# Code removed
		#------------------------------------------------------------------------------
	 
	 if (kmav[latest]>1.001*kmav[latest-1]>1.001*kmav[latest-2]>1.001*kmav[latest-3]) or \
	 (kmav[latest]<0.999*kmav[latest-1]<0.999*kmav[latest-2]<0.999*kmav[latest-3]):flatornot[latest]=kmav[latest]
	 else: flatornot[latest]=0

	 Uvolt=(hhv-(3.5*atrv[latest]))
	 Dvolt=(llv+(3.5*atrv[latest]))	 
	 #---- FOR PLOT -----------
	 if graph==1:
	  tech_one[i]= Uvolt 
	  tech_two[i]=Dvolt
	  tech_three[i]=flatornot[latest]

	 # ------------------------ ENTRY --------------------------------------
	 #-------------------Uptrend ------------------------------  
	 '''if (status == 0 and tdata_hi[latest]<tdata_hi[latest-1]) and \
	 (status == 0 and tdata_hi[latest]<tdata_hi[latest-2]) and \
	 (status == 0 and tdata_hi[latest]<tdata_hi[latest-3]) and \
	 (status == 0 and upordown_ltplong[latest]>upordown_ltplong[latest-1]) :'''
 	 if (status == 0 and '') #Strategy removed
	  
	  trend=0
	  if flatornot[latest]>0: trend=1
	  if(trend>=1):
	   status=1
	   lot_size,StopPrice=funct.PositionSizing_Method(status,AccountSize,stop_loss,tdata_ltp[latest],atrv[latest],Uvolt,Dvolt,alltrades,PL,i)
	   leftamt=AccountSize-(tdata_ltp[latest]*lot_size)
	   if (tick_analysis_display==1):print "  BUY - %.2f, Investment - %.2f, Lots - %.2f, Accountsize - %.2f, StopPrice - %.2f"%(tdata_ltp[latest],(lot_size*tdata_ltp[latest]),lot_size,AccountSize,StopPrice)
	   bprice=tdata_ltp[latest]
	   if graph==1:buy[i]=bprice
	   tprice=bprice


	 #-------------------Down trend (short cover strategy)------------------------------  
 	 if (status == 0 and 'strategy removed'):
	  
	  trend=0
	  if flatornot[latest]>0: trend=1
	  if(trend>=1):
	   status=2
	   lot_size,StopPrice=funct.PositionSizing_Method(status,AccountSize,stop_loss,tdata_ltp[latest],atrv[latest],Uvolt,Dvolt,alltrades,PL,i)
	   leftamt=AccountSize-(tdata_ltp[latest]*lot_size)
	   if (tick_analysis_display==1):print "  Short - %.2f, Investment - %.2f, Lots - %.2f, Accountsize - %.2f, StopPrice - %.2f"%(tdata_ltp[latest],(lot_size*tdata_ltp[latest]),lot_size,AccountSize,StopPrice)
	   stprice=tdata_ltp[latest]
	   if graph==1:short[i]=stprice
	   tprice=stprice
	   
	   
	   # ------------------------ EXIT STRATEGY -----------------------------------------   
	 #------------------------  Trailing Stop Loss --------------------------- 
	# SELL trailing for uptrend buy strategy
	 '''if (status == 1 and ((tdata_ltp[latest] >= bprice*target_profit))): # if only bought
	  bprice=tdata_ltp[latest]
	  target_profit=1.0025
	  stop_loss=0.9975'''
	 #if (status == 1 and tick_analysis_display==1): print "%d, cl_price - %.2f, PF %.2f >= %.2f,  SL %.2f <= %.2f"%(i+maxtick,tdata_ltp[latest],tdata_ltp[latest],(bprice*target_profit),tdata_ltp[latest],(bprice*stop_loss))
	 if (status == 1 and tick_analysis_display==1): print "%d, LTP - %.2f,  StopPrice - %.2f, Uvolt- %.2f"%(i+maxtick,tdata_ltp[latest],StopPrice,Uvolt)
	  # --------------------------SELL STRATEGY -------------------------------------------------------- 
	 if (status == 1 and  'strategy removed'): #or \
	 #(status == 1 and tdata_ltp[latest] >= tprice*target_profit) :	  

	  bk_amt=((tprice+tdata_ltp[latest])*lot_size)
	  broker=(bk_amt*90/100000) # 16.69 for equities. 90 for option
	  PL[i]=(lot_size*(tdata_ltp[latest]-tprice))-broker
	  PLP[i]=(PL[i]*100/(tprice*lot_size))
	  fp=fp+PLP[i]
	  pot=pot+PL[i]
	  trade=trade+1
	  if PLP[i]>0.0: alltrades[i]=1
	  elif PLP[i]<0.0:alltrades[i]=-1
	  else:pass
	  if graph==1:sell[i]=tdata_ltp[latest]
	  if (tick_analysis_display==1):print "  SELL - %.2f, Percentage  %.2f"%(tdata_ltp[latest],PLP[i])
	  if (tick_analysis_display==1):print "-------------------------------"
	  stop_loss=tsl
	  target_profit=tpf
	  AccountSize=leftamt+PL[i]+(tprice*lot_size)
	  AS[i]=AccountSize
	  status=0 

	#----------------------------------------------	 
	 # Cover trailing for downtrend
	 '''if (status == 2 and ((tdata_ltp[latest]*target_profit <= stprice))): # if only bought
	  stprice=tdata_ltp[latest]
	  target_profit=1.0025
	  stop_loss=0.9975'''
	 #if (status == 2 and tick_analysis_display==1):print "%d, cl_price - %.2f, PF %.2f <= %.2f,  SL %.2f >= %.2f"%(i+maxtick,tdata_ltp[latest],(tdata_ltp[latest]*target_profit),stprice,(tdata_ltp[latest]*stop_loss),stprice)
	 if (status == 2 and tick_analysis_display==1): print "%d, LTP - %.2f,  StopPrice - %.2f,Dvolt- %.2f"%(i+maxtick,tdata_ltp[latest],StopPrice,Dvolt)

	# -----------------COVER strategy  ---------------------------------------
	 if (status == 2 and 'strategy removed'):

	  bk_amt=((tprice+tdata_ltp[latest])*lot_size)
	  broker=(bk_amt*90/100000)  # 16.69 for equities. 90 for option
	  PL[i]=-((lot_size*(tdata_ltp[latest]-tprice))+broker)
	  PLP[i]=(PL[i]*100/(tprice*lot_size))
	  fp=fp+PLP[i]
	  pot=pot+PL[i]
	  trade=trade+1
	  if PLP[i]>0.0: alltrades[i]=1
	  elif PLP[i]<0.0:alltrades[i]=-1
	  else:pass
	  if graph==1:cover[i]=tdata_ltp[latest]
	  if (tick_analysis_display==1):print "  Cover - %.2f, Percentage  %.2f"%(tdata_ltp[latest],PLP[i])
	  if (tick_analysis_display==1):print "-------------------------------"
	  stop_loss=tsl
	  target_profit=tpf
	  AccountSize=leftamt+PL[i]+(tprice*lot_size)
	  AS[i]=AccountSize
	  status=0
	 
	 if AS[i]==0:AS[i]=AccountSize

	kfp=kfp+fp
	kpot=kpot+pot
	ktrades=ktrades+trade	
	#print "-------------------------------"
	print "  %d. Final Amt =  %.2f, Trades = %d"%(k+1, kpot,ktrades)
	#---------------Expectancy ---------------------------
	funct.Expectancy(alltrades,PLP,PL,numb-maxtick)
	
#------------- PLOTS ----------------------------------------
	if graph==1:
	#---------------- CANDLE STICK PLOTS ----------------------------------------------------------------------------
	 quotes=np.zeros((numb-1,5))
	 for i in range(0,numb-1):
	  if file_format==1 or file_format==3:quotes[i]=(minute[i],price_open[i],price_close[i],price_high[i],price_low[i])	  
	  if file_format==2:quotes[i]=(minute[i],price_ohlc.open[i],price_ohlc.close[i],price_ohlc.high[i],price_ohlc.low[i])	  
	  
	 #axes = plt.gca()
	 #axes.set_xlim([0,numb])
	 #axes.set_ylim([xoi,yoi])
	 fig, ax1 = plt.subplots()
	 ax2 = ax1.twinx()
	 ax1.set_xlim([0,numb])
	 ax2.set_xlim([0,numb])
	 ax1.set_ylim([xoi,yoi])
	 ax2.set_ylim([xoi,yoi])
	 candlestick(ax1,quotes,width=0.6, colorup=u'g', colordown=u'r', alpha=1.0)
	 #ax2.plot(minute,price_ohlc.close,'gray',bstime,buy,'ko', marker=r'$\downarrow$', markersize=20,bstime,sell,'ro',bstime,short,'r*',bstime,cover,'g*')
	 ax2.plot(bstime,buy-1,'go', marker=r'$\Uparrow$', markersize=8)
	 ax2.plot(bstime,sell+1,'ro', marker=r'$\Downarrow$', markersize=8)
	 ax2.plot(bstime,short+1,'ro', marker=r'$\blacktriangledown$', markersize=8)
	 ax2.plot(bstime,cover-1,'go', marker=r'$\blacktriangle$', markersize=8)
	 ax2.plot(bstime,tech_one,'blue',bstime,tech_two,'orange')
	 plt.grid(b=True, which='major', color='grey', linestyle='--')
	 plt.show()
	 #---------------------------------------- NORMAL LINE PLOTS ----------------------------------------------------
	 plt.figure(1)
	 gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1]) 
	 ax1=plt.subplot(gs[0])
	 axes = plt.gca()
	 axes.set_xlim([0,numb])
	 axes.set_ylim([xoi,yoi])
	 #figure,ax1 = plt.subplots()
	 ax2 = ax1.twinx()
	 if file_format==1 or file_format==3:ax1.plot(minute,price_close,'black',bstime,buy,'go',bstime,sell,'ro',bstime,short,'bo',bstime,cover,'ro',bstime,tech_one,'seagreen',bstime,tech_two,'lightcoral')#,bstime,tech_three,'bo')
	 if file_format==2:ax1.plot(minute,price_ohlc.close,'black',bstime,buy,'go',bstime,sell,'ro',bstime,short,'bo',bstime,cover,'ro',bstime,tech_one,'seagreen',bstime,tech_two,'lightcoral')#,bstime,tech_three,'bo')
	 #ax2.plot(bstime,tech_three,'b-')
	 plt.fill_between(bstime,tech_three,facecolor='seagreen', alpha=0.5, interpolate=True)
	 plt.grid(b=True, which='major', color='grey', linestyle='-')
	 
	 plt.subplot(gs[1])
	 axes = plt.gca()
	 axes.set_xlim([0,numb])
	 plt.plot(bstime,AS,'r-')
	 plt.grid(b=True, which='major', color='grey', linestyle='-')
	 plt.show()
		 
