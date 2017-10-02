# autotrade
多策略多账户自动化交易管理

# 核心原理
核心实盘交易使用'实盘易'软件，交易信号由聚宽，米框，果仁，雪球等量化交易平台生成，通过http方式将信号回传至autotrade处理中心，由autotrade选择对应的账户执行买卖标的操作。


# 网络拓补
见网络拓补结构

# 运行
先启动`server/index.py` flask服务器，然后参照`test`文件夹下的各个例子调用。

# 模块说明
- common 常用的公共借口API
- config 全局参数配置
- db 数据库操作
- doc 项目说明文档
- logs 日志目录
- server flask服务器
- test 测试example
- trade_api 核心交易API


