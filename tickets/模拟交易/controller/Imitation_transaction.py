# -*- coding: utf-8 -*-
# @Author: Marte
# @Date:   2021-10-06 22:21:20
# @Last Modified by:   Marte
# @Last Modified time: 2021-11-12 23:29:52
import datetime
import tushare as ts
import pymysql
import sys
sys.path.append('..')
from model.Stocks_model import Stocks_model
from model.Stock_all_model import Stock_all_model
from model.Stock_info_model import Stock_info_model
from request.Tushare_request import Tushare_request
from model.Stocks_model import Stocks_model
from model.Capital_model import Capital_model
from model.Pool_model import Pool_model
# 使用的策略
from strategy.Trend import Trend
from config import *
from factor.Average_factor import Average_factor
class Imitation_transaction( object ):

    def __init__( self, stock_all: Stock_all_model, tushare: Tushare_request, stocks: Stocks_model , capital: Capital_model, stock_info: Stock_info_model, pool: Pool_model):
        self.stock_all_model = stock_all
        self.tushare = tushare
        self.stocks_model = stocks
        self.capital_model = capital
        self.stock_info_model = stock_info
        self.pool_model = pool


    """
        def demo(name: str, age: 'int > 0'=20)->str:  # ->str 表示该函数的返回值是str类型的
        以上是注解表达式的应用方法, 注解中最常用的就是  类(str 或 int )类型 和 字符串(如 'int>0')

        注解不会做任何处理, 只是存储在函数的__annotations__属性(1个字典)中   return 返回的值的注解

        对于注解, python不做检查, 不做强制, 不做验证, 什么操作都不做.  换而言之, 注释对python解释器没有任何意义, 只是为了方便使用函数的人
    """

    # ->str 表示该函数的返回值是str类型的
    def boot( self,stock ):

        self.capital_model.empty()
        self.pool_model.empty()
        self.stock_info_model.empty()

        # 收集对应的行情数据到数据库
        self.tushare.collect_history_datas([stock])
        self.stock_info_model.get_stocks_form_stock_all([stock])
        datas = self.stock_info_model.get_all({'stock_code': stock}, order_by = '"state_dt"')
        self.stock_info_model.set_datas(datas)
        print('self.stock_info_model.date_col:',self.stock_info_model.date_col)
        dates = self.stock_info_model.date_col
        # 创建一个策略模型
        trend = Trend()

        # 注册模型和注册因子
        trend.registe({stock: self.stock_info_model},[(Average_factor,100)])
        for i in range(len(dates)-60):

            date = dates[i+60]
            item = datas[i+60]
            # 经过策略预测的结果集
            rlist = trend.boot(date)
            # print(rlist) 对策略预测结果每只股票都进行对应的操作
            for it in rlist:
                stock_code = it['stock_code']
                # 交易方向
                act = it['act']
                # 交易量量
                vol = it['vol']
                # 策略预测的后期上涨概率
                percentage = it['percentage']
                # 执行买入操作
                if act == 1:
                    price = float(item[3])
                    self.capital_model.buy_stock( stock, price, 10000, date)
                # 执行卖出操作
                if act == -1:
                    price = float(item[3])
                    # 如果第一次为卖出操作，则跳过
                    if not self.capital_model.get_first({}):
                        continue
                    self.capital_model.sell_stock( stock, price, 100000, date)

    # 模拟复盘
    def imitation( self, stock_all: Stock_all_model ):
        pass



if __name__ == '__main__':

    db = pymysql.connect(host=MYSQL.host, user=MYSQL.user, passwd=MYSQL.passwd, db=MYSQL.db, charset=MYSQL.charset)
    sel = Imitation_transaction( Stock_all_model(db), Tushare_request(db), Stocks_model(db), Capital_model(db) ,Stock_info_model(db), Pool_model(db))
    sel.boot('601857.SH')
    Stock_all_model(db).close_db()