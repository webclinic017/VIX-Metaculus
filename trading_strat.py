from pickle import FALSE, TRUE
import backtrader as bt
import pandas as pd
import datetime
import yfinance as yf
import matplotlib.dates
import glob
import statsmodels.api as sm


class Metaculus_Momentum(bt.Strategy):
    # Always define parameters first
    def __init__(self):
        self.order = None
        self.data = self.data0.close
        self.meta=self.data1.close
        self.buy_counter = 0
        self.sell_counter = 0
        self.init_val = self.broker.getvalue()
        self.underwater = 0
       
        

    # Trading logic second
    def next(self):
        pnl =  self.broker.getvalue() - self.init_val
        if pnl < 0:
            self.underwater = self.underwater + 1


        #If there is an order, return
        if self.order:
            return

        #if there is no position
        if not self.position:
            #
            if self.meta[-1] < self.meta[0]:
                self.log(f'BUY CREATE {self.data[0]:2f}, Metaculus: {self.meta[0]},{self.meta[-1]} ')
                self.order = self.buy(data=self.datas[0])
                
        elif self.meta[-1] > self.meta[0]:
            self.log(f'CLOSE CREATE {self.data[0]:2f}, Metaculus: {self.meta[0]},{self.meta[-1]}')
            self.order = self.close(data=self.datas[0])
            

    def log (self, txt, dt = None):
        dt = dt or self.datas[1].datetime.date(0)
        buy_count = f'BUY COUNT: {self.buy_counter}'
        sell_count = f'SELL COUNT: {self.sell_counter}'
        #print('%s, %s, %s, %s' % (dt.isoformat(), txt,buy_count, sell_count))
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            #log if buy
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
                self.buy_counter = self.buy_counter + 1
            #log if sell
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
                self.sell_counter = self.sell_counter + 1
            self.bar_executed = len(self)
            
        #Log if order didnt go through
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            
        #reset order
        self.order = None

class Metaculus_MA_SPY(bt.Strategy):

    #moving average parameters
    params = (("pfast", 16), ("pslow", 50), ('lag',19),)
    
    def log (self, txt, dt = None):
        dt = dt or self.datas[0].datetime.date(0)
        #print('%s, %s' % (dt.isoformat(), txt))
    
    def __init__(self):
        self.sma_dataclose = self.data1.close
        self.dataclose = self.datas[0].close
        self.order = None
        
        self.slow_sma = bt.indicators.MovingAverageSimple(self.sma_dataclose, period=self.params.pslow, plot = False)
        self.fast_sma = bt.indicators.MovingAverageSimple(self.sma_dataclose, period=self.params.pfast, plot = False)

        self.init_val = self.broker.getvalue()
        self.underwater = 0

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            #log if buy
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
            #log if sell
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
            self.bar_executed = len(self)
            
        #Log if order didnt go through
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            
        #reset order
        self.order = None
    
    def next(self):
        pnl =  self.broker.getvalue() - self.init_val
        if pnl < 0:
            self.underwater = self.underwater + 1
        
        #check for open orders (limit to one trade at a time)
        if self.order:
            return

        #Check existing positions in market
        if not self.position:
            #Not in market so look for Open Trades
            
            if self.fast_sma[0] > self.slow_sma[0] and self.fast_sma[-1] < self.slow_sma[-1]:
                #USE FOR SPY
                self.log(f'SELL CREATE {self.dataclose[0]:2f}')
                self.order = self.sell(data = self.data0)
                

            elif self.fast_sma[0] < self.slow_sma[0] and self.fast_sma[-1] > self.slow_sma[-1]:
                #USE FOR SPY
                self.log(f'BUY CREATE {self.dataclose[0]:2f}')
                self.order = self.buy(data = self.data0)
                
                
        else:
            #In market so look to Close Trades
            
            #Exit after 5 bars
            if len(self) >= (self.bar_executed + self.params.lag):
                self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
                self.order = self.close(data = self.data0)

class Metaculus_MA_VXX(bt.Strategy):
    #moving average parameters
    params = (("pfast", 10), ("pslow", 66), ('lag',16),)
    
    def log (self, txt, dt = None):
        dt = dt or self.datas[0].datetime.date(0)
        #print('%s, %s' % (dt.isoformat(), txt))
    
    def __init__(self):
        self.sma_dataclose = self.data1.close
        self.dataclose = self.datas[0].close
        self.order = None
        
        self.slow_sma = bt.indicators.MovingAverageSimple(self.sma_dataclose, period=self.params.pslow, plot = False)
        self.fast_sma = bt.indicators.MovingAverageSimple(self.sma_dataclose, period=self.params.pfast, plot = False)

        self.init_val = self.broker.getvalue()
        self.underwater = 0

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            #log if buy
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
            #log if sell
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
            self.bar_executed = len(self)
            
        #Log if order didnt go through
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            
        #reset order
        self.order = None
    
    def next(self):
        pnl =  self.broker.getvalue() - self.init_val
        if pnl < 0:
            self.underwater = self.underwater + 1
        
        #check for open orders (limit to one trade at a time)
        if self.order:
            return

        #Check existing positions in market
        if not self.position:
            #Not in market so look for Open Trades
            
            if self.fast_sma[0] > self.slow_sma[0] and self.fast_sma[-1] < self.slow_sma[-1]:

                #USE FOR VXX
                self.log(f'BUY CREATE {self.dataclose[0]:2f}')
                self.order = self.buy(data = self.data0)

            elif self.fast_sma[0] < self.slow_sma[0] and self.fast_sma[-1] > self.slow_sma[-1]:

                #USE FOR VXX
                self.log(f'SELL CREATE {self.dataclose[0]:2f}')
                self.order = self.sell(data = self.data0)
        else:
            #In market so look to Close Trades
            
            #Exit after 5 bars
            if len(self) >= (self.bar_executed + self.params.lag):
                self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
                self.order = self.close(data = self.data0)

