# coding: utf-8
# @Time: 2019/9/18 11:14
# @Author:renpingsheng
from __future__ import division
import time
import datetime


def get_cutten_timestr(flag=True):
    """
    获取当前时间字符串
    @return:
    """
    if flag:
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return datetime.datetime.now().strftime('%Y-%m-%d')


def parse_timestr_to_timestamp(time_str, flag=True):
    """
    把时间字符串转换为时间戳格式
    :param time_str: 时间字符串,格式为：2019-01-01 12:12:12 或 2019-01-01
    :param flag: 标志位，决定输入时间字符串的格式
    :return: 时间戳格式
    """
    if flag:
        struct_time = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")  # 2019-01-01 12:12:12
    else:
        struct_time = time.strptime(time_str, "%Y-%m-%d")  # 2019-01-01
    return time.mktime(struct_time)


def parse_month_to_timestamp(month_str, flag=True):
    """
    把月份字符串转化为时间戳
    :param month_str: 月份，例如：2019-01 或者 2019.01
    :param flag: 标志位，控制输入月份字符串的格式
    :return:
    """
    if flag:
        struct_time = time.strptime(month_str, "%Y-%m")
    else:
        struct_time = time.strptime(month_str, "%Y.%m")
    return time.mktime(struct_time)


def parse_timestamp_to_timestr(time_stamp, flag=True):
    """
    把时间戳转换为时间字符串
    :param time_stamp: 时间戳
    :param flag: 标志位，可以指定输出时间字符串的格式
    :return: 时间字符串,格式为：2019-01-01 12:12:12 或 2019-01-01
    """
    localtime = time.localtime(time_stamp)
    if flag:
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
    else:
        time_str = time.strftime("%Y-%m-%d", localtime)
    return time_str


def get_day_list(start_timestamp, end_timestamp, flag=True):
    """
    传入开始时间戳和结束时间戳，获取时间段内的日期列表
    :param start_timestamp: 开始时间戳
    :param end_timestamp: 结束时间戳
    :param flag: 标志位
    :return: 日期列表
    """
    tmp = range(int(start_timestamp), int(end_timestamp), 3600 * 24)
    if flag:
        tmp_range = [{"day_str": parse_timestamp_to_timestr(i, flag=False)} for i in tmp]
    else:
        tmp_range = [parse_timestamp_to_timestr(i, flag=False) for i in tmp]
    return tmp_range


def day_range(interval_day):
    """
    获取指定天内的时间字符串的列表
    :return:
    """
    c_time = (int(time.time() / (24 * 3600)) + 1) * 24 * 3600
    day_range_str = c_time - 24 * 3600 * interval_day

    day_list = [{"day_str": parse_timestamp_to_timestr(t, flag=False)} for t in range(day_range_str, c_time, 3600 * 24)]
    return day_list


def covert_time(time_str):
    """
    把时间段转换为秒数
    :param time_str:
    :return:
    """
    if time_str.endswith("h"):
        stamp = float(time_str.strip("h")) * 3600
    elif time_str.endswith("m"):
        stamp = float(time_str.strip("m")) * 60
    else:
        stamp = float(time_str)
    return stamp


def parse_timestr_to_datetime(timestr, flag=1):
    """
    把时间字符串转化为datetime
    :param timestr: 时间字符串，例如：2019-01-01 12:12:12 或者 2019.01.01 12:12:12
    :param flag: 标志位，控制输入时间字符串的格式
    :return:
    """
    if flag == 1:
        tmp_datetime = datetime.datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
    elif flag == 2:
        tmp_datetime = datetime.datetime.strptime(timestr, "%Y.%m.%d %H:%M:%S")
    elif flag == 3:
        tmp_datetime = datetime.datetime.strptime(timestr, "%Y-%m-%d")
    elif flag == 4:
        tmp_datetime = datetime.datetime.strptime(timestr, "%Y-%m-%d %H:%M")
    else:
        tmp_datetime = datetime.datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
    return tmp_datetime


################################################

def parse_format_timestr(format_timestr):
    """
    将格式字符串转换为时间戳
    :param format_timestr: 格式字符串,格式： "Sat Mar 28 22:24:24 2016"
    :return:
    """
    tmp_timestamp = time.mktime(time.strptime(format_timestr, "%a %b %d %H:%M:%S %Y"))
    return tmp_timestamp


def parse_datetime_to_string(datetime_str, flag=True):
    """
    把datetime时间转化成时间字符串
    :param datetime_str: datetime生成的时间，例子：datetime.datetime.now()
    或者： datetime.datetime.now() - datetime.timedelta(hours=1)       # 一个小时之前
    或者： datetime.datetime.now() - datetime.timedelta(days=1)        # 一天之前
    :return:
    """
    # 将日期转化为字符串 datetime => string
    # 在数据库中定义字段信息时为：models.DateTimeField(auto_now_add=True)
    # 查询数据库之后，使用此方法把查询到的时间转换成可用的时间字符串
    # when_insert__range=(an_hour_time, now_time)
    # an_hour_time和 now_time 都是 datetime时间字符串，查询两个datetime时间字符串之间的数据
    if flag:
        return datetime_str.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return datetime_str.strftime('%Y-%m-%d')


def parse_datetime_to_timestamp(datetime_str):
    """
    把datetime转化成时间戳
    @param datetime_str: datetime时间，比如：datetime.datetime.now()
    @return: 时间戳，比如：1565663994.0
    """
    return time.mktime(datetime_str.timetuple())


def parse_timestamp_to_datetime(timestamp, flag=True):
    """
    把时间戳转化为datetime时间
    @param timestamp: 时间戳，比如：1553361411
    @param flag: 标志位，决定转化成datetime的时间
    @return:
    """
    if flag:
        return datetime.datetime.fromtimestamp(timestamp)  # 东八区的datetime时间
    return datetime.datetime.utcfromtimestamp(timestamp)  # 正常的UTC时间


def parse_dur_time(d1, d2):
    """
    获取两个datetime时间 间隔的日期数(天数，小时数和秒数)
    :param d1: 开始时间
    :param d2: 结束时间
    :return:
    """
    dur_str = ""
    dur_day = (d2 - d1).days
    dur_second = (d2 - d1).seconds
    if dur_day > 0:
        dur_str += "%s天" % str(dur_day)
    if dur_second - 3600 > 0:
        dur_hour = dur_second // 3600
        dur_str += "%s小时" % str(dur_hour)
    if (dur_second % 3600) > 60:
        dur_minute = (dur_second % 3600) // 60
        dur_str += "%s分钟" % str(dur_minute)
    dur_str += "%s秒" % str(dur_second % 60)
    return dur_str


def get_month_start(datetime_str):
    """
    datetime_str可以是：datetime.date.today() ,也可以是：datetime.datetime.now()
    传入datetime时间，获取datetime时间当月第一天
    返回传入的datetime时间的第一天的时间字符串
    """
    month_start = datetime.datetime(datetime_str.year, datetime_str.month, 1)
    return month_start.strftime('%Y-%m-%d')


def get_month_end(datetime_str):
    """
    datetime_str可以是：datetime.date.today() ,也可以是：datetime.datetime.now()
    传入datetime时间，获取datetime时间当月最后一天
    返回传入的datetime时间的最后一天的时间字符串
    """
    if data_date.month == 12:
        month_end = datetime.datetime(datetime_str.year, 12, 31)
    else:
        month_end = datetime.datetime(datetime_str.year, datetime_str.month + 1, 1) - datetime.timedelta(days=1)
    return month_end.strftime('%Y-%m-%d')