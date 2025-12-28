
from selenium import webdriver
import logging

class BaiduPanLogin:
  @staticmethod
  def GuaranteeBaiduPanLogin(driver: webdriver.Chrome):
    while True:
      driver.get("https://pan.baidu.com/disk/main#/index")
      
      logging.info(f"logging baidu yun, title: {driver.title}")
      logging.info(f"current url: {driver.current_url}")
    
      if not driver.current_url.startswith("https://pan.baidu.com/login"):
        break

      logging.info("wait for login, press enter after login")
      input()

    logging.info("login success")