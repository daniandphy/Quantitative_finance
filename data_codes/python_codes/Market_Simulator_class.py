import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep
import copy
import datetime as dt
import csv
import pandas as pd
import numpy as np
class MarketSimulator():
 def __init__(self,*args):
     if len(args)==3:
         ##format start_date,end_date,ls_symbols
         self.load_data(*args)
     elif len(args)==1:
         self.start_date,self.end_date,ls_symbols=self.read_orders(*args)
         self.load_data(self.start_date,self.end_date,ls_symbols)
         
     
 def load_data(self,start_date,end_date,ls_symbols):
    dt_timeofday=dt.timedelta(hours=16)
    print "start_date,end_date",start_date,end_date
    self.ldt_timestamps=du.getNYSEdays(start_date,end_date,dt_timeofday)
    self.c_dataobj=da.DataAccess('Yahoo')
    #Checkif it is filename
    if type(ls_symbols) is str:
        ls_symbols=self.c_dataobj.get_symbols_from_list(ls_symbols)
        ls_symbols.append('SPY')
    
    
    self.ls_keys=['open','high','low','close','volume','actual_close']
    self.ldf_data=self.c_dataobj.get_data(self.ldt_timestamps,ls_symbols,self.ls_keys)
    #print "np.shape(self.ldf_data)",np.shape(self.ldf_data)
    #preparing data for simulation and analysis
    self.d_data=dict(zip(self.ls_keys,self.ldf_data))
    #print "np.shape(self.d_data['actual_close'])",len(self.d_data['actual_close'])
    for s_key in self.ls_keys:
        self.d_data[s_key]=self.d_data[s_key].fillna(method = 'ffill')
        self.d_data[s_key]=self.d_data[s_key].fillna(method = 'bfill')
        self.d_data[s_key]=self.d_data[s_key].fillna(1.0)
    
    
    self.df_close=self.d_data['close']
    #print "self.df_close",self.df_close[:5]
    self.df_rets=self.df_close.copy()
    self.na_rets = self.df_rets.values
    self.normalized_df_rets=self.na_rets/self.na_rets[0,:]
    self.total_days=len(self.na_rets[:,0])
    self.daily_portrets=np.zeros(self.total_days)
     #####
    self.ls_symbol=ls_symbols
####################################
 def read_orders(self,file_name):
     ls_dates=[]
     ls_symbols=[]     
    
     #reader=csv.reader(open(file_name,'rU'),delimiter=',')
     #for row in reader:
         #date=dt.datetime(int(row[0]),int(row[1]),int(row[2]))
         #ls_dates.append(date)
     self.df_orders=pd.read_csv(file_name,sep=',',parse_dates={'date':[0,1,2]},header=None,skiprows=0)
     #self.df_orders.sort(columns='date',inplace=True)
     print self.df_orders.ix[0:20,:]
     ls_symbols=list(self.df_orders[:][3])
     ls_dates=list(self.df_orders.ix[:,0])
     #self.df_orders.shift(periods=0,freq=dt.timedelta(hours=16))
     #print self.df_orders.ix[:,:]
     #removing repeated dates and symbols from date and symbol lists
     ls_dates=list(set(ls_dates))
     ls_dates.sort()
     number_of_ordering_dates=len(ls_dates)
     
     ls_symbols=list(set(ls_symbols))
     ls_symbols.sort()
     
     extra_date=ls_dates[number_of_ordering_dates-1]+dt.timedelta(1)
     ls_dates.append(extra_date)
     
     #self.df_orders.ix[:,6]=-self.df_orders.ix[self.df_orders[:,4].lower()=='buy'][5]
     #self.df_orders[self.df_orders[:][4]=='Buy'][5]*=(-1)
     
     #self.df_orders[:][5].where(self.df_orders[:][4]=='Buy',other=(-1)*self.df_orders[:][5])
     #print self.df_orders[self.df_orders[:][4]=='Buy'][5]*(-1)
     
     #print 'ls_datessss',ls_dates
     #print ls_symbols
     #self.df_orders.pop(column=6)
     
     return ls_dates[0],ls_dates[number_of_ordering_dates],ls_symbols
    
