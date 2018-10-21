'''
London breakout strategy.

TODO:   Implement take profit
        Tighten stoploss
        Determine trend
        Comments
'''
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

class LondonBreakoutStrategy(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2014,5,5)    #Set Start Date
        self.SetEndDate(2014,5,10)      #Set End Date 
        self.SetCash(100000)             #Set Strategy Cash
        self.pair = self.AddForex("EURUSD", Resolution.Second).Symbol
        self.Consolidate(self.pair,Resolution.Hour,self.HourEurUsdBarHandler)

        # define our 30 minute trade bar consolidator. we can
        # access the 30 minute bar from the DataConsolidated events
        threeHourConsolidator = QuoteBarConsolidator(TimeSpan.FromHours(3))

        # attach our event handler. the event handler is a function that will
        # be called each time we produce a new consolidated piece of data.
        threeHourConsolidator.DataConsolidated += self.ThreeHourBarHandler

        # this call adds our 30 minute consolidator to
        # the manager to receive updates from the engine
        self.SubscriptionManager.AddConsolidator(self.pair,threeHourConsolidator)
        self.__last = None

        self.buyTicket = None
        self.sellTicket = None
        self.limitTicket = None
        self.stopTicket = None
        self.high = None
        self.low = None
        self.trigger = d.Decimal(0.0002)
        self.percent1 = d.Decimal(1.01)
        self.percent2 = d.Decimal(1.02)
        self.quantity = 1000
        self.Schedule.On(self.DateRules.EveryDay(self.pair), \
                         self.TimeRules.At(17,45),self.SpecificTime0)
        self.Schedule.On(self.DateRules.EveryDay(self.pair), \
                         self.TimeRules.At(20,00),self.SpecificTime1)

    def OnData(self, data):
        if self.high != None and self.low != None:
#            self.Debug("price "+str(data[self.pair].Price))
#            self.Debug("high  "+str(self.high))
#            self.Debug("low   "+str(self.low))
            if self.buyTicket == None and data[self.pair].Price > (self.high + self.trigger):

                self.buyTicket = self.MarketOrder(self.pair,self.quantity)

                self.limitTicket = self.LimitOrder(self.pair, \
                                                   -self.quantity, \
                                                   data[self.pair].Price * self.percent1)

                self.stopTicket = self.StopMarketOrder(self.pair, \
                                                       -self.quantity, \
                                                       self.low - self.trigger)

                self.sellTicket = 0
#                self.Debug("buy "+str(self.buyTicket))
            elif self.sellTicket == None and data[self.pair].Price < (self.low - self.trigger):

                self.sellTicket = self.MarketOrder(self.pair,-self.quantity)

                self.limitTicket = self.LimitOrder(self.pair, \
                                                   self.quantity, \
                                                   data[self.pair].Price / self.percent1)

                self.stopTicket = self.StopMarketOrder(self.pair, \
                                                       self.quantity, \
                                                       self.high + self.trigger)

                self.buyTicket = 0
#                self.Debug("sell "+str(self.sellTicket))
        else:
            pass

    def HourEurUsdBarHandler(self, consolidated):
        pass
#        self.Log("1 "+str(consolidated.Open))
#        self.Log("2 "+str(consolidated.High))
#        self.Log("3 "+str(consolidated.Low))
#        self.Log("4 "+str(consolidated.Close))

    def ThreeHourBarHandler(self, sender, consolidated):
        if self.__last != None: pass
#            self.Log("1 "+str(self.__last.Open))
#            self.Log("2 "+str(self.__last.High))
#            self.Log("3 "+str(self.__last.Low))
#            self.Log("4 "+str(self.__last.Close))
        self.__last = consolidated

    def SpecificTime0(self):
        self.high = self.__last.High
        self.low = self.__last.Low

#        self.Log("high "+str(self.high))
#        self.Log("low  "+str(self.low))
#        pass
#        self.buyTicket = self.StopLimitOrder(self.pair, 1000,
#                            round(self.high,5),
#                            round(self.high + self.atr.Current.Value,5))
#        self.sellTicket = self.StopLimitOrder(self.pair,-1000,
#                            round(self.low,5),
#                            round(self.low - self.atr.Current.Value,5))

    def SpecificTime1(self):
        self.buyTicket = None
        self.sellTicket = None
        self.stopTicket = None
        self.limitTicket = None
        self.high = None
        self.low = None

    def OnOrderEvent(self, orderEvent):
        order = self.Transactions.GetOrderById(orderEvent.OrderId)
        self.Debug("{0}: {1}: {2}".format(self.Time, order.Type, orderEvent))
        # Get open orders
#        openOrders = self.Transactions.GetOpenOrders()
        # Get all orders
#        orders = self.Transactions.GetOrders()
        # Get all orders tickets
#        openOrderTickets = self.Transactions.GetOrderTickets()
#        self.Debug("{0}: {1}".format(openOrders,openOrderTickets))
        pass
