
import logging, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from scrab_browser.utils.wait import *

def IsInRequirePasswordPage(driver: webdriver.Chrome):
  # print(driver.title)
  return "请输入提取码" in driver.title

class BaiduPanSharedLink:
  @staticmethod
  def GetSharedLink(driver: webdriver.Chrome, shared_link_url: str, password: str=None):
    """
    get baidu pan shared link
    
    returns:
      empty string if no error
      otherwise, error message
    """
    driver.get(shared_link_url)

    if IsInRequirePasswordPage(driver):
      if password is None:
        logging.error("need password")
        return "need password"
      if len(password) != 4:
        logging.error("password length must be 4")
        return "password length must be 4"
      access_code_input = driver.find_element(By.ID, "accessCode")
      access_code_input.send_keys(password)

      submit_button = driver.find_element(By.ID, "submitBtn")
      submit_button.click()
      WaitAfterClick()
      
      WaitForPageLoad(driver)

    if IsInRequirePasswordPage(driver):
      logging.error("password error")
      return "password error"

    logging.info("get shared link success")
    return ""