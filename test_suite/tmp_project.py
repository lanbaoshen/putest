# @Time     : 2022/5/9 16:01
# @Author   : ShenYiFan
# -*- coding: utf-8 -*-
# 测试套件示例
# 若想通过 main.py 启动测试，测试用例请按照 pytest 函数式编写规范

import pytest
import allure


# 一个自定义的前置和收尾，将会在 setup_and_teardown_demo 的前置后执行前置，收尾前执行收尾
@pytest.fixture(scope="function")
def d(setup_and_teardown_demo):
    """
    额外前置收尾，将实例化对象重命名
    @Author: ShenYiFan
    @Create: 2022/5/10 10:19
    :return: Uiautomator
    """
    print("Setup")
    yield setup_and_teardown_demo
    print("Teardown")


@allure.severity("normal")
def test_case01(d):
    assert d.check_text_exists("相机")


@pytest.mark.skipif(True, reason="Skip if demo")
def test_case02(d):
    assert d.check_text_exists("QQ")



@pytest.mark.skipif(False, reason="Skip if demo")
def test_case02(d):
    # 必定 Fail 的命令
    d.click(100)
