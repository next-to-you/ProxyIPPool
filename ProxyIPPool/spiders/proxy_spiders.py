import requests
import re
import js2py

from spiders.base_spider import BaseSpider
from utils.http import get_request_header
from domain import Proxy

"""
1. 实现`西刺代理`爬虫: `http://www.xicidaili.com/nn/1`
    - 定义一个类,继承通用爬虫类(BasicSpider)
    - 提供urls, group_xpath 和 detail_xpath
"""

class XiciSpider(BaseSpider):
    urls = ['http://www.xicidaili.com/nn/{}'.format(i) for i in range(1, 10)]
    group_xpath = '//*[@id="ip_list"]/tr[position()>1]'
    detail_xpath = {'ip': './td[2]/text()', 'port': './td[3]/text()', 'area': './td[4]/a/text()'}

"""
2. 实现`ip3366代理`爬虫: `http://www.ip3366.net/free/?stype=1&page=1`
        - 定义一个类,继承通用爬虫类(BasicSpider)
        - 提供urls, group_xpath 和 detail_xpath
"""
class Ip3366Spider(BaseSpider):
    urls = ['http://www.ip3366.net/free/?stype={}&page={}'.format(i, j) for j in range(1, 10) for i in range(1, 4, 2)]
    group_xpath = '//*[@id="list"]/table/tbody/tr'
    detail_xpath = {'ip':'./td[1]/text()', 'port':'./td[2]/text()','area':'./td[5]/text()' }

"""
3. 实现`ip嗨代理`爬虫:   `http://www.iphai.com/free/ng`
    - 定义一个类,继承通用爬虫类(BasicSpider)
    - 提供urls, group_xpath 和 detail_xpath
"""
class IphaiSpider(BaseSpider):
    urls = ['http://www.iphai.com/free/ng', 'http://www.iphai.com/free/wg']
    group_xpath = '//table/tr[position()>1]'
    detail_xpath = {'ip':'./td[1]/text()', 'port':'./td[2]/text()', 'area':'./td[5]/text()' }

"""
4. 实现`proxylistplus代理`爬虫: `https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1`
    - 定义一个类,继承通用爬虫类(BasicSpider)
    - 提供urls, group_xpath 和 detail_xpath
"""
class ProxylistplusSpider(BaseSpider):
    urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-{}'.format(i) for i in range(1, 7)]
    group_xpath = '//*[@id="page"]/table[2]/tr[position()>2]'
    detail_xpath = {'ip':'./td[2]/text()', 'port':'./td[3]/text()', 'area':'./td[5]/text()'}

"""
5. 实现`66ip`爬虫: `http://www.66ip.cn/1.html`
    - 定义一个类,继承通用爬虫类(BasicSpider)
    - 提供urls, group_xpath 和 detail_xpath
"""
class Ip66Spider(BaseSpider):
    urls = ['http://www.66ip.cn/{}.html'.format(i) for i in range(1, 10)]
    group_xpath = '//*[@id="main"]/div/div[1]/table/tr[position()>1]'
    detail_xpath = {'ip': './td[1]/text()', 'port': './td[2]/text()', 'area': './td[3]/text()'}
    def get_page_from_url(self, url):
        """发送请求, 获取响应的方法"""
        # 获取session对象, session可以记录服务器设置过来的cookie信息
        session = requests.session()
        session.headers = get_request_header()
        respsone = session.get(url)
        # 如果响应码是521
        if respsone.status_code == 521:
            # 通过正则获取, 需要执行的js
            rs = re.findall('window.onload=setTimeout\("(\w+\(\d+\))", \d+\); (function \w+\(\w+\).+?)</script>', respsone.content.decode())
            # 获取js2py的js执行环境
            context = js2py.EvalJs()

            # 把执行执行js, 修改为返回要执行的js
            func = rs[0][1].replace('eval("qo=eval;qo(po);");', 'return po;')
            # 让js执行环境, 加载要执行的js
            context.execute(func)
            # 把函数的执行结果赋值给一个变量
            context.execute( "a={}".format(rs[0][0]))
            # 从变量中取出cookie信息
            cookie = re.findall("document.cookie='(\w+)=(.+?);", context.a)
            # 把从js中提取的cookie信息设置给session
            session.cookies[cookie[0][0]] = cookie[0][1]
            # print(session.cookies)
            respsone = session.get(url)

        return respsone.content.decode('gbk')

if __name__ == '__main__':
    # spider = XiciSpider()
    # spider = Ip3366Spider()
    # spider = IphaiSpider()
    # spider = ProxylistplusSpider()
    spider = Ip66Spider()
    for proxy in spider.get_proxies():
        print(proxy)