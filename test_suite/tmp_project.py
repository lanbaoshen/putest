# @Time     : 2022/5/9 16:01
# @Author   : ShenYiFan
# -*- coding: utf-8 -*-
import pytest
from util import yaml_util
from core.uiautomator import Uiautomator

yaml_dict = yaml_util.get_yaml_data()
d = Uiautomator(yaml_dict["device_id"])


@pytest.fixture(autouse=True)
@pytest.mark.parametrize("d", d)
def setup_and_teardown_demo():
    """
    前置：亮屏
    收尾：回到主页面
    @Author: ShenYiFan
    @Create: 2022/5/9 17:32
    :return: Uiautomator
    """
    d.screen_on()
    yield d
    d.press("home")


def test_case01():
    assert d.check_text_exists("相机")


def test_case02():
    assert d.check_text_exists("QQ")
