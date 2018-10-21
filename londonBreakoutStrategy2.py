import clr
clr.AddReference("System")
clr.AddReference("QuantConnect.Algorithm")
clr.AddReference("QuantConnect.Indicators")
clr.AddReference("QuantConnect.Common")

from System import *
from QuantConnect import *
from QuantConnect.Algorithm import *
from QuantConnect.Indicators import *
from QuantConnect.Orders import *
from QuantConnect.Data import *
from QuantConnect.Data.Market import QuoteBar
from QuantConnect.Data.Consolidators import *
from datetime import timedelta
import decimal as d
import time

class Test(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2014,5,1)    #Set Start Date
        self.SetEndDate(2014,5,14)      #Set End Date 
        self.SetCash(100000)             #Set Strategy Cash
        self.pair = self.AddForex("EURUSD", Resolution.Second,Market.FXCM).Symbol
        self.Consolidate(self.pair,Resolution.Hour,self.HourEurUsdBarHandler)
        self.sma50 = self.SMA(self.pair,50,Resolution.Hour)
        self.sma200 = self.SMA(self.pair,200,Resolution.Hour)

        self.__last = None
        self.buyTicket = None
        self.sellTicket = None
        self.trailingTicket = None
        self.stopTicket = None
        self.high = None
        self.low = None
        self.trigger1 = d.Decimal(0.00001)
        self.trigger2 = d.Decimal(0.0005)
        self.percent1 = d.Decimal(1.01)
        self.percent2 = d.Decimal(1.02)
        self.quantity = 10000
        self.Schedule.On(self.DateRules.Every(DayOfWeek.Monday,DayOfWeek.Tuesday,DayOfWeek.Wednesday,DayOfWeek.Thursday,DayOfWeek.Friday), \
                         self.TimeRules.At(3,00),self.SpecificTime0)
        self.Schedule.On(self.DateRules.Every(DayOfWeek.Monday,DayOfWeek.Tuesday,DayOfWeek.Wednesday,DayOfWeek.Thursday,DayOfWeek.Friday), \
                         self.TimeRules.At(7,00),self.SpecificTime1)

    def OnData(self, data):
#        if self.high != None and self.low != None:
        pass

    def HourEurUsdBarHandler(self, consolidated):
#        self.Log("Open  "+str(consolidated.Open))
#        self.Log("high  "+str(consolidated.High))
#        self.Log("low   "+str(consolidated.Low))
#        self.Log("close "+str(consolidated.Close))
        self.high = consolidated.High
        self.low = consolidated.Low

        pass

    def SpecificTime0(self):
#        self.Log("highS "+str(self.high))
#        self.Log("lowS  "+str(self.low))
        if not self.sma200.IsReady: return
        if self.sma50 > self.sma200:
#            self.Log("high       "+str(self.high))
#            self.Log("low        "+str(self.low))
            self.buyTicket = self.LimitOrder(self.pair, \
                                             self.quantity, \
                                             round(self.high + self.trigger1,5))
#            self.Log("high+t1    "+str(self.high + self.trigger1))
            self.stopTicket = self.StopMarketOrder(self.pair, \
                                                   -self.quantity, \
                                                   round(self.low,5))
#            self.Log("lowStop    "+str(self.low))
            self.trailingTicket = self.LimitOrder(self.pair, \
                                                  -self.quantity, \
                                                  round(self.high + self.trigger1 + self.trigger2,5))
#            self.Log("high+t1+t2 "+str(self.high + self.trigger1 + self.trigger2))
#            self.Log(" ")
        else:
            self.sellTicket = self.LimitOrder(self.pair, \
                                              -self.quantity, \
                                              round(self.low,5))
            self.stopTicket = self.StopMarketOrder(self.pair, \
                                                   self.quantity, \
                                                   round(self.high,5))
            self.trailingTicket = self.LimitOrder(self.pair, \
                                                  self.quantity, \
                                                  round(self.low - self.trigger2,5))

    def SpecificTime1(self):
        self.buyTicket = None
        self.sellTicket = None
        self.stopTicket = None
        self.limitTicket = None
        self.high = None
        self.low = None

    def OnOrderEvent(self, orderEvent):
        order = self.Transactions.GetOrderById(orderEvent.OrderId)
        self.Debug("{0}: {1}: {2}".format(order.Price, order.Type, orderEvent))
        pass
