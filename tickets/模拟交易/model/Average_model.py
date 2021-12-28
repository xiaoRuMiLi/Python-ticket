# -*- coding:utf8 -*-
import numpy as np
import pymysql
import sys
sys.path.append("..")
from model.Base_model import Base_model
from config import *
#.代表当前目录，..代表上一层目录，...代表上上层目录。
class Average_model(Base_model):
    datas = []
    cols = []
    col_name = {
    'date': 0,
    'stock':1,
    'open': 2,
    'close': 3,
    'high': 4,
    'low': 5,
    'vol': 6,
    'amount': 7,
    'pre_close':8,
    'amt_change':9,
    'pct_change':10
    }
    def __init__( self, db, in_code, start_dt, end_dt ):
        # 建立数据库连接，获取日线基础行情(开盘价，收盘价，最高价，最低价，成交量，成交额)
        super().__init__(db)
        self.cols = self.column(self.get_datas( in_code, start_dt,end_dt ))
        self.date_col = self.cols[self.col_name['date']]
        # 取收盘价列表
        self.close_col = self.cols[self.col_name['close']]
        # print( self.cols )
        # ans = self.collect_data(in_code,start_dt,end_dt)

    # 取均线，默认为5日
    # dt str 日期
    # days 取几日均线
    # return list [5,10,20,60]
    def get_avg_line ( self, dt, days = [5,10,20,60], datas = [] ):
        ndatas = datas
        if not datas:
            ndatas = self.datas
        column = self.column(ndatas)
        # 取日期列表
        days_list = column[self.col_name['date']]
        # 取收盘价列表
        close_list = column[self.col_name['close']]
        # 取出对应日期的索引
        # index 必须加1，因为切片，【0:4】相当于从0开始取到索引4的元素，但是不包括4
        index = days_list.index( dt ) + 1
        # 切片
        rdict = []
        for i in range(len(days)):
            num = days[i]
            nlist = close_list[index-num if index-num else 0: index]
            total = sum(nlist)
            price = total/len(nlist)
            # 保留两位小数
            price = ('%.2f' % price)
            rdict.append(price)
        return rdict

    ##
    # 格式化数据 返回适应机器学习的数据
    # arr 数组型数据
    # return dict
    def format_datas ( self, arr ):
        pass
    #
    # 判断某天的均线的趋势
    #  days_ago int 现在与前几天比较
    #  days int 几日均线
    #  return 1 or -1 1均线向上趋势，-1 均线向下趋势
    def get_avg_moving ( self, dt, days_ago , days ):
        pass

    # 取成交量均线
    def get_vol_avg_line ( self, dt, days ):
        pass

    # 取成交量趋势
    def get_vol_avg_moving ( self, dt, days_ago, days ):
        pass

    # 取两条均线的状态,如果前一天短期均线没有上穿今日上穿则返回1 下穿返回-1 或没有相交返回0 失败返回0
    # dt str 日期
    # avg_line1 int 短期均线
    # avg_line2 int 长期均线
    # return 1 均线1上穿均线2 -1 均线1下穿均线2
    def is_put_on ( self, dt, avg_line1, avg_line2 ):
        index = self.date_col.index(dt)
        if index <= 0:
            return 0
        # 取当日均线
        mas = self.get_avg_line(dt,[avg_line1,avg_line2])
        # 取前一天均线
        las = self.get_avg_line(self.date_col[index-1],[avg_line1,avg_line2])
        ma1 = mas[0]
        ma2 = mas[1]
        la1 = las[0]
        la2 = las[1]
        if ma1 > ma2 and la2 > la1:
            return 1
        if ma1 < ma2 and la1 > la2:
            return -1
        else:
            return 0

    def get_datas ( self, in_code, start_dt, end_dt ):
        query =  "SELECT * FROM stock_all a where stock_code = '%s' and state_dt >= '%s' and state_dt <= '%s' order by state_dt asc" % (in_code, start_dt, end_dt)
        self.cursor.execute( query )
        datas = self.cursor.fetchall()
        if len( datas ) == 0:
            # raise() raise Exception("抛出一个异常")
            # 用raise语句来引发一个异常。异常/错误对象必须有一个名字，且它们应是Error或Exception类的子类。
            raise Exception
        self.datas = datas
        return self.datas

    def collect_data(self,in_code,start_dt,end_dt):
        # 建立数据库连接，获取日线基础行情(开盘价，收盘价，最高价，最低价，成交量，成交额)
        db = pymysql.connect(host=MYSQL.host, user=MYSQL.user, passwd=MYSQL.passwd, db=MYSQL.db, charset=MYSQL.charset)
        cursor = db.cursor()
        sql_done_set = "SELECT * FROM stock_all a where stock_code = '%s' and state_dt >= '%s' and state_dt <= '%s' order by state_dt asc" % (in_code, start_dt, end_dt)
        cursor.execute(sql_done_set)
        done_set = cursor.fetchall()
        if len(done_set) == 0:
            raise Exception
        self.date_seq = []
        self.open_list = []
        self.close_list = []
        self.high_list = []
        self.low_list = []
        self.vol_list = []
        self.amount_list = []
        for i in range(len(done_set)):
            self.date_seq.append(done_set[i][0])
            self.open_list.append(float(done_set[i][2]))
            self.close_list.append(float(done_set[i][3]))
            self.high_list.append(float(done_set[i][4]))
            self.low_list.append(float(done_set[i][5]))
            self.vol_list.append(float(done_set[i][6]))
            self.amount_list.append(float(done_set[i][7]))
        cursor.close()
        db.close()
        # 将日线行情整合为训练集(其中self.train是输入集，self.target是输出集，self.test_case是end_dt那天的单条测试输入)
        self.data_train = []
        self.data_target = []
        self.data_target_onehot = []
        self.cnt_pos = 0
        self.test_case = []
        # print('self.open_list',self.open_list)
        # Python中提供了list容器，可以当作数组使用。但列表中的元素可以是任何对象，因此列表中保存的是对象的指针，这样一来，为了保存一个简单的列表[1,2,3]。就需要三个指针和三个整数对象。对于数值运算来说，这种结构显然不够高效。
        # Python虽然也提供了array模块，但其只支持一维数组，不支持多维数组(在TensorFlow里面偏向于矩阵理解)，也没有各种运算函数。因而不适合数值运算。
        # NumPy的出现弥补了这些不足。numpy.array 实际上就把整个数作为一个对象，一个内存指针有返回的对象有dtype 属性，指他的类型

        for i in range(1,len(self.close_list)):
            #　将上一天开盘价，收市价等作为数组的元素
            train = [self.open_list[i-1],self.close_list[i-1],self.high_list[i-1],self.low_list[i-1],self.vol_list[i-1],self.amount_list[i-1]]
            # 打包成二维数组
            self.data_train.append(np.array(train))
            # 如果当日收盘价大于上一日收盘价，target记录为1.0
            if self.close_list[i]/self.close_list[i-1] > 1.0:
                self.data_target.append(float(1.00))
                self.data_target_onehot.append([1,0,0])
            else:
                self.data_target.append(float(0.00))
                self.data_target_onehot.append([0,1,0])
        self.cnt_pos =len([x for x in self.data_target if x == 1.00])
        # 取时间段中最后一天的内容数组打包成numpy
        self.test_case = np.array([self.open_list[-1],self.close_list[-1],self.high_list[-1],self.low_list[-1],self.vol_list[-1],self.amount_list[-1]])
        # 所有交易日天数的二维数组，这是其中一个[[3.3050000e+01 3.3210000e+01 3.3350000e+01 3.2560000e+01 5.5441000e+04 1.8252611e+05]
        self.data_train = np.array(self.data_train)
        # 每一日是否上涨的数组
        self.data_target = np.array(self.data_target)
        return 1
if __name__ == '__main__':
    db = pymysql.connect(host=MYSQL.host, user=MYSQL.user, passwd=MYSQL.passwd, db=MYSQL.db, charset=MYSQL.charset)
    avg = Average_model(db,'002049.SZ','2010-03-01','2011-06-30')
    avgLine = avg.get_avg_line('2011-02-01')
    print(avgLine)
    is_puton = avg.is_put_on('2011-03-30',5,10)
    print('is_puton',is_puton)

