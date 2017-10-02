# -*- coding: utf-8 -*-
"""
在这里写文档说明...
"""
import os
import autotrade


# 全局变量配置
# 工作目录
workpath=autotrade.__path__._path[0]

# 日志目录
logpath=os.path.join(workpath, 'logs')

# 服务器ip，port
webserver_ip=['http://suzhenyu.320.io',33591]

# 加密解密密钥,16位长度

# pgsql数据库访问
db_params=['127.0.0.1',5432,'postgres','123456']

# sqlite3数据库文件地址
db_file=os.path.join(autotrade.__path__._path[0], 'db','stock_sqlite3.db')

# 实盘易访问地址
shipane_ip=['http://localhost',8888]