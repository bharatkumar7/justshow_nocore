# scraper stuff
import datetime, binascii
import lxml.html
from datetime import datetime
import os
from bs4 import BeautifulSoup
import datetime
from datetime import date
import json
import feedparser
import time

import classes

# check a webpage for validity
####################################################################
def pagecheck(doc):
 stat = 0
 xstr ='Unauthorized'
 if doc!=None:
  if len(doc)>1024:
   for word in str(doc).split(' '):
    if word==xstr: stat = 1
    break
 return stat

# mon string to int
####################################################################
def mon_conv(date):
 return{'Jan' : 1,'Feb' : 2,'Mar' : 3,'Apr' : 4,'May' : 5,'Jun' : 6,\
        'Jul' : 7,'Aug' : 8,'Sep' : 9,'Oct' : 10,'Nov' : 11,'Dec' : 12}[date]


####################################################################
# Yahoo finance scraper
####################################################################
def yahoo(doc2):
 doc = doc2.decode(encoding='UTF-8')
 idata=[]

 empty = ''
 lempty = ['']
 atype = 'Yahoo Finance'
 info  = ''
 base = 'https://in.finance.yahoo.com'
 timey = time.mktime(datetime.datetime.now().timetuple())

 soup = BeautifulSoup(doc,"lxml")
 gdata = soup.find_all("",{"class":"description"})

 #tdata=[]
 #ydata=[]
 n = len(gdata)
 for i in range(0,n):
  j=0
  #print i, gdata[i].text
  #print i, gdata[i].contents
  # get href link
  lstr = str(gdata[i].contents)
  #print lstr

  soup2 = BeautifulSoup(lstr,"lxml")
  for link in soup2.find_all('a'):
   xlink = base+str(link.get('href'))
   break

  # get info, announ, atype
  t1 = 'More'#+str(175)
  t2 = 'More'
  xstr = ''.join(str(gdata[i].text.encode('ascii', 'ignore')))
  xstr2 = ''.join(xstr).split(t1)
  #xstr = (str(gdata[i].text.encode('ascii', 'ignore').split(t1)).replace(t2,''))

  #print i, xstr2
  if xstr2!=['']:
   #tdata.append(xstr2[1])# announ
   #tdata.append(xstr2[0])# info
   #tdata.append(timey) # time stamp
   #tdata.append(xlink) # link
   idata.append(classes.ticker(xstr2[1],atype,xlink,timey,xstr2[0],0))
   #print i, xstr2[0]
   #print i, xstr2[1]
   if i==50: break # 50 articles in each page

   #soup2 = BeautifulSoup(str(gdata))
   #tables = soup2.find_all("tr")
    
 idata.sort(key=lambda x: x.time, reverse=True)
 return idata[0:classes.ticker.narticles]


####################################################################
# IIFL scraper - 1
####################################################################
# -----------------code removed-----------------------------------


####################################################################
# livemint scraper
####################################################################
def livemint(doc2,id):
 doc = doc2.decode(encoding='UTF-8')
 atype = 'livemint'+id
 feed = feedparser.parse(doc)
 i=0
 idata = []
 for post in feed.entries:
  i=i+1
  announ = str(post.title.encode('ascii', 'ignore'))
  xlink  = str(post.link.encode('ascii', 'ignore'))
  timestamp = int(time.mktime(post.updated_parsed))
  info = str(post.summary.encode('ascii', 'ignore')).split('>')

  idata.append(classes.ticker(announ, atype, xlink, timestamp, info[1],0))
 idata.sort(key=lambda x: x.time, reverse=True)
 return idata[0:classes.ticker.narticles]



####################################################################
# mydigitalfc scraper
####################################################################
def mydigitalfc(doc2):
 doc = doc2.decode(encoding='UTF-8')
 atype = 'mydigitalfc'

 feed = feedparser.parse(doc)
 i=0
 idata = []
 for post in feed.entries:
  i=i+1
  announ = str(post.title.encode('ascii', 'ignore'))
  xlink  = str(post.link.encode('ascii', 'ignore'))
  timestamp = int(time.mktime(post.updated_parsed))
  info = str(post.summary.encode('ascii', 'ignore')).split('>')

  idata.append(classes.ticker(announ, atype, xlink, timestamp, info[1],0))
 idata.sort(key=lambda x: x.time, reverse=True)
 return idata[0:classes.ticker.narticles]



####################################################################
# ibnlive scraper
####################################################################
# -----------------code removed-----------------------------------
	
####################################################################
# MControl scraper
####################################################################
def mc(doc2):
 doc = doc2.decode(encoding='UTF-8')
 atype = 'mc'

 feed = feedparser.parse(doc)
 i=0
 idata = []
 for post in feed.entries:
  i=i+1
  announ = str(post.title.encode('ascii', 'ignore'))
  xlink  = str(post.link.encode('ascii', 'ignore'))
  timestamp = int(time.mktime(post.updated_parsed))
  info = str(post.summary.encode('ascii', 'ignore')).split('>')

  idata.append(classes.ticker(announ, atype, xlink, timestamp, info[1],0))
 idata.sort(key=lambda x: x.time, reverse=True)
 return idata[0:classes.ticker.narticles]
	
####################################################################
# Economic times scraper
####################################################################
def etimes(doc2):
 doc = doc2.decode(encoding='UTF-8')
 atype = 'etimes'
 feed = feedparser.parse(doc)
 i=0
 idata = []
 for post in feed.entries:
  i=i+1
  announ = str(post.title.encode('ascii', 'ignore'))
  xlink  = str(post.link.encode('ascii', 'ignore'))
  timestamp = int(time.mktime(post.updated_parsed))
  info = str(post.summary.encode('ascii', 'ignore')).split('>')
  #print announ
  #print xlink
  #print timestamp, util.ts_conv(timestamp)
  #print info[3]
  idata.append(classes.ticker(announ, atype, xlink, timestamp, info[3],0))
  #print i, announ, atype, xlink, timestamp, info[3]
  #pline2()
  #pline()
 idata.sort(key=lambda x: x.time, reverse=True)
 return idata[0:classes.ticker.narticles]	
	
	
####################################################################
# SMERA scraper
####################################################################
def smera(doc2):
 doc = doc2.decode(encoding='UTF-8')
 atype = 'SMERA'

 soup = BeautifulSoup(doc,"lxml")
 gdata = soup.find_all("",{"class":"company"})

 idata=[]
 for items in gdata:
  announ = str(items.text).replace('View','')
  xlink = str(items.contents[1].get('href'))
  timestamp = int(time.time())
  info = ''
  idata.append(classes.ticker(announ, atype, xlink, timestamp, info,0))
  if(len(idata)==0): idata = None
 idata.sort(key=lambda x: x.time, reverse=True)
 return idata[0:classes.ticker.narticles]
	
.ticker.narticles]	

# ------------- Rest of code deleted -------------------------------------
