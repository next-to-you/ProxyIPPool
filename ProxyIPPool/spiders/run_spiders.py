#!/usr/bin/python3
# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool
import importlib
import schedule
import time

import settings
from validator.httpbin_validator import check_proxy
from db.mongo_pool import MongoPool
from utils.log import logger


class RunSpider(object):
    def __init__(self):
        self.pool = Pool()
        self.proxy_pool = MongoPool()

    def _auto_import_instances(self):
        """根据配置信息, 自动导入爬虫"""
        instances = []
        # 遍历配置的爬虫, 获取爬虫路径
        for path in settings.PROXIES_SPIDERS:
            # 根据路径, 获取模块名 和 类名
            module_name, cls_name = path.rsplit('.', maxsplit=1)
            # 根据模块名导入模块
            module = importlib.import_module(module_name)
            # 根据类名, 从模块中, 获取爬虫类
            cls = getattr(module, cls_name)
            # 创建爬虫对象, 添加到列表中
            instances.append(cls())

        # 返回爬虫对象列表
        return instances

    def run(self):
        """启动爬虫"""
        # 获取代理爬虫
        spiders = self._auto_import_instances()
        # 执行爬虫获取代理
        for spider in spiders:
           # 使用协程异步调用该方法,提高爬取的效率
           self.pool.apply_async(self.__run_one_spider, args=(spider, ))

        # 等待所有爬虫任务执行完毕
        self.pool.join()

    def __run_one_spider(self, spider):
        try:
            for proxy in spider.get_proxies():
                if proxy is None:
                    # 如果是None继续一个
                    continue
                # 检查代理, 获取代理协议类型, 匿名程度, 和速度
                proxy = check_proxy(proxy)
                # 如果代理速度不为-1, 就是说明该代理可用
                if proxy.speed != -1:
                    # 保存该代理到数据库中
                    self.proxy_pool.save(proxy)
        except Exception as e:
            logger.exception(e)
            logger.exception("爬虫{} 出现错误".format(spider))

    @classmethod
    def start(cls):
        # 创建本类对象
        run_spider = RunSpider()
        run_spider.run()

        # 每隔 SPIDER_INTERVAL 小时检查下代理是否可用
        schedule.every(settings.SPIDER_INTERVAL).hours.do(run_spider.run())
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == '__main__':
    RunSpider.start()