####################################
 def trade_array_builder(self,initial_cash):
     self.df_trade=copy.deepcopy(self.df_close)
     #Fill the matrix with nan,i.e., the default is that there is no events
     self.df_trade=self.df_trade*np.float(0)
     #print "self.df_trade.ix[0,:]",type(self.df_trade),self.df_trade.ix[0:2,:]
     #print "self.df_close.ix[0,:]",self.df_close.ix[0:2,:]
     #print np.shape(self.df_trade),type(self.df_trade)
     for order in self.df_orders.values:
         #print order[0],order[1],order[2],order[3],type(order)
         date,symbol,action,share_number=order
         #print "date",date
         #print self.df_trade.ix[self.df_trade.ix[:,0]==date,:]
         date+=dt.timedelta(hours=16)
    
         if action.lower()== 'buy':
             self.df_trade.ix[self.df_trade.index[:]==date,symbol]=share_number
         elif action.lower()== 'sell':
             self.df_trade.ix[self.df_trade.index[:]==date,symbol]=-share_number
     #print self.df_trade.ix[self.df_trade.index[:]==date,:] ,date,symbol
     #print self.df_trade.ix[:,0]
     
     #self.ts_cash=pd.Series(initial_cash,index=self.df_close.index)
     self.minus_ts_cash=(self.df_close*self.df_trade).sum(axis=1)
     #print "self.start_date",self.start_date,"self.end_date",self.end_date
     #print "np.shape(self.ts_cash)",np.shape(self.ts_cash)
     #print "np.shape(self.df_close)",np.shape(self.df_close)
     #print self.minus_ts_cash[0:5]
     #print self.df_trade [:5]
     #print (self.df_close*self.df_trade)[:5]
     #print (self.df_close*self.df_trade).sum(axis=1)[:5]
     #print self.ts_cash[:5]
     self.df_close['_cash']=1.0
     self.df_trade['_cash']=-self.minus_ts_cash ###-self.minus_ts_cash=self.ts_cash
     self.df_trade.ix[0,'_cash']+=initial_cash
     self.df_holding=self.df_trade.cumsum(axis=0)
     #print "self.df_close[:5]",self.df_close[:5]
     #print "self.df_holding[:5]",self.df_holding[:5]
     self.ts_portvalues=(self.df_close*self.df_holding).sum(1)
     
     #print "self.ts_values[:,5]",self.ts_portvalues[0:5]
#####################
 def statistics(self):
    
    #print self.total_days,np.shape(self.ts_portvalues[1:])
    print self.ts_portvalues[1:5]
    arr_portvalues=np.array(self.ts_portvalues[:])
    
    self.daily_portrets[1:]=(arr_portvalues[1:]/arr_portvalues[0:self.total_days-1])-1.0
    #self.daily_portrets[1:]=(self.ts_portvalues[1:]/self.ts_portvalues[0:self.total_days-1])-1.0
    print "daily_portrets",self.daily_portrets[0:5]
    print np.cumprod(self.daily_portrets+1.0)[:5]
    cum_portrets=np.cumprod(self.daily_portrets+1.0)
    ave_daily_portrets=np.average(self.daily_portrets)
    std_daily_portrets=np.std(self.daily_portrets) #volatility
    K=np.sqrt(252)
    sharpe_ratio=K*ave_daily_portrets/std_daily_portrets #Sharpe ratio
    #print "shape cum_portrets",np.shape(cum_portrets)
    
    return ave_daily_portrets,std_daily_portrets,self.daily_portrets[self.total_days-1],sharpe_ratio,cum_portrets[self.total_days-1]    
############
 def write_portfolio_val(self,file_name):
     writer =csv.writer(open(file_name,'wb'),delimiter=',')
     for row_index in self.ts_portvalues.index:
         date_str=str(row_index).split()
                     #print date_str
         date=date_str[0].split('-')
         row_to_enter=[date[0],date[1],date[2],self.ts_portvalues[row_index]]
         writer.writerow(row_to_enter)
####################################     
 def Bollinger_Values(self,lookback,write_BV_file=False,BV_file="BV_file.csv"):
         df_mean=pd.rolling_mean(self.df_close,lookback)
         df_std=pd.rolling_std(self.df_close,lookback)
         df_bands=(self.df_close-df_mean)/df_std
         self.bollinger_val=(self.df_close-df_mean)/df_std
         if write_BV_file:
             self.bollinger_val.to_csv(BV_file)
         return


