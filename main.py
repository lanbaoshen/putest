# @Time     : 2022/5/9 16:03
# @Author   : ShenYiFan
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import pytest
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


TITLE = "{0} PUTEST {0}".format("=" * 30)
TEST_RESULT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "result")
TEST_SUITE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_suite")


def get_device():
    """
    获取连接设备
    @Author: ShenYiFan
    @Create: 2022/5/9 16:04
    :return: dict
    """
    cmd = "adb devices | findstr /E device"
    run_out = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True).stdout.splitlines()
    device_ids = {str(index): info.split()[0] for index, info in enumerate(run_out)}
    return device_ids


def get_test_suites():
    """
    获取已有测试套件
    @Author: ShenYiFan
    @Create: 2022/5/9 16:08
    :return: dict{key: (绝对路径, 相对路径)}
    """
    key, test_suites = 0, {}
    for root, dirs, files in os.walk(TEST_SUITE_FOLDER):
        for name in files:
            # 所有 .py 文件视为测试套件
            if not name.endswith(".py") or "conftest.py" == name:
                continue
            file_path = os.path.join(root, name)
            test_suites.update({str(key): (file_path, file_path.replace(TEST_SUITE_FOLDER, ""))})
            key += 1
    return test_suites


def select_device_and_suite():
    """
    确定测试设备和测试套件
    @Author: ShenYiFan
    @Create: 2022/5/10 10:51
    :return: str, tuple(绝对路径，相对路径)
    """
    # 确定测试设备
    while True:
        print("正在检测连接设备...")
        devices = get_device()
        if not devices:
            print("未检测到连接设备！请确保存在 adb 连接设备")
            exit(0)
        print("获取如下连接设备, 请键入数字选择设备:\n{}".format("\n".join([" {}: {}".format(k, v) for k, v in devices.items()])))
        key = input("选择设备: ")
        device = devices.get(key)
        if device:
            print("测试设备选择为: {}\n".format(device))
            break
        print("不存在的设备，请重新选择\n")

    # 确定测试套件
    while True:
        print("正在获取测试套件...")
        test_suites = get_test_suites()
        if not test_suites:
            print("未检测到测试套件！请将测试套件放在 test_suite 目录下")
            exit(0)
        print("获取如下套件, 请键入数字选择套件:\n{}".format("\n".join([" {}: {}".format(k, v[-1]) for k, v in test_suites.items()])))
        key = input("选择测试套件: ")
        test_suite = test_suites.get(key)
        if test_suite:
            print("测试套件选择为: {}\n".format(test_suite[-1]))
            break
        print("不存在的测试套件, 请重新选择\n")

    return device, test_suite


def get_task_id():
    """
    生成不会重复的自增 task id
    @Author: ShenYiFan
    @Create: 2022/5/10 17:20
    :return: str
    """
    _, exists_dir, _ = next(os.walk(TEST_RESULT_FOLDER))
    max_name = -1
    for name in exists_dir:
        try:
            name = int(name)
            max_name = name if name > max_name else max_name
        except ValueError:
            continue
    return str(max_name + 1)


def start_test(device, test_suite):
    """
    启动 pytest
    @Author: ShenYiFan
    @Create: 2022/5/11 13:40
    :param device: 测试设备
    :param test_suite: 测试套件
    :return: str
    """
    task_id = get_task_id()
    allure_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "result", task_id, "allure")
    print("本次任务 ID 为 {} \n测试开始...".format(task_id))

    # TODO 丰富入参控制
    cmd = "-sv {} --device_id {} --task_id {} --alluredir={}".format(test_suite[0], device, task_id, allure_dir)
    pytest.main(cmd.split())
    return allure_dir


def allure_report(allure_dir):
    """
    生成 allure 报告
    @Author: ShenYiFan
    @Create: 2022/5/11 13:49
    :param allure_dir: allure 目录
    :return: None
    """
    # 生成查看报告的 bat 文件
    bat_path = os.path.join(allure_dir, "..", "allure_report.bat")
    cmd = "echo allure serve allure> {}".format(bat_path)
    subprocess.run(cmd, shell=True, timeout=10)

    print("测试结束，是否查看 html 报告？")
    if input("y or yes\n").upper() in ("y", "Y", "yes", "YES"):
        cmd = "allure serve {}".format(allure_dir)
        subprocess.Popen(cmd, shell=True)
    else:
        print("若稍后想查看报告，请执行 result/task id 目录下 allure_report.bat 文件")


def main():
    print(TITLE)
    device, test_suite = select_device_and_suite()
    allure_dir = start_test(device, test_suite)
    allure_report(allure_dir)
    print(TITLE)


if __name__ == '__main__':
    main()
