"""
代理IP数据模型类, 用于封装代理IP信息
"""
import settings
class Proxy(object):

    def __init__(self, ip, port, protocol=-1, nick_type=-1, speed=-1, area=None, score=settings.MAX_SCORE, disable_domains=[]):
        self.ip = ip # 代理的IP地址
        self.port = port # 代理IP的端口号
        self.protocol=protocol #  代理IP支持协议类型,http是0, https是1, https和http都支持是2
        self.nick_type = nick_type # 代理IP的匿名程度, 高匿:0, 匿名: 1, 透明:0
        self.speed = speed # 代理IP的响应速度, 单位s
        self.area = area # 代理IP所在地区
        self.score = score # 代理IP的评分, 默认分值可以通过配置文件进行配置. 在进行代理可用性检查的时候, 每遇到一次请求失败就减1份,
                           # 减到0的时候从池中删除. 如果检查代理可用, 就恢复默认分值
        self.disable_domains = disable_domains # 不可用域名列表, 有些代理IP在某些域名下不可用, 但是在其他域名下可用

    def __str__(self):
        # 为了方便查看代理信息, 重写__str__魔法方法.
        return str(self.__dict__)

if __name__ == '__main__':
    p = Proxy('1', 12)
    dic = dict(p.__dict__)
    print(dic)