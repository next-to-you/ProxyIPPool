#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gevent.monkey
gevent.monkey.patch_all()
from gevent.pool import Pool

from queue import Queue
from db.mongo_pool import MongoPool
from validator.httpbin_validator import check_proxy
from utils.log import logger
import settings
import schedule
import time

'''
代理检测者
'''
class ProxyTester(object):
    def __init__(self):
        self.queue = Queue()
        self.pool = Pool() # 协程池
        self.proxy_pool = MongoPool() # 基于MongoDB的代理池

    def _test_proxy(self):
        # 从代理队列中, 获取请求
        proxy = self.queue.get()
        try:
            # 验证当前的代理
            proxy = check_proxy(proxy)
            # 如果速度为-1就说明请求失败了
            if proxy.speed == -1:
                # 代理的分数-1
                proxy.score -= 1

                # 如果分数为0, 就删除该代理
                if proxy.score == 0:
                    self.proxy_pool.delete(proxy)
                    logger.info('删除代理:{}'.format(proxy))
                else:
                    # 如果分数不为0 ,就更新当前的代理
                    self.proxy_pool.update(proxy)
            else:
                # 如果请求成功了, 恢复为最高分数
                proxy.score = settings.MAX_SCORE
                self.proxy_pool.update(proxy)

        except Exception as ex:
            logger.exception(ex)

        self.queue.task_done()

    def _test_proxy_finish(self, temp):
        self.pool.apply_async(self._test_proxy, callback=self._test_proxy_finish)

    def run(self):
        # 1. 获取所有代理IP
        proxies = self.proxy_pool.find()
        # 2. 如果代理池为空, 直接返回
        if proxies is None or len(proxies) == 0:
            print("代理池为空")
            return

        # 获取所有的代理, 放到队列中
        for proxy in proxies:
            self.queue.put(proxy)

        # 开启多个异步任务执行检查IP的任务
        for i in range(settings.TESTER_ANSYC_COUNT):
            self.pool.apply_async(self._test_proxy,callback=self._test_proxy_finish)

        # 让主线程等待异步任务完成
        self.queue.join()

    @staticmethod
    def start():
        tester = ProxyTester()
        tester.run()
        # 每隔2小时检查下代理是否可用
        schedule.every(settings.TESTER_INTERVAL).hours.do(tester.run)
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == '__main__':
    ProxyTester.start()



