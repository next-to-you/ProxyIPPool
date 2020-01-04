# 默认分数: 用于配置代理IP的最大评分,
# 在进行代理可用性检查的时候, 每遇到一次请求失败就减1份, 减到0的时候从池中删除. 如果检查代理可用, 就恢复默认分值
MAX_SCORE = 50

import logging
# 默认的配置
LOG_LEVEL = logging.INFO    # 默认等级
LOG_FMT = '%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s: %(message)s'   # 默认日志格式
LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'  # 默认时间格式
LOG_FILENAME = 'log.log'    # 默认日志文件名称


# 设置超时时间
TIMEOUT = 10
# 默认给抓取的ip分配50分,每次连接失败,减一分,直到分数全部扣完从数据库中删除
DEFAULT_SCORE = 50
# MongoDB数据库连接
MONGO_URL = 'mongodb://localhost:27017/'

# 配置代理爬虫列表
PROXIES_SPIDERS = [
    'spiders.proxy_spiders.Ip66Spider',
    'spiders.proxy_spiders.Ip3366Spider',
    'spiders.proxy_spiders.IphaiSpider',
    'spiders.proxy_spiders.ProxylistplusSpider',
    'spiders.proxy_spiders.XiciSpider',
]

# 抓取IP的时间间隔, 单位小时
SPIDER_INTERVAL = 2

# 异步
TESTER_ANSYC_COUNT = 10

# 检查可用IP的时间间隔, 单位小时
TESTER_INTERVAL = 1

# 提供可用代理IP的默认数量, 数量越少可用性越高.
AVAILABLE_IP_COUNT = 20