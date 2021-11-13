import numpy as np
import pymysql
import sys

sys.path.append("..")
from model.Base_model import Base_model
from model.Stock_all_model import Stock_all_model
from config import *
class Pool_model(Base_model):
    """docstring for ClassName"""
    table = 'my_stock_pool'
    col_name = {
    'stock_code': 0,
    'buy_price':1,
    'hold_vol': 2,
    'hold_days': 3
    }
    field = ('stock_code','buy_price','hold_vol','hold_days')
    def __init__( self, db ):
        super().__init__(db)
    #
    # stock str
    # price float
    # vol int
    def add_stock( self, stock, price, vol ):
        ostock = self.get_first(stock)
        if ostock:
            ovol = int(ostock[self.col_name['hold_vol']])
            oprice = float(ostock[self.col_name['buy_price']])
            odays = int(ostock[self.col_name['hold_days']])
            # 取平均股价
            avg_price = (ovol * float(oprice) + price * int(vol))/(ovol+int(vol))
            query = "UPDATE my_stock_pool SET hold_vol='%i', buy_price='%.2f' where stock_code='%s' "%(ovol+int(vol), avg_price, stock)

        else:
            query = "INSERT INTO my_stock_pool(stock_code, buy_price, hold_vol) VALUES ('%s', '%.2f', '%i')" % (str(stock), float(price), int(vol) )

        self.execute(query)

    # 判断股票是否存在股票池中
    # return bool 存在返该股票在股票池的数据 不存在返回 false
    '''def get_first( self, stock ):
        query = "SELECT * from my_stock_pool where stock_code='%s'" %str(stock)
        print(query)
        self.cursor.execute(query)
        datas = self.cursor.fetchall()
        if len(datas) > 0:
            return datas[0]
        else:
            return False
    '''
    # turn bool
    def reduce_stock( self, stock, price, vol ):
        res = False
        ostock = self.get_first(stock)
        if ostock:
            ovol = int(ostock[self.col_name['hold_vol']])
            oprice = float(ostock[self.col_name['buy_price']])
            odays = int(ostock[self.col_name['hold_days']])
            nvol = vol
            if int(vol) > ovol:
                print('卖出数量大于持仓数量,按平仓操作')
                nvol = ovol
            # 卖出金额
            amount = float(price) * int(nvol)
            # 手续费
            charge = amount * CAPITAL.charge_rate
            # 求卖出后的新的持仓成本价
            if ovol-int(nvol) > 0:
                avg_price = (ovol * float(oprice) - amount + charge)/(ovol-int(nvol))
            else:
                avg_price = 0
            query = "UPDATE my_stock_pool SET hold_vol='%i', buy_price='%.2f' where stock_code='%s' "%(ovol-int(nvol), avg_price, stock)
            res = self.execute(query)
        return res
    # 取股票池所有股票的某个时间的市值
    # dat str 时间,
    # is_open bool default true 根据当日开盘价计算，false 根据收盘价计算
    def get_market_value( self, dat="", is_open=True ):
        datas = self.get_all_stock()
        # print('pool',datas)
        amount = 0
        if datas:
            stock_all = Stock_all_model(self.db)
            # print("stock_all",stock_all)
            for i in datas:
                stock_code = i[self.col_name['stock_code']]
                vol = int(i[self.col_name['hold_vol']])
                # print ('stock is %s , hold_val is %i, date is %s'%(stock_code,vol,dat))
                current_stock = stock_all.get_data_on_date(stock_code,str(dat))
                # print("current_stock",current_stock)
                current_date_price = 0.00
                if current_stock:
                    i_o = 'open'  if is_open else 'close'
                    current_date_price =  '%.2f'%current_stock[stock_all.field.index(i_o)]
                    amount += vol * float(current_date_price)
                else:
                    amount = 0
                    print('取全部市值出错')
                    raise Exception ("get_market_value is error")
                    break
                    # 跳出整个循环，不会再执行循环后面的内容
                    # continue:跳出本次循环，continue后面的代码不再执行，但是循环依然继续
        return amount

    # 取股票池中所有股票
    # return list or False like []
    def get_all_stock( self ):
        query = "SELECT * FROM %s WHERE hold_vol > 0"%self.table
        self.cursor.execute(query)
        datas = self.cursor.fetchall()
        if len(datas) > 0:
            return datas
        return False
if __name__ == '__main__':
    db = pymysql.connect(host=MYSQL.host, user=MYSQL.user, passwd=MYSQL.passwd, db=MYSQL.db, charset=MYSQL.charset)
    pool = Pool_model(db)
    pool.add_stock('002049.SZ',29.28,1000)
    # pool.reduce_stock('002049.SZ',50.28,400)
    pool.get_market_value('2012-01-05',True)
    # pool.empty()
