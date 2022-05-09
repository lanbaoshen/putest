# @Time     : 2022/5/6 15:42
# @Author   : CN-LanBao
# -*- coding: utf-8 -*-
import os
import time
import traceback
import subprocess
import uiautomator2 as u2
from util.log_util import LogUtil


# 自备 python 环境
PYTHON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../venv/Scripts/python.exe")


class UiautomatorException(Exception):
    """
    uiautomator2 api 异常，中止测试
    @Author: CN-LanBao
    @Create: 2022/5/6 15:45
    """
    def __init__(self, msg):
        self.msg = msg


class Uiautomator(object):

    def __init__(self, device_id):
        self.device_id = device_id
        # 为设备创建 logger 对象
        self.log_util = LogUtil(self.device_id, logger_name=self.device_id)
        # uiautomator2 初始化
        try:
            init_cmd = "python -m uiautomator2 init {}".format(self.device_id)
            self.log_util.info(init_cmd)
            init_process = subprocess.Popen(init_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while init_process.poll() is None:
                line = init_process.stdout.readline()
                if line:
                    self.log_util.debug(line)
            # 被测设备
            self.dut = u2.connect(self.device_id)
        except Exception:
            msg = "Fail to connect uiautomator2: \n{}".format(traceback.format_exc())
            self.log_util.error(msg)
            raise UiautomatorException(msg)

    def _fail_screenshot(self, func_name):
        """
        uiautomator2 api 失败时保存设备截图至本地
        @Author: CN-LanBao
        @Create: 2022/5/7 16:21
        :param func_name: 异常的方法名
        :return: str 截图路径
        """
        screenshot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../screenshot")
        # 创建保存目录
        if not os.path.exists(screenshot_dir):
            os.mkdir(screenshot_dir)
        elif not os.path.isdir(screenshot_dir):
            screenshot_dir = os.path.dirname(os.path.abspath(__file__))
        # 保存截图
        filepath = os.path.join(
            screenshot_dir,
            time.strftime("{}_{}_%Y_%m_%d_%H_%M_%S.png".format(self.device_id, func_name), time.localtime()))
        return self.screenshot(filepath)

    def u2_log(func):
        """
        装饰器，用来打印并保存执行 uiautomator2 api 的 log
        @Author: CN-LanBao
        @Create: 2022/5/6 16:05
        :return: func
        """
        def wrapper(self, *args, **kwargs):
            """
            写入 log (设备 ID, 方法名和入参, 方法 return)
            @Author: CN-LanBao
            @Create: 2022/5/6 16:06
            :return: func()
            """
            # 获取方法信息，去除 self 参数
            func_name, var_names = func.__name__, func.__code__.co_varnames[1:]
            # 入参信息格式化
            params = ", ".join(["{}={}".format(k, v) for k, v in zip(var_names, args)]
                               + ["{}={}".format(k, v) for k, v in kwargs.items()])
            try:
                func_return = func(self, *args, **kwargs)
            except Exception:
                msg = "Fail to execute {}, {}({}): \n{}".format(self.device_id, func_name, params,
                                                                traceback.format_exc())
                self.log_util.error(msg)
                # 保存截图
                self.log_util.error("The path of fail time screenshot is {}".format(self._fail_screenshot(func_name)))
                raise UiautomatorException(msg)
            else:
                msg = "{}, {}({}), {}".format(self.device_id, func_name, params, func_return)
                self.log_util.info(msg)
                return func_return
        return wrapper

    @u2_log
    def shell(self, cmdargs, stream=False, timeout=60):
        """
        带参数运行 adb shell 命令并返回其输出，需要 atx-agent > = 0.3.3，当 command 出错时，exit_code 总是1，否则 exit_code 总是0
        @Author: CN-LanBao
        @Create: 2022/5/7 13:16
        :param cmdargs: str 或 list，eg "ls -l" 或 ["ls", "-l"]
        :param stream: bool used for long running process.
        :param timeout: 命令运行的秒数，在 stream 为 False 时有效
        :return: 当 stream 为 False (output, exit_code)
            当 stream 为 True，requests.Response，需要在使用后关闭
        :raise: RuntimeError
        """
        return self.dut.shell(cmdargs, stream=stream, timeout=timeout)

    @u2_log
    def device_info(self):
        """
        获取设备信息
        @Author: CN-LanBao
        @Create: 2022/5/6 17:58
        :return: dict
        """
        return self.dut.device_info

    @u2_log
    def window_size(self):
        """
        获取屏幕尺寸
        @Author: CN-LanBao
        @Create: 2022/5/7 10:52
        :return: (int, int)
        """
        return self.dut.window_size()

    @u2_log
    def screenshot(self, filename=None, format="pillow"):
        """
        截图
        Examples:
            screenshot("saved.jpg")
            screenshot().save("saved.png")
            cv2.imwrite('saved.jpg', screenshot(format='opencv'))
        @Author: CN-LanBao
        @Create: 2022/5/7 11:00
        :param filename: 截图名，如果设置了则返回 None
        :param format: 当 filename 为空时使用，["pillow"， "opencv"， "raw"] 中的一个
        :return: PIL.Image.Image, np.ndarray (OpenCV format) or None
        :raise: IOError, SyntaxError, ValueError
        """
        return self.dut.screenshot(filename=filename, format=format)

    @u2_log
    def click(self, x, y):
        """
        坐标点击
        @Author: CN-LanBao
        @Create: 2022/5/6 17:06
        :param x: x 坐标
        :param y: y 坐标
        :return: None
        """
        return self.dut.click(x, y)

    @u2_log
    def click_resource_id(self, resource_id):
        """
        点击指定 resource id 控件
        @Author: CN-LanBao
        @Create: 2022/5/7 14:13
        :param resource_id: 控件 resourceId 属性值
        :return: None
        """
        return self.dut(resourceId=resource_id).click()

    @u2_log
    def click_resource_id_exists(self, resource_id, timeout=0):
        """
        指定 resource id 控件存在则点击
        @Author: CN-LanBao
        @Create: 2022/5/7 14:17
        :param resource_id: 控件 resourceId 属性值
        :param timeout: 最长等待时间
        :return: bool
        """
        return self.dut(resourceId=resource_id).click_exists(timeout=timeout)

    @u2_log
    def click_text(self, text):
        """
        点击指定 text 控件
        @Author: CN-LanBao
        @Create: 2022/5/7 14:15
        :param text: 控件 text 属性值
        :return: None
        """
        return self.dut(text=text).click()

    @u2_log
    def click_text_exists(self, text, timeout=0):
        """
        指定 text 控件存在则点击
        @Author: CN-LanBao
        @Create: 2022/5/7 14:20
        :param text: 控件 text 属性值
        :param timeout: 最长等待时间
        :return: bool
        """
        return self.dut(text=text).click_exists(timeout=timeout)

    @u2_log
    def click_xpath(self, xpath):
        """
        点击指定 xpath 控件
        @Author: CN-LanBao
        @Create: 2022/5/7 14:16
        :param xpath: 控件 xpath 属性值
        :return: None
        """
        return self.dut.xpath(xpath).click()

    @u2_log
    def click_xpath_exists(self, xpath, timeout=0):
        """
        指定 xpath 控件存在则点击
        @Author: CN-LanBao
        @Create: 2022/5/7 14:22
        :param xpath: 控件 xpath 属性值
        :param timeout: 最长等待时间
        :return: None
        """
        return self.dut.xpath(xpath).click_exists(timeout=timeout)

    @u2_log
    def double_click(self, x, y, duration=0.1):
        """
        双击
        @Author: CN-LanBao
        @Create: 2022/5/6 18:05
        :param x: x 坐标
        :param y: y 坐标
        :param duration: 持续时间
        :return: None
        """
        return self.dut.double_click(x, y, duration=duration)

    @u2_log
    def double_click_resource_id(self, resource_id, duration=0.1):
        """
        双击指定 resource_id 控件
        @Author: CN-LanBao
        @Create: 2022/5/7 15:13
        :param resource_id: 指定 resource_id 属性值
        :param duration: 持续时间
        :return: None
        """
        return self.dut(resourceId=resource_id).double_click(duration=duration)

    @u2_log
    def double_click_text(self, text, duration=0.1):
        """
        双击指定 text 控件
        @Author: CN-LanBao
        @Create: 2022/5/7 15:15
        :param text: 指定 text 属性值
        :param duration: 持续时间
        :return: None
        """
        return self.dut(text=text).double_click(duration=duration)

    @u2_log
    def double_click_xpath(self, xpath, duration=0.1):
        """
        双击指定 xpath 控件
        @Author: CN-LanBao
        @Create: 2022/5/7 15:15
        :param xpath: 指定 xpath 属性值
        :param duration: 持续时间
        :return: None
        """
        return self.dut.xpath(xpath).double_click(duration=duration)

    @u2_log
    def long_click(self, x, y, duration=0.5):
        """
        长按
        @Author: CN-LanBao
        @Create: 2022/5/6 18:08
        :param x: x 坐标
        :param y: y 坐标
        :param duration: 持续时间
        :return: touch
        """
        return self.dut.long_click(x, y, duration=duration)

    @u2_log
    def long_click_resource_id(self, resource_id, duration=0.5):
        """
        长按 resource_id 控件
        @Author: CN-LanBao
        @Create: 2022/5/7 15:16
        :param resource_id: 指定 resource_id 属性值
        :param duration: 持续时间
        :return: None
        """
        return self.dut(resourceId=resource_id).long_click(duration=duration)

    @u2_log
    def long_click_text(self, text, duration=0.5):
        """
        长按 text 控件
        @Author: CN-LanBao
        @Create: 2022/5/7 15:18
        :param text: 指定 text 属性值
        :param duration: 持续时间
        :return: None
        """
        return self.dut(text=text).long_click(duration=duration)

    @u2_log
    def long_click_xpath(self, xpath, duration=0.5):
        """
        长按 xpath 控件
        @Author: CN-LanBao
        @Create: 2022/5/7 15:18
        :param xpath: 指定 xpath 属性值
        :param duration: 持续时间
        :return: None
        """
        return self.dut.xpath(xpath).long_click(duration=duration)

    @u2_log
    def swipe(self, fx, fy, tx, ty, duration=None, steps=None):
        """
        滑动
        @Author: CN-LanBao
        @Create: 2022/5/6 18:12
        :param fx: 起始 x 坐标
        :param fy: 起始 y 坐标
        :param tx: 终点 x 坐标
        :param ty: 终点 y 坐标
        :param duration: 持续时间
        :param steps: 1 个 step 约为 5ms，如果设置，持续时间将被忽略
        :return: bool
        """
        return self.dut.swipe(fx, fy, tx, ty, duration=duration, steps=steps)

    @u2_log
    def swipe_points(self, points, duration=0.5):
        """
        滑动多个点，可用于九宫格解锁
        @Author: CN-LanBao
        @Create: 2022/5/7 10:40
        :param points: 点数组，至少包含一个点对象  eg [[200, 300], [200, 500]]
        :param duration: 间隔时间
        :return: bool
        """
        return self.dut.swipe_points(points, duration=duration)

    @u2_log
    def drag(self, sx, sy, ex, ey, duration=0.5):
        """
        从起点拖拽至终点
        @Author: CN-LanBao
        @Create: 2022/5/7 14:56
        :param sx: 起始 x 坐标
        :param sy: 起始 y 坐标
        :param ex: 终点 x 坐标
        :param ey: 终点 y 坐标
        :param duration: 持续时间
        :return: bool
        """
        return self.dut.drag(sx, sy, ex, ey, duration=duration)

    @u2_log
    def drag_resource_id_to(self, resource_id, ex, ey, duration=0.5, timeout=None):
        """
        拖拽指定 resource_id 控件
        @Author: CN-LanBao
        @Create: 2022/5/7 15:02
        :param resource_id: 指定 resource_id 属性值
        :param ex: 终点 x 坐标
        :param ey: 终点 y 坐标
        :param duration: 持续时长
        :param timeout: 最长等待时间
        :return: bool
        """
        return self.dut(resourceId=resource_id).drag_to(ex, ey, duration=duration, timeout=timeout)

    @u2_log
    def drag_text_to(self, text, ex, ey, duration=0.5, timeout=None):
        """
        拖拽指定 text 控件
        @Author: CN-LanBao
        @Create: 2022/5/7 15:05
        :param text: 指定 text 属性值
        :param ex: 终点 x 坐标
        :param ey: 终点 y 坐标
        :param duration: 持续时长
        :param timeout: 最长等待时间
        :return: bool
        """
        return self.dut(text=text).drag_to(ex, ey, duration=duration, timeout=timeout)

    @u2_log
    def drag_xpath_to(self, xpath, ex, ey, duration=0.5, timeout=None):
        """
        拖拽指定 xpath 控件
        @Author: CN-LanBao
        @Create: 2022/5/7 15:05
        :param xpath: 指定 xpath 属性值
        :param ex: 终点 x 坐标
        :param ey: 终点 y 坐标
        :param duration: 持续时长
        :param timeout: 最长等待时间
        :return: bool
        """
        return self.dut.xpath(xpath).drag_to(ex, ey, duration=duration, timeout=timeout)

    @u2_log
    def wait_resource_id(self, resource_id, timeout=None):
        """
        等待指定 resource_id 控件出现
        @Author: CN-LanBao
        @Create: 2022/5/7 15:35
        :param resource_id: 指定 resource_id 属性值
        :param timeout: 最长等待时间
        :return: bool
        """
        return self.dut(resourceId=resource_id).wait(timeout=timeout)

    @u2_log
    def wait_resource_id_gone(self, resource_id, timeout=None):
        """
        等待指定 resource_id 控件消失
        @Author: CN-LanBao
        @Create: 2022/5/7 15:36
        :param resource_id: 指定 resource_id 属性值
        :param timeout: 最长等待时间
        :return: bool
        """
        return self.dut(resourceId=resource_id).wait_gone(timeout=timeout)

    @u2_log
    def wait_text(self, text, timeout=None):
        """
        等待指定 text 控件出现
        @Author: CN-LanBao
        @Create: 2022/5/7 15:36
        :param text: 指定 text 属性值
        :param timeout: 最长等待时间
        :return: bool
        """
        return self.dut(text=text).wait(timeout=timeout)

    @u2_log
    def wait_text_gone(self, text, timeout=None):
        """
        等待指定 text 控件消失
        @Author: CN-LanBao
        @Create: 2022/5/7 15:37
        :param text: 指定 text 属性值
        :param timeout: 最长等待时间
        :return: bool
        """
        return self.dut(text=text).wait_gone(timeout=timeout)

    @u2_log
    def wait_xpath(self, xpath, timeout=None):
        """
        等待指定 xpath 控件出现
        @Author: CN-LanBao
        @Create: 2022/5/7 15:37
        :param xpath: 指定 xpath 属性值
        :param timeout: 最长等待时间
        :return: bool
        """
        return self.dut.xpath(xpath).wait(timeout=timeout)

    @u2_log
    def wait_xpath_gone(self, xpath, timeout=None):
        """
        等待指定 xpath 控件消失
        @Author: CN-LanBao
        @Create: 2022/5/7 15:38
        :param xpath: 指定 xpath 属性值
        :param timeout: 最长等待时间
        :return: bool
        """
        return self.dut.xpath(xpath).wait_gone(timeout=timeout)

    @u2_log
    def press(self, key, meta=None):
        """
        模拟按键
        @Author: CN-LanBao
        @Create: 2022/5/7 10:43
        :param key: 通过名称或 keycode 模拟按键，支持以下名称：
            home, back, left, right, up, down, center, menu, search, enter,
            delete(or del), recent(recent apps), volume_up, volume_down,
            volume_mute, camera, power
        :param meta: 缺少注释，不知道具体含义
        :return: bool
        """
        return self.dut.press(key, meta=meta)

    @u2_log
    def screen_on(self):
        """
        打开屏幕
        @Author: CN-LanBao
        @Create: 2022/5/7 10:49
        :return: None
        """
        return self.dut.screen_on()

    @u2_log
    def screen_off(self):
        """
        关闭屏幕
        @Author: CN-LanBao
        @Create: 2022/5/7 10:50
        :return: None
        """
        return self.dut.screen_off()

    @u2_log
    def open_notification(self):
        """
        打开通知栏
        @Author: CN-LanBao
        @Create: 2022/5/7 11:19
        :return: bool
        """
        return self.dut.open_notification()

    @u2_log
    def open_quick_settings(self):
        """
        打开快速设置
        @Author: CN-LanBao
        @Create: 2022/5/7 11:21
        :return: bool
        """
        return self.dut.open_quick_settings()

    @u2_log
    def check_resource_id_exists(self, resource_id):
        """
        指定 resourceId 控件是否存在
        @Author: CN-LanBao
        @Create: 2022/5/7 11:25
        :param resource_id: 控件 resourceId 属性值
        :return: bool
        """
        return self.dut(resourceId=resource_id).exists

    @u2_log
    def check_text_exists(self, text):
        """
        指定 text 控件是否存在
        @Author: CN-LanBao
        @Create: 2022/5/7 13:04
        :param text: 控件 text 属性值
        :return: bool
        """
        return self.dut(text=text).exists

    @u2_log
    def check_xpath_exists(self, xpath):
        """
        指定 xpath 控件是否存在
        @Author: CN-LanBao
        @Create: 2022/5/7 13:06
        :param xpath: 控件 xpath 属性值
        :return: bool
        """
        return self.dut.xpath(xpath).exists

    @u2_log
    def keyevent(self, v):
        """
        执行 adb shell keyevent 命令
        @Author: CN-LanBao
        @Create: 2022/5/7 13:26
        :param v: keyevent eg home wakeup back "3"
        :return: None
        """
        return self.dut.keyevent(v)

    @u2_log
    def app_current(self):
        """
        当前应用信息
        @Author: CN-LanBao
        @Create: 2022/5/7 13:30
        :return: dict(package, activity, pid?)
        :raise: OSError
        """
        return self.dut.app_current()

    @u2_log
    def app_install(self, data):
        """
        安装 app
        @Author: CN-LanBao
        @Create: 2022/5/7 13:33
        :param data: 文件路径或 url 或文件对象
        :return: None
        """
        return self.dut.app_install(data)

    @u2_log
    def wait_activity(self, activity, timeout=10):
        """
        等待 activity
        @Author: CN-LanBao
        @Create: 2022/5/7 13:38
        :param activity: activity 名
        :param timeout: 最大等待时间
        :return: bool
        """
        return self.dut.wait_activity(activity, timeout=timeout)

    @u2_log
    def app_start(self, package_name, activity=None, wait=False, stop=False, use_monkey=False):
        """
        启动 app
        @Author: CN-LanBao
        @Create: 2022/5/7 13:42
        :param package_name: 包名
        :param activity: app activity
        :param wait: 等待 app 启动
        :param stop: 冷启动（启动前先停止 app），需要设置 activity
        :param use_monkey: 当没有设置 activity 时，用 monkey 命令启动 app
        :return: None
        """
        return self.dut.app_start(package_name, activity=activity, wait=wait, stop=stop, use_monkey=use_monkey)

    @u2_log
    def app_wait(self, package_name, timeout=20, front=False):
        """
        等待 app 启动
        @Author: CN-LanBao
        @Create: 2022/5/7 13:47
        :param package_name: 包名
        :param timeout: 最长等待时间
        :param front: 等待 app 成为当前应用
        :return: pid (int)，若启动失败 返回 0
        """
        return self.dut.app_wait(package_name, timeout=timeout, front=front)

    @u2_log
    def app_list(self, filter=None):
        """
        获取 app 列表
        @Author: CN-LanBao
        @Create: 2022/5/7 13:51
        :param filter: 过滤器，[-f] [-d] [-e] [-s] [-3] [-i] [-u] [--user USER_ID] [FILTER]
        :return: list
        """
        return self.dut.app_list(filter=filter)

    @u2_log
    def app_list_running(self):
        """
        获取正在运行的 app 列表
        @Author: CN-LanBao
        @Create: 2022/5/7 13:54
        :return: list
        """
        return self.dut.app_list_running()

    @u2_log
    def app_stop(self, package_name):
        """
        停止 app (am force-stop)
        @Author: CN-LanBao
        @Create: 2022/5/7 13:56
        :param package_name: 包名
        :return: None
        """
        return self.dut.app_stop(package_name)

    @u2_log
    def app_stop_all(self, excludes=[]):
        """
        停止所有的三方 app
        @Author: CN-LanBao
        @Create: 2022/5/7 14:00
        :param excludes: 指定不停止的 app
        :return: 停止的 app list
        """
        return self.dut.app_stop_all(excludes=excludes)

    @u2_log
    def app_clear(self, package_name):
        """
        停止并清空 app 的所有数据 (pm clear)
        @Author: CN-LanBao
        @Create: 2022/5/7 14:02
        :param package_name: 包名
        :return: None
        """
        return self.dut.app_clear(package_name)

    @u2_log
    def app_uninstall(self, package_name):
        """
        卸载 app
        @Author: CN-LanBao
        @Create: 2022/5/7 14:03
        :param package_name: 包名
        :return: bool
        """
        return self.dut.app_uninstall(package_name)

    @u2_log
    def app_uninstall_all(self, excludes=[], verbose=False):
        """
        卸载所有 app
        @Author: CN-LanBao
        @Create: 2022/5/7 14:04
        :param excludes: 不卸载的 app
        :param verbose: 是否打印信息（仅 print）
        :return: 卸载的 app list
        """
        return self.dut.app_uninstall_all(excludes=excludes, verbose=verbose)

    @u2_log
    def app_info(self, package_name):
        """
        获取 app 信息
        @Author: CN-LanBao
        @Create: 2022/5/7 14:09
        :param package_name: 包名
        :return: dict
        """
        return self.dut.app_info(package_name)

    @u2_log
    def push(self, src, dst, mode=0o644, show_progress=False):
        """
        push 文件至设备
        @Author: CN-LanBao
        @Create: 2022/5/7 14:34
        :param src: (path or fileobj) 源文件
        :param dst: 文件或目录路径
        :param mode: 没有注释
        :param show_progress: 没有注释且代码中没用到
        :return: None
        :raise: IOError (如果 push 出现错误)
        """
        return self.dut.push(src, dst, mode=mode, show_progress=show_progress)

    @u2_log
    def pull(self, src, dst):
        """
        从设备中导出文件至本地，需要 atx-agent >= 0.0.9
        @Author: CN-LanBao
        @Create: 2022/5/7 14:45
        :param src: 设备内源文件
        :param dst: 本地路径
        :return: None
        :raise: FileNotFoundError
        """
        return self.dut.pull(src, dst)

    @u2_log
    def click_watcher(self, text):
        """
        监控，出现则点击（在守护线程中监控）
        可以重复调用，来监控多个 text，先设置的优先级高
        创建后调用 start_watcher 才会生效！
        @Author: CN-LanBao
        @Create: 2022/5/7 15:52
        :param text: 内部代码命名为 xpath 但是 github 示例用的 text
        :return: None
        """
        return self.dut.watcher.when(text).click()

    @u2_log
    def start_watcher(self, interval=2):
        """
        启动监控，重复启动无效
        @Author: CN-LanBao
        @Create: 2022/5/7 16:00
        :param interval: 监控间隔
        :return: None
        """
        return self.dut.watcher.start(interval=interval)

    @u2_log
    def remove_watcher(self, name=None):
        """
        移除监控
        @Author: CN-LanBao
        @Create: 2022/5/7 16:01
        :param name: 指定移除监控名，不设置则移除全部
        :return: None
        """
        return self.dut.watcher.remove(name=name)