##################################event finders
 def Bollinger_events_finder(self,thresholds,write_order_file=False,order_file="BV_order_file.csv"):
     if write_order_file:
         writer =csv.writer(open(order_file,'w'),delimiter=',')
   
     ######preparing for event_profiler test
     #self.df_close=d_data['close']
     df_events=copy.deepcopy(self.df_close)
     #Fill the matrix with nan,i.e., the default is that there is no events
     df_events=df_events*np.NAN
     #time index for the event range this is pandas object
     self.ldt_time_index= self.bollinger_val.index
     event_counter=0
     for s_sym in self.ls_symbol:
         for i in range(1,len(self.ldt_time_index)):
             f_symBV_today= self.bollinger_val[s_sym].ix[self.ldt_time_index[i]]
             f_symBV_yest= self.bollinger_val[s_sym].ix[self.ldt_time_index[i-1]]
             f_spyBV_today=self.bollinger_val['SPY'].ix[self.ldt_time_index[i]]
             #print s_sym,f_symprice_today,f_symprice_yest
             if(f_symBV_today<thresholds[0] and f_symBV_yest >=thresholds[1] and f_spyBV_today >=thresholds[2]):
                 #print "event_detected",s_sym
                 event_counter+=1
                 df_events[s_sym].ix[self.ldt_time_index[i]]=1
                 if write_order_file:
                     date_str=str(self.ldt_time_index[i]).split()
                     #print date_str
                     date=date_str[0].split('-')
                     #print date
                     row_to_enter=[date[0],date[1],date[2],s_sym,"BUY",str(100)]
                     writer.writerow(row_to_enter)
                     if i< len(self.ldt_time_index)-5:
                         date_str=str(self.ldt_time_index[i+5]).split()
                         date=date_str[0].split('-')
                         row_to_enter=[date[0],date[1],date[2],s_sym,"SELL",str(100)]
                         writer.writerow(row_to_enter)
                     else:
                         date_str=str(self.ldt_time_index[-1]).split()
                         date=date_str[0].split('-')
                         row_to_enter=[date[0],date[1],date[2],s_sym,"SELL",str(100)]
                         writer.writerow(row_to_enter)
     print "number of events=",event_counter
     return df_events
 def simple_events_finder(self,threshold,write_order_file=False,order_file="order_file.cvs"):
     if write_order_file:
         writer =csv.writer(open(order_file,'w'),delimiter=',')
   
     ######preparing for event_profiler test
     #self.df_close=d_data['close']
     df_events=copy.deepcopy(self.df_close)
     #Fill the matrix with nan,i.e., the default is that there is no events
     df_events=df_events*np.NAN
     #time index for the event range this is pandas object
     self.ldt_time_index=df_events.index
     event_counter=0
     for s_sym in self.ls_symbol:
         for i in range(1,len(self.ldt_time_index)):
             f_symprice_today=self.df_close[s_sym].ix[self.ldt_time_index[i]]
             f_symprice_yest=self.df_close[s_sym].ix[self.ldt_time_index[i-1]]
             #print s_sym,f_symprice_today,f_symprice_yest
             if(f_symprice_today<threshold and f_symprice_yest >=threshold):
                 #print "event_detected",s_sym
                 event_counter+=1
                 df_events[s_sym].ix[self.ldt_time_index[i]]=1
                 if write_order_file:
                     date_str=str(self.ldt_time_index[i]).split()
                     #print date_str
                     date=date_str[0].split('-')
                     #print date
                     row_to_enter=[date[0],date[1],date[2],s_sym,"BUY",str(100)]
                     writer.writerow(row_to_enter)
                     if i< len(self.ldt_time_index)-5:
                         date_str=str(self.ldt_time_index[i+5]).split()
                         date=date_str[0].split('-')
                         row_to_enter=[date[0],date[1],date[2],s_sym,"SELL",str(100)]
                         writer.writerow(row_to_enter)
     print "number of events=",event_counter
     return df_events
############################################33
 def statistics_2(self,file_name):
    ts_portvalues=self.csv_read_fund(file_name)
    #print self.total_days,np.shape(self.ts_portvalues[1:])
    print ts_portvalues[1:5]
    arr_portvalues=np.array(ts_portvalues[:])
    daily_portrets=np.zeros(len(arr_portvalues))
    daily_portrets[1:]=(arr_portvalues[1:]/arr_portvalues[0:len(arr_portvalues)-1])-1.0
    #self.daily_portrets[1:]=(self.ts_portvalues[1:]/self.ts_portvalues[0:self.total_days-1])-1.0
    print "daily_portrets",daily_portrets[0:5]
    print np.cumprod(daily_portrets+1.0)[:5]
    cum_portrets=np.cumprod(daily_portrets+1.0)
    ave_daily_portrets=np.average(daily_portrets)
    std_daily_portrets=np.std(daily_portrets) #volatility
    K=np.sqrt(252)
    sharpe_ratio=K*ave_daily_portrets/std_daily_portrets #Sharpe ratio
    #print "shape cum_portrets",np.shape(cum_portrets)
    
    return ave_daily_portrets,std_daily_portrets,daily_portrets[len(arr_portvalues)-1],sharpe_ratio,cum_portrets[len(arr_portvalues)-1]
 
 def csv_read_fund(self,filename):
    reader = csv.reader(open(filename, 'rU'), delimiter=',')
    vals = []
    dates = []
    for row in reader:
        vals.append(float(row[3]))
        date = dt.datetime(int(row[0]), int(row[1]), int(row[2]), 16)
        dates.append(date)
    ts_fund = pd.TimeSeries(dict(zip(dates, vals)))
    return ts_fund