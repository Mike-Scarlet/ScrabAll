
from bs4 import BeautifulSoup
import logging, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrab_browser.utils.wait import *


def IsInSharedLinkPage(driver: webdriver.Chrome):
  return "百度网盘" in driver.title

class BaiduPanSharedLinkNavigation:
  @staticmethod
  def GetCurrentSharedLinkPath(driver: webdriver.Chrome):
    if not IsInSharedLinkPage(driver):
      raise RuntimeError("not in shared link page")

    path_holder_element = driver.find_element(By.CLASS_NAME, "FuIxtL")
    style_value = path_holder_element.get_attribute("style")
    if "none" in style_value:
      return "/"   # root path
    
    full_path_element = driver.find_element(By.CSS_SELECTOR, "li[node-type='tbAudfb']")
    
    path_text = full_path_element.text.replace(">", "/")
    return path_text.removeprefix("全部文件")

  @staticmethod
  def ListCurrentSharedLinkFiles(driver: webdriver.Chrome):
    """
    returns:
      [(file_name, is_dir), ...]
    """
    if not IsInSharedLinkPage(driver):
      raise RuntimeError("not in shared link page")
    
    # wait = WebDriverWait(driver, 10)
    # try:
    #   element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='QxJxtg cazEfA']")))
    # except:
    #   raise RuntimeError("no file listed in current folder")
    WaitForPageLoad(driver)
    
    folder_content_element = driver.find_element(By.CLASS_NAME, "vdAfKMb")
    
    content_html = folder_content_element.get_attribute("outerHTML")
    soup = BeautifulSoup(content_html, "lxml")

    all_dds = soup.find_all("dd")
    result = []
    for dd in all_dds:
      content_name = dd.find(class_="filename").attrs["title"]
      file_icon_soup = dd.find(class_="JS-fileicon")
      is_dir = False
      for attr in file_icon_soup.attrs["class"]:
        if "dir" in attr:
          is_dir = True
          break

      result.append((content_name, is_dir))
    return result

  @staticmethod
  def AccessFolder(driver: webdriver.Chrome, folder_name: str):
    element = driver.find_element(By.CSS_SELECTOR, f"a[class='filename'][title='{folder_name}']")
    element.click()
    WaitAfterClick()
    
    WaitForPageLoad(driver)

  @staticmethod
  def ReturnToPrevFolder(driver: webdriver.Chrome):
    try:
      element = driver.find_element(By.LINK_TEXT, "返回上一级")
      element.click()
    
      WaitAfterClick()
    
      WaitForPageLoad(driver)
      return True
    except:
      logging.error("return to prev folder failed")
      return False

  @staticmethod
  def MultiSelectAll(driver: webdriver.Chrome):
    head_line_element = driver.find_element(By.CSS_SELECTOR, f"ul[class='QAfdwP tvPMvPb']")
    multi_select_button_element = head_line_element.find_element(By.CSS_SELECTOR, f"span[class='zbyDdwb']")
    # TODO: instant