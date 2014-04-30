import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkstudy.EventProfiler as ep
import copy
import datetime as dt
import csv
#import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
class Analysis():
 def __init__(self,start_date,end_date,ls_symbols):
 	self.load_data(start_date,end_date,ls_symbols)
 	
 	
 def load_data(self,start_date,end_date,ls_symbols):
 	dt_timeofday=dt.timedelta(hours=16)
	self.ldt_timestamps=du.getNYSEdays(start_date,end_date,dt_timeofday)
	self.c_dataobj=da.DataAccess('Yahoo')
	#Checkif it is filename
	if type(ls_symbols) is str:
		ls_symbols=self.c_dataobj.get_symbols_from_list(ls_symbols)
		ls_symbols.append('SPY')
	
	
	self.ls_keys=['open','high','low','close','volume','actual_close']
	self.ldf_data=self.c_dataobj.get_data(self.ldt_timestamps,ls_symbols,self.ls_keys)
	
	#preparing data for simulation and analysis
	self.d_data=dict(zip(self.ls_keys,self.ldf_data))
	for s_key in self.ls_keys:
		self.d_data[s_key]=self.d_data[s_key].fillna(method = 'ffill')
		self.d_data[s_key]=self.d_data[s_key].fillna(method = 'bfill')
		self.d_data[s_key]=self.d_data[s_key].fillna(1.0)
	
	
	self.df_close=self.d_data['actual_close']
	self.df_rets=self.df_close.copy()
	self.na_rets = self.df_rets.values
	self.normalized_df_rets=self.na_rets/self.na_rets[0,:]
 	self.total_days=len(self.na_rets[:,0])
 	self.daily_portrets=np.zeros(self.total_days)
 	#####
 	self.ls_symbol=ls_symbols
 def Bollinger_Values(self,lookback,write_BV_file=False,BV_file="BV_file.csv"):
 		df_mean=pd.rolling_mean(self.df_close,lookback)
 		df_std=pd.rolling_std(self.df_close,lookback)
 		df_bands=(self.df_close-df_mean)/df_std
 		self.bollinger_val=(self.df_close-df_mean)/df_std
 		if write_BV_file:
 			self.bollinger_val.to_csv(BV_file)
 		return
 def simple_events_finder(self,threshold,write_order_file=False,order_file="order_file.csv"):
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
 	for i in range(1,len(self.ldt_time_index)):
  		for s_sym in self.ls_symbol:
 			f_symprice_today=self.df_close[s_sym].ix[self.ldt_time_index[i]]
 			f_symprice_yest=self.df_close[s_sym].ix[self.ldt_time_index[i-1]]
 			#print s_sym,f_symprice_today,f_symprice_yest
 			if(f_symprice_today<threshold and f_symprice_yest >=threshold):
 				#print "event_detected",s_sym
 				event_counter+=1
 			 	df_events[s_sym].ix[self.ldt_time_index[i]]=1
 			 	if write_order_file:
 			 		date_str=str(self.ldt_time_index[i]).split()
 			 		date=date_str[0].split('-')
 			 		row_to_enter=[date[0],date[1],date[2],s_sym,"BUY",str(100)]
 			 		writer.writerow(row_to_enter)
 			 		if i< len(self.ldt_time_index)-5:
	 			 		date_str=str(self.ldt_time_index[i+5]).split()
	 			 		date=date_str[0].split('-')
	 			 		row_to_enter=[date[0],date[1],date[2],s_sym,"SELL",str(100)]
	 			 		writer.writerow(row_to_enter)
 		
 	print "number of events=",event_counter
 	
 		
 	return df_events


		
 def simulate(self,allocations):
	
	
	na_portrets=np.sum(self.normalized_df_rets*allocations, axis=1)
	
	#print "normalized_df_rets*allocations"
	#print normalized_df_rets*allocations
	#print np.shape(normalized_df_rets*allocations)
	#print "na_portrets"
	#print na_portrets
	#print np.shape(na_portrets)
	
	self.daily_portrets[1:self.total_days]=(na_portrets[1:]/na_portrets[0:self.total_days-1])-1.0
	#print "daily_portrets",daily_portrets[0:5]
	cum_portrets=np.cumprod(self.daily_portrets+1.0)
	ave_daily_portrets=np.average(self.daily_portrets)
	std_daily_portrets=np.std(self.daily_portrets) #volatility
	K=np.sqrt(250)
	sharpe_ratio=K*ave_daily_portrets/std_daily_portrets #Sharpe ratio
	#print "shape cum_portrets",np.shape(cum_portrets)
	
	return ave_daily_portrets,std_daily_portrets,self.daily_portrets,sharpe_ratio,cum_portrets[self.total_days-1]
	#######################
 def B_F_optimizer(self,step):
		#Brute_Force_optimizer
		step_ladder=int(1.0/step)
		port_size=len(ls_symbols)
		my_range=np.arange(0.0,1.0,step)
		allocations=np.zeros(len(ls_symbols))
		best_allocation=np.zeros(len(ls_symbols))
		max_sharpe_ratio=0.0
		for i in my_range:
			for j in my_range:
				for k in my_range:
					all_but_last=i+j+k
					if all_but_last<=1.0 :
						allocations[0]=i 
						allocations[1]=j
						allocations[2]=k
						l=1.0-all_but_last
						allocations[3]=l
						ave_daily_portrets,std_daily_portrets,daily_portrets,sharpe_ratio,cum_portrets=\
						self.simulate(allocations)
						#print "i,j,k,l=",i,j,k,l
						#print "std_daily_portrets,daily_portrets,sharpe_ratio,cum_portrets"
						#print  std_daily_portrets,daily_portrets,sharpe_ratio,cum_portrets
						if sharpe_ratio>max_sharpe_ratio :
							max_sharpe_ratio=sharpe_ratio
							best_allocation[0]=i 
							best_allocation[1]=j
							best_allocation[2]=k
							best_allocation[3]=l
							print "i,j,k,l=",i,j,k,l
							print "max_sharpe_ratio",max_sharpe_ratio
		print max_sharpe_ratio,best_allocation
		return max_sharpe_ratio,best_allocation
 							
				
			
		
	