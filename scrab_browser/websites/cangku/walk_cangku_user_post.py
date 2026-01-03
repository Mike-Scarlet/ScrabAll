
from bs4 import BeautifulSoup
import logging, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrab_browser.websites.cangku.cangku_def import CangkuDef
from scrab_browser.utils.wait import *

class WalkCangkuUserPost:
  def __init__(self, driver: webdriver.Chrome):
    self.driver = driver
    
  def GetUserPostLinks(self, user_id: str, till_page: int):
    result = []
    for i in range(till_page + 1):
      self.driver.get(f"{CangkuDef.cangku_root_url}/user/{user_id}/post?page={i}")
      
      user_post_element = self.driver.find_element(By.ID, "user-post")
      
      soup = BeautifulSoup(user_post_element.get_attribute("outerHTML"), "lxml")
      
      soup_all_href = soup.find_all("a", href=True)
      for soup_a in soup_all_href:
        full_url = f"{CangkuDef.cangku_root_url}{soup_a.attrs['href']}"
        title = soup_a.attrs["title"]
        result.append((full_url, title))
    return result