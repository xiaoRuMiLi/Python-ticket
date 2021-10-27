import numpy as np
import pymysql
import sys
sys.path.append("..")
from model.Base_model import Base_model
from config import *
class Stock_all_model(Base_model):

    datas = []
    cols = []
    table = 'stock_all'
    field = ['state_dt', 'stock_code', 'open', 'close', 'high', 'low', 'vol', 'amount', 'pre_close', 'amt_change', 'pct_change']
    def __init__( self, db ):
        super().__init__(db)

    # 取均线，默认为5日
    # dt str 日期
    # days 取几日均线
    # return list [5,10,20,60]
    def get_avg_line ( self, dt, days = [5,10,20,60], datas = [] ):
        ndatas = datas
        if not datas:
            ndatas = self.datas
        column = self.column(ndatas)
        # print(dt)
        # 取日期列表
        days_list = column[self.field.index('state_dt')]
        # 取收盘价列表
        close_list = column[self.field.index('close')]
        # 取出对应日期的索引
        # index 必须加1，因为切片，【0:4】相当于从0开始取到索引4的元素，但是不包括4
        index = days_list.index( dt ) + 1
        # 切片
        rdict = []
        for i in range(len(days)):
            num = days[i]
            nlist = close_list[index-num: index]
            total = sum(nlist)
            if(len(nlist) == 0):
                print('dt %s,index %i, num %i, total %.2f, length%i'%(dt,index,num,total,len(nlist)))

            price = total/len(nlist)
            # 保留两位小数
            price = ('%.2f' % price)
            rdict.append(float(price))
        return rdict
    # 往前取一定天数内股价的均线列表，【1号均线位置， 2号均线位置】
    # days 取多少天均线，
    # num 取多少天
    def get_avg_price( self, dt, days,num = 30 ):
        sindex = self.date_col.index( dt ) - num
        eindex = self.date_col.index( dt ) + 1
        rlist = []
        if eindex < sindex or sindex < days:
            return False
        for i in range(eindex - sindex):
            datas = self.close_col[sindex + i - days: sindex + i]
            total = sum(datas)
            price = total/len(datas)
            rlist.append(float('%.3f'%price))
            # print(self.date_col[sindex + i-days],'____',len(datas),'____',self.date_col[sindex + i])

        return rlist

    # 取运行通道，就是最高价和最低价组成的元祖列表
    # dt 日期
    # days 从日期前该天数 1 表示往前取一天和该天取平均值，取最高价和最低价的平均值，作为该日期通道的元祖（最高价，最低价）。
    # num 共返回多少天的通道值组成列表
    def get_avg_passageway( self, dt, days, num=30):
        high_col = self.get_col_datas('high')
        low_col = self.get_col_datas('low')
        sindex = self.date_col.index( dt ) - num
        eindex = self.date_col.index( dt )
        rlist = []
        if eindex < sindex or sindex < days:
            return False
        for i in range(eindex - sindex):
            high_datas = high_col[sindex + i - days + 1: sindex + i + 1]
            high_total = sum(high_datas)
            high_price = high_total/len(high_datas)

            low_datas = low_col[sindex + i - days + 1: sindex + i + 1]
            low_total = sum(low_datas)
            low_price = low_total/len(low_datas)

            rlist.append(  (float('%.3f'%high_price), float('%.3f'%low_price)))

            print(self.date_col[sindex + i-days + 1],'____',(float('%.3f'%high_price), float('%.3f'%low_price)),'____',self.date_col[sindex + i + 1])

        return rlist





    # 求一定时间周期内股票振幅平均值
    # 以本周期的最高价与最低价的差，除以上一周期的收盘价，再以百分数表示的数值。以日震幅为例，就是今天的最高价减去最低价，再除以昨收盘，再换成百分数。
    # dt 时间点 从该时间点向前取一定天数
    # days int 时间周期
    def get_avg_amplitude( self, dt, days=30):
        index = self.date_col.index(dt)
        if index <= days:
            return False
        dates = self.date_col[index-days +1: index+1]
        if len(dates) <= 0:
            return False
        rlist = []
        for i in dates:
            ind = self.date_col.index(i)
            before_close = self.get_col_datas('close')[ind-1]
            high = self.get_col_datas('high')[ind]
            low = self.get_col_datas('low')[ind]
            num = (float(high) - float(low))/float(before_close) * 100
            num = '%.3f'%num
            rlist.append(float(num))
            #print( 'before:%s,high:%s,low:%s,num:%s,date%s'%(before_close,high,low,num,i))
        val = sum(rlist)/len(rlist)
        return float('%.3f'%val)

    # 取一定时间股价涨跌幅平均数，其中涨的按正数计，10就相当于涨幅10%
    # days 是因子意思是取dt前days天数的的收盘价来计算平均涨跌幅
    def get_avg_price_range( self, dt, days = 30):
        index = self.date_col.index(dt)
        if index <= days:
            return False
        dates = self.date_col[index-days + 1: index+1]
        if len(dates) <= 0:
            return False
        rlist = []
        for i in dates:
            ind = self.date_col.index(i)
            before_close = self.get_col_datas('close')[ind-1]
            close = self.get_col_datas('close')[ind]
            num = (float(close) - float(before_close))/float(before_close)*100
            num = '%.3f'%num
            rlist.append(float(num))
            # print( 'before:%s,close:%s,num:%s,date%s'%(before_close,close,num,i))
        #print(rlist)
        val = sum(rlist)/len(rlist)
        # print( i, val)
        return float('%.3f'%val)

    # 获取指定的列数据，datas 默认是使用cols
    def get_col_datas( self, column_key,datas = None):
        ndatas = self.cols
        if isinstance(datas, list):
            ndatas = datas
        if column_key not in self.field:
            return False
        result = ndatas[self.field.index(column_key)]
        return result

    # 取指定时间的交易日,但不包括end_dt那一天
    def get_days_by_two_date( self, start_dt, end_dt )->list:
        sindex = int(self.date_col.index(start_dt))
        eindex = int(self.date_col.index(end_dt))
        rlist = self.date_col[sindex:eindex]
        return rlist

    # 取一定时间股价累计涨跌幅百分数,从参数dt 往前推days天数,dt这一天的收盘价除以days 天以前的收盘价 减去1 得到涨跌幅 正数代表上涨，负数代表下跌 1代表上涨100%，反之亦然
    def get_price_total( self, dt, days=10):
        index = int(self.date_col.index(dt))
        if index < days:
            raise Exception('function get_price_total index must greater than days')
        # 多一天要不就会取到比实际days多一天
        before = self.close_col[index-days+1]

        current = self.close_col[index]

        price_range = (current/before - 1)*100

        return float('%.3f'%price_range)
        # print(self.date_col[index-days+1])
        # print(self.date_col[index])
        # print(price_range)

    # 取参数1 时间的股票价格趋势，
    def get_current_moving( self, dt, factor = (60,50,40,30,20,10,5,3), wrong_time = 2 ):

        start_dt = self.get_price_moving_start( dt, factor )
        end_dt = dt
        lis = self.get_days_by_two_date(start_dt,dt)
        price_range = self.get_avg_price_range(dt,len(lis))
        avg_amplitude = self.get_avg_amplitude(dt,len(lis))
        price_total = self.get_price_total(dt,len(lis))
        return {
        'start_dt': start_dt,
        'end_dt': end_dt,
        'days': len(lis),
        'price_range': price_range,
        'avg_amplitude': avg_amplitude,
        'price_total': price_total
        }




    # 取指定时间以前的所有股票走势
    def get_all_price_moving( self,dt, factor = (20,10,5,3,2,1), wrong_time = 1):
        rlist = []
        def fun (dt, factor, wrong_time):
            res = self.get_current_moving(dt,factor,wrong_time)
            print(res)
            rlist.append(res)
            ndt = res['start_dt']
            if self.date_col.index(ndt) <= int(factor[0]):
                return
            ndt = self.date_col[self.date_col.index(ndt)-1]
            fun(ndt,factor,wrong_time)
        fun(dt,factor,wrong_time)
        # # 倒序列表 函数reversed 返回一个迭代对象，需要list化
        return list(reversed(rlist))

    # 根据股票走势数据寻找符合条件的波(条件中days：5 表示趋势连续天数不得小于5,price_total:10 表示要大于10, trend: 1，RAISE or  -1FALL 0 all)
    def get_price_raise_wave( self, datas, condition = {'days': 5, 'price_total': 10,'trend': 1}):
        price_total = condition['price_total']
        days = condition['days']
        trend = condition['trend']
        tup = ()
        if isinstance(datas, list):
            for i in range(len(datas) -1):
                item = datas[i]
                # 取下一个
                nex_item = datas[i+1]
                total = item['price_total']
                current_days = item['days']

                # 寻找上升波的逻辑
                # print(trend == 1 and total >= price_total and current_days >= days and nex_item['days'] >= days and nex_item['price_total'] < 0)
                if trend == 1 and total >= price_total and current_days >= days and nex_item['days'] >= days and nex_item['price_total'] < 0 and nex_item['price_total']>-total:
                    print(item)
                    tup = tup + ({
                    'type': trend,
                    'start_dt': item['start_dt'],
                    'peak_dt': item['end_dt'],
                    'end_dt': nex_item['end_dt'],
                    'raise_range': total,
                    'fall_range': nex_item['price_total']
                    },)

                # 寻找下降波的逻辑
                if trend == -1 and total >= price_total and current_days >= days and nex_item['days'] >= days and nex_item['price_total'] < 0 and nex_item['price_total']<-total:

                    tup = tup + ({
                    'type': trend,
                    'start_dt': item['start_dt'],
                    'peak_dt': item['end_dt'],
                    'end_dt': nex_item['end_dt'],
                    'raise_range': total,
                    'fall_range': nex_item['price_total']
                    },)
                # 寻找所有波的逻辑
                if trend == 0 and total >= price_total and current_days >= days and nex_item['days'] >= days and nex_item['price_total'] < 0:

                    rtrend =  1 if nex_item['price_total']>-total else -1
                    tup = tup + ({
                    'type': rtrend,
                    'start_dt': item['start_dt'],
                    'peak_dt': item['end_dt'],
                    'end_dt': nex_item['end_dt'],
                    'raise_range': total,
                    'fall_range': nex_item['price_total']
                    },)
        return tup

    # 根据波动计算波动幅度
    def get_price_wave_range( self, factor):
        pass

    # 取当前趋势的起点,只取上涨或者下跌趋势
    # 例如当前为下跌趋势那么取到趋势开始的那天
    # factor 因子， 从因子的第一个开始取平均涨跌幅，如果更dt 趋势一致（上涨或下跌）则继续往前取前一天，直到取到连续出现wrongtime次数的不同趋势，则跳到factor下一个元素继续上述操作
    def get_price_moving_start( self, dt , factor = (60,50,40,30,20,10,5,3), wrong_time = 2):
        current = self.get_avg_price_range(dt,factor[0])
        # print('current is %s'%current)
        # 上涨或者下跌
        features = 1 if float(current) > 0 else -1
        nind = self.date_col.index(dt)
        true_wrong = 0
        factor_index = 0
        result = ''
        while True:
            if nind < 0:
                result = date
                break

            if factor_index >= len(factor):
                result = self.date_col[nind + 1]
                break

            date = self.date_col[nind]
            days = factor[factor_index]
            ran = self.get_avg_price_range(date,days)
            # print('date is %s, days is %i, ran is %s'%(date,days,ran))
             # 当天为上涨的逻辑
            if features == 1:
                if float(ran) < 0:
                    true_wrong += 1
                    # 错误次数达到上限，
                    if true_wrong >= wrong_time:
                        factor_index += 1
                else:
                    true_wrong = 0
                    nind = nind-1
            else:
                if float(ran) > 0:
                    true_wrong += 1
                    # 错误次数达到上限，
                    if true_wrong >= wrong_time:
                        factor_index += 1
                else:
                    true_wrong = 0
                    nind = nind-1
        return result


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

    # 获取指定日期段的数据
    def get_datas ( self, in_code, start_dt, end_dt ):
        query =  "SELECT * FROM stock_all a where stock_code = '%s' and state_dt >= '%s' and state_dt <= '%s' order by state_dt asc" % (in_code, start_dt, end_dt)
        self.cursor.execute( query )
        datas = self.cursor.fetchall()
        if len( datas ) == 0:
            # raise() raise Exception("抛出一个异常")
            # 用raise语句来引发一个异常。异常/错误对象必须有一个名字，且它们应是Error或Exception类的子类。
            raise Exception
        self.datas = datas
        self.set_datas(datas)
        return self.datas

    # 设置datas
    def set_datas ( self, datas ):
        self.datas = datas
        self.cols = self.column(self.datas)
        # 取日期列表
        self.date_col = self.cols[self.field.index('state_dt')]
        # 取收盘价列表
        self.close_col = self.cols[self.field.index('close')]
        # 开盘价列表
        self.open_col = self.cols[self.field.index('open')]

        # 最高价列表
        # 最低价列表


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
            #　将每一行开盘价，收市价等作为数组的元素
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

    # 获取指定股票某一天的数据
    # dt str ['2018-01-02']
    def get_data_on_date( self, stock, dt):
        wh = {
        'stock_code': stock,
        'state_dt': dt
        }
        return self.get_first(wh)




