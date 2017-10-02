"""
sqlite3高并发读写测试.

多进程高并发确实会出现数据库锁，不仅仅是表锁

读的频率是0.01秒
删除的频率是0.01秒
写的频率是5秒

如果在外部没有Navicat的连接锁库，在单个py程序中，是可以实现高并发的，测试中并没有出现锁库的情况。
但是程序一旦运行起来，外部的Navicat连接就报错说锁库了

"""
import traceback
import sqlite3
import datetime
import time
import multiprocessing
import threading
from autotrade.db.dbserver import dbserbser

def write():
    # 每隔5秒钟写一条记录
    while True:
        db=dbserbser()
        try:
            sql="insert into testsqlite3 (t) values ('%s')"%\
                str(datetime.datetime.now())[:19]
            db.execute(sql)
            time.sleep(0.01)
            print('write ')
        except Exception as e:
            traceback.print_exc()

def delete():
    # 每隔7秒中删除表记录
    while True:
        db=dbserbser()
        try:
            sql="delete from testsqlite3"
            db.execute(sql)
            time.sleep(0.01)
            print('delete')
        except Exception as e:
            traceback.print_exc()

def read():
    # 每隔0.05秒读取表数据
    while True:
        db=dbserbser()
        try:
            sql="select * from testsqlite3"
            db.execute(sql)
            time.sleep(0.01)
            print('read')
        except Exception as e:
            traceback.print_exc()

def main():
    # 成交多进程
    thread_list = []  # 定义一个线程列表

    # 多进程方式
    # 每隔操作函数复制几次
    thread_list.append(multiprocessing.Process(target=delete))
    thread_list.append(multiprocessing.Process(target=delete))
    thread_list.append(multiprocessing.Process(target=delete))
    thread_list.append(multiprocessing.Process(target=write))
    thread_list.append(multiprocessing.Process(target=write))
    thread_list.append(multiprocessing.Process(target=write))
    thread_list.append(multiprocessing.Process(target=read))
    thread_list.append(multiprocessing.Process(target=read))
    thread_list.append(multiprocessing.Process(target=read))

    # 多线程方式
    # thread_list.append(threading.Thread(target=write))
    # thread_list.append(threading.Thread(target=delete))
    # thread_list.append(threading.Thread(target=read))
    # thread_list.append(threading.Thread(target=write))
    # thread_list.append(threading.Thread(target=delete))
    # thread_list.append(threading.Thread(target=read))

    for a in thread_list:
        a.start()
        time.sleep(0.1)

    for a in thread_list:
        a.join()  # 表示等待直到线程运行完毕

if __name__ == '__main__':
    main()