import time
import sys
sys.path.append("..")
from config import *
class Base_model(object):
    test_val = 1
    table = ''
    field = []
    def __init__(self, db):
        print ('Base_model.__init__()')
        self.db = db
        self.cursor = self.db.cursor()

    def insert_one( self, dic ):
        if not self.table:
            return False
        # 取键名
        keys = dic.keys()
        # 取值
        values = dic.values()
        key_text = ','.join(keys)
        def to_str(val):
            #是否string类型
            if isinstance (val,str):
                return "'" + val +"'"
            if isinstance (val,float):
                return str(val)
            if isinstance (val,int):
                return str(val)
            if val == None:
                return str('NULL')
            return val
        values = map(to_str,values)
        val_text = ','.join(values)
        query = "INSERT INTO %s(%s) VALUES (%s)"%(self.table,key_text,val_text)
        # print (query)
        return self.execute(query)

    # 将where字典format,将不同数据类型的变量转换成符合SQL标准的变量值
    def format_val_to_query(self, val ):

        #是否string类型
        if isinstance (val,str):
            return "'" + val +"'"
        if isinstance (val,float):
            return str(val)
        if isinstance (val,int):
            return str(val)
        if val == None:
            return str('NULL')
        return val


    def get_first( self, where={}, order_by="", desc="" ):
        field = '*'
        where_text = ''
        order_text = ''
        if not self.table:
            return False
        if hasattr( self, field):
            field = ','.join(self.field)
        # 判断类型
        if isinstance(where,dict) and where:

            where_text = 'where'
            # dict.items()遍历字典列表 我们可以看到，返回了一个列表，列表中包含数个元组，每个元组中的内容对应的就是字典中的键值对。
            # 那么我们遍历字典时，采用如下方式：
            for key,value in  where.items():
                nval = self.format_val_to_query(value)
                where_text = where_text + ' %s=%s and'%(key,nval)
            where_text = where_text[0:-3]
            # print(where_text)
        if order_by:
            order_text = "order by %s %s"%(order_by,desc)
        query = "SELECT %s FROM %s %s %s"%(field,self.table,where_text,order_text)
        # print(query)
        self.execute(query)
        res = self.cursor.fetchone()
        if res and len(res) > 0:
            return res
        else:
            return False
    # 一次删除符合条件的多条数据
    def delete_all( self, where):
        where_text = ''
        if not self.table:
            return False
        where_text = 'where'
        # dict.items()遍历字典列表 我们可以看到，返回了一个列表，列表中包含数个元组，每个元组中的内容对应的就是字典中的键值对。
        # 那么我们遍历字典时，采用如下方式：
        for key,value in  where.items():
            nval = self.format_val_to_query(value)
            where_text = where_text + ' %s=%s and'%(key,nval)
        where_text = where_text[0:-3]
        # print(where_text)
        query = 'DELETE FORM %s %s'%(self.table,where_text)
        res = self.execute(query)
        return res

    # 多条记录
    def get_all( self, where={}, order_by="", desc="" ):
        field = '*'
        where_text = ''
        order_text = ''
        if not self.table:
            return False
        if hasattr( self, field):
            field = ','.join(self.field)
        # 判断类型
        if isinstance(where,dict) and where:

            where_text = 'where'
            # dict.items()遍历字典列表 我们可以看到，返回了一个列表，列表中包含数个元组，每个元组中的内容对应的就是字典中的键值对。
            # 那么我们遍历字典时，采用如下方式：
            for key,value in  where.items():
                nval = self.format_val_to_query(value)
                where_text = where_text + ' %s=%s and'%(key,nval)
            where_text = where_text[0:-3]
            print(where_text)
        if order_by:
            order_text = "order by %s %s"%(order_by,desc)
        query = "SELECT %s FROM %s %s %s"%(field,self.table,where_text,order_text)
        self.execute(query)
        res = self.cursor.fetchall()
        if res and len(res) > 0:
            return res
        else:
            return False
    def execute( self, query):
        res = True
        try:
            # 执行sql语句
            self.cursor.execute(query)
            # 提交到数据库执行
            self.db.commit()
        except:
            print('执行SQL语句发生错误:%s'%query)
            # 发生错误时回滚
            self.db.rollback()
            res = False
            return res
        return res
    # 计算并返回手续费
    def get_charge( self, amount , charge_rate):
        return float(amount) * charge_rate

    def __del__( self ):
        print('这是析构函数')
        # 这里回收资源会引起MySQL出错
        #self.cursor.close()
        #self.db.close()

    def close_db( self ):
        self.cursor.close()
        self.db.close()
    # 转换双重集合变成以列为元素的列表((col1,col2),(col1,col2)) 变成 ((co11,col1),(col2,col2))
    def column( self, datas ):
        lis = []
        # 更根据有几列来初始化列的列表
        if len(datas) > 0:
            line = datas[0]
            for i in range( len ( line )):
                lis.append([])
        # 循环填充数据
        for i in range( len( datas )):
            row = datas[i]
            for col in range( len ( row )):
                lis[col].append(row[col])
        return lis

    # 将查询结果行转换成dict
    # return dict
    def to_dict ( self, row ):
        print("row",row)
        dic = dict(zip(self.field,row))
        return dic

    # 清空表内容
    def empty ( self ):
        query = "truncate table %s"%self.table
        return self.execute(query)

    def to_connect(self):
        return pymysql.connect(host=MYSQL.host, user=MYSQL.user, passwd=MYSQL.passwd, db=MYSQL.db, charset=MYSQL.charset)


    def is_connected(self):
        """Check if the server is alive"""
        try:
            self.db.ping(reconnect=True)
            print ("db is connecting")
        except:
            traceback.print_exc()
            self.db = self.to_connect()
            print ("db reconnect")

    # 原则上，类方法是将类本身作为对象进行操作的方法。假设有个方法，且这个方法在逻辑上采用类本身作为对象来调用更合理，那么这个方法就可以定义为类方法。另外，如果需要继承，也可以定义为类方法。类方法可以对类进行原型进行操作
    @classmethod
    def get_lis(cls):
        # cls 是本类原型
        cls.test_val +=1
        return cls.test_val

    # 使用装饰器@staticmethod。
    # 静态方法是类中的函数，不需要实例。静态方法主要是用来存放逻辑性的代码，逻辑上属于类，但是和类本身没有关系，也就是说在静态方法中，不会涉及到类中的属性和方法的操作。可以理解为，静态方法是个独立的、单纯的函数，它仅仅托管于某个类的名称空间中，便于使用和维护。

    @staticmethod
    def showTime():
        return time.strftime("%H:%M:%S", time.localtime())

if __name__ == '__main__':
    # 类方法调用，每次被继承的类被实例化就会被调用一次
    print(Base_model.get_lis())
    print(Base_model.get_lis())
    # 静态方法调用
    Base_model.showTime()