if __name__ == '__main__':
    db = pymysql.connect(host=MYSQL.host, user=MYSQL.user, passwd=MYSQL.passwd, db=MYSQL.db, charset=MYSQL.charset)
    stock_all = Stock_all_model(db)
    # data = stock_all.get_data_on_date('002049.SZ','2010-01-14')
    # print(data)
    avg = Stock_all_model(db)
    avg.get_datas('002049.SZ','2018-05-20','2021-10-09')

    # print( avg.cols )
    '''# ans = self.collect_data(in_code,start_dt,end_dt)
    avgLine = avg.get_avg_line('2016-04-20')
    print(avgLine)
    is_puton = avg.is_put_on('2016-04-20',5,60)
    print('is_puton',is_puton)

    print(avg.get_data_on_date('002051.SZ','2016-04-20'))'''

    #print( avg.get_avg_amplitude('2021-10-08'))
    rlist = []
    for i in range(len(avg.date_col)+30):
        item = avg.date_col[i - 30]

        val = avg.get_avg_price_range(item,days=20)

        rlist.append(val)
    #print(rlist)

    resu = avg.get_price_moving_start('2021-10-08',factor = (20,10,5,3,2,1), wrong_time = 1)



    # print(resu)


    rdays = avg.get_days_by_two_date(resu, '2021-10-08')
    # print(rdays)
    # print('days is %i'%len(rdays))


    # print(avg.get_price_total('2021-10-08',650))

    lis = avg.get_all_price_moving('2021-10-08')
    # print(lis)
    #
    lis1 = avg.get_price_raise_wave(lis,condition = {'days': 5, 'price_total': 5,'trend': 0})

    print(lis1)

    avg_price_list = avg.get_avg_price('2021-10-08',5,30)
    print(avg_price_list)

    passageway_list = avg.get_avg_passageway('2021-10-08',5,10)

    print(passageway_list)