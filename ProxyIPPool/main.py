
from multiprocessing import Process
from spiders.run_spiders import RunSpider
from proxy_test import ProxyTester
from proxy_api import ProxyApi


def run():
    """总启动方法"""
    # 创建
    process_list = []
    process_list.append(Process(target=RunSpider.start, name='run_spider'))
    process_list.append(Process(target=ProxyTester.start, name='run_tester'))
    process_list.append(Process(target=ProxyApi.start, name='run_api'))

    # 启动进程
    for p in process_list:
        # 设置进程为守护进行
        p.daemon = True
        # 进程启动
        p.start()

    # 让主进程等待子进程完成
    for p in process_list:
        p.join()


if __name__ == '__main__':
    run()