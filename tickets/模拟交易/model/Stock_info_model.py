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
    def get_stocks_form_stock_all( self, stock_pool: list )->bool:
        self.empty()
        in_str = '('
        for x in range(len(stock_pool)):
            if x != len(stock_pool)-1:
                in_str += str('\'') + str(stock_pool[x])+str('\',')
            else:
                in_str += str('\'') + str(stock_pool[x]) + str('\')')
        print( 'in_str is %s'%(in_str))
        # 将stock_all 中包含股票池中数据拷贝到stock_info 中来
        sql_insert = "insert into stock_info(select * from stock_all a where a.stock_code in %s)"%(in_str)
        res = self.execute(sql_insert)

        return res

if __name__ == '__main__':
    db = pymysql.connect(host=MYSQL.host, user=MYSQL.user, passwd=MYSQL.passwd, db=MYSQL.db, charset=MYSQL.charset)
    stock_info = Stock_info_model(db)
    stock_info.empty()
    stock_info.get_stocks_form_stock_all(['002051.SZ','603912.SH'])