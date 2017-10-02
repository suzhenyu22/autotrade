"""
从数据库读取信号，然后执行对应的操作
"""

import traceback
import time
import datetime

from autotrade.trade_api.order_api import trade as trade_api
from autotrade.db.dbserver import dbserbser
from autotrade.common.log.logger import mylogger

# 配置全局的数据库连接和日志
log = mylogger('order.log', name='order')
db = dbserbser()


def get_orders():
    # 从信号表中读取未执行的交易信号
    sql = " select * from orders where done=0 "  # 不对-1失败的单操作
    data = db.read_data_from_db_to_df(sql=sql)
    data = data.to_dict(orient='record')  # 转成list-dict格式
    return data

def update_orders(order,code,log):
    # 如果成功执行买卖指令，那么就更新orders信号表
    # 更新signal表，成功done=1,失败done=-1
    if code == 200:
        sql = "update orders set done=1 where order_id='{order_id}'".format(order_id=order['order_id'])
    else:
        sql = "update orders set done=-1 where order_id='{order_id}'".format(order_id=order['order_id'])
    db.execute(sql)
    log.info(sql)

def update_position(key, action, symbol, amount,log):
    # 更新本地持仓列表
    # 判断key是否存在（key=JQ+策略+账户）
    db = dbserbser()
    sql = "select 1 from position_local where key='{key}' and symbol='{symbol}'".format(key=key, symbol=symbol)
    log.info(sql)
    data = db.read_data_from_db_to_df(sql=sql)
    # 如果不存在，则插入该表记录
    add_time = str(datetime.datetime.now())[:19]
    if len(data) == 0:
        sql = "insert into position_local (key,symbol,total_amount,add_time) " \
              "values ('{key}','{symbol}',{amount},'{add_time}')". \
            format(key=key, symbol=symbol, amount=amount, add_time=add_time)
    # 如果已存在，则更新
    elif action == 'BUY':
        sql = "update position_local set total_amount=total_amount+{amount} , add_time='{add_time}'" \
              "where key='{key}' and symbol='{symbol}'".format(amount=amount, key=key, add_time=add_time,symbol=symbol)
    elif action == 'SELL':
        sql = "update position_local set total_amount=total_amount-{amount}, add_time='{addtime}' " \
              "where key='{key}' and symbol='{symbol}' ".format(amount=amount, key=key,add_time=add_time,symbol=symbol)
    db.execute(sql)
    log.info(sql)
    # 最后删除那些持仓未0的记录
    sql = "delete from position_local where total_amount<=0"
    db.execute(sql)
    log.info(sql)


def do_order(dict_,log):
    # 执行下单操作.dataframe的一行表示一个下单信号.
    # dict_是一个字段，为了防止和dict重命名，加了下划线
    # 取出需要的字段传给api借口即可
    cols = ["action", "symbol", "type", "priceType", "price", "amount"]
    body = {}
    for col in cols:
        body[col] = dict_[col]
    trade = trade_api()
    # 如果失败，则重试三次
    for i in range(3):
        if body['action'] == 'BUY':
            code, text = trade.buy(data=body, account=dict_['account'])
        elif body['action'] == 'SELL':
            code, text = trade.buy(data=body, account=dict_['account'])
        if code == 200:
            break
        log.info(code)
        log.info(text)
    return code


def main():
    while True:
        try:
            # 获取信号列表
            data = get_orders()
            # 如果没有数据，则等待几秒钟
            if len(data) == 0:
                time.sleep(3)
                continue
            # 有数据，则执行下单操作
            for order in data:
                log.info(order)
                code=do_order(dict_=order,log=log)
                # 如果下单，不管成功失败够更新orders表的状态
                update_orders(order=order, code=code, log=log)
                # 除了更新orders信号表外，还需要更新position_local本地持仓表
                if code==200:
                    update_position(key=order['key'], action=order['action'],
                                    symbol=order['symbol'],amount=order['amount'], log=log)
        except Exception as e:
            log.error(traceback.format_exc())


if __name__ == '__main__':
    main()
