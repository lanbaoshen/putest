# @Time     : 2022/5/10 9:55
# @Author   : ShenYiFan
# -*- coding: utf-8 -*-
import pytest
from util import yaml_util
from core.uiautomator import Uiautomator


# 自动创建 Uiautomator 对象
yaml_dict = yaml_util.get_yaml_data()
d = Uiautomator(yaml_dict["device_id"])


# d 只需要实例化一次，所以这样写
@pytest.fixture(scope="function")
@pytest.mark.parametrize("d", d)
def setup_and_teardown_demo():
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
