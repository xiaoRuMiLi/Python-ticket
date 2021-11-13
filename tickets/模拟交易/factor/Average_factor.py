# -*- coding: utf-8 -*-
# @Author: Marte
# @Date:   2021-10-30 22:23:55
# @Last Modified by:   Marte
# @Last Modified time: 2021-11-12 23:02:37
import sys
sys.path.append('..')
from model.Stock_all_model import Stock_all_model
from model.Stock_info_model import Stock_info_model
from factor.Factor import Factor
import numpy as np
import pymysql
from config import *
class Average_factor(Factor):

    # 短期涨跌幅
    short_price_range = 0.00

    # 长期股价涨跌幅
    long_price_range = 0.00

    # 最近横盘天数
    balance_days = 0

    # 股价短期振幅\
    short_price_amplitude = 0

    # 股价长期振幅
    long_price_amplitude = 0

    # 风险偏好 分为几个等级 0 正常， -1 谨慎 1 激进
    risk_appetite = 0
    # 购买权重构成
    buy_weight = {
        "shortMovingRange": 0.1,
        "longMovingRange": 0.1,
        'middleMovingRange': 0.2,
        "5AverageBias": 0.1,
        "inPassageway": 0.05,
        "amplitude": 0.1,
        "priceRange": 0.05,
        "isPutOn": 0.3
    }
    # 卖出权重构成
    sell_weight = {
        "shortMovingRange": 0.2,
        "longMovingRange": 0.1,
        'middleMovingRange': 0.1,
        "5AverageBias": 0.1,
        "inPassageway": 0.05,
        "amplitude": 0.1,
        "priceRange": 0.05,
        "isPutOn": 0.3
    }
    def __init__( self ):
        super().__init__()


    # 假设参数1的时间处于横盘趋势中，取横盘天数,返回该日期前连续横盘天数
    # dt, str 目标日期
    # avg_num int 以某天均线为标准
    # price_range float 参数2 均线在百分之多少波动范围会被识别成连选横盘，该数值越大返回天数就会越多，越对波动不敏感
    # return int 返回计算后得到的天数
    def get_balance_days( self, dt ,avg_num = 60, price_range = 5):
        rlist = self.stomod.get_balance_days( dt, avg_num, price_range)
        return rlist

    # 判断趋势
    # dt 判断的日期
    # type str 类型长期或中期或短期，有几个可选值 SHORT MIDDLE LONG
    # return tuple (涨跌幅，)涨跌幅为0表示横盘，并不是绝对意义的涨跌幅=0，只是根据横盘条件判断（涨跌幅在?百分之内）
    def get_trend( self, dt , typ = "MIDDLE"):
        # 用来判断上涨或下跌的因子
        factor = (20,10,5,3,2,1)
        # 用来判断横盘的标的均线
        avg_num = 60
        # 用来判断横盘的涨跌幅区间百分之
        price_range = 5

        if typ == "MIDDLE":
            factor = (30,20,10,5,3,2,1)
            avg_num = 30
            price_range = 5
        if typ == "SHORT":
            factor = (7,6,5,3,2,1)
            avg_num = 10
            price_range = 3
        if typ == "LONG":
            factor = (90,60,50,40,30,20,10,5,3,2,1)
            avg_num = 90
            price_range = 10
        #横盘天数
        balance_days = self.get_balance_days(dt,avg_num,price_range)

        # 取最近一个趋势时间
        resu = self.stomod.get_price_moving_start(dt,factor, wrong_time = 1)

        # 取最近趋势持续天数
        rdays = self.stomod.get_days_by_two_date(resu, dt)
        days = len(rdays)
        # 取累计涨跌幅
        price_range = self.stomod.get_price_total(dt, days)

        trend = 0 if len(balance_days) > days else price_range

        if len(balance_days) > days:
            return  (0, len(balance_days),balance_days[-1],balance_days[0])
        else:
            return (price_range, days, rdays[0],rdays[-1])



    # 注册
    def register( self, model):
        self.stomod = model

    # 买入指标分析,注册进策略之后会被自动调用，用来对买进行预测
    # 返回一个元祖（ int后市下跌概率百分比，bool是否应该买入）
    def buying( self, dt ):
        o = self.stomod
        # 收盘价
        close = o.close_col[o.date_col.index(dt)]
        # 长期趋势
        ltuple = self.get_trend(dt,typ="LONG")
        # 中期走势
        mtuple = self.get_trend(dt,typ="MIDDLE")
        # 短期走势
        stuple = self.get_trend(dt,typ="SHORT")
        # 中期趋势持续天数
        mdays = mtuple[1]
        sdays = stuple[1]
        # 股价相较于5-60日均线乖离率
        bias = o.get_bias_from_avg_line(dt,days=(60,20,10,5))
        # 取股价通道以短期期趋势持续天数作为基准
        passageway = o.get_avg_passageway(dt,sdays,1)[0]
        # 股价短期振幅平均值，任然以短期为基准
        amplitude = o.get_avg_amplitude(dt,sdays)
        # 股价平均涨跌幅， 以短期趋势为基准
        price_range = o.get_avg_price_range(dt,sdays)
        # 短期均线是否上穿长期均线
        is_put_on = o.is_put_on(dt,1,60)

        # 根据本数据和self。weight计算得到一个上涨概率百分比
        result = {
        "shortMovingRange": stuple[0] > 0, #短期趋势向上
        'middleMovingRange': mtuple[0] >= 0, # 中期趋势向上或者平行
        "longMovingRange": ltuple[0] >= 0, # 长期趋势平行或向上
        "5AverageBias": float(bias[3]) >=0,# 5日均线上运行
        "inPassageway": close < float(passageway[0]) and close > float(passageway[1]), # 股价在中期趋势通道运行
        "amplitude": amplitude < 4, # 股价中期平均振幅为小振幅
        "priceRange": price_range > 0, # 股价短期平均涨幅为正，意思是上涨
        "isPutOn": is_put_on > 0 # 股价于当日上穿60天均线
        }
        data = {
        "shortMovingRange": stuple, #短期趋势向上
        'middleMovingRange': mtuple, # 中期趋势向上或者平行
        "longMovingRange": ltuple, # 长期趋势平行或向上
        "AverageBias": bias,# 5日均线上运行
        "inPassageway": passageway, # 股价在中期趋势通道运行
        "amplitude": amplitude, # 股价中期平均振幅为小振幅
        "priceRange": price_range, # 股价短期平均涨幅为正，意思是上涨
        "isPutOn": is_put_on # 股价于当日上穿60天均线
        }

        r = self.calculation_probability(result,wei = self.buy_weight)
        # print(dt)
        # print( {"probability": r, "result": result, "data": data})
        return {"probability": r, "result": result, "data": data}
    # 卖出指标
    def selling( self, dt):
        o = self.stomod
        # 收盘价
        close = o.close_col[o.date_col.index(dt)]
        # 长期趋势
        ltuple = self.get_trend(dt,typ="LONG")
        # 中期走势
        mtuple = self.get_trend(dt,typ="MIDDLE")
        # 短期走势
        stuple = self.get_trend(dt,typ="SHORT")
        # 中期趋势持续天数
        mdays = mtuple[1]
        sdays = stuple[1]
        # 股价相较于5-60日均线乖离率
        bias = o.get_bias_from_avg_line(dt,days=(60,20,10,5))
        # 取股价通道以短期期趋势持续天数作为基准
        passageway = o.get_avg_passageway(dt,sdays,1)[0]
        # 股价短期振幅平均值，任然以短期为基准
        amplitude = o.get_avg_amplitude(dt,sdays)
        # 股价平均涨跌幅， 以短期趋势为基准
        price_range = o.get_avg_price_range(dt,sdays)

        is_put_on = o.is_put_on(dt,1,60)
        if float(bias[0]) > 10:
            # # 如果和60天均线乖离率大于10%  ，那么下穿20天均线反馈卖出指标
            is_put_on = o.is_put_on(dt,1,20)

            if float(bias[1]) > 20:
                # # 如果和20天均线乖离率大于20%  ，那么下穿10天均线反馈卖出指标
                is_put_on = o.is_put_on(dt,1,10)
        # 根据本数据和self。weight计算得到一个上涨概率百分比
        result = {
        "shortMovingRange": stuple[0] < 0, #短期趋势向下
        'middleMovingRange': mtuple[0] <= 0, # 中期趋势向下或者平行
        "longMovingRange": ltuple[0] <= 0, # 长期趋势平行或向下
        "5AverageBias": float(bias[3]) <=0,# 5日均线下运行
        "inPassageway": close < float(passageway[1]) , # 股价在短期趋势通道下运行
        "amplitude": amplitude > 3, # 股价中期平均振幅为大振幅
        "priceRange": price_range < 0, # 股价短期平均涨幅为负，意思是下跌
        "isPutOn": is_put_on < 0 # 股价于当日下穿60天均线
        }
        data = {
        "shortMovingRange": stuple,
        'middleMovingRange': mtuple,
        "longMovingRange": ltuple,
        "AverageBias": bias,
        "inPassageway": passageway,
        "amplitude": amplitude,
        "priceRange": price_range,
        "isPutOn": is_put_on
        }

        r = self.calculation_probability(result,wei = self.sell_weight)
        # print( {"probability": r, "result": result, "data": data})
        return {"probability": r, "result": result, "data": data}


    def is_after_rising( self):

        pass
    # 根据buying返回值计算成功概率
    def calculation_probability( self, o, wei):
        res = 0.00
        for key in wei:
            res += float(wei[key]) if key in o.keys() and o[key] else 0.00
        return float('%.3f'%res) * 100



    # 股价是否在某条均线上运行
    #
    # 前期是否经过长时间的下跌
    #
    # 股价属于哪一种走势

    def boot( self,dt ):
        pass


