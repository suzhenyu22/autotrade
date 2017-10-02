"""
定义聚宽的数据请求格式和案例。

以下脚本在聚宽策略中运行，不是本地pycharm
"""
# 导入函数库
import jqdata
import datetime
import requests

# 两种不同的时间格式
now1 = lambda: datetime.datetime.now().strftime('%Y%m%d%H%M%S')
now2 = lambda: str(datetime.datetime.now())[:19]

order_data = {
    'key': 'JQ+strategy_name+account:47875693',
    'order_id': 'JQ+strategy_name+account:47875693+{now}'.format(now=now1()),
    'account': 'account:47875693',
    'symbol': '600001',
    'amount': 100,
    'action': 'BUY',
    'type': 'MARKET',
    'priceType': 4,
    'price': 10.1,
    'done': 0,
    'add_time': now2()
}
sync_data = {
    'key': 'JQ+strategy_name+account:47875693',
    'account': 'account:47875693',
    'symbol': '600001',
    'total_amount': 100,
    'add_time': now2()
}


# 初始化函数，设定基准等等
def initialize(context):
    log.set_level('order', 'error')
    g.security = ['000001.XSHE', '601398.XSHG']
    set_universe(g.security)


def handle_data(context, data):
    # 下单操作
    print('-' * 50)
    # 买入
    security = g.security[0]
    order1 = order(security, +200)
    print('order1=', order1)
    # ('order1=', UserOrder({'status': held, 'style': MarketOrderStyle,
    # 'order_id': 1506906158, 'price': 8.47, 'pindex': 0, 'amount': 100,
    # 'action': u'open', 'security': '000001.XSHE',
    # 'side': u'long', 'filled': 100,
    # 'add_time': datetime.datetime(2016, 6, 2, 9, 30)}))
    if order1:
        order_data2 = order_data
        order_data2['symbol'] = str(order1.security)[:6]
        order_data2['amount'] = str(order1.amount)
        order_data2['price'] = str(order1.price)
        order_data2['action'] = 'BUY' if str(order1.action) == 'open' else 'SELL'
        print(order_data2)
        # {'order_id': u'JQ+strategy_name+account:47875693+20171002094124',
        # 'price': '8.51', 'done': 0, 'key': u'JQ+strategy_name+account:47875693',
        # 'add_time': '2017-10-02 09:41:24', 'account': 'account:47875693',
        # 'amount': '200', 'action': 'BUY', 'type': 'MARKET', 'symbol': '000001', 'priceType': 4}
        # 接下来测试数据回传
        url = 'http://suzhenyu.320.io:33591/order'
        r = requests.get(url, params=order_data2)
        print(r.text)
        # 检查数据库，数据正常回传到处理中心，并写入数据库

    # 同步持仓
    print('-' * 50)
    print(context.portfolio.positions)
    # {'000001.XSHE':
    # UserPosition({'avg_cost': 8.5, 'security': '000001.XSHE',
    #               'closeable_amount': 100, 'price': 8.47, 'total_amount': 200}),
    # '601398.XSHG': UserPosition({'avg_cost': 3.945, 'security': '601398.XSHG',
    #               'closeable_amount': 200, 'price': 3.94, 'total_amount': 400})}

    # 通过上面的信息，我们就可以取需要的几个重要字段了
    position = context.portfolio.positions
    if len(position) > 0:
        for symbol, position in context.portfolio.positions.items():
            sync_data2 = sync_data
            sync_data2['symbol'] = position.security[:6]
            sync_data2['total_amount'] = position.total_amount
            # 数据传输
            url = 'http://suzhenyu.320.io:33591/sync'
            r = requests.get(url, params=sync_data2)
            print(r.text)





