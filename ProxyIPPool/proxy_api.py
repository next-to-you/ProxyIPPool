#!/usr/bin/python3
# -*- coding: utf-8 -*-

from flask import Flask
from flask import request
import json
from db.mongo_pool import MongoPool
import settings


class ProxyApi(object):
    def __init__(self):
        # 初始一个Flask的Web服务
        self.app = Flask(__name__)
        self.proxy_pool = MongoPool()

        @self.app.route('/random')
        def random():
            # 从传入参数中获取URL
            # 根据protocol参数获取协议
            protocol = request.args.get('protocol')
            # 根据domain参数获取域名
            domain = request.args.get('domain')

            proxy = self.proxy_pool.random(protocol=protocol, domain=domain, count=settings.AVAILABLE_IP_COUNT)

            # 如果有协议, 就返回带有协议代理IP和端口号
            if protocol:
                return '{}://{}:{}'.format(protocol, proxy.ip, proxy.port)
            else:
                # 如果没有协议就返回, 不带协议的IP和端口号
                return '{}:{}'.format(proxy.ip, proxy.port)

        @self.app.route('/proxies')
        def proxies():
            # 根据protocol参数获取协议
            protocol = request.args.get('protocol')
            # 根据domain参数获取域名
            domain = request.args.get('domain')

            proxies = self.proxy_pool.get_proxies(protocol=protocol, domain=domain, count=settings.AVAILABLE_IP_COUNT)
            lis = []
            for proxy in proxies:
                lis.append(proxy.__dict__)
            return json.dumps(lis)

        @self.app.route('/disable_domain')
        def disable_domain():
            # 获取IP地址
            ip = request.args.get('ip')
            # 获取不可用域名
            domain = request.args.get('domain')
            if ip is None:
                return '请传入ip参数'
            if domain is None:
                return '请传入domain参数'

            # 更新域名成功
            self.proxy_pool.disable_domain(ip=ip, domain=domain)
            return '该IP添加不可用域名成功'

    def run(self):
        self.app.run(host="0.0.0.0", port=6868)

    @classmethod
    def start(cls):
        proxy_api = cls()
        proxy_api.run()


if __name__ == '__main__':
    ProxyApi.start()