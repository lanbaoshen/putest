# @Time     : 2022/5/10 9:55
# @Author   : ShenYiFan
# -*- coding: utf-8 -*-
import os
import sys
import pytest
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from core.uiautomator import Uiautomator


d = None


def pytest_addoption(parser):
    """
    hook 函数，增加执行参数
    @Author: ShenYiFan
    @Create: 2022/5/10 16:01
    :return: None
    """
    parser.addoption("--device_id", action="store", type=str)


@pytest.fixture(scope="function")
def device_id(request):
    """
    实例化 Uiautomator
    @Author: ShenYiFan
    @Create: 2022/5/10 16:09
    :return: Uiautomator
    """
    global d
    # d 每次执行测试只需要实例化一次，所以这样写
    if not d:
        d = Uiautomator(request.config.getoption("--device_id"))
    return d


# TODO 之前是从文件中读取 id，所以用装饰器 @pytest.mark.parametrize("d", d)
@pytest.fixture(scope="function")
def setup_and_teardown_demo(device_id):
    """
    通用前置：亮屏
    通用收尾：回到主页面
    @Author: ShenYiFan
    @Create: 2022/5/9 17:32
    :return: Uiautomator
    """
    d.screen_on()
    yield d
    d.press("home")
