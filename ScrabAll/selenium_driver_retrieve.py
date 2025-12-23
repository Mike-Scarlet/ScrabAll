
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

_file_dir = os.path.dirname(os.path.dirname(__file__))

def GetDefaultSeleniumDriver():
  session_save_path = os.path.join(_file_dir, 'browser_session')
  
  if not os.path.exists(session_save_path):
    os.makedirs(session_save_path)

  chrome_options = Options()
  chrome_options.add_argument(rf"--user-data-dir={session_save_path}")

  driver = webdriver.Chrome(options=chrome_options)
  return driver