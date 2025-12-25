

import time, sys, os

from python_general_lib.environment_setup.logging_setup import *
logging.basicConfig(
    level=logging.NOTSET,
    format="[%(asctime)s] %(message)s",
    # datefmt="[%X]",
)

from scrab_browser.selenium_driver_retrieve import GetDefaultSeleniumDriver
from scrab_browser.websites.baidu_pan.login import GuaranteeBaiduPanLogin
from scrab_browser.websites.baidu_pan.get_shared_link import GetSharedLink

driver = GetDefaultSeleniumDriver()

baidu_share_url = "https://pan.baidu.com/s/1flqi_JjQRHhCvtN-JJHUJA"
GetSharedLink(driver, baidu_share_url, "yezi")



# # 打开网页
# driver.get("https://pan.baidu.com/disk/main#/index")

# # 打印页面标题
# print("页面标题:", driver.title)
# print("当前URL:", driver.current_url)

input()

# 等待3秒
time.sleep(3)

# 关闭浏览器
driver.quit()