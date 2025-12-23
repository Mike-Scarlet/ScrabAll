
from selenium import webdriver
import logging

def GuaranteeBaiduPanLogin(driver: webdriver.Chrome):
  driver.get("https://pan.baidu.com/disk/main#/index")
  
  
  print("页面标题:", driver.title)
  print("当前URL:", driver.current_url)
  
  