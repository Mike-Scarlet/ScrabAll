
from bs4 import BeautifulSoup
import logging, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from scrab_browser.websites.cangku.cangku_def import CangkuDef
from scrab_browser.websites.cangku.walk_cangku_user_post import WalkCangkuUserPost
from scrab_browser.utils.wait import *

from python_general_lib.database.sqlite3_wrap import *

"""
storage
"""
@PySQLModel(initialize_fields=True)
class PostItem:
  title: str = Field(not_null=True)
  url: str = Field(not_null=True)
  process_stat: int = Field(not_null=True)
  retrive_time: float = Field(not_null=True)
  use_shared_link: str = Field(not_null=True)
  shared_link_collect: str = Field(not_null=True)   # json

"""
logic
"""
class YejiangScrab:
  def __init__(self, driver: webdriver.Chrome):
    self.driver = driver
    self.user_id = "309550"
    self.retrieve_page_max = 2
    self.retrieve_update_time_min = None
    
  def Run(self):
    walk_cangku_user_post = WalkCangkuUserPost(self.driver)
    post_items = walk_cangku_user_post.GetUserPostLinks(self.user_id, self.retrieve_page_max)
    
    for item in post_items:
      