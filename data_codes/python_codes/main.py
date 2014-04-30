

####homwork 1:portfolio optimizer
#execfile("/home/danial/Dropbox/Computer_science/Quantitative_finance/homeworks/1/opt_sim.py")

#start_date=dt.datetime(2010,1,1)
#end_date=dt.datetime(2010,12,31)
#ls_symbols=['AAPL', 'GLD', 'GOOG', 'XOM']
#ls_symbols=['C', 'GS', 'IBM', 'HNZ']
#step=0.1
#hw_1_read_analysis=Analysis(start_date,end_date,ls_symbols)
#min_sharpe_ratio,best_allocation=hw_1_read_analysis.B_F_optimizer(step)

################homework 2: event studies
#execfile("/home/danial/Dropbox/Computer_science/Quantitative_finance/homeworks/1/Market_Simulator_class.py")
#start_date=dt.datetime(2008,1,1)
#end_date=dt.datetime(2009,12,31)
#ls_symbols="sp5002008"
#hw_2_event_studies=MarketSimulator(start_date,end_date,ls_symbols)
#threshold=8.0
#simple_events=hw_2_event_studies.simple_events_finder(threshold)
#ep.eventprofiler(simple_events, hw_2_event_studies.d_data, i_lookback=20, i_lookforward=20,s_filename='simple_events_1.pdf', b_market_neutral=True, b_errorbars=True,s_market_sym='SPY')

################homework 3: merket simulation
#execfile("/home/danial/Dropbox/Computer_science/Quantitative_finance/homeworks/1/Market_Simulator_class.py")

#hw_3_market_simulator=MarketSimulator("/home/danial/Dropbox/Computer_science/Quantitative_finance/homeworks/1/orders.csv")
#hw_3_market_simulator.trade_array_builder(initial_cash=1000000)
#hw_3_market_simulator.write_portfolio_val('test.csv')

#ave_daily_portrets,std_daily_portrets,daily_portrets,sharpe_ratio,cum_portrets_last=hw_3_market_simulator.statistics()
#print ave_daily_portrets,std_daily_portrets,daily_portrets,sharpe_ratio,cum_portrets_last
################################ homework4 
'''
You should use actual close (actual_close) in event study and order generation (the program to code in HW4). 

Once the offers are written to a file, your marketsim.py from HW3 will use adjusted close (close) to generate fund values.


execfile("/home/danial/Dropbox/Computer_science/Quantitative_finance/homeworks/1/opt_sim.py")

start_date=dt.datetime(2008,1,1)
end_date=dt.datetime(2009,12,31)
ls_symbols="sp5002012"
hw_4_event_studies=Analysis(start_date,end_date,ls_symbols)
threshold=6.0
simple_events=hw_4_event_studies.simple_events_finder(threshold,True,"orders_6_events.csv")
#ep.eventprofiler(simple_events, hw_2_event_studies.d_data, i_lookback=20, i_lookforward=20,s_filename='simple_events_1.pdf', b_market_neutral=True, b_errorbars=True,s_market_sym='SPY')
execfile("/home/danial/Dropbox/Computer_science/Quantitative_finance/homeworks/1/Market_Simulator_class.py")
hw_4_market_simulator=MarketSimulator("/home/danial/Dropbox/Computer_science/Quantitative_finance/homeworks/1/orders_5_events.csv")
#hw_4_market_simulator.trade_array_builder(initial_cash=50000)
#hw_4_market_simulator.write_portfolio_val('port_values_5_events.csv')
#ave_daily_portrets,std_daily_portrets,daily_portrets,sharpe_ratio,cum_portrets_last=hw_4_market_simulator.statistics()
ave_daily_portrets,std_daily_portrets,daily_portrets,sharpe_ratio,cum_portrets_last=hw_4_market_simulator.statistics_2("port_values_5_events.csv")
print "ave_daily_portrets ",ave_daily_portrets
print "std_daily_portrets ",std_daily_portrets
print "sharpe_ratio ", sharpe_ratio
print "cum_portrets_last",cum_portrets_last
'''
################# HW 5
'''
execfile("/home/danial/Dropbox/Computer_science/Quantitative_finance/homeworks/1/opt_sim.py")
start_date=dt.datetime(2010,1,1)
end_date=dt.datetime(2010,12,31)
ls_symbols=['AAPL', 'GOOG','IBM', 'MSFT']
hw_5=Analysis(start_date,end_date,ls_symbols)
lookback=20
hw_5.Bollinger_Values(lookback,write_BV_file=True,BV_file="BV_file.csv")
'''
################ HW 6
execfile("/home/danial/Dropbox/Computer_science/Quantitative_finance/homeworks/1/Market_Simulator_class.py")
start_date=dt.datetime(2008,1,1)
end_date=dt.datetime(2009,12,31)
ls_symbols="sp5002012"
lookback=20
hw_6=MarketSimulator(start_date,end_date,ls_symbols)
thresholds=np.zeros(3)
thresholds[0]=-2.0
thresholds[1]=-2.0
thresholds[2]=1.5
hw_6.Bollinger_Values(lookback,write_BV_file=True,BV_file="BV_file1.csv")
BV_events=hw_6.Bollinger_events_finder(thresholds,write_order_file=True,order_file="BV_order_file.csv")
#ep.eventprofiler(BV_events, hw_6.d_data, i_lookback=20, i_lookforward=20,s_filename='BV_events_plot.pdf', b_market_neutral=True, b_errorbars=True,s_market_sym='SPY')
ave_daily_portrets,std_daily_portrets,daily_portrets,sharpe_ratio,cum_portrets_last=hw_6.statistics_2("port_value_BV_events.csv")
print "ave_daily_portrets ",ave_daily_portrets
print "std_daily_portrets ",std_daily_portrets
print "sharpe_ratio ", sharpe_ratio
print "cum_portrets_last",cum_portrets_last