class Metaculus_lead_SPY(bt.Strategy):


    params = (("lead", 21),("pct_chng", 0.5),("range", 5) )
    
    def log (self, txt, dt = None):
        dt = dt or self.datas[0].datetime.date(0)
        #print('%s, %s' % (dt.isoformat(), txt))
        
    
    def __init__(self):
        self.data = self.data0.close
        self.meta=self.data1.close
        self.order = None
        self.init_val = self.broker.getvalue()
        self.underwater = 0
        self.time_elapse = 0
        

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            #log if buy
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
            #log if sell
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
            self.bar_executed = len(self)
            
        #Log if order didnt go through
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            
        #reset order
        self.order = None
    
    def next(self):
        self.time_elapse = self.time_elapse + 1
        pnl =  self.broker.getvalue() - self.init_val
        if pnl < 0:
            self.underwater = self.underwater + 1
        
        #check for open orders (limit to one trade at a time)
        if self.order:
            return

        if self.time_elapse > self.params.lead + self.params.range:
            past_val = self.meta[-self.params.range]
            curr_val = self.meta[0]
            #Check existing positions in market
            if not self.position:
                past_val = self.meta[-1*self.params.lead - self.params.range]
                curr_val = self.meta[-1*self.params.lead]
                if (curr_val- past_val)/past_val > self.params.pct_chng:
                    self.log(f'BUY CREATE {self.data[0]:2f}, Metaculus: {self.meta[0]},{self.meta[-1]} ')
                    self.order = self.buy(data=self.datas[0])

            
            elif (curr_val- past_val)/past_val < -1*self.params.pct_chng:
                self.log(f'CLOSE CREATE {self.data[0]:2f}, Metaculus: {self.meta[0]},{self.meta[-1]}')
                self.order = self.close(data=self.datas[0])

class Metaculus_lead_VXX(bt.Strategy):


    params = (("lead", 11),("pct_chng", 0.2),("range", 5) )
    
    def log (self, txt, dt = None):
        dt = dt or self.datas[0].datetime.date(0)
        #print('%s, %s' % (dt.isoformat(), txt))
        
    
    def __init__(self):
        self.data = self.data0.close
        self.meta=self.data1.close
        self.order = None
        self.init_val = self.broker.getvalue()
        self.underwater = 0
        self.time_elapse = 0
        

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            #log if buy
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
            #log if sell
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
            self.bar_executed = len(self)
            
        #Log if order didnt go through
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            
        #reset order
        self.order = None
    
    def next(self):
        self.time_elapse = self.time_elapse + 1
        pnl =  self.broker.getvalue() - self.init_val
        if pnl < 0:
            self.underwater = self.underwater + 1
        
        #check for open orders (limit to one trade at a time)
        if self.order:
            return

        if self.time_elapse > self.params.lead + self.params.range:
            past_val = self.meta[-self.params.range]
            curr_val = self.meta[0]
            #Check existing positions in market
            if not self.position:
                past_val = self.meta[-1*self.params.lead - self.params.range]
                curr_val = self.meta[-1*self.params.lead]
                if (curr_val- past_val)/past_val > self.params.pct_chng:
                    self.log(f'BUY CREATE {self.data[0]:2f}, Metaculus: {self.meta[0]},{self.meta[-1]} ')
                    self.order = self.buy(data=self.datas[0])

            
            elif (curr_val- past_val)/past_val < -1*self.params.pct_chng:
                self.log(f'CLOSE CREATE {self.data[0]:2f}, Metaculus: {self.meta[0]},{self.meta[-1]}')
                self.order = self.close(data=self.datas[0])

#Incomplete
class Metaculus_BOLL(bt.Strategy):

    # Entry Critria:
    #     - Long:
    #         - Price closes below the lower band
    #         - Stop Order entry when price crosses back above the lower band
    #     - Short:
    #         - Price closes above the upper band
    #         - Stop order entry when price crosses back below the upper band
    # Exit Critria
    #     - Long/Short: Price touching the median line

    params = (
        ("period", 20),
        ("devfactor", 2),
        ("size", 20),
        ("debug", False)
        )
    
    def __init__(self):
        self.boll = bt.indicators.BollingerBands(period=self.p.period, devfactor=self.p.devfactor)
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            #log if buy
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
            #log if sell
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
            self.bar_executed = len(self)
            
        #Log if order didnt go through
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
            
        #reset order
        self.order = None
    
    def next(self):
 
        orders = self.broker.get_orders_open()
 
        # Cancel open orders so we can track the median line
        if orders:
            for order in orders:
                self.broker.cancel(order)
 
        if not self.position:
 
            if self.data0.close > self.boll.lines.top:
 
                self.sell(exectype=bt.Order.Stop, price=self.boll.lines.top[0], size=self.p.size)
 
            if self.data.close < self.boll.lines.bot:
                self.buy(exectype=bt.Order.Stop, price=self.boll.lines.bot[0], size=self.p.size)
 
 
        else:
 
 
            if self.position.size > 0:
                self.sell(exectype=bt.Order.Limit, price=self.boll.lines.mid[0], size=self.p.size)
 
            else:
                self.buy(exectype=bt.Order.Limit, price=self.boll.lines.mid[0], size=self.p.size)
  