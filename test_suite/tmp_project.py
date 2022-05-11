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
@allure.feature("功能测试")
@allure.story("检查页面相机文本控件")
def test_case01(d):
    assert d.check_text_exists("相机")


@allure.severity("blocker")
@allure.feature("功能测试")
@allure.story("检查页面 QQ 文本控件")
@pytest.mark.skipif(True, reason="Skip if demo")
def test_case02(d):
    assert d.check_text_exists("QQ")


@allure.severity("blocker")
@allure.feature("API 测试")
@allure.story("click 参数不正确")
@allure.step("click 失败")
@pytest.mark.skipif(False, reason="Skip if demo")
def test_case03(d):
    # 必定 Fail 的命令
    d.click(100)


@allure.severity("normal")
@allure.title("Case 04 测试正确的 click")
@allure.feature("API 测试")
@allure.story("click 参数正确")
def test_case04(d):
    # 必定 Fail 的命令
    with allure.step("第一次 click"):
        d.click(100, 100)
    with allure.step("第二次 click"):
        d.click(200, 200)
