
from scrab_browser.websites.cangku.cangku_def import CangkuDef
from selenium import webdriver
import logging

class CangkuLogin:
  @staticmethod
  def GuaranteeCangkuLogin(driver: webdriver.Chrome):
    while True:
      driver.get(CangkuDef.cangku_root_url)
      
      logging.info(f"logging cangku, title: {driver.title}")
      logging.info(f"current url: {driver.current_url}")
    
      if not driver.current_url.startswith(f"{CangkuDef.cangku_root_url}/login"):
        break

      logging.info("wait for login, press enter after login")
      input()

    logging.info("login success")