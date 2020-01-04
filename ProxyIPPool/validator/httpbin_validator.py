import requests
import time
import json
from utils import http
import settings
from domain import Proxy
from utils.log import logger

def check_proxy(proxy):
    '''
    检测代理协议类型, 匿名程度
    :param
    :return:(协议: http和https:2,https:1,http:0, 匿名程度:高匿:0,匿名: 1, 透明:0 , 速度, 单位s )
    '''

    # 根据proxy对象构造, 请求使用的代理
    proxies = {
        'http': "http://{}:{}".format(proxy.ip, proxy.port),
        'https':"https://{}:{}".format(proxy.ip, proxy.port),
    }

    http, http_nick_type, http_speed = _check_http_proxy(proxies)
    https, https_nick_type, https_speed = _check_http_proxy(proxies, False)
    if http and https:
        # 如果http 和 https 都可以请求成功, 说明支持http也支持https, 协议类型为2
        proxy.protocol = 2
        proxy.nick_type = http_nick_type
        proxy.speed = http_speed
    elif http:
        # 如果只有http可以请求成功, 说明支持http协议, 协议类型为 0
        proxy.protocol = 0
        proxy.nick_type = http_nick_type
        proxy.speed = http_speed
    elif https:
        # # 如果只有https可以请求成功, 说明支持https协议, 协议类型为 1
        proxy.protocol = 1
        proxy.nick_type = https_nick_type
        proxy.speed = https_speed
    else:
        proxy.protocol = -1
        proxy.nick_type = -1
        proxy.speed = -1

    logger.debug(proxy)
    return proxy


def _check_http_proxy(proxies, isHttp=True):
    nick_type = -1 # 匿名程度
    speed = -1 # 响应速度
    if isHttp:
        test_url = 'http://httpbin.org/get'
    else:
        test_url = 'https://httpbin.org/get'
    try:
        start = time.time()
        r = requests.get(url=test_url, headers=http.get_request_header(), timeout=settings.TIMEOUT, proxies=proxies)
        if r.ok:
            # 计算响应速度, 保留两位小数
            speed = round(time.time() - start, 2)
            # 把响应内容转换为字典
            content = json.loads(r.text)
            # 获取请求头
            headers = content['headers']
            # 获取origin, 请求来源的IP地址
            ip = content['origin']
            # 获取请求头中 `Proxy-Connection` 如果有, 说明匿名代理
            proxy_connection = headers.get('Proxy-Connection', None)

            if ',' in ip:
                # 如果 `origin` 中有','分割的两个IP就是透明代理IP
                nick_type = 2 # 透明
            elif proxy_connection:
                # 如果 `headers` 中包含 `Proxy-Connection` 说明是匿名代理IP
                nick_type = 1 # 匿名
            else:
                #  否则就是高匿代理IP
                nick_type = 0 # 高匿
            return True, nick_type, speed
        else:
            return False, nick_type, speed
    except Exception as e:
        # logger.exception(e)
        return False, nick_type, speed

if __name__ == '__main__':
    proxy = Proxy('118.190.95.35', '9001')
    # proxy = Proxy('150.107.143.33', '9797')
    rs = check_proxy(proxy)
    print(proxy.protocol)
    print(rs)