
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

DEFAULT_WAIT_TIME_AFTER_CLICK = 1

def WaitAfterClick(override_time=DEFAULT_WAIT_TIME_AFTER_CLICK):
  time.sleep(override_time)

def WaitForPageLoad(driver, timeout=10):
  wait = WebDriverWait(driver, timeout)
  # 等待 JS 返回 'complete' 状态，表示页面资源已加载完毕
  wait.until(lambda d: d.execute_script("return document.readyState") == "complete")