from sklearn import svm
import pymysql.cursors
import datetime
import DC
import tushare as ts

# 机器学习模型
# param stock string 股票
# start_dt string 预测涨跌的结束日期
# param_window  int 预测涨跌的天数，结束日期-回测天数 = 开始日期 取该时间段的实时行情数据，对该时间段每一天做一个预测
# para_dc_window int 每天的预测需要向前取多少天的数据作为训练集
def model_eva(stock,state_dt,para_window,para_dc_window):
    # 建立数据库连接，设置tushare token
    db = pymysql.connect(host='127.0.0.1', user='stock', passwd='Aa780428', db='stock', charset='utf8')
    cursor = db.cursor()
    ts.set_token('2d8e71911ffec057ebde16aab0348714dfe8348f67ee89e2125877b8')
    pro = ts.pro_api()
    # 建评估时间序列, para_window参数代表回测窗口长度
    model_test_date_start = (datetime.datetime.strptime(state_dt, '%Y-%m-%d') - datetime.timedelta(days=para_window)).strftime(
        '%Y%m%d')
    model_test_date_end = state_dt
    # 访问tushare 接口取得某只股票的行情数据
    df = pro.trade_cal(exchange_id='', is_open = 1,start_date=model_test_date_start, end_date=model_test_date_end)
    # 取出交易时间作为列表
    date_temp = list(df.iloc[:,1])
    # 转换成2017-08-05 这种时间格式
    model_test_date_seq = [(datetime.datetime.strptime(x, "%Y%m%d")).strftime('%Y-%m-%d') for x in date_temp]
    # 清空评估用的中间表model_ev_mid
    sql_truncate_model_test = 'truncate table model_ev_mid'
    cursor.execute(sql_truncate_model_test)
    db.commit()
    return_flag = 0
    # 开始回测，其中para_dc_window参数代表建模时数据预处理所需的时间窗长度
    # 遍历交易日
    for d in range(len(model_test_date_seq)):
        # 取当前时间减去para_dc_window得到的日期作为开始时间，从数据库中取对应股票的行情数据
        model_test_new_start = (datetime.datetime.strptime(model_test_date_seq[d], '%Y-%m-%d') - datetime.timedelta(days=para_dc_window)).strftime('%Y-%m-%d')
        model_test_new_end = model_test_date_seq[d]
        try:
            # stock = 股票代码， 从数据库取行情数据
            dc = DC.data_collect(stock, model_test_new_start, model_test_new_end)
        except Exception as exp:
            print("DC Errrrr")
            return_flag = 1
            break
        train = dc.data_train
        target = dc.data_target
        test_case = [dc.test_case]
        # print('train__', train)
        # print('target__', target)
        # print('test_case',test_case)
        model = svm.SVC()           # 建模
        model.fit(train, target)        # 训练，train是训练所使用的数据，target保存训练集每一项的结果，训练之后就可以预测了
        ans2 = model.predict(test_case) # 预测
        # print('预测结果',ans2)
        # 将预测结果插入到中间表
        sql_insert = "insert into model_ev_mid(state_dt,stock_code,resu_predict)values('%s','%s','%.2f')" % (model_test_new_end, stock, float(ans2[0]))
        cursor.execute(sql_insert)
        db.commit()
    if return_flag == 1:
        acc = recall = acc_neg = f1 = 0
        return -1
    else:
        # 在中间表中刷真实值
        for i in range(len(model_test_date_seq)):
            sql_select = "select * from stock_all a where a.stock_code = '%s' and a.state_dt >= '%s' order by a.state_dt asc limit 2" % (stock, model_test_date_seq[i])
            cursor.execute(sql_select)
            done_set2 = cursor.fetchall()
            if len(done_set2) <= 1:
                break
            resu = 0
            # print('done_set2',done_set2)
            # 取前一天股价和今天比较resu 为1 代表上涨，为0代表下跌
            if float(done_set2[1][3]) / float(done_set2[0][3]) > 1.00:
                resu = 1
            #将股价是否上涨真实的结果写入数据库字段resu_real
            sql_update = "update model_ev_mid w set w.resu_real = '%.2f' where w.state_dt = '%s' and w.stock_code = '%s'" % (resu, model_test_date_seq[i], stock)
            cursor.execute(sql_update)
            db.commit()
        # 计算查全率， 计算预测上涨确实也上涨的天数
        sql_resu_recall_son = "select count(*) from model_ev_mid a where a.resu_real is not null and a.resu_predict = 1 and a.resu_real = 1"
        cursor.execute(sql_resu_recall_son)
        # 预测成功的上涨天数
        recall_son = cursor.fetchall()[0][0]
        print('做出预测上涨并且成功上涨的天数',recall_son)

        # 计算总的上涨天数
        sql_resu_recall_mon = "select count(*) from model_ev_mid a where a.resu_real is not null and a.resu_real = 1"
        cursor.execute(sql_resu_recall_mon)
        # 总的上涨天数
        recall_mon = cursor.fetchall()[0][0]
        print('总的上涨天数',recall_mon)
        recall = recall_son / recall_mon
        print('预测准确的天数占上涨天数的百分比',recall)
        # 计算查准率
        sql_resu_acc_son = "select count(*) from model_ev_mid a where a.resu_real is not null and a.resu_predict = 1 and a.resu_real = 1"
        cursor.execute(sql_resu_acc_son)
        # 做出预测上涨并且成功上涨的天数
        acc_son = cursor.fetchall()[0][0]
        sql_resu_acc_mon = "select count(*) from model_ev_mid a where a.resu_real is not null and a.resu_predict = 1"
        cursor.execute(sql_resu_acc_mon)
        # 总的预测上涨天数
        acc_mon = cursor.fetchall()[0][0]
        print('做出预测上涨的天数',acc_mon)
        if acc_mon == 0:
            acc = recall = acc_neg = f1 = 0
        else:
            acc = acc_son / acc_mon
        # 计算查准率(负样本)
        sql_resu_acc_neg_son = "select count(*) from model_ev_mid a where a.resu_real is not null and a.resu_predict = 0 and a.resu_real = 0"
        cursor.execute(sql_resu_acc_neg_son)
        acc_neg_son = cursor.fetchall()[0][0]
        print('成功预测下跌的天数',acc_neg_son)
        sql_resu_acc_neg_mon = "select count(*) from model_ev_mid a where a.resu_real is not null and a.resu_predict = 0"
        cursor.execute(sql_resu_acc_neg_mon)
        acc_neg_mon = cursor.fetchall()[0][0]
        print('总的预测下跌的天数',acc_neg_mon)
        if acc_neg_mon == 0:
            acc_neg_mon = -1
            acc_neg = -1
        else:
            acc_neg = acc_neg_son / acc_neg_mon
        # 计算 F1 分值
        if acc + recall == 0:
            acc = recall = acc_neg = f1 = 0
        else:
            # f1 综合上涨成功率
            f1 = (2 * acc * recall) / (acc + recall)
    sql_predict = "select resu_predict from model_ev_mid a where a.state_dt = '%s'" % (model_test_date_seq[-1])
    cursor.execute(sql_predict)
    done_predict = cursor.fetchall()
    predict = 0
    if len(done_predict) != 0:
        predict = int(done_predict[0][0])
    # 将评估结果存入结果表model_ev_resu中
    sql_final_insert = "insert into model_ev_resu(state_dt,stock_code,acc,recall,f1,acc_neg,bz,predict)values('%s','%s','%.4f','%.4f','%.4f','%.4f','%s','%s')" % (state_dt, stock, acc, recall, f1, acc_neg, 'svm', str(predict))
    cursor.execute(sql_final_insert)
    db.commit()
    db.close()
    # Precision
    print(str(state_dt) + '   预测上涨的成功率（总有效预测数/预测上涨并且成功的次数） : ' + str(acc) + '   预测准确的天数占上涨天数的百分比 : ' + str(recall) + '   总成功率 : ' + str(f1) + '   预测下跌的成功率（总有效预测数/预测跌并且成功的次数） : ' + str(acc_neg))
    print(str(state_dt) + '   Precision : ' + str(acc) + '   Recall : ' + str(recall) + '   F1 : ' + str(f1) + '   Acc_Neg : ' + str(acc_neg))
    return 1

if __name__ == '__main__':
    stock_pool = ['002049.SZ']
    for stock in stock_pool :
        ans = model_eva(stock,'2011-02-01',90,730)
    print('All Finished !!')

