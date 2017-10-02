# -*- coding: utf-8 -*-
"""
加密解密.

key+iv 为加密方式

id 为当天日期，因此在午夜24点的时候会出现问题，不过这时候也没有应用访问。


"""

from Crypto.Cipher import AES
import binascii
import datetime
from autotrade.config.config import crypto_key

key=crypto_key['key']


class cropto():
    """加密解密"""
    def __init__(self):
        key=None

    def encode(self,string):
        # 加密
        iv=datetime.datetime.now().strftime('%Y%m%d%Y%m%d')
        cipher1 = AES.new(key, AES.MODE_CFB, iv)  # 密文生成器,MODE_CFB为加密模式
        encrypt_msg = cipher1.encrypt(iv+string)  # 附加上iv值是为了在解密时找到在加密时用到的随机iv
        encrypt_msg = binascii.b2a_hex(encrypt_msg)
        return encrypt_msg.decode()

    def decode(self, string):
        # 解密
        encrypt_msg = binascii.a2b_hex(string.encode())
        iv=datetime.datetime.now().strftime('%Y%m%d%Y%m%d')
        cipher2 = AES.new(key, AES.MODE_CFB, iv)  # 解密时必须重新创建新的密文生成器
        try:
            data=cipher2.decrypt(encrypt_msg).decode('utf-8')
            if data[:16]==iv:
                return data[16:]
            else:
                return False
        except:
            return False



def test():
    # 原始字符串
    string = 'i am suzhenyu'
    # 加密
    passwd=cropto()
    string2=passwd.encode(string)
    print(string2)

    # 解密
    string3=passwd.decode(string2)
    print(string3)
