# @Time     : 2022/5/9 16:01
# @Author   : ShenYiFan
# -*- coding: utf-8 -*-
import pytest


@pytest.fixture(scope="function")
def d(setup_and_teardown_demo):
    """
    额外前置收尾
    @Author: ShenYiFan
    @Create: 2022/5/10 10:19
    :return: Uiautomator
    """
    print("TEST START 屏幕已被点亮")
    yield setup_and_teardown_demo
    print("TEST END 将返回主页面")


def test_case01(d):
    assert d.check_text_exists("相机")


@pytest.mark.skipif(True, reason="Skip demo")
def test_case02(d):
    assert d.check_text_exists("QQ")


@pytest.mark.skipif(False, reason="Skip demo")
def test_case02(d):
    d.click(100)
