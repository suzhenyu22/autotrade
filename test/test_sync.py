"""
测试同步持仓

由于测试买卖的时候，已经往本地持仓列表买入股票，接下来测试，再买入一只股票，卖出刚才的股票
"""

import datetime
import requests
from autotrade.trade_api import order_api
from autotrade.trade_api import sync_position as sync_api
from autotrade.common.log.logger import mylogger

def now():
    # 获取当前时间
    return str(datetime.datetime.now())[:19]

def test_create_order():
    # 生成JQ持仓列表信号
    # 市价单买入100股
    data = {
        'key': 'JQ+28小市值+account:47875693',
        'account': 'account:47875693',
        'symbol': '600001',
        'total_amount': 100,
        'add_time': now() }
    url='http://localhost:5000/sync'
    r=requests.get(url,params=data)
    print(r.status_code) # 由于做了错误捕捉，这里永远返回200
    print(r.text)
    # 查看数据库是否插入对应的记录
    return


def test_sync():
    log=log = mylogger('sync.log', name='sync')
    # 获取远程持仓列表
    all_remote = sync_api.get_position_remote()
    #
    key=all_remote['key'].unique()[0]
    # 获取本地持仓列表
    local = sync_api.get_position_local(key=key)

    # 对比差异
    remote = all_remote.loc[all_remote['key'] == key]
    orders = sync_api.different(remote, local, log)
    # 结果是买入600001 100股，卖出000001 200股

    # 执行买卖操作
    trade = order_api.trade()
    for account, order in orders:
        if order['action'] == 'BUY':
            # account, order=orders[0]
            code, text = trade.buy(data=order, account=account)
        elif order['action'] == 'SELL':
            # account, order=orders[1]
            code, text = trade.sell(data=order, account=account)
        log.info(code)
        log.info(text)


