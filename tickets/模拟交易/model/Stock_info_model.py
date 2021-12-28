import numpy as np
import pymysql
import sys
sys.path.append("..")
from model.Stock_all_model import Stock_all_model
from config import *
class Stock_info_model(Stock_all_model):
    table = 'stock_info'
    def __init__( self, db ):
        super().__init__(db)

    # 从all库移交数据过来
    #
    def get_stocks_form_stock_all( self, stock_pool: list, start_dt = '1970-01-01',end_dt='2035-01-01' )->bool:
        self.empty()
        in_str = '('
        for x in range(len(stock_pool)):
            if x != len(stock_pool)-1:
                in_str += str('\'') + str(stock_pool[x])+str('\',')
            else:
                in_str += str('\'') + str(stock_pool[x]) + str('\')')
        print( 'in_str is %s'%(in_str))
        # 将stock_all 中包含股票池中数据拷贝到stock_info 中来，这个地方注意资源表中的字段如果含有拷贝表中么没有的字段则会报错，要选择性拷贝 指定字段可以(字段一，字段二)
        sql_insert = "insert into stock_info (open, close,state_dt,stock_code,high,low,vol,amount,pre_close,amt_change,pct_change) select open, close,state_dt,stock_code,high,low,vol,amount,pre_close,amt_change,pct_change from stock_all a where a.stock_code in %s and state_dt between '%s' and '%s'"%(in_str,start_dt,end_dt)
        res = self.execute(sql_insert)

        return res

if __name__ == '__main__':
    db = pymysql.connect(host=MYSQL.host, user=MYSQL.user, passwd=MYSQL.passwd, db=MYSQL.db, charset=MYSQL.charset)
    stock_info = Stock_info_model(db)
    stock_info.empty()
    stock_info.get_stocks_form_stock_all(['002051.SZ','603912.SH'])