if __name__ == "__main__":

    db = pymysql.connect(host=MYSQL.host, user=MYSQL.user, passwd=MYSQL.passwd, db=MYSQL.db, charset=MYSQL.charset)
    stock_all = Stock_all_model(db)
    # data = stock_all.get_data_on_date('002049.SZ','2010-01-14')
    # print(data)
    avg = Stock_all_model(db)
    avg.get_datas('600089.SH','2018-10-18','2021-10-09')
    o = Average_factor()
    o.register(avg)
    # print( avg.cols )
    '''# ans = self.collect_data(in_code,start_dt,end_dt)
    avgLine = avg.get_avg_line('2016-04-20')
    print(avgLine)
    is_puton = avg.is_put_on('2016-04-20',5,60)
    print('is_puton',is_puton)

    print(avg.get_data_on_date('002051.SZ','2016-04-20'))'''

    #print( avg.get_avg_amplitude('2021-10-08'))
    rlist = []
    for i in range(len(avg.date_col)-60):
        # 缩后60天取日期
        dt = avg.date_col[i+60]
        print(dt)
        o.buying(dt)
        o.selling(dt)

    last = (0,)
    days = 0
    result = []
    for i in rlist:
        if i[0] > 0:
            if last[0] > 0 and int(i[1]) > days:
                days = i[1]
                last = i
            if last[0] <=0:
                result.append(last)
                last = i
                days = i[1]

        if i[0] == 0:
            if last[0] == 0 and int(i[1]) > days:
                days = i[1]
                last = i
            if last[0] != 0:
                result.append(last)
                last = i
                days = i[1]

        if i[0] == 0:
            if last[0] < 0 and int(i[1]) > days:
                days = i[1]
                last = i
            if last[0] < 0:
                result.append(last)
                last = i
                days = i[1]
    print(result)