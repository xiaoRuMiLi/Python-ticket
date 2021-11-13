import numpy as np
import pymysql
import sys
sys.path.append("..")
from model.Base_model import Base_model
from model.Pool_model import Pool_model
from config import *
from lib import dt
class Capital_model(Base_model):
    # 佣金比例
    charge_rate= CAPITAL.charge_rate
    col_name = {
    'capital':0,
    'money_lock':1,
    'money_rest':2,
    'deal_action':3,
    'stock_code':4,
    'deal_price':5,
    'stock_vol':6,
    'profit':7,
    'profit_rate':8,
    'bz':9,
    'state_dt':10,
    'seq':11
    }
    table = 'my_capital'
    field = ['*']
    def __init__( self, db , charge_rate=0.003):
        super().__init__(db)
        self.charge_rate = charge_rate
        self.pool = Pool_model(db)
    #记录买入某只股票，如果剩余现金不足以支付买入数量则取最大的数量来买入
    def buy_stock( self, stock, price, vol, dat="" ):
        val = self.get_first({},'seq','desc')
        if val:
            omoney_rest = '%.2f'%val[self.col_name['money_rest']]
        else:
            # 默认初始资金
            ocapital = CAPITAL.capital
            omoney_rest = CAPITAL.money_rest
            omoney_lock = CAPITAL.money_lock
        # print(ocapital,omoney_lock,omoney_rest)
        # 购买市值
        amount = float(price) * int(vol)
        # 手续费
        charge = float(amount) * float(self.charge_rate)
        #剩余资金 不够的操作
        if float(omoney_rest)-amount-charge < 0:
            # // 取整运算符 c=7//2 c=3
            nvol = int((float(omoney_rest) - charge) // price)
            # 如果少于100股则返回
            if nvol < 100:
                return False
            # 去除个位数和十位数
            nvol = int(str(nvol)[0:-2]) *100
            namount = float(price) * int(nvol)
            charge = float(namount) * float(self.charge_rate)
        else:
            nvol = vol
            namount = amount
        # print(charge)
        money_rest = float(omoney_rest) - float(namount) - charge
        # 加手续费后的单价
        nprice = (namount + charge)/int(nvol)
        date = dat
        if date == '':
            date = dt.get_cutten_timestr(True)

        dic = {
        'capital':0.00,
        'money_lock':0.00,
        'money_rest':money_rest,
        'deal_action':'1',
        'stock_code':stock,
        'deal_price':float(price),
        'stock_vol':int(nvol),
        'profit': -float(charge),
        'profit_rate': -(float(charge)/float(namount)),
        'state_dt':date,
        }
        res = self.insert_one(dic)
        if res:
            print(str(stock),float(price),int(nvol))
            self.pool.add_stock(str(stock),float(nprice),int(nvol))
            self.update_capital(date)
        return res

    # 记录卖出某只股票，如果股票池没有该股票不会成功，或者股票数量不足则会卖出库存的全部
    def sell_stock( self, stock, price, vol , dat=""):
        val = self.get_first({},'seq','desc')
        stock_pool = self.pool.get_first({'stock_code': stock})
        # 如果没有买入记录或库存记录则不会卖出
        print('val',val)
        print('stock_pool',stock_pool)
        if not val or not stock_pool:
            print('this is do ')
            return
        hold_vol = stock_pool[self.pool.field.index('hold_vol')]
        if int(hold_vol) <= 0 :
            return
        if int(hold_vol) < int(vol):
            nvol = int(hold_vol)
        else:
            nvol = vol
        omoney_rest = '%.2f'%val[self.col_name['money_rest']]
        # 出售市值
        amount = float(price) * int(nvol)
        # 手续费
        charge = float(amount) * float(self.charge_rate)
        date = dat
        if date == '':
            date = dt.get_cutten_timestr(True)
        # 取股票池股票均价
        pool_data = self.pool.get_first(str(stock))
        avg_buy_price = '%.2f'%float(pool_data[self.pool.col_name['buy_price']])
        money_rest = float(omoney_rest) + float(amount) - float(charge)
        # 计算盈利
        # print('卖价：%.2f X %i - %s X %i'%(price,nvol,avg_buy_price,nvol))
        profit = '%.2f'%float(float(price) * int(nvol) - float(avg_buy_price) * int(nvol) - charge)
        profit_rate = '%.2f'%float(float(profit) / (float(price) * int(nvol)))
        # print('sell',profit,profit_rate)
        dic = {
        'capital':0.00,
        'money_lock':0.00,
        'money_rest':money_rest,
        'deal_action':'-1',
        'stock_code':stock,
        'deal_price':float(price),
        'stock_vol':int(nvol),
        'profit': profit,
        'profit_rate': profit_rate,
        'state_dt':date,
        }
        res = self.insert_one(dic)
        if res:
            # 计入股票池
            self.pool.reduce_stock(str(stock),float(price),int(nvol))
            self.update_capital(date)
        return res

    # 更具某天股价更新总资产,只修改最后一条记录
    def update_capital( self, dat ):
        val = self.get_first({},'seq','desc')
        seq = val[self.col_name['seq']]
        omoney_rest = '%.2f'%val[self.col_name['money_rest']]
        amount = self.pool.get_market_value(str(dat))
        capital = amount + float(omoney_rest)
        query =  "UPDATE %s SET capital = %.2f, money_lock=%.2f WHERE seq = %i"%(self.table,capital,amount,seq)
        # query =  "UPDATE my_capital SET capital = 0.2, money_lock=2.00 WHERE seq = 122"
        self.cursor.execute(query)

if __name__ == '__main__':
    db = pymysql.connect(host=MYSQL.host, user=MYSQL.user, passwd=MYSQL.passwd, db=MYSQL.db, charset=MYSQL.charset)
    capital = Capital_model(db)
    dic = {
        'capital':0.1,
        'money_lock':1.0,
        'money_rest':2.33,
        'deal_action':'3',
        'stock_code':'002049.SZ',
        'deal_price':5.00,
        'stock_vol':6,
        'profit':7.0,
        'profit_rate':0.08,
        'bz':'9',
        'state_dt':'2021-09-01',

    }
    # capital.insert_one(dic)
    #res = capital.get_first({'profit':'7.0','bz':'9'},'seq','desc')
    # print(res)
    capital.empty()
    capital.buy_stock('002049.SZ',12.00,1000,'2010-01-04')
    capital.buy_stock('002049.SZ',12.00,1000,'2010-01-04')
    capital.buy_stock('002049.SZ',12.00,1000,'2010-01-04')
    capital.buy_stock('002049.SZ',12.00,1000,'2010-01-04')
    capital.buy_stock('002049.SZ',12.00,1000,'2010-01-04')
    # amount = capital.pool.get_market_value('2010-02-22')
    # print('amount',amount)
    capital.sell_stock('002049.SZ',12.10,100,'2010-01-06')
    capital.sell_stock('002049.SZ',12.10,1000,'2010-01-06')
    capital.sell_stock('002049.SZ',12.10,1000,'2010-01-06')
    capital.sell_stock('002049.SZ',12.10,1000,'2010-01-06')
    capital.sell_stock('002049.SZ',12.10,1000,'2010-01-06')
    capital.sell_stock('002049.SZ',12.10,100000,'2010-01-06')
    capital.update_capital('2010-01-06')
    capital.close_db()


