import numpy as np
import time,os,talib
import matplotlib.pyplot as plt
import math


stock_derv=25.0  #1- Stocks/Futures , 25- Nifty options,etc.,
 
def range_bar(cl_price,vol,rangeper):
 price_open=np.zeros(40000,'f')
 price_high=np.zeros(40000,'f')
 price_low=np.zeros(40000,'f')
 price_close=np.zeros(40000,'f')
 n=len(cl_price)
 lastbar=0
 k=0
 for i in range (0,n):
  if lastbar==0:
   price_open[k]=cl_price[i]
   temp_o=price_open[k]
   lastbar=1
   start=i
  elif lastbar==1 and ((cl_price[i]>=(temp_o*rangeper+temp_o)) or (cl_price[i]<=(temp_o-temp_o*rangeper))):
   price_close[k]=cl_price[i]
   stop=i
   #print start,stop
   price_high[k]=np.max(cl_price[start:stop+1])
   price_low[k]=np.min(cl_price[start:stop+1])
   #print k,price_open[k],price_high[k],price_low[k],price_close[k] 
   k+=1
   lastbar=0
  else:pass
 price_open=filter(lambda x: x!=0,price_open)
 price_high=filter(lambda x: x!=0,price_high)
 price_low=filter(lambda x: x!=0,price_low)
 price_close=filter(lambda x: x!=0,price_close)
 return  price_open,price_high,price_low,price_close 
    

def Expectancy(alltrades,PLP,PL,n):
 i=0
 wintrades=0.0
 losstrades=0.0
 totaltrades=0.0
 profper=0.0
 lossper=0.0
 winprob=0.0
 losprob=0.0
 profamt=0.0
 lossamt=0.0
 for i in range(0,n):
  if alltrades[i]==1: 
   wintrades+=1
   profamt=profamt+PL[i]
   profper=profper+PLP[i]
  if alltrades[i]==-1: 
   losstrades+=1
   lossamt=lossamt+PL[i]
   lossper=lossper+PLP[i]
 
 print wintrades,losstrades
 winprob=(wintrades/(wintrades+losstrades))
 lossprob=1-winprob
 print "--------------------------  Expectancy ----------------------------"
 print "Profit Probability= %.2f, Loss Probability= %.2f "%(winprob,lossprob)
 print "Profit Avg_Percent=%.2f, Loss Avg_Percent= %.2f "%(profper/wintrades,lossper/losstrades)
 print "Profit Avg_Amt= %.2f, Loss Avg_Amt= %.2f"%((profamt/wintrades),(lossamt/losstrades))
 expect=(winprob*(profamt/wintrades))-abs(lossprob*(lossamt/losstrades))
 print "Expectancy = %.2f, Final P/L= %.2f"%(expect,(profamt-abs(lossamt)))
 print "----------------------------------------------------------------------"
 
 
#-------------------------Position Sizing - Method ------------------------------------
def PositionSizing_Method(postype,AccountSize,stop_loss,EntryPrice,Volatility,Uvolt,Dvolt,alltrades,PL,iter):
 Volatility=3*Volatility
 if iter<=100:qty,StopPrice=PS_Per(postype,AccountSize,stop_loss,EntryPrice,Uvolt,Dvolt)
 else:qty,StopPrice=PS_Kelly(postype,AccountSize,EntryPrice,alltrades,PL,iter,Uvolt,Dvolt)
 #else: qty,StopPrice=PS_Volatility(postype,AccountSize,EntryPrice,Volatility,Uvolt,Dvolt)
 #print EntryPrice, StopPrice,Volatility,qty 
 #qty=1000
 return qty,StopPrice
 
 
#-------------------------PS - Percentage Risk Capital ------------------------------------
#lot_size,leftamt=funct.PS_Per(status,AccountSize,RiskPer, stop_loss,tdata_ltp[latest])
def PS_Per(postype,AccountSize,stop_loss,EntryPrice,Uvolt,Dvolt):
 RiskPer=1.0 #percentage of amount at risk
 if postype==1:StopPrice=Uvolt
 if postype==2:StopPrice=Dvolt
 EntryStop=abs(EntryPrice-StopPrice)
 temp=(AccountSize*(RiskPer/100.0))
 #print temp,EntryStop
 qty=(temp/EntryStop)
 if (qty*EntryPrice)>AccountSize:qty=(AccountSize/EntryPrice)
 qtysize=(math.ceil(qty / stock_derv) * stock_derv)-stock_derv
 #qty=1000
 return qtysize,StopPrice
 
'''
 #-------------------------PS - Thomas Bulkowski - NOT CORRECT-------------------------
#Shares = (PositionSize * (MarketVolatility / StockVolatility)) / StockPrice
#http://thepatternsite.com/MoneyMgmt.html
def PS_Bulkowski(postype,AccountSize,RiskPer,stop_loss,EntryPrice):

 return qty,leftamt
'''
#-------------------------PS - Voltality Risk (ATR)- ------------------------------------
def PS_Volatility(postype,AccountSize,EntryPrice,Volatility,Uvolt,Dvolt):
 RiskPer=1.0 #percentage of amount at risk
 if postype==1:StopPrice=Uvolt
 if postype==2:StopPrice=Dvolt 
 #if postype==1:StopPrice=EntryPrice-((1.0-stop_loss)*EntryPrice)
 #if postype==2:StopPrice=EntryPrice+((1.0-stop_loss)*EntryPrice)
 temp=(AccountSize*(RiskPer/100.0))
 #print 3*Volatility
 qty=(temp/(Volatility))
 if (qty*EntryPrice)>AccountSize:qty=(AccountSize/EntryPrice)
 qtysize=(math.ceil(qty / stock_derv) * stock_derv)-stock_derv
 return qtysize,StopPrice

 
#-------------------------PS - KELLY------------------------------------
def PS_Kelly(postype,AccountSize,EntryPrice,alltrades,PL,n,Uvolt,Dvolt):
 if postype==1:StopPrice=Uvolt
 if postype==2:StopPrice=Dvolt 
 wintrades=0.0
 losstrades=0.0
 profamt=0.0
 lossamt=0.0
 for i in range(0,n):
  if alltrades[i]==1: 
   wintrades+=1
   profamt=profamt+PL[i]
  if alltrades[i]==-1: 
   losstrades+=1
   lossamt=lossamt+PL[i]
 
 WinProbPer=(wintrades*1/(wintrades+losstrades))
 ProfFact=abs(profamt/lossamt)
 qtyper=WinProbPer-((1-WinProbPer)/ProfFact)
 qty=(AccountSize*qtyper/1)/(EntryPrice)
 if qtyper<=0 or qty<=2:qty=2.0
 #print WinProbPer,ProfFact,qtyper,qty
 if (qty*EntryPrice)>AccountSize:qty=(AccountSize/EntryPrice)
 qtysize=(math.ceil(qty / stock_derv) * stock_derv)-stock_derv
 return qtysize,StopPrice
 
