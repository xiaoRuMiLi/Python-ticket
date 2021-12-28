# -*- coding: utf-8 -*-
# @Author: Marte
# @Date:   2021-09-13 20:31:08
# @Last Modified by:   Marte
# @Last Modified time: 2021-09-13 21:11:07
import tushare as ts
import pandas
import datetime
import pymysql
# ts.set_token('your token here')
# pro = ts.pro_api()
# # 设置tushare pro的token并获取连接
ts.set_token('2d8e71911ffec057ebde16aab0348714dfe8348f67ee89e2125877b8')
pro = ts.pro_api()
# data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
# print(data)

# 设定获取日线行情的初始日期和终止日期，其中终止日期设定为昨天。
start_dt = '20100101'
time_temp = datetime.datetime.now() - datetime.timedelta(days=1)
end_dt = time_temp.strftime('%Y%m%d')
# 建立数据库连接,剔除已入库的部分
db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
cursor = db.cursor()
# 设定需要获取数据的股票池
stock_pool = ['603912.SH','300666.SZ','300618.SZ','002049.SZ','300672.SZ']
total = len(stock_pool)
# 循环获取单个股票的日线行情
for i in range(len(stock_pool)):
    try:
        df = pro.daily(ts_code=stock_pool[i], start_date=start_dt, end_date=end_dt)
        # 打印进度
        print('Seq: ' + str(i+1) + ' of ' + str(total) + '   Code: ' + str(stock_pool[i]))