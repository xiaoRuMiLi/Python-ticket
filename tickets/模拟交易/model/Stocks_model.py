
import numpy as np
import pymysql
import sys
if '..' not in sys.path:
    sys.path.append('..')
from model.Base_model import Base_model
from config import *
# print(dir(Base_model))
class Stocks_model(Base_model):
    """docstring for ClassName"""
    table = 'model_stocks'
    field =(
    'ts_code',# str,# Y   TS代码
    'symbol',#  str ,#Y   股票代码
    'name',#    str ,#Y   股票名称
    'area',#    str ,#Y   地域
    'industry',#    ,#str Y   所属行业
    'fullname',#    ,#str N   股票全称
    'enname',#  str ,#N   英文全称
    'cnspell',# str ,#N   拼音缩写
    'market',#  str ,#Y   市场类型（主板/创业板/科创板/CDR）
    'exchange',#    ,#str N   交易所代码
    'curr_type',#   ,#str N   交易货币
    'list_status',# ,#str N   上市状态 L上市 D退市 P暂停上市
    'list_date',#   ,#str Y   上市日期
    'delist_date',# ,#str N   退市日期
    'is_hs' #str  N   是否沪深港通标的，N否 H沪股通 S深股通
    )

    def __init__( self, db ):
        super().__init__(db)


if __name__ == '__main__':
    db = pymysql.connect(host=MYSQL.host, user=MYSQL.user, passwd=MYSQL.passwd, db=MYSQL.db, charset=MYSQL.charset)
    stock = Stocks_model(db)
    dic = {'ts_code': '689009.SH', 'symbol': '689009', 'name': '九号公司-WD', 'area': '北京', 'industry': '摩托车', 'fullname': '九号有限公司', 'enname': 'Ninebot Limited', 'cnspell': 'jhgs-wd', 'market': 'CDR', 'exchange': 'SSE', 'curr_type': 'CNY', 'list_status': 'L', 'list_date': '20201029', 'delist_date': None, 'is_hs': None}
    stock.insert_one(dic)
