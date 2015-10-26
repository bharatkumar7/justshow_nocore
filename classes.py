class symbol:
 'Common base class for all symbols'
 maxtick = 20 # 20 for MACD   max ticks to store for analysis say 5 min = 5*60
 ntick = -1
 risk = 4
 target_profit = 1.01 # 1.0075 for MACD  percentage of profit for 100
 stop_loss = 0.98 #0.99 for MACD
 brokerage = 0.001 # 0.05-intraday 0.37-delivery
 sample_investment = 300 # max amount to use per symbol
 lot_size = 25 #  lot sizes
 sleeptime = 1 # 3 for MACD# seconds to wait before fetch
 work_dir = ''
   
  
 def __init__(self, tname, rname, type, strategy, status, bprice, sprice, bd, stop_loss, perc, btime, stime,\
  nsells, nbuys, investment, lot_size, optype, stkprice):
  
  symbol.ntick += 1
  self.tname = tname # the name for reference
  self.rname = rname # the trading symbol (for NEST PLUS)
  self.type = type # if index (0) or option (1) or equity (2)
  
  # for trade
  self.strategy = strategy
  self.status = status # if in a trade or not - get from nest plus
  self.bprice = bprice # bought price
  self.sprice = sprice # sell price
  self.bd = bd  #for trend
  self.stop_loss = stop_loss  #for stop loss
  self.perc = perc # perc
  self.btime = btime # buy time
  self.stime = stime # sell time
  
  # for ledger
  self.nsells = nsells
  self.nbuys = nbuys 

  self.investment = investment # investment
  self.lot_size = symbol.lot_size # set lot size for individual symbols or from global size
  self.optype = optype   # option type call or put 
  self.stkprice = stkprice #strike price if option

  def displayCount(self):
   print "Total symbol %d" % symbol.ntick

  def displaysymbol(self):
   print self.cid, self.name

  def displayReturns(self):
   iperc = (self.investment-symbol.sample_investment)*100.0/self.investment
   print self.cid, self.name, 'Inv = ',self.investment,'Perc = %5.2f'% iperc


import numpy as np
import time
class tickdata:
  ntick = 0 # start from zero 

  def __init__(self):
    tickdata.ntick += 1

    #DATE,LTP, VOLUME
    self.ticktime = np.zeros(symbol.maxtick,'f')
    self.ltp = np.zeros(symbol.maxtick,'f')
    self.vol = np.zeros(symbol.maxtick,'f')
    self.bp = np.zeros(symbol.maxtick,'f')
    self.ap = np.zeros(symbol.maxtick,'f')
   
    for i in range(0,symbol.maxtick):
      self.ticktime[i] = np.random.randint(10)
      self.ltp[i] = np.random.randint(10)
      self.vol[i] = np.random.randint(10)
      self.bp[i] = np.random.randint(10)
      self.ap[i] = np.random.randint(10)
