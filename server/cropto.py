"""
检查通信密钥是否正确。
如果有必要，可以加上。
"""


from Crypto.Cipher import AES
import binascii
import datetime
import json

key='iamsuzhenyu12345' # 要求16位长度


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

    def decode(self, params_dict):
        # 解密，如果是正常的get则正常返回，否则解密信息
        # 这里约定，如果是加密的，则dict中只有一个字段，这样对取出来的字段进行解密处理
        # 如果没有加密，则判断有没有key字段，且和系统约定的key相同则握手成功
        # 如果是一个字段，则判断是否是加密信息
        signal,data=0,None
        if len(params_dict)==1:
            try:
                string=''.join([v for k,v in params_dict.items()])
                encrypt_msg = binascii.a2b_hex(string.encode())
                iv=datetime.datetime.now().strftime('%Y%m%d%Y%m%d')
                cipher2 = AES.new(key, AES.MODE_CFB, iv)  # 解密时必须重新创建新的密文生成器
                data=cipher2.decrypt(encrypt_msg).decode('utf-8')
                if data[:16]==iv:
                    return 1, json.loads(data[16:])   # data[16:]可能不是字典数据
            except:
                pass
        # 如果不是加密信息，则判断是否是明文传输，还是普通测试
        if not signal:
            if 'key' in params_dict and params_dict['key']==key: # 注意判断顺序不能写反
                return 1,params_dict
            else:
                return 0,params_dict




def test():
    # 原始字符串
    import json
    string = json.dumps({"id":123})
    # 加密
    passwd=cropto()
    string2=passwd.encode(string)
    print(string2)

    # 解密
    string3=passwd.decode(string2)
    print(string3)