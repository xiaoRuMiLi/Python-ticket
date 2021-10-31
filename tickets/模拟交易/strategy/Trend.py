# -*- coding: utf-8 -*-
# @Author: Marte
# @Date:   2021-10-09 20:52:36
# @Last Modified by:   Marte
# @Last Modified time: 2021-10-30 21:29:08
import sys
sys.path.append('..')
from model.Stocks_model import Stocks_model
from model.Stock_all_model import Stock_all_model
from model.Stock_info_model import Stock_info_model
from request.Tushare_request import Tushare_request
from model.Stocks_model import Stocks_model
from model.Capital_model import Capital_model
from model.Pool_model import Pool_model
class Trend( object ):

    def __init__( self ):
        pass
    # 支持同时传入多个模型一起操作
    # models = { stock_code1: stock_info, tock_code1: stock_info }键名代表股票代码，键值是有股票代码历史数据的model该模型值继承自stock——all的模型
    def registe( self , models):
        self.models = models
        # self.sim = models[list(models.keys())[0]]

    # 判断策略
    # stock_code str 股票代码
    # date str 日期
    # return dict  返回进过本策略模型预测的预测结果
    def strategy( self , stock_code, date )-> dict:
        model = self.models[stock_code]
        # 2日均线上穿60日均线为条件
        is_put_on = model.is_put_on( date,2,60 )
        return {
            'stock_code': stock_code,
            #  操作方式 ，1 买入 -1 卖出 0 不动作
            'act': is_put_on,
            'vol': 10000,
            # 预测后期上涨概率百分比
            'percentage':50

        }



    # 被外部调用的方法
    # dt str 日期
    # return list 返回经过各个模型策略预测返回值组成的列表，
    def boot( self, dt)->list:
        rlist = []
        for i in self.models:
            stock_code = i
            res = self.strategy( stock_code, dt )
            rlist.append( res )

        return rlist


