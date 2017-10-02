"""
连接数据库。

由于整个交易系统不会频繁读写数据库，而且不是高频高并发，
所以简单些，用sqlite3数据库

sqlite3中，如果sql不需要返回，则用conn.execute,如果有返回，则需要打开游标cursor

"""
import traceback
import pandas as pd
import sqlite3

from autotrade.config.config import db_file

class dbserbser():
    """
    sqlite3的dbserver
    """
    def __init__(self):
        self.db=db_file

    def connect(self):
        """连接数据库"""
        return sqlite3.connect(db_file)

    def execute(self,sql):
        """执行SQL"""
        conn=sqlite3.connect(db_file)
        conn.execute(sql)
        conn.commit()
        conn.close()

    def df_into_db(self,tb,df,types='insert'):
        """将dataframe导入数据库"""
        # 先将df全部转成字符串格式，主要是针对数值，df中的时间此时肯定是字符串类型
        df2 = df.applymap(lambda s: str(s))
        # 处理空值问题，因为刚才转成字符串时，None被转成"None"
        df2 = df2.where(df.notnull(), None)  # 对于原来是NaN的，要转成空字符串
        # 创建导数是sql
        sql = "insert into tb_name (cols) values (?_many_times) "
        cols = list(df2.columns)
        cols_string = ', '.join(cols)
        num = len(list(df2.columns))
        num_string = ','.join(['?' for i in range(num)])
        sql = sql.replace('tb_name', tb)
        sql = sql.replace('cols', cols_string)
        sql = sql.replace('?_many_times', num_string)
        # 导入数据
        param = df2.to_records(index=False).tolist()
        # 打开数据库
        conn=sqlite3.connect(db_file)
        cur=conn.cursor()
        # 先判断是否要清空表
        if types.upper() in "TRUNCATE,DELETE":
            truncate_sql = "delete from " + tb
            cur.execute(truncate_sql)
            conn.commit()
        # 然后是导入数据
        try:
            print(sql)
            cur.executemany(sql,param)
            conn.commit()
        except:
            traceback.print_exc()
        # 关闭链接
        cur.close()
        conn.close()

    def dict_into_db(self, tb, data):
        """将字典数据插入到表中.为什么是字典呢，因为字典带有字段名称呀"""
        df = pd.DataFrame(data, index=range(1))  # 字典转成dataframe
        self.df_into_db(tb,df)


    def read_data_from_db_to_df(self,tb=None,sql=None):
        """读取数据，可以指定表明，或者指定SQL"""
        conn = sqlite3.connect(db_file)
        # 读取表格
        if not sql:
            sql = "select * from %s" % tb
        # 执行SQL
        data = pd.read_sql(sql,conn)
        conn.close()
        return data


def test():
    # 测试
    db=dbserbser()
    # 测试插入字典
    tb = 'tb'
    dict_data = {'id': '1', 'name': '123', 'score':'5.32'}
    db.dict_into_db(tb,dict_data)
    # 测试插入df
    tb='test'
    df=pd.DataFrame({'a':[1,2,3], 'b':['a','b','c'],'c':['aa',None,'cc']})
    db.df_into_db(tb,df)



