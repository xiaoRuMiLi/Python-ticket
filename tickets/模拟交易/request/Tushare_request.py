# -*- coding: utf-8 -*-
# @Author: Marte
# @Date:   2021-09-28 20:37:05
# @Last Modified by:   Marte
# @Last Modified time: 2021-10-11 20:54:44
import datetime
import tushare as ts
import pymysql
import sys
sys.path.append('..')
from model.Stocks_model import Stocks_model # 被引用的文件中，有引用其它文件的容易引起找不到文件的问题，原因是sys.path 是共用的，比如我这里的相对路径是本文件所在的路劲，那么被引用文件的相对路径是被引用文件的，但是当前文件会从当前路径去找被引用文件的引用文件，所以会报找不到模块，最好的解决方式是将根目录添加到sys。path.所有文件的引用都从根目录开始。
from config import *
class Tushare_request(object):
    # print('\n'.join(['%s:%s' % item for item in object.__dict__.items()]))
    # ts tushare 库
    # token tushare 申请的token
    def __init__( self, db ):
        self.ts = ts
        self.ts.set_token(TUSHARE.token)
        self.pro = self.ts.pro_api()
        self.db = db
        self.cursor = self.db.cursor()

    # 从tushare 下载历史数据到本地数据库
    # db
    # stock_pool ['str','str'] 股票池list
    # start_dt 开始时间，为空则代表该股票从上市开始当天开始
    def collect_history_datas(self, stock_pool, start_dt = None, end_dt = None ):
        self.stock_pool = stock_pool
        total_len = len(stock_pool)
        # 循环获取单个股票的日线行情
        for i in range(len(stock_pool)):
            stock = stock_pool[i]
            # 先删除以前有的数据
            query = 'DELETE FROM stock_all WHERE stock_code = "%s"'%stock
            self.cursor.execute(query)
            self.db.commit()

            nstart_dt = None
            nend_dt = end_dt
            if not start_dt:
                stocks_obj = Stocks_model(self.db)
                row = stocks_obj.get_first({"ts_code":stock})
                # print(row)
                # 这里有个坑，现在都不知道原因，马上对row进行元祖相关操作的话就会出错,放在try里面就能购调用
                try:
                    nstart_dt = stocks_obj.to_dict(row)['list_date']
                    # print(nstart_dt)
                except Exception as err:
                    print(err)
            if not end_dt:
                time_temp = datetime.datetime.now() - datetime.timedelta(days=1)
                nend_dt = time_temp.strftime('%Y%m%d')
            try:

                df = self.pro.daily(ts_code=stock, start_date=nstart_dt, end_date=nend_dt)
                # 打印进度
                print('Seq: ' + str(i+1) + ' of ' + str(total_len) + '   Code: ' + str(stock))
                #
                #输出数组的行和列数
                # print x.shape  #结果： (4, 3)
                #只输出行数
                # print x.shape[0] #结果： 4
                #只输出列数
                # print x.shape[1] #结果： 3
                c_len = df.shape[0]
                print(df)
            except Exception as aa:
                print(aa)
                print('No DATA Code: ' + str(i))
                continue
            for j in range(c_len):
                # 相当于倒叙
                # 简单来说，iloc（）和loc（）区别就在于前者是通过索引名来索引，后者通过索引值索引
                # 同时要注意，当一个DataFrame的索引是默认状态时，二者没有什么区别，因为索引值和索引名都是一样的
                resu0 = list(df.iloc[c_len-1-j])
                resu = []
                for k in range(len(resu0)):
                    if str(resu0[k]) == 'nan':
                        resu.append(-1)
                        resu0[key]
                    else:
                        resu.append(resu0[k])
                state_dt = (datetime.datetime.strptime(resu[1], "%Y%m%d")).strftime('%Y-%m-%d')
                try:
                    sql_insert = "INSERT INTO stock_all(state_dt,stock_code,open,close,high,low,vol,amount,pre_close,amt_change,pct_change) VALUES ('%s', '%s', '%.2f', '%.2f','%.2f','%.2f','%i','%.2f','%.2f','%.2f','%.2f')" % (state_dt,str(resu[0]),float(resu[2]),float(resu[5]),float(resu[3]),float(resu[4]),float(resu[9]),float(resu[10]),float(resu[6]),float(resu[7]),float(resu[8]))
                    self.cursor.execute(sql_insert)
                    self.db.commit()
                except Exception as err:
                    continue
    def collect_stocks_in_market( self ):
        field = (
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
        keys = ','.join(field)
        try:
            #查询当前所有正常上市交易的股票列表
            data = self.pro.stock_basic(exchange='', list_status='L', fields=keys)
            # print( data )
            # 取行数
            length = data.shape[0]
            # print ('length',length)
            stocks = Stocks_model(self.db)
            for i in range(length):
                # 倒序取行
                row = list(data.iloc[length - 1 - i])
                # 将两个列表组合成一个字典，如果两个列表长度不一，那么只取能购配对的部分，无论是key还是value 多余的元素会被省略
                dic = dict(zip(field,row))
                # print (dic)
                stocks.insert_one(dic)
        except Exception as err:
            print('collect_stocks_in_market is err',err)
    # 取交易所交易的日期列表
    # date_seq_star 开始日期
    # date_seq_end 结束日期
    # return list
    def get_in_market_date( self, date_seq_start, date_seq_end):

        # 建回测时间序列
        back_test_date_start = (datetime.datetime.strptime(date_seq_start, '%Y-%m-%d')).strftime('%Y%m%d')
        back_test_date_end = (datetime.datetime.strptime(date_seq_end, "%Y-%m-%d")).strftime('%Y%m%d')
        # 接口：trade_cal，可以通过数据工具调试和查看数据。描述：获取各大交易所交易日历数据,默认提取的是上交所
        # exchange  str Y   交易所 SSE上交所 SZSE深交所,cal_date str Y   日历日期,is_open    str Y   是否交易 0休市 1交易,pretrade_date  str N   上一个交易日
        df = self.pro.trade_cal(exchange_id='', is_open=1, start_date=back_test_date_start, end_date=back_test_date_end)
        print(df)
        # X[:,1] 取所有行的第1个数据
        date_temp = list(df.iloc[:, 1])
        # 获取时间段可以交易的号数列表
        date_seq = [(datetime.datetime.strptime(x, "%Y%m%d")).strftime('%Y-%m-%d') for x in date_temp]
        return date_seq




if __name__ == '__main__':

    db = pymysql.connect(host=MYSQL.host, user=MYSQL.user, passwd=MYSQL.passwd, db=MYSQL.db, charset=MYSQL.charset)
    # 设定获取日线行情的初始日期和终止日期，其中终止日期设定为昨天。
    start_dt = '20100101'
    time_temp = datetime.datetime.now() - datetime.timedelta(days=1)
    end_dt = time_temp.strftime('%Y%m%d')
    stock_pool = ['603912.SH', '300666.SZ', '300618.SZ', '002049.SZ', '300672.SZ']

    tush = Tushare_request( db )
    # print( tush )
    tush.collect_history_datas( stock_pool )
    # data = tush.get_stocks_in_market()

    # tush.collect_stocks_in_market()
    # res = tush.get_in_market_date('2019-01-01','2021-01-01')
    # print(res)
