# -*- coding: utf-8 -*-
# @Author: Marte
# @Date:   2021-10-09 20:52:36
# @Last Modified by:   Marte
# @Last Modified time: 2021-12-08 19:50:51
import sys
import re
import numpy as np
sys.path.append('..')
from model.Stocks_model import Stocks_model
from model.Stock_all_model import Stock_all_model
from model.Stock_info_model import Stock_info_model
from request.Tushare_request import Tushare_request
from model.Stocks_model import Stocks_model
from model.Capital_model import Capital_model
from model.Pool_model import Pool_model
from factor.Average_factor import Average_factor
class Trend( object ):
    # 短期涨跌幅
    short_price_range = 0.00

    # 长期股价涨跌幅
    long_price_range = 0.00

    # 最近横盘天数
    balance_days = 0

    # 股价短期振幅\
    short_price_amplitude = 0

    # 股价长期振幅
    long_price_amplitude = 0

    # 股价运行通道
    passageway = None

    # 风险偏好 分为几个等级 0 正常， -1 谨慎 1 激进
    risk_appetite = 0

    # 止盈价位
    stop_surplus = 0

    # 止损位
    stop_loss = 0

    # 买入综合评分
    buy_probability = 0

    # 卖出综合评分
    sell_probability = 0

    # 活跃度 0 一般
    active = 0

    # 当前股票代码
    stock_code = ''

    # 股票最大涨跌幅10表示10%
    max_range = 10

    # 循环调用数组中函数，如果有一个函数返回真则卖出，主要用来动态增加卖出指标
    sell_must = {}

    # 循环调用只要一个返回真，则买入
    buy_must = {}

    # 均线是否上穿
    is_puton = {}

    # 收盘价
    close = 0

    # 训练集
    data_train = []

    # 结果集 ，用于机器学习训练
    data_target = []

    # 买入或者卖出动作0不动作，1买入， -1 卖出
    act = 0


    def __init__( self ):


        def fun3( strategy ):
            if strategy.close < float(strategy.stop_loss):
                print(" 触发止损操作")
                return True
            else:
                return False

        def fun2( strategy ):
            if float(strategy.stop_surplus) < strategy.close:
                print(" 触发止盈操作")
                return True
            else:
                return False


        def fun1( strategy ):
            # 如果风险偏好激进，60日均线乖离率小于 -5
            if strategy.risk_appetite == 1 and float(strategy.bias[0]) < -5:
                # print('strategy.risk_appetite == 1 and float(strategy.bias[0]) > -5 and float(strategy.bias[0]) < 0')
                return True
            else:
                return False

        def fun( strategy ):
            # 下穿60日均线，卖出评分大于80
            if strategy.sell_probability > 80 or strategy.is_puton['sixty']< 0:
               return True
            else:
                return False
        def fun4( strategy ):
            # 股价短期振幅过大则下破20日均线卖出
            if strategy.short_price_range > 5 and strategy.is_puton['twenty']< 0:
                return True
            else:
                return False
        # 注册卖出条件。其中一个条件返回真则会触发卖出，
        # 'already_times': 0, 初始执行次数为0
        # 'all_times': 1, 总共执行多少次，每执行一次则already_times 加1，执行到all_times 则该字典会从sell_must 中删除,省略则不会被删除
        # 'fun': fun 不可以省略, 会得到一参数会是该trend 对象,
        # 'auto_destruct': bool default False 是否在下一次卖出动作后自动销毁，不管是不是调用的该卖出程序都要销毁True 是False 否
        self.sell_must['put_down_sixtyline'] = {
        'already_times': 0,
        'all_times': 1,
        'fun': fun
        }
        self.sell_must['high_risk_appetite'] = {
        'fun': fun1,
        'already_times': 0,
        'all_times': 1,
        }
        self.sell_must['high_short_price_range'] = {
        'fun': fun4,
        }
        self.sell_must['stop_surplus'] = {
        'fun': fun2
        }
        '''self.sell_must['stop_loss'] = {
        'fun': fun3
        }'''

        # 注册常用的买入条件
        #
        # 符合以下条件的任意一种则买入，如果前一个判断为买入则不会继续做后面的判断

        def fun4( strategy ):
            # 评分大于70 长期趋势向上或者横盘，股价短期振幅<4% （说明股价稳定）
            if strategy.buy_probability >= 70 and strategy.long_price_range >=0 and strategy.is_puton['sixty'] > 0 and strategy.active < 4:
                # print('self.buy_probability >= 70 and self.long_price_range >=0 and self.active < 4')
                            # 如果以这个策略买入则下穿10均线必须卖出，所以增加了一个卖出条件
                def fun( strate ):
                    if strate.is_puton['sixty'] < 0:
                        return True
                    else:
                        return False
                strategy.add_sell_condition( 'is_putdown_six_line', fun, times = 1)# 如果以这个策略买入则下穿10均线必须卖出，所以增加了一个卖出条件
                return True
            else:
                return False


        def fun5( strategy ):
            # 如果风险偏好为积极,评分高于70 和活跃度小于6% 上穿10日线则买入
            if strategy.risk_appetite == 1 and strategy.buy_probability >= 70 and strategy.is_puton['ten'] > 0 and strategy.active < 4:
                # print('self.risk_appetite == 1 and self.buy_probability >= 70 and self.active < 6')
                # 如果以这个策略买入则下穿10均线必须卖出，所以增加了一个卖出条件
                def fun( strate ):
                    if strate.is_puton['ten'] < 0:
                        return True
                    else:
                        return False
                strategy.add_sell_condition( 'is_putdown_ten_line', fun, times = 1, auto_distruct= True)
                return True
            else:
                return False


        def fun6( strategy ):
            # 如果风险偏好为积极,股价上穿20日均线 和活跃度小于6% 则买入
            if strategy.risk_appetite == 1 and strategy.is_puton['twenty'] > 0 and strategy.active < 4:
                # print('self.risk_appetite == 1 and self.is_puton[twenty] > 0 and self.active < 6')
                # 如果以这个策略买入则下穿20均线必须卖出，所以增加了一个卖出条件
                def fun( strate ):
                    if strate.is_puton['twenty'] < 0:
                        return True
                    else:
                        return False
                # auto_distruct': True, 如果有过一次卖出行为就会被销毁
                strategy.add_sell_condition( 'is_putdown_twenty_line', fun, times = 1, auto_distruct= True)
                return True
            else:
                return False


        self.buy_must['probability_big'] = {
        'already_times': 0,
        'all_times': 100,
        'fun': fun4
        }
        '''self.buy_must['probability_and_risk_appetite'] = {
        'already_times': 0,
        'all_times': 100,
        'fun': fun5,
        }'''
        self.buy_must['risk_appetite_and_isputon'] = {
        'already_times': 0,
        'all_times': 100,
        'fun': fun6,
        }

    # 支持同时传入多个模型一起操作
    # models = { stock_code1: stock_info, tock_code1: stock_info }键名代表股票代码，键值是有股票代码历史数据的model该模型值继承自stock——all的模型
    # factors =【(factor,percent)】 第二个参数是该因子对结果的影响占比
    def registe( self , models, factors):
        self.models = models
        self.factors = factors
        # self.sim = models[list(models.keys())[0]]

    # 返回风险偏好
    # return int 返回值可以是0、 1 或者-1
    def update_risk_appetite( self ):

        if self.long_price_range > 0:
            # 风险偏好 分为几个等级 0 正常， -1 谨慎 1 激进
            risk_appetite = 1
            return risk_appetite

        elif self.long_price_range == 0:
            risk_appetite = 0
            return risk_appetite

        else:
            risk_appetite = -1
            return risk_appetite

    # 更新止盈止损
    # return tuple (止盈 价， 止损价)
    def update_stop_surplus_loss( self ):
        if self.long_price_range > 0:
            # 止盈 是超过60日均线50%
            stop_surplus = self.close * (100 - float(self.bias[0]) + 50 )/100
            # 止损位是跌破60日均线5%
            stop_loss = self.close * (100 - float(self.bias[0]) - 5 )/100
            return ('%.2f'%stop_surplus, '%.2f'%stop_loss)

        elif self.long_price_range == 0:
            # 止盈 是超过60日均线
            stop_surplus = self.close * (100 - float(self.bias[0]) + 30)/100
            # 止损位是跌破60日均线
            stop_loss = self.close * (100 - float(self.bias[0]))/100

            return ('%.2f'%stop_surplus, '%.2f'%stop_loss)
        else:
            # 止盈 是超过60日均线10%
            stop_surplus = self.close * (100 - float(self.bias[0]) + 10)/100
            # 止损位是跌破60日均线5%
            stop_loss = self.close * (100 - float(self.bias[0]) - 5 )/100

            return ('%.2f'%stop_surplus, '%.2f'%stop_loss)

    # 根据条件返回是否买入
    # return int 0 不买入 1 买入
    def buy_condition( self ):
        act = 0
        res = False
        index = ''
        do_del = False
        for key in self.buy_must:
            fun = self.buy_must[key]['fun']
            all_times = self.buy_must[key]['all_times'] if 'all_times' in self.buy_must[key] else 100
            already_times = self.buy_must[key]['already_times'] if 'already_times' in self.buy_must[key] else 0
            # 判断是否是function
            if(hasattr(fun, '__call__')):
                res = fun(self)
                if res and already_times <= all_times:
                    already_times += 1
                    if 'already_times' in self.buy_must[key]:
                        self.buy_must[key]['already_times'] += 1
                    index = key
                    print("%s共执行了买入%i次"%(index,already_times))
                    if already_times >= all_times:
                        do_del = True
                    break

        # 如果执行次数够了则删除该条目
        if do_del:
            del self.buy_must[index]
            print("删除了该项目")


        if res:
            # 销毁auto_distruct 属性为真的的方法
            def fil(item):
                if 'auto_distruct' in item and item['auto_distruct'] == True:
                    return False
                else:
                    return item
            new_must = {}
            for key in self.buy_must:
                if fil(self.buy_must[key]):
                    new_must[key] = self.buy_must[key]


            self.buy_must = new_must
            act = 1

        return act

    # 添加一个卖出的条件，如果该条件名字存在则会增加 一次执行次数
    # name str 名称
    # fun  function 函数 条件内容必须返回一个bool
    # times int 执行次数
    def add_sell_condition( self, name: str , fun ,times = 1, auto_distruct = False):
        if name in self.sell_must:
            if 'all_times' in self.sell_must[name]:
                self.sell_must[name]['all_times'] += times
                if auto_distruct != False:
                    self.sell_must[name]['auto_distruct'] = auto_distruct
        else:
            print('add a sell_condition %s'%name)
            self.sell_must[name] = {
            'already_times': 0,
            'all_times': times,
            'fun': fun,
            'auto_distruct': auto_distruct,
            }

    # 添加一个买入的条件，如果该条件名字存在则会增加一次执行次数
    # name str 名称
    # fun  function 函数 条件内容必须返回一个bool
    # times int 执行次数
    def add_buy_condition( self, name: str , fun ,times = 1, auto_distruct = False):
        if name in self.buy_must:
            if 'all_times' in self.buy_must[name]:
                self.buy_must[name]['all_times'] += times,
                if auto_distruct != False:
                    self.buy_must[name]['auto_distruct'] = auto_distruct
        else:
            self.buy_must[name] = {
            'already_times': 0,
            'all_times': times,
            'fun': fun,
            'auto_distruct': auto_distruct,
            }

    # 根据条件返回是否卖出,
    # return int 0 不买入 1 买入
    def sell_condition( self ):
        act = 0
        res = False
        index = ''
        do_del = False
        for key in self.sell_must:
            # print('sell_conditon is %s'%key)
            fun = self.sell_must[key]['fun']
            all_times = self.sell_must[key]['all_times'] if 'all_times' in self.sell_must[key] else 100
            already_times = self.sell_must[key]['already_times'] if 'already_times' in self.sell_must[key] else 0
            # 判断是否是function
            if(hasattr(fun, '__call__')):
                res = fun(self)

                if res and already_times <= all_times:
                    already_times += 1
                    if 'already_times' in self.sell_must[key]:
                        self.sell_must[key]['already_times'] += 1
                    index = key
                    print("%s共执行了卖出%i次"%(index,already_times))
                    if already_times >= all_times:
                        do_del = True
                    break

        # 如果执行次数够了则删除该条目
        if do_del:

            del self.sell_must[index]
            print("删除了该项目")

        if res:
            # 销毁auto_distruct 属性为真的的方法
            def fil(item):
                if 'auto_distruct' in item and item['auto_distruct'] == True:
                    return False
                else:
                    return item
            new_must = {}
            for key in self.sell_must:
                if fil(self.sell_must[key]):
                    new_must[key] = self.sell_must[key]

            self.sell_must = new_must
            act = -1

        return act

    # 根据股票代码返回交易所规定的股票最大涨跌幅
    # return int (20 最大涨跌幅20% or  10 or 30 )
    def get_max_range( self , code ):
        if re.match('^[6,0]0', code):
            return 10
        elif re.match('^30', code):
            return 20
        elif re.match('^68', code):
            return 20
        else:
            return 10


    # 判断策略
    # stock_code str 股票代码
    # date str 日期
    # return dict  返回进过本策略模型预测的预测结果
    def strategy( self , stock_code, date )-> dict:
        model = self.models[stock_code]
        factors = self.factors
        # 累计买入评价得分
        buy_probability_total = 0
        # 个模型累计卖出评价
        sell_probability_total = 0
        self.stock_code = stock_code
        # 股票最大涨跌幅
        self.max_range = self.get_max_range(stock_code)

        # 对注册的因子进行循环预测，然后求各因子预测后得到的平均百分比
        for factor in factors:
            fac = factor[0]()
            percent = factor[1]
            fac.register(model)
            # 对上涨或下跌进行预测
            buy = fac.buying(date)
            sell = fac.selling(date)
            if type(fac) == Average_factor:
                data = buy["data"]
                # 短期涨跌幅
                self.short_price_range = float(data["shortMovingRange"][0])
                self.middlie_price_range = float(data["middleMovingRange"][0])
                # 长期股价涨跌幅
                self.long_price_range = float(data["longMovingRange"][0])
                # 股价短期振幅\
                self.short_price_amplitude = float(data["amplitude"])
                # 当天收盘价
                self.close = data["close"]
                # 乖离率
                self.bias = data["AverageBias"]
                # 股价运行通道
                self.passageway = data["inPassageway"]
                # 是否上穿均线
                self.is_puton = data["isPutOn"]
                # 风险偏好
                self.risk_appetite = self.update_risk_appetite()
                # 止盈止损价格
                self.stop_surplus, self.stop_loss = self.update_stop_surplus_loss()
                # 活跃度 如果是10%涨跌幅等于振幅 如果是20%涨跌幅的等于其2分之一
                self.active = self.short_price_amplitude / ( self.max_range/10 )


            print(date)
            '''
            print("股价:",self.close)
            print("60日乖离率:", self.bias[0])
            print("止盈价：",self.stop_surplus)
            print("止损价:", self.stop_loss)
            # print(buy)'''
            buy_probability_total += float(buy['probability']) * percent / 100
            sell_probability_total += float(sell['probability']) * percent / 100


        # 求多因子的预测平均值
        self.buy_probability = float('%.2f'%(buy_probability_total/len(factors)))
        self.sell_probability = float('%.2f'%(sell_probability_total/len(factors)))

        # 大于80 做出买入或者卖出动作 和必须满足长期趋势为上涨
        print('self.long_price_range:%.2f'%self.long_price_range)
        print('self.middlie_price_range:%.2f'%self.middlie_price_range)
        print('self.short_price_range:%.2f'%self.short_price_range)
        # 保存到表适用于分析数据
        model.update( {'long_price_range': self.long_price_range,'middlie_price_range': self.middlie_price_range,'short_price_range': self.short_price_range,'active': self.active }, {'state_dt': date})
        buy_act = self.buy_condition()

        sell_act = self.sell_condition()
        # 保存是否买入动作
        self.act = 1 if buy_act > 0 else sell_act


        # print('buy_act',buy_act,'buy', buy)
        return {
            'stock_code': stock_code,
            #  操作方式 ，1 买入 -1 卖出 0 不动作
            'act': buy_act if buy_act > 0 else sell_act,
            'vol': 10000,
            # 预测后期上涨概率百分比
            'percentage': self.buy_probability
        }
    # 收集机器学习训练集,如果需要被加到训练集的结果返回数据，如果不需要则返回空
    # return [np.array] or return False
    def collect_data_train ( self ):

        if self.act == 1:
            self.train_price = self.close
            train = [
            self.long_price_range,
            self.middlie_price_range,
            self.short_price_range,
            self.active,
            self.close

            ]
            # 打包成二维数组
            self.data_train.append(np.array(train))
            return self.data_train
        else:
            return False
    # 收集结果集，如果结果集为成功计入float（1.00）
    # 返回一个数组，数组元素必须对应上面的训练集，
    def collect_data_target ( self ):
        if self.act == -1:
            if self.close / self.train_price > 1:
                self.data_target.append( float(1.00) )
            else:
                self.data_target.append( float(0.00) )
            return self.data_target
        else:
            return False



    # 被外部调用的方法
    # dt str 日期
    # return list 返回经过各个模型策略预测返回值组成的列表，
    def boot( self, dt)->list:
        rlist = []
        for i in self.models:
            stock_code = i
            res = self.strategy( stock_code, dt )
            rlist.append( res )

        return rlist

    # 进行机器学习的控制,只能对模型的第一只进行
    def ai( self, dt ):
        print( self.models)
        stock_code = list(self.models.keys())[0]
        res = self.strategy( stock_code, dt )
        # 保证一个训练集后收集一个结果集
        if len( self.data_train ) <= len( self.data_target ):
            data_train = self.collect_data_train()
        else:
            data_target = self.collect_data_target()

        if len( self.data_train) - len( self.data_target ) == 1:
            return (self.data_train,self.data_target )






if __name__ == '__main__':
    res = Trend().get_max_range('000001.SZ')
    print(res)