"""
测试下单模块.
同花顺模拟测试账号 'account:47875693'

先启动webserver服务器

"""

import datetime
import requests
from autotrade.trade_api import order as order_do
from autotrade.common.log.logger import mylogger

def now():
    # 获取当前时间
    return str(datetime.datetime.now())[:19]


def test_create_order():
    # 生成下单信号，需要的字段见数据字典
    # 市价单买入100股
    data = {
        'key': 'JQ+28小市值+account:47875693',
        'order_id': 'JQ+28小市值+account:47875693+{now}'.format(now=now()),
        'account': 'account:47875693',
        'symbol': '601398',
        'amount': 100,
        'action': 'SELL',
        'type': 'MARKET',
        'priceType': 4,
        'price': 10.1,
        'cash': 1000.0,
        'done': 0,
        'add_time': now() }
    url='http://localhost:5000/order'
    r=requests.get(url,params=data)
    print(r.status_code)
    print(r.text)
    # 查看数据库是否插入对应的记录
    return

def test_orders():
    #
    log = mylogger('order.log', name='order')

    # 测试是否能正常获取回传的信号
    data=order_do.get_orders()

    # 测试日志
    order=data[0]
    log.info(order)

    # 测试模拟账户下单
    code = order_do.do_order(dict_=order, log=log)
    # code=200,查看下单软件，正常下单成功

    # 更新orders信号表
    order_do.update_orders(order=order, code=code, log=log)
    # 查看数据库，done被更新为1

    # 更新本地持仓列表
    order_do.update_position(key=order['key'], action=order['action'],
                    symbol=order['symbol'], amount=order['amount'], log=log)
    # 查看数据库，total_amount为100，再次重复执行，为200





