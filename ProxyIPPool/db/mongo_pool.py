import pymongo
import random

from settings import MONGO_URL, DEFAULT_SCORE
from domain import Proxy
from utils.log import logger

class MongoPool(object):
    def __init__(self):
        """初始化"""
        self.client = pymongo.MongoClient(MONGO_URL)
        # 获取要操作的集合
        self.proxies = self.client['proxy_pool']['proxies']

    def __del__(self):
        # 关闭数据库连接
        self.client.close()

    def insert(self, proxy=None):
        """保存代理IP到数据库中"""
        if proxy:
            # 把Proxy对象转换为转换为字典
            dic = proxy.__dict__
            # 设置_id字段, 为代理IP的IP地址
            dic['_id'] = proxy.ip
            # 向集合中插入代理IP
            self.proxies.insert_one(dic)
            logger.info("插入新代理IP:{}".format(dic))
        else:
            logger.error("没有传入要插入的proxy")

    def update(self, proxy=None):
        """更新代理"""
        if proxy:
            self.proxies.update_one({'_id':proxy.ip}, {"$set": proxy.__dict__})
            logger.info("更新代理: {}".format(proxy))
        else:
            logger.error("请求传入要更新的代理")

    def save(self, proxy):
        """ 保存代理信息: 如果代理IP不存在就插入, 存在就更新"""
        # 1. 根据IP查询代理IP数量, 如果数量为0 , 说明该代理IP是新的, 否则该代理IP已经存在
        count = self.proxies.count_documents({'_id': proxy.ip})
        # 如果如果代理IP不存在就插入, 否则, 更新原来的代理IP信息
        if count == 0:
            self.insert(proxy)
        else:
            self.update(proxy)

    def find(self, conditions=None, count=0):
        """
        根据条件查询代理IP
        :param conditions: # 字典形式的查询条件
        :param count: 查询多少条数据
        :return: 返回先按分数降序, 后按响应速度升序排列前count条数据, 如果count==0, 就查询所有的,
        """
        # 如果没有conditions, 将conditions设置为{}
        if conditions is None:
            conditions = {}

        # 获取查询的游标地下
        cursor = self.proxies.find(conditions, limit=count).sort(
             [("score", pymongo.DESCENDING), ("speed", pymongo.ASCENDING)])
        # 创建一个list, 用于存储Proxy
        results = []
        # 变量游标, 获取代理IP
        for item in cursor:
            # 创建Proxy对象
            proxy = Proxy(item['ip'], item['port'],
                           score=item['score'], protocol=item['protocol'],
                           nick_type=item['nick_type'], speed=item['speed'],
                           disable_domains=item['disable_domains'])
            # 把Proxy对象添加到结果集
            results.append(proxy)
        # 返回查询的结果
        return results

    def delete(self, proxy=None):
        """根据条件删除代理IP"""
        if proxy:
            self.proxies.delete_one({'_id': proxy.ip})
            logger.info('删除代理: {}'.format(proxy))
        else:
            logger.error("请传入要删除的代理")

    def get_proxies(self, protocol=None, domain=None, count=0, nick_type=0):
        """
        根据协议类型, 获取代理IP, 默认查询都是高匿的
        :param protocol: 协议: http 或 https
        :param domain: 要访问网站的域名
        :param count: 代理IP的数量, 默认全部
        :param nick_type: 匿名程度, 默认为高匿

        :return:
        """

        conditions = {'nick_type': nick_type}
        if domain:
            # 如果有域名, 就获取不可用域名中, 没有该域名的代理
            conditions['disable_domains'] = {'$nin':[domain]}

        if protocol is None:
            # 如果没有协议, 就获取及支持http 又支持https的协议
            conditions['protocol'] = 2
        elif protocol.lower() == 'http':
            # 如果是HTTP的请求, 使用支持http 和 支持http/https均可以
            conditions['protocol'] = {'$in': [2, 0]}
        elif protocol.lower() == 'https':
            # 如果是HTTP的请求, 使用支持https 和 支持http/https均可以
            conditions["protocol"] = {'$in': [2, 1]}

        print(conditions)
        return self.find(conditions, count=count)

    def random(self, protocol=None, domain=None, count=0):
        """
        从指定数量代理IP中, 随机获取一个
        :param protocol: 协议: http 或 https
        :param domain: 要访问网站的域名
        :param count: 代理IP的数量
        :return: 一个随机获取代理IP
        """
        proxy_list = self.get_proxies(protocol, domain=domain, count=count)
        return random.choice(proxy_list)

    def disable_domain(self, ip, domain):
        # 如果该IP下没有这个域名才更新
        if self.proxies.count_documents({'_id':ip,'disable_domains':domain}) == 0:
            # 向指定IP的不可用域名中添加域名
            self.proxies.update_one({'_id': ip}, {'$push': {'disable_domains': domain}})


if __name__ == '__main__':
    # 1. 保存代理IP
    proxy_pool = MongoPool()
    # proxy = Proxy('124.89.97.43', '80', protocol=1, nick_type=0, speed=0.36, area='陕西省商洛市商州区')
    # proxy = Proxy('124.89.97.43', '80', protocol=2, nick_type=0, speed=0.36, area='陕西省商洛市商州区')
    # proxy = Proxy('124.89.97.44', '80', protocol=1, nick_type=0, speed=0.36, area='陕西省商洛市商州区')
    # proxy = Proxy('124.89.97.45', '80', protocol=0, nick_type=0, speed=0.36, area='陕西省商洛市商州区')
    # proxy = Proxy('124.89.97.46', '80', protocol=0, nick_type=2, speed=0.36, area='陕西省商洛市商州区')
    # mongo.save(proxy)

    # 获取大理IP列表
    # proxies = mongo.get_proxies('http')
    # proxies = mongo.get_proxies('https', domain='baidu.com')
    # 随机获取一个代理IP
    # proxy = mongo.random('http')
    # proxy = mongo.random('https')
    # print(proxy)
    # 删除代理IP
    # proxy = Proxy('124.89.97.46', '80', protocol=0, nick_type=2, speed=0.36, area='陕西省商洛市商州区')
    # mongo.delete(proxy)

    # 向不可用字段中,添加不可用域名
    proxy_pool.disable_domain('124.89.97.44', 'baidu.com')
    # 查询高匿代理IP
    # proxies = proxy_pool.get_proxies(protocol='http', domain='baidu.com')
    proxies = proxy_pool.find({'disable_domains': {'$nin':['baidu.com']}})
    for proxy in proxies:
        print(proxy)
    print(len(proxies))











