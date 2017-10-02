"""
使用实盘易实现查询持仓和交易功能基本的功能.
函数命名和SDK保持一致

注意，实盘易以管理员身份启动
注意，关闭360等杀毒软件

"""

import pandas as pd
import requests
import json

from autotrade.trade_api import order_api_columns_map

# 下面是本地测试的参数
# host, port = 'localhost', 8888
host, port = 'suzhenyu.320.io', 23464


# 同花顺和通达信两个客户端的账户
# 注意格式：
# ths = 'account:47875693'
# tdx = 'account:17051079489'
# account = ths


class trade():
    """使用http的方式进行查询，而不是SDK"""

    def __init__(self):
        self.url = host
        self.port = port

    def geturl(self, page=None, account=None):
        # 拼接http-url，page，即路由转发访问内容，比如持仓，账户信息等
        # 需要注意字符串拼接顺序
        # url
        url = 'http://{url}:{port}'.format(url=host, port=port)
        # page
        if page:
            url = url + '/{page}'.format(page=page)
        # account
        if account:
            url = url + '?client={account}'.format(account=account)
        return url

    def get_account(self, account=None):
        # 查询账号
        # url2=geturl(page='accounts',account=account)
        url2 = self.geturl(page='accounts', account=account)
        r = requests.get(url2)
        if r.status_code == 200:
            return r.status_code, r.text
        else:
            return r.status_code, r.text

    def get_positions(self, account=None):
        # 获取资金和持仓列表
        # url2=geturl(page='positions',account=account)
        url2 = self.geturl(page='positions', account=account)
        r = requests.get(url2)
        if r.status_code == 200:
            data = json.loads(r.text)
            # 取出总资金，可用资金,转成dict，这样方便读取其他模块读取数据
            # 虽然转成dict更方便，但是为了和SDK保持一致，还是输出dataframe
            money = pd.DataFrame.from_dict(data['subAccounts'], orient='index')
            # account.to_dict(orient='recorde')[0]
            # 取出持仓
            position = pd.DataFrame(data['dataTable']['rows'], columns=data['dataTable']['columns'])
            # 返回
            return r.status_code, money, position
        else:
            return r.status_code, r.text, r.text  # 统一返回值类型

    def get_orders(self, account=None, status=None):
        # 查询当日委托，包括当日委托，查询可撤单,查询当日成交
        # status: None:查询当日委托, filled: 查询当日成交, open: 查询可撤单
        # url2=geturl(page='orders',account=account)
        url2 = self.geturl(page='orders', account=account)
        r = requests.get(url2, params={'status': status})
        if r.status_code == 200:
            data = json.loads(r.text)
            data2 = pd.DataFrame(data['dataTable']['rows'],
                                 columns=data['dataTable']['columns'])
            return r.status_code, data2
        else:
            return r.status_code, r.text

    def cancel(self, account=None, order_id=''):
        # 撤单
        # order_id='O1709251406300073221'
        # url2=geturl(page='orders', account=account)
        url2 = self.geturl(page='orders', account=account)
        url2 = url2.replace('?', '/%s?' % order_id)  # 将订单id插在account前面
        r = requests.delete(url2)
        return r.status_code, r.text

    def cancel_all(self, account):
        # 全部撤单
        # url2=geturl(page='orders', account=account)
        url2 = self.geturl(page='orders', account=account)
        r = requests.delete(url2)
        return r.status_code, r.text

    def buy(self, data, account=None):
        # 买入
        # url2=geturl(page='orders',account=tdx)
        # data={ "action": "BUY", "symbol": "601398", "type": "MARKET", "priceType": 4, "price": 9.00, "amount": 100 }
        url2 = self.geturl(page='orders', account=account)
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url2, json=data, headers=headers)
        # 返回订单id
        if r.status_code == 200:
            data = json.loads(r.text)
            return r.status_code, data['id']  # 解析交易订单id
        else:
            return r.status_code, r.text

    def sell(self, data, account=None):
        # 卖出
        # url2=geturl(page='orders',account=tdx)
        # data={ "action": "SELL", "symbol": "000001", "type": "MARKET", "priceType": 4, "price": 9.00, "amount": 100 }
        url2 = self.geturl(page='orders', account=account)
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url2, json=data, headers=headers)
        print('123')
        # 返回订单id
        if r.status_code == 200:
            data = json.loads(r.text)
            return r.status_code, data['id']  # 解析交易订单id
        else:
            return r.status_code, r.text

    def get_statuses(self, account=None):
        # 查询账户状态
        # url2=geturl(page='statuses', account=tdx)
        url2 = self.geturl(page='statuses', account=account)
        r = requests.get(url2)
        return r.status_code, r.text

    def clients_status(self, account=None, change_status=None):
        # 查看客户端状态
        # 已登录：LOGGED, 已锁定：LOCKED, 已断开：DISCONNECTED, 已退出：STOPPED
        # url2 = geturl(page='clients',account=tdx)  # account=mn_account
        url2 = self.geturl(page='clients')
        r = requests.get(url2)
        data = [data for data in json.loads(r.text)
                if account.split(':')[-1] in data['accountInfo']][0]
        # 如果不是改变客户端状态，那么直接返回客户端现在的状态
        if not change_status:
            return r.status_code, data['status']
        # 如果是要改变状态，则改变状态
        name = data['name']
        if len(name) == 0:
            return -1, '当前客户端client没有指定名字，请检查'
        url2 = self.geturl(page='clients') + '/%s' % name
        r = requests.patch(url2, data={'status': change_status})  # change_status='STOPPED'
        return r.status_code, r.text


def test():
    # 实例化
    client = trade()

    account = 'account:47875693'
    account = 'account:17051079489'

    # 获取账号名
    client.get_account(account=account)
    # (200, '47875693  UID_413620  模拟炒股')

    # 获取资金与持仓列表
    code, money, positions = client.get_positions(account=account)

    # 买入，市价单
    data = {"action": "BUY", "symbol": "601398", "type": "MARKET",
            "priceType": 4, "price": 5.5, "amount": 1000000}
    code, order_id = client.buy(data=data, account=account)

    # 卖出，市价单
    data = {"action": "SELL", "symbol": "601398", "type": "MARKET",
            "priceType": 4, "price": 9.00, "amount": 100}
    code, order_id = client.sell(data=data, account=account)

    # 查看当日委托
    code, orders = client.get_orders(account=account)
    # 返回dataframe

    # 查询当日成交
    code, orders = client.get_orders(account=account, status='filled')

    # 查询可撤单
    code, orders = client.get_orders(account=account, status='open')

    # 撤销订单
    code, text = client.cancel(account=account, order_id='809510231')

    # 撤销全部订单
    code, text = client.cancel_all(account=account)

    # 查询状态
    code, statu = client.get_statuses(account=account)
    # (200, '运行正常')

    # 客户端状态
    code, status = client.clients_status(account=account)
