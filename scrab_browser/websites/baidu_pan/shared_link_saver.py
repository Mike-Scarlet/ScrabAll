
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from scrab_browser.utils.wait import WaitForPageLoad, WaitAfterClick
import logging

class SharedLinkSaver:
  def __init__(self, driver: webdriver.Chrome):
    self.driver = driver
    
  def has_save_dialog(self):
    try:
      self.driver.find_element(By.ID, "fileTreeDialog")
      return True
    except NoSuchElementException:
      return False

  def open_save_dialog(self):
    if self.has_save_dialog():
      return
    self.driver.find_element(By.CSS_SELECTOR, "div[class='bottom-save-path-icon']").click()
    WaitAfterClick()
    WaitForPageLoad(self.driver)
    
  def confirm_selection(self):
    dialog = self._get_dialog()
    try:
      confirm_btn = dialog.find_element(
        By.CSS_SELECTOR, 
        "a[node-type='confirm']"
      )
      confirm_btn.click()
      WaitAfterClick()
      WaitForPageLoad(self.driver)
      
      time.sleep(5.0)
      
      try:
        WebDriverWait(self.driver, 5).until(
          EC.presence_of_element_located((By.XPATH, "//div[@class='info-section-title' and text()='保存成功']"))
        )
      except TimeoutException:
        logging.error("cannot find save success")
        return False
      
      return True
    except Exception as e:
      print(f"click confirm button failed: {e}")
      return False

  def cancel_selection(self):
    dialog = self._get_dialog()
    try:
      cancel_btn = dialog.find_element(
        By.CSS_SELECTOR, 
        "a[node-type='cancel']"
      )
      cancel_btn.click()
      WaitAfterClick()
      WaitForPageLoad(self.driver)
      return True
    except Exception as e:
      print(f"click cancel button failed: {e}")
      return False
    
  def navigate_to_path(self, target_path, create_if_missing=True):      
    parts = [""] + [p for p in target_path.strip("/").split("/")]
    parent_node_path = None
    
    try:
      # fast skip
      last_visible_index = -1
      for i, part in enumerate(parts):
        if i == 0:
          target_node_path = "/"
        else:        
          target_node_path = "/".join(parts[:i+1])
        
        if self._has_element_node(target_node_path):
          last_visible_index = i
          parent_node_path = target_node_path
      
      for i, part in enumerate(parts):
        if i <= last_visible_index:
          continue
        
        if i == 0:
          target_node_path = "/"
        else:        
          target_node_path = "/".join(parts[:i+1])
        
        print(f"parent -> target: {parent_node_path} -> {target_node_path}")
        
        if parent_node_path and self._has_element_node(parent_node_path):
          self._ensure_node_select_and_expanded(parent_node_path)
        
        if self._has_element_node(target_node_path):
          # print("child path exists")
          parent_node_path = target_node_path
        elif create_if_missing:
          child_node = self._create_folder(part, parent_node_path)
          if child_node:
            parent_node_path = target_node_path
          else:
            return False, f"创建文件夹失败: {part}"
        else:
          return False, f"路径不存在: {target_node_path}"
      self._ensure_node_select_and_expanded(target_path)
      
      return True, f"成功导航到: {target_path}"
      
    except Exception as e:
      return False, f"导航失败: {str(e)}"
    
  def _get_dialog(self):
    try:
      return WebDriverWait(self.driver, 5).until(
        EC.presence_of_element_located((By.ID, "fileTreeDialog"))
      )
    except TimeoutException:
      logging.error("cannot find file tree dialog")
    
  def _has_element_node(self, full_path):
    return self._find_element_node_by_full_path(full_path) is not None
    
  def _find_element_node_by_full_path(self, full_path):
    """
    the element node holds necessary info for full path
    """
    try:
      node_path_span_element = self.driver.find_element(By.XPATH, f"//span[@class='treeview-txt' and @node-path='{full_path}']")
      node_div_element = node_path_span_element.find_element(By.XPATH, "./ancestor::div[1]")
      return node_div_element
    except NoSuchElementException:
      return None
    
  def _ensure_node_select_and_expanded(self, path: str):
    print(f"do select and expand path: {path}")
    while True:
      parent_div_element = self._find_element_node_by_full_path(path)
      try:
        expand_btn = parent_div_element.find_element(
          By.CSS_SELECTOR, 
          "em.plus.icon-operate"
        )
        
        need_click = False
        expandible = "treenode-empty" not in parent_div_element.get_attribute("class")
        if expandible and "minus" not in expand_btn.get_attribute("class"):
          need_click = True
          
        if "treeview-node-on" not in parent_div_element.get_attribute("class"):
          need_click = True
          
        if need_click:
          # print("do expand node")
          expand_btn.click()
          WaitAfterClick()
          WaitForPageLoad(self.driver)
        else:
          break
          
      except NoSuchElementException:
        print("no expand found")
        break
      except Exception as e:
        print(f"expand error: {e}")
        break
    # print(f"end of do select and expand path: {path}")
      
  def _create_folder(self, new_folder_name, parent_node_path):
    print(f"create folder: {new_folder_name} (path: {parent_node_path})")
    
    try:
      self._ensure_node_select_and_expanded(parent_node_path)
      
      new_folder_btn = WebDriverWait(self.driver, 5).until(
        EC.element_to_be_clickable((
          By.CSS_SELECTOR, 
          "a[title='新建文件夹']"
        ))
      )
      new_folder_btn.click()
      WaitAfterClick()
      WaitForPageLoad(self.driver)
      
      edit_input = self._find_edit_input()
      
      if edit_input:
        edit_input.clear()
        edit_input.send_keys(new_folder_name)
        
        edit_input.send_keys("\n")
        WaitAfterClick()
        WaitForPageLoad(self.driver)
        
        error_msg = self._check_for_error()
        if error_msg:
          print(f"创建文件夹失败: {error_msg}")
          
      return None
      
    except Exception as e:
      print(f"创建文件夹过程中出错: {e}")
      return None
    
  def _find_edit_input(self):
    try:
      return WebDriverWait(self.driver, 3).until(
        EC.presence_of_element_located((
          By.CSS_SELECTOR, 
          ".treeview-edit, input[type='text']"
        ))
      )
    except TimeoutException:
      return None
    
  def _check_for_error(self):
    try:
      error_elem = self.driver.find_element(
        By.CSS_SELECTOR, 
        ".dialog-error, .error-msg, .tips-error"
      )
      return error_elem.text
    except:
      return None