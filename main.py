# @Time     : 2022/5/9 16:03
# @Author   : ShenYiFan
# -*- coding: utf-8 -*-
import os
import subprocess
import pytest
from util import yaml_util


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
    device_ids = {index: info.split()[0] for index, info in enumerate(run_out)}
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
            file_path = os.path.join(root, name)
            test_suites.update({key: (file_path, file_path.replace(TEST_SUITE_FOLDER, ""))})
            key += 1
    return test_suites


def set_test_device(device_id):
    """
    修改配置文件以确定当前测试设备
    @Author: ShenYiFan
    @Create: 2022/5/9 16:59
    :return: None
    """
    # 合并写会导致重复输入（多个 device_id）
    yaml_dict = yaml_util.get_yaml_data()
    yaml_dict["device_id"] = device_id
    yaml_util.dump_yaml_data(yaml_dict)


def main():
    # cmd = ""
    # pytest.main(cmd)
    set_test_device("181827V00500102")


if __name__ == '__main__':
    main()
