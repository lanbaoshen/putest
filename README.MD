**version: v1.0.0**
# 简介
通过 pytest 和 uiautomator2 搭建的一个 Android UI 自动化测试框架，生成 allure 测试报告  
提供了入口文件，自动获取连接设备和扫描测试套件，以便快速开始测试  
封装后的 uiautomator2 更便携的使用，实现 log 自动保存和失败截图，插入 allure 报告  
提供测试套件 demo，即便未学习过 pytest 也能在该框架内编写用例执行测试
# 依赖
自动获取连接设备需本机安装 adb 环境  
执行测试需安装 common.txt 内依赖  
查看 allure 报告需要安装 jdk 1.8+ 和 [allure2/release](https://github.com/allure-framework/allure2/releases) 
