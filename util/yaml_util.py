# @Time     : 2022/5/9 17:22
# @Author   : ShenYiFan
# -*- coding: utf-8 -*-
import os
import yaml


# 配置文件路径
YAML_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../conf/config.yaml")


def get_yaml_data(yaml_path=YAML_CONFIG_PATH):
    """
    获取 yaml 数据
    @Author: ShenYiFan
    @Create: 2022/5/9 17:23
    :param yaml_path: yaml 文件路径
    :return: dict
    """
    with open(yaml_path, "r") as f:
        yaml_dict = yaml.safe_load(f)
    return yaml_dict


def dump_yaml_data(data, yaml_path=YAML_CONFIG_PATH):
    """
    转储 yaml 数据
    @Author: ShenYiFan
    @Create: 2022/5/9 17:24
    :param data: yaml 文件数据（python 对象）
    :param yaml_path: yaml 文件路径
    :return: None
    """
    with open(yaml_path, "w") as f:
        yaml.dump(data, f)
