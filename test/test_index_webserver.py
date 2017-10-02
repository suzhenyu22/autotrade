"""
测试web服务器是否能正常接受外部get请求，并将数据写到sqlite3
"""

import requests
import datetime

# 构造订单url参数，见数据字典
# 由于order与数据库order关键字重复，用order_重命名
data = {
    'key': 'JQ+28小市值+account:15012345',
    'order_id': 'JQ+28小市值+account:15012345+{now}'. \
        format(now=datetime.datetime.now().strftime('%Y%m%d%H%M%S')),
    'account': 'account:15012345',
    'add_time': '2017-10-01 21:13:45',
    'amount': 100,
    'cash': 1000.0,
    'done': 0,
    'action': 'BUY',
    'price': 10.1,
    'priceType': 4,
    'security': '000001',
    'status': 'filled',
    'symbol': '000001',
    'type': 'MARKET'}


def test_order_page():
    # 测试order页面接收请求，并将数据保存到数据库
    url = 'http://localhost:5000/order'
    r = requests.get(url, params=data)
    if r.status_code == 200:
        print('200 OK')
    else:
        print(r.text)


# 构造同步持仓url参数
data = {
    'key': 'JQ+28小市值+account:15012345',
    'account': 'account:15012345',
    'add_time': str(datetime.datetime.now())[:19],
    'symbol': '000001',
    'total_amount': 100,
    'price': 9.5}


def test_sync_page():
    url = 'http://localhost:5000/sync'
    r = requests.get(url, params=data)
    if r.status_code == 200:
        print('200 OK')
    else:
        print(r.text)
