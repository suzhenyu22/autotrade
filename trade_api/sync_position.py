"""
同步持仓
"""
import time
import traceback

from autotrade.trade_api.order_api import trade as trade_api
from autotrade.db.dbserver import dbserbser
from autotrade.common.log.logger import mylogger


def get_position_remote():
    # 读取sync回来的JQ持仓表数据
    sql = "select key,symbol,price,total_amount from position_remote"
    db = dbserbser()
    data = db.read_data_from_db_to_df(sql=sql)
    return data


def get_position_local(key):
    # 获取本地某个账号对应某个策略的持仓信息
    sql = "select key,symbol,price,total_amount from position_local " \
          "where key='{key}'".format(key=key)
    db = dbserbser()
    data = db.read_data_from_db_to_df(sql=sql)
    return data


def get_account_from_key(key):
    # 从key中解析account
    return [s for s in key.split('+') if 'account' in s][0]




def different(remote, local, log):
    # 对比远程持仓和本地持仓的不同，然后执行对应的操作
    # 输入的都是df
    all_orders = []
    for symbol in remote['symbol'].unique():
        # 初始化order命令
        order = {"action": "", "symbol": "", "type": "MARKET",
                 "priceType": 4, "price": 0.00, "amount": 100}
        # 取出本地和远程持仓数据
        r_amount = remote.loc[remote['symbol'] == symbol, 'total_amount'].iat[0]
        l_amount = local.loc[local['symbol'] == symbol, 'total_amount']
        l_amount = l_amount.iat[0] if len(l_amount) else 0
        # 判断需要卖出还是买入
        if r_amount > l_amount and (r_amount - l_amount) >= 100:
            order['action'] = 'BUY'
            order['symbol'] = symbol
            order['amount'] = int((r_amount - l_amount) / 100) * 100
            log.info(order)
        elif r_amount > l_amount and (r_amount - l_amount) < 100:
            log.info('需要买入，但是差额<100股，买入失败')
        elif r_amount < l_amount:
            order['action'] = 'SELL'
            order['symbol'] = symbol
            order['amount'] = int(l_amount - r_amount)
            log.info(order)
        # 将order添加到all_orders中
        if order['symbol']:
            key = remote.loc[remote['symbol'] == symbol, 'key'].iat[0]
            account = get_account_from_key(key)
            all_orders.append([account, order])
    # 上面是判断remote中有local中没有或者有一部分，还没有判断local中有而remote中没有的
    # 这种清空下需要对local中的symbol清仓
    for symbol in local['symbol'].unique():
        if symbol not in remote['symbol'].tolist():
            order = {"action": "", "symbol": "", "type": "MARKET",
                     "priceType": 4, "price": 0.00, "amount": 100}
            l_amount = local.loc[local['symbol'] == symbol, 'total_amount'].iat[0]
            order['action'] = 'SELL'
            order['symbol'] = symbol
            order['amount'] = int(l_amount)  # 转成普通的int型，不然报错
            key = local.loc[local['symbol'] == symbol, 'key'].iat[0]
            account = get_account_from_key(key)
            all_orders.append([account, order])
    return all_orders


def sync():
    # 获取日志
    log = mylogger('sync.log', name='sync')

    # 开始同步
    while True:
        try:
            # 获取远程持仓和本地持仓
            all_remote = get_position_remote()
            if len(all_remote) == 0:
                time.sleep(5 * 50)
                continue
            # 对每个账户每隔策略key，进行判断
            for key in all_remote['key'].unique():
                local = get_position_local(key=key)
                # 获取差异对比订单
                remote = all_remote.loc[all_remote['key'] == key]
                orders = different(remote, local, log)
                # 执行买卖操作
                if len(orders) == 0:
                    time.sleep(5 * 60)
                    continue
                #
                trade = trade_api()
                for account, order in orders:
                    if order['action'] == 'BUY':
                        code, text = trade.buy(data=order, account=account)
                    elif order['action'] == 'SELL':
                        code, text = trade.sell(data=order, account=account)
                    log.info(code)
                    log.info(text)
        except Exception as e:
            log.info(traceback.format_exc())
            time.sleep(5 * 60)


if __name__ == '__main__':
    sync()
