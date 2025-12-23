

import time
from python_general_lib.environment_setup.logging_setup import *

from ScrabAll.selenium_driver_retrieve import GetDefaultSeleniumDriver
from ScrabAll.websites.baidu.baidu_pan_login import GuaranteeBaiduPanLogin

driver = GetDefaultSeleniumDriver()

GuaranteeBaiduPanLogin(driver)

# 打开网页
driver.get("https://pan.baidu.com/disk/main#/index")

# 打印页面标题
print("页面标题:", driver.title)
print("当前URL:", driver.current_url)

input()

# 等待3秒
time.sleep(3)

# 关闭浏览器
driver.quit()