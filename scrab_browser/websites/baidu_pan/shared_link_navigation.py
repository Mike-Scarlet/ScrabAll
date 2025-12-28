
from bs4 import BeautifulSoup
import logging, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrab_browser.utils.wait import *


SELECT_ALL = "all"
SELECT_PART = "part"
SELECT_NONE = "none"


def IsInSharedLinkPage(driver: webdriver.Chrome):
  return "百度网盘" in driver.title


class BaiduPanEntry:
  def __init__(self):
    self.name = None
    self.is_dir = False
    self.is_selected = False
    
  def __repr__(self):
    return f"BaiduPanEntry(name={self.name}, is_dir={self.is_dir}, is_selected={self.is_selected})"


class BaiduPanSharedLinkNavigation:
  """
  Chrome drivers
  """
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
  def ListCurrentSharedLinkFiles(driver: webdriver.Chrome) -> list[BaiduPanEntry]:
    """
    returns:
      [BaiduPanEntry, ...]
    """
    if not IsInSharedLinkPage(driver):
      raise RuntimeError("not in shared link page")

    WaitForPageLoad(driver)
    
    folder_content_element = driver.find_element(By.CLASS_NAME, "vdAfKMb")
    
    content_html = folder_content_element.get_attribute("outerHTML")
    soup = BeautifulSoup(content_html, "lxml")

    all_dds = soup.find_all("dd")
    result = []
    for dd in all_dds:
      is_dir = False
      is_selected = "JS-item-active" in dd.attrs["class"]
      
      dd.attrs["class"]
      
      content_name = dd.find(class_="filename").attrs["title"]
      file_icon_soup = dd.find(class_="JS-fileicon")
      for attr in file_icon_soup.attrs["class"]:
        if "dir" in attr:
          is_dir = True
          break

      ent = BaiduPanEntry()
      ent.name = content_name
      ent.is_dir = is_dir
      ent.is_selected = is_selected
      result.append(ent)
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
  def MultiSelectTo(driver: webdriver.Chrome, select_status: str):
    """
    select_status: accept [all, none]
    """
    if select_status not in (SELECT_NONE, SELECT_ALL):
      raise RuntimeError("invalid select status")
      
    list_entries = BaiduPanSharedLinkNavigation.ListCurrentSharedLinkFiles(driver)

    current_select_status = BaiduPanSharedLinkNavigation.GetCurrentMultiSelectStatus(list_entries)
    if current_select_status == select_status:
      return
    
    display_select_checked = sum([ent.is_selected for ent in list_entries]) == 1 or current_select_status == SELECT_ALL
    click_count = 0
    if display_select_checked:
      click_count = 1 if select_status == SELECT_NONE else 2
    else:
      click_count = 1 if select_status == SELECT_ALL else 2
    
    head_line_element = driver.find_element(By.CSS_SELECTOR, f"ul[class='QAfdwP tvPMvPb']")
    multi_select_button_element = head_line_element.find_element(By.CSS_SELECTOR, f"span[class='zbyDdwb']")
    
    for _ in range(click_count):
      multi_select_button_element.click()
      WaitAfterClick()
      
  @staticmethod
  def SelectFiles(driver: webdriver.Chrome, file_names: list[str]):
    BaiduPanSharedLinkNavigation.MultiSelectTo(driver, SELECT_NONE)
    for file_name in file_names:
      name_element = driver.find_element(By.CSS_SELECTOR, f"a[class='filename'][title='{file_name}']")
      dd_element = name_element.find_element(By.XPATH, "./ancestor::dd[1]")
      button_element = dd_element.find_element(By.CLASS_NAME, "EOGexf")
      button_element.click()
      WaitAfterClick(0.2)
      
  @staticmethod
  def OpenSaveToDialog(driver: webdriver.Chrome):
    button_element = driver.find_element(By.CSS_SELECTOR, f"div[class='bottom-save-path-icon']")
    button_element.click()
    WaitAfterClick(0.2)
    WaitForPageLoad(driver)
    
  # TODO: navigate dialog
    
  """
  Simple judgement
  """
  @staticmethod
  def GetCurrentMultiSelectStatus(entries: list[BaiduPanEntry]):
    total_count = len(entries)
    selected_count = sum([ent.is_selected for ent in entries])
    if total_count == selected_count:
      return SELECT_ALL
    elif selected_count == 0:
      return SELECT_NONE
    else:
      return SELECT_PART