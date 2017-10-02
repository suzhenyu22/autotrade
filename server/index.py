# -*- coding: utf-8 -*-
"""
flask异步http服务器
所有网页请求，都必须有返回，不然报错。

外网地址 http://suzhenyu.320.io:33591

注意：通过key参数来判断是普通测试还是买卖指令:
'account' in dict.get('key','')

"""

import datetime
import time
import requests
from flask import Flask, request
import multiprocessing

# log
from autotrade.common.log.logger import mylogger
# dbserver
from autotrade.db.dbserver import dbserbser

# 配置全局app
app = Flask(__name__)
app.config.update(DEBUG=True)
# 配置全局日志
log=mylogger('WebServer.log',name='webserver')


@app.route('/')
def index():
    return str(datetime.datetime.now())[:19]

@app.route('/order',methods=['GET', 'POST','DELETE'])
def order():
    """接收get请求，解析url中的参数"""
    log.info(request.url)
    data=request.args.to_dict()
    if 'account' in data.get('key','0'):
        print(data['key'])
        db = dbserbser()
        db.dict_into_db(tb='orders',data=data)
    return 'I have received you data at time '\
           +str(datetime.datetime.now())[:19]

@app.route('/sync',methods=['GET', 'POST','DELETE'])
def sync():
    # 接收同步持仓数据的页面
    log.info(request.url)
    data = request.args.to_dict()
    if 'account' in data.get('key', '0'):
        db = dbserbser()
        sql="delete from position_remote where key='{key}'".format(key=data['key'])  # 入库前先删除
        db.execute(sql)
        db.dict_into_db(tb='position_remote', data=data)
        return 'I have received you data at time ' \
           + str(datetime.datetime.now())[:19]



def run_index():
    # 启动web服务器，使用多线程方式
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

def run_orders():
    # 启动查询交易程序
    pass



def main():
    # 主程序
    # 创建子进程
    jobs = []
    jobs.append(multiprocessing.Process(target=run_index))
    jobs.append(multiprocessing.Process(target=run_orders))
    # 启动子进程
    for job in jobs:
        job.start()

    # 等待子进程结束返回
    for job in jobs:
        job.join()

if __name__ == '__main__':
    main()