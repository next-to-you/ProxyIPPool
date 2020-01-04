import requests
from lxml import etree
from domain import Proxy
from utils.http import get_request_header
"""
### 实现通用爬虫
- `目标`: 实现一个可以通过指定不同URL列表, 分组的XPATH和详情的XPATH, 从不同页面上提取数据;
- `步骤`:
1. 创建spiders的包, 创建base_spider.py文件
2. 定义一个类, 继承object
3. 提供三个类成员变量:
    - urls: 代理IP网址的URL的列表
    - group_xpath: 分组XPATH, 获取包含代理IP信息标签列表的XPATH
    - detail_xpath: 组内XPATH, 获取代理IP详情的信息XPATH
4. 提供初始方法, 传入爬虫URL列表, 分组XPATH, 详情(组内)XPATH
5. 对外提供一个获取代理IP的方法
    - 遍历URL列表, 获取URL
    - 根据发送请求, 获取页面数据
    - 解析页面, 提取数据
    - 把数据返回
"""

class BaseSpider(object):

    urls = [] #  代理IP网址的URL的列表
    group_xpath='' # 分组XPATH, 获取包含代理IP信息标签列表的XPATH
    detail_xpath = {} # 组内XPATH, 获取代理IP详情的信息XPATH

    def __init__(self, urls=[], group_xpath=None, detail_xpath={}):

        if urls: # 如果urls中有数据
            self.urls = urls
        if group_xpath: # 如果group_xpath中有数据
            self.group_xpath = group_xpath
        if detail_xpath: # 如果detail_xpath中有数据
            self.detail_xpath = detail_xpath

    def get_page_from_url(self, url):
        response = requests.get(url, headers=get_request_header())
        return response.content

    def get_first(self, lis):
        return lis[0].strip() if len(lis) != 0 else ''

    def get_proxies_from_page(self, page):
        """解析页面数据"""
        element = etree.HTML(page)
        trs = element.xpath(self.group_xpath)
        # print(len(trs))
        for tr in trs:
            ip = self.get_first(tr.xpath(self.detail_xpath['ip']))
            port = self.get_first(tr.xpath(self.detail_xpath['port']))
            area = self.get_first(tr.xpath(self.detail_xpath['area']))
            proxy = Proxy(ip, port, area=area)
            # 返回代理IP
            yield proxy

    def get_proxies(self):
        """获取代理IP信息"""
        # - 遍历URL列表, 获取URL
        for url in self.urls:
            # - 根据发送请求, 获取页面数据
            page = self.get_page_from_url(url)
            # - 解析页面, 提取数据
            proxies = self.get_proxies_from_page(page)
            # - 把数据返回
            yield from proxies

if __name__ == '__main__':
    config = {
        'urls':['https://www.xicidaili.com/nn/1'.format(i) for i in range(1, 2)],
        'group_xpath': '//*[@id="ip_list"]/tr[position()>1]',
        'detail_xpath': {'ip':'./td[2]/text()', 'port':'./td[3]/text()', 'area':'./td[4]/a/text()'},
    }
    # 创建通用代理对象
    base_spider = BaseSpider(**config)
    for proxy in base_spider.get_proxies():
        print(proxy)






