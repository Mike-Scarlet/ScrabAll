import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

class FileTreeNavigator:
    def __init__(self, driver, dialog=None):
        """
        初始化文件树导航器
        
        Args:
            driver: Selenium WebDriver
            dialog: 文件树对话框元素，如果为None则自动查找
        """
        self.driver = driver
        self.dialog = dialog or self._find_dialog()
        
    def _find_dialog(self):
        """查找文件树对话框"""
        try:
            return WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "fileTreeDialog"))
            )
        except TimeoutException:
            # 如果ID找不到，尝试通过class查找
            dialogs = self.driver.find_elements(By.CSS_SELECTOR, ".dialog-fileTreeDialog")
            if dialogs:
                return dialogs[0]
            raise Exception("文件树对话框未找到")
    
    def navigate_to_path(self, target_path, create_if_missing=True, timeout=10):
        """
        导航到指定路径，如果路径不存在则创建
        
        Args:
            target_path: 目标路径，如 "/我的资源/子文件夹"
            create_if_missing: 如果路径不存在是否创建
            timeout: 超时时间（秒）
            
        Returns:
            tuple: (是否成功, 最后处理的节点元素, 错误信息)
        """
        if not target_path or target_path == "/":
            return True, None, "根路径"
            
        # 确保对话框可见
        self._ensure_dialog_visible()
        
        # 解析路径
        parts = [p for p in target_path.strip("/").split("/") if p]
        if not parts:
            return True, None, "根路径"
        
        current_path = "/"
        current_node = None
        
        try:
            for i, part in enumerate(parts):
                target_node_path = "/" + "/".join(parts[:i+1])
                
                # 如果当前节点不为空，先展开当前节点
                if current_node:
                    self._expand_node(current_node)
                
                # 尝试查找目标节点
                child_node = self._find_child_node_by_name(part, current_path)
                
                if child_node:
                    # 节点存在，继续处理下一级
                    current_node = child_node
                    current_path = target_node_path
                elif create_if_missing:
                    # 节点不存在，创建文件夹
                    print(f"创建文件夹: {part} (路径: {target_node_path})")
                    child_node = self._create_folder(part, current_path, current_node)
                    if child_node:
                        current_node = child_node
                        current_path = target_node_path
                    else:
                        return False, current_node, f"创建文件夹失败: {part}"
                else:
                    return False, current_node, f"路径不存在: {target_node_path}"
            
            # 导航成功后，如果当前节点是文件夹，展开它
            if current_node:
                self._expand_node(current_node)
                
            return True, current_node, f"成功导航到: {target_path}"
            
        except Exception as e:
            return False, current_node, f"导航失败: {str(e)}"
    
    def _ensure_dialog_visible(self):
        """确保对话框可见"""
        if not self.dialog.is_displayed():
            # 可能需要点击某些按钮来显示对话框
            # 这里可以添加显示对话框的逻辑
            pass
    
    def _find_child_node_by_name(self, folder_name, parent_path="/"):
        """
        在当前节点的子节点中查找指定名称的文件夹
        
        Args:
            folder_name: 文件夹名称
            parent_path: 父路径
            
        Returns:
            WebElement or None: 找到的节点元素
        """
        try:
            # 先尝试通过node-path属性精确查找
            target_path = f"{parent_path}/{folder_name}" if parent_path != "/" else f"/{folder_name}"
            
            # 尝试多种定位方式
            selectors = [
                f"//span[@class='treeview-txt' and @node-path='{target_path}']",
                f"//span[@class='treeview-txt' and text()='{folder_name}' and starts-with(@node-path, '{parent_path}/')]",
                f"//span[@class='treeview-txt' and text()='{folder_name}']"
            ]
            
            for selector in selectors:
                try:
                    element = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    # 返回包含这个span的li元素
                    return element.find_element(By.XPATH, "./ancestor::li[contains(@class, 'treeview-')]")
                except (TimeoutException, NoSuchElementException):
                    continue
            
            return None
            
        except Exception as e:
            print(f"查找节点时出错: {e}")
            return None
    
    def _expand_node(self, node_element):
        """
        展开节点（如果已展开则跳过）
        
        Args:
            node_element: 节点li元素
        """
        try:
            # 查找展开/收起按钮
            expand_btn = node_element.find_element(
                By.CSS_SELECTOR, 
                "em.plus.icon-operate"
            )
            
            # 检查是否已展开（有minus类表示已展开）
            if "minus" not in expand_btn.get_attribute("class"):
                expand_btn.click()
                time.sleep(0.5)  # 等待展开动画
                
        except NoSuchElementException:
            # 没有找到展开按钮，可能是空文件夹或叶子节点
            pass
        except Exception as e:
            print(f"展开节点时出错: {e}")
    
    def _create_folder(self, folder_name, parent_path, parent_node):
        """
        在当前路径下创建新文件夹
        
        Args:
            folder_name: 文件夹名称
            parent_path: 父路径
            parent_node: 父节点元素
            
        Returns:
            WebElement: 新创建的节点元素
        """
        try:
            # 1. 确保父节点可见并展开
            if parent_node:
                # 点击父节点使其处于活动状态
                txt_element = parent_node.find_element(By.CSS_SELECTOR, "span.treeview-txt")
                txt_element.click()
                time.sleep(0.5)
                
                # 展开父节点
                self._expand_node(parent_node)
            
            # 2. 点击"新建文件夹"按钮
            new_folder_btn = WebDriverWait(self.dialog, 5).until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR, 
                    "a[title='新建文件夹']"
                ))
            )
            new_folder_btn.click()
            time.sleep(1)  # 等待输入框出现
            
            # 3. 查找并输入文件夹名称
            # 在百度网盘中，新建文件夹时会创建一个可编辑的节点
            # 需要找到可编辑的输入框
            edit_input = self._find_edit_input()
            if not edit_input:
                # 如果找不到输入框，尝试其他方式
                edit_input = self._find_edit_input_alternative()
            
            if edit_input:
                # 清空并输入新名称
                edit_input.clear()
                edit_input.send_keys(folder_name)
                
                # 按下回车键确认
                edit_input.send_keys("\n")
                time.sleep(2)  # 等待创建完成
                
                # 4. 查找新创建的节点
                new_node = self._find_child_node_by_name(folder_name, parent_path)
                if new_node:
                    return new_node
                else:
                    # 如果找不到，可能创建失败，检查是否有错误提示
                    error_msg = self._check_for_error()
                    if error_msg:
                        print(f"创建文件夹失败: {error_msg}")
                    
            return None
            
        except Exception as e:
            print(f"创建文件夹过程中出错: {e}")
            return None
    
    def _find_edit_input(self):
        """查找可编辑的输入框"""
        try:
            # 尝试查找具有treeview-edit类的输入框
            return WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, 
                    ".treeview-edit, input[type='text']"
                ))
            )
        except TimeoutException:
            return None
    
    def _find_edit_input_alternative(self):
        """查找可编辑输入框的备选方法"""
        try:
            # 尝试查找当前聚焦的元素
            return self.driver.switch_to.active_element
        except:
            pass
            
        try:
            # 查找所有输入框
            inputs = self.driver.find_elements(By.CSS_SELECTOR, "input")
            for input_elem in inputs:
                if input_elem.is_displayed():
                    return input_elem
        except:
            pass
            
        return None
    
    def _check_for_error(self):
        """检查是否有错误提示"""
        try:
            # 查找错误提示元素（根据实际网页结构调整）
            error_elem = self.driver.find_element(
                By.CSS_SELECTOR, 
                ".dialog-error, .error-msg, .tips-error"
            )
            return error_elem.text
        except:
            return None
    
    def get_current_selected_path(self):
        """获取当前选中的路径"""
        try:
            # 查找当前选中的节点
            selected_node = self.dialog.find_element(
                By.CSS_SELECTOR, 
                ".treeview-node-on .treeview-txt"
            )
            return selected_node.get_attribute("node-path")
        except:
            return "/"
    
    def confirm_selection(self):
        """点击确定按钮"""
        try:
            confirm_btn = self.dialog.find_element(
                By.CSS_SELECTOR, 
                "a[node-type='confirm']"
            )
            confirm_btn.click()
            return True
        except Exception as e:
            print(f"点击确定按钮失败: {e}")
            return False
    
    def cancel_selection(self):
        """点击取消按钮"""
        try:
            cancel_btn = self.dialog.find_element(
                By.CSS_SELECTOR, 
                "a[node-type='cancel']"
            )
            cancel_btn.click()
            return True
        except Exception as e:
            print(f"点击取消按钮失败: {e}")
            return False