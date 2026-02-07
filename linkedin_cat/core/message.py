import time
import random
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from colorama import Fore, Style
from typing import List
from linkedin_cat.core.base import LinkedinBase

# Message Button Class，eg:<button aria-label="Invite Laura Gong to connect" id="ember840"
# class="artdeco-button artdeco-button--2
# artdeco-button--primary ember-view ieSHXhFfVTxQfadOJdXYOIDuVKsBXgPtjNxI"
# type="button">
# message_class = 'ieSHXhFfVTxQfadOJdXYOIDuVKsBXgPtjNxI'

class LinkedinMessage(LinkedinBase):
    """
    Encapsulates the functionality related to interacting with
    LinkedIn using Selenium.
    """
    def __init__(self,linkedin_cookies_json:str,headless = False,**kwargs):
        super().__init__(linkedin_cookies_json,headless,**kwargs)
        self.message_button_class = kwargs.get('button_class')

    def open_linkedin_url(self,url,wait=True):
        try:
            # Wait for a short duration
            self.short_wait()

            # Get the URL
            print(Fore.GREEN + f"Opening Linkedin URL: {url}" + Style.RESET_ALL)
            self.driver.get(url)

            # Wait for a medium duration
            self.medium_wait()

            if wait:
                # Scroll to the middle of the page
                print(Fore.GREEN + "Scrolling to the middle of the page" + Style.RESET_ALL)
                self.scroll_to_middle()

                # Wait for a short duration
                self.medium_wait()

                # Scroll to a random position
                print(Fore.GREEN + "Scrolling to a random position" + Style.RESET_ALL)
                self.scroll_to_random()

                # Wait for a short duration
                self.medium_wait()

                # Scroll to the bottom of the page
                print(Fore.GREEN + "Scrolling to the bottom of the page" + Style.RESET_ALL)
                self.scroll_to_bottom()

                # Wait for a short duration
                self.medium_wait()

                # Scroll to the top of the page
                print(Fore.GREEN + "Scrolling to the top of the page" + Style.RESET_ALL)
                self.scroll_to_top()

                # Wait for a medium duration
                self.short_wait()
            

        except Exception as e:
            # If an exception occurs, print an error message
            print(Fore.RED + f'Error: {e}' + Style.RESET_ALL)
    def send_connection_request(self, message):
        """
        Sends a connection request to a LinkedIn profile.

        Returns: True if connection request was successful, False otherwise.

        Parameter message: The connection message being sent.
        Precondition: message must be a String where len(message) <= 300.
        """
        try:
            print(Fore.GREEN + "Locating the 'Connect' button" + Style.RESET_ALL)
            connect_button = self.driver.find_element(By.XPATH, f"(//button[contains(@aria-label, 'Invite') and contains(@class, '{self.message_button_class}')])")
            connect_button.click()
            self.medium_wait()
            print(Fore.GREEN + "Clicked on the 'Connect' button" + Style.RESET_ALL)

            print(Fore.GREEN + "Locating the 'Add a note' button" + Style.RESET_ALL)
            add_note_button = self.driver.find_element(By.XPATH, "//button[@aria-label='Add a note']")
            add_note_button.click()
            self.medium_wait()
            print(Fore.GREEN + "Clicked on the 'Add a note' button" + Style.RESET_ALL)

            print(Fore.GREEN + "Locating the message entry field" + Style.RESET_ALL)
            message_entry = self.driver.find_element(By.XPATH, "//textarea[@name='message']")
            message_entry.send_keys(message)
            self.medium_wait()
            print(Fore.GREEN + "Typed the message" + Style.RESET_ALL)

            print(Fore.GREEN + "Locating the 'Send now' button" + Style.RESET_ALL)
            send_button = self.driver.find_element(By.XPATH, "//button[@aria-label='Send invitation']")
            send_button.click()
            self.medium_wait()
            print(Fore.GREEN + "Clicked on the 'Send now' button" + Style.RESET_ALL)

            print(Fore.GREEN + "Verifying if connection request is sent" + Style.RESET_ALL)
            if self.is_pending():
                print(Fore.GREEN + "Connection request sent" + Style.RESET_ALL)
                return True
            else:
                print(Fore.RED + "Failed to send connection request" + Style.RESET_ALL)

        except Exception as e:
            print(Fore.RED + f"Failed to send connection request, Error: {e}" + Style.RESET_ALL)
            return False

    def more_then_connect(self, message):
        """
        Sends a conenction request to a LinkedIn profile when the blue
        connection button isn't visible.

        Returns: True if the connection request was successful, False otherwise.

        Parameter message: The connection message being sent.
        Precondition: message must be a String where len(message) <= 300.
        """
        try:
            print(Fore.GREEN + "Locating and clicking the 'More' button" + Style.RESET_ALL)
            more_button = self.driver.find_element(By.XPATH, f"//button[contains(@aria-label, 'More actions') and contains(@class, '{self.message_button_class}')]")

            # more_button = self.driver.find_element(By.XPATH,
            #                                   "//button[contains(@aria-label, 'More actions') and contains(@class, 'ieSHXhFfVTxQfadOJdXYOIDuVKsBXgPtjNxI')]")
            more_button.click()




            self.driver.execute_script("window.scrollBy(0, 300)")
            self.medium_wait()
            print(Fore.GREEN + "Clicked on the 'More' button" + Style.RESET_ALL)

            print(Fore.GREEN + "Locating and clicking the 'Connect' button" + Style.RESET_ALL)

            connect_button = self.driver.find_element(By.XPATH, "//li//div[contains(@aria-label, 'Invite')]")
            self.driver.execute_script("arguments[0].click();", connect_button)
            self.medium_wait()
            print(Fore.GREEN + "Clicked on the 'Connect' button" + Style.RESET_ALL)

            print(Fore.GREEN + "Locating and clicking the 'Add a note' button" + Style.RESET_ALL)
            add_note_button = self.driver.find_element(By.XPATH, "//button[@aria-label='Add a note']")
            add_note_button.click()
            self.medium_wait()
            print(Fore.GREEN + "Clicked on the 'Add a note' button" + Style.RESET_ALL)

            print(Fore.GREEN + "Locating the message entry field" + Style.RESET_ALL)
            message_entry = self.driver.find_element(By.XPATH, "//textarea[@name='message']")
            message_entry.send_keys(message)
            self.medium_wait()
            print(Fore.GREEN + "Typed the message" + Style.RESET_ALL)

            print(Fore.GREEN + "Locating and clicking the 'Send now' button" + Style.RESET_ALL)
            send_button = self.driver.find_element(By.XPATH, "//button[@aria-label='Send invitation']")
            send_button.click()
            self.medium_wait()
            print(Fore.GREEN + "Clicked on the 'Send now' button" + Style.RESET_ALL)

            pending = self.is_pending()
            if pending:
                print(Fore.GREEN + "Connection request sent" + Style.RESET_ALL)
            else:
                print(Fore.RED + "Failed to send connection request" + Style.RESET_ALL)

            return True

        except Exception as e:
            print(Fore.RED + f"Failed to send connection request: {e}" + Style.RESET_ALL)
            return False

    def is_friend(self):
        try:
            print(Fore.GREEN + "Checking friend status" + Style.RESET_ALL)
            friend_status = self.driver.find_element(By.XPATH,
                                                     "//span[contains(@class, 'distance-badge')]/span[contains(@class, 'dist-value')]")
            if friend_status.text.strip() == "1st":
                print(Fore.GREEN + "Friend status: True" + Style.RESET_ALL)
                return True
            else:
                print(Fore.GREEN + "Friend status: False" + Style.RESET_ALL)
                return False
        except NoSuchElementException:
            print(Fore.RED + "Friend status: Element not found" + Style.RESET_ALL)
            return False
        finally:
            self.short_wait()

    def is_pending(self):
        try:
            print(Fore.GREEN + "Checking pending status" + Style.RESET_ALL)
            self.driver.find_element(By.XPATH, (f"//button[contains(@aria-label, 'Pending') and contains(@class, '{self.message_button_class}')]"))
            print(Fore.GREEN + "Pending status: True" + Style.RESET_ALL)
            return True
        except NoSuchElementException:
            print(Fore.GREEN + "Pending status: False" + Style.RESET_ALL)
            return False
        finally:
            self.short_wait()

    def has_connect_button(self):
        """
        Checks if LinkedIn gives the user the option to connect with the current profile.

        Returns: True if the profile has the conenct button, False otherwise.
        """
        try:
            connect = self.driver.find_element(By.XPATH,
                                               "(//span[@class='artdeco-button__text'])[6]")
            connect_following = self.driver.find_element(By.XPATH,
                                                         "(//span[@class='artdeco-button__text'])[8]")
            if connect.text == "Connect" or connect_following.text == "Connect":
                return True
            else:
                return False
        except NoSuchElementException:
            return False

    def has_hidden_connect_button(self):
        """
        Checks if the user can send a request after clicking more.

        Returns True if the profile has a hidden connect button, False otherwise.
        """
        try:
            self.driver.find_element(By.XPATH,
                                     ("(//div[contains(@class, 'artdeco-dropdown__item') and "
                                      "contains(@class, 'artdeco-dropdown__item--is-dropdown')"
                                      " and contains(@class, 'ember-view') and contains(@class,"
                                      " 'full-width') and contains(@class, 'display-flex') and"
                                      " contains(@class, 'align-items-center')]/"
                                      "span[text()='Connect'])[1]"))
            return True
        except NoSuchElementException:
            return False

    def generate_message(self,message:str):
        """
        Extracts the first name from the LinkedIn profile page,
        then assembles the personalized message to send. Allows the
        user the put [FULL NAME] and [FIRST NAME] in their message to instruct the
        program to automatically insert the profile's name.

        Returns: A String representing the personalized connection message.
        """
        full_name = self.driver.find_element(By.XPATH, '//h1[contains(@class, "inline t-24 v-align-middle break-words")]').text

        name_list = full_name.split(" ")
        first = name_list[0]
        if first.lower() not in ['dr.', 'mr.' 'mrs.',
                                 'ms.', 'dr', 'mr', 'mrs' 'ms']:
            first_name = name_list[0]
        else:
            first_name = name_list[1]

        msg = message.replace('FULLNAME', full_name)
        msg = msg.replace('FIRSTNAME', first_name)
        return msg.strip()

    def send_msg_to_friend(self,message:str):
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            msg_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH,
                     f"//button[contains(@aria-label, 'Message') and contains(@class, '{self.message_button_class}')]")
                )
            )
            msg_button.click()

            time.sleep(random.uniform(3, 5))

            msg_box = self.driver.find_element(By.XPATH, "//div[@contenteditable='true']/p")
            msg_box.click()

            last_msg = self.find_last_message()

            if last_msg == message:
                print(Fore.RED + f'Message already sent:{last_msg}' +  Style.RESET_ALL)
                return

            # 清空消息输入框
            from selenium.webdriver.common.keys import Keys
            msg_box.send_keys(Keys.CONTROL + "a")  # Windows/Linux系统可以用CTRL+A；如果是macOS，使用Keys.COMMAND
            msg_box.send_keys(Keys.DELETE)

            time.sleep(random.uniform(3, 5))

            # print('box count', self.get_msg_box_count())
            # if self.get_msg_box_count() != 1:
            #     print(Fore.RED + f'Message box count is not 1' +  Style.RESET_ALL)
            #     self.close_msg_box()
            #     print(Fore.RED + f'Closing boxes' +  Style.RESET_ALL)

            # 重新定位 msg_box
            msg_box = self.driver.find_element(By.XPATH, "//div[@contenteditable='true']/p")
            msg_box.send_keys(message)

            # send_button =  self.driver.find_element(By.XPATH, ("(//button[contains(@class,'msg-form__send-button') and contains(@type, 'submit')])"))

            # 等待发送按钮可点击
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            send_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "(//button[contains(@class,'msg-form__send-button') and contains(@type, 'submit')])"))
            )

            time.sleep(random.uniform(1, 3))
            send_button.click()
            time.sleep(random.uniform(1, 3))
            print(Fore.BLUE + f'Message successfully sent:{message}'+ Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f'Error sending message: {e}'+ Style.RESET_ALL)

    def send_single_request(self, url, message, wait=True):
        """
        发送单个连接请求或消息
        
        Returns:
            dict: {
                "success": bool,
                "status": "sent" | "pending" | "already_friend" | "failed" | "error",
                "message": str,
                "url": str
            }
        """
        result = {
            "success": False,
            "status": "unknown",
            "message": "",
            "url": url
        }
        
        try:
            print(Fore.BLACK + "="*30 + " Sending Request "+ "="*30 + Style.RESET_ALL)
            self.open_linkedin_url(url,wait=wait)

            msg = self.generate_message(message)
            print(Fore.BLUE + "Generating message:", msg + Style.RESET_ALL)

            while self.is_msg_box_exist():
                print(Fore.YELLOW + "Message box exists, Closing it now" + Style.RESET_ALL)
                self.close_msg_box()

            # 情况1: 已经是好友，发送私信
            if self.is_friend():
                print(Fore.GREEN + "Sending message to friend" + Style.RESET_ALL)
                self.send_msg_to_friend(msg)
                result["success"] = True
                result["status"] = "already_friend"
                result["message"] = "Message sent to existing friend"
                return result

            # 情况2: 已发送待确认
            if self.is_pending():
                print(Fore.YELLOW + 'Connection request is pending:', url + Style.RESET_ALL)
                result["success"] = True  # 视为成功，无需重发
                result["status"] = "pending"
                result["message"] = "Connection request already pending"
                return result

            # 情况3: 发送连接请求
            if self.has_hidden_connect_button():
                print(Fore.GREEN + "Taking more than connect action" + Style.RESET_ALL)
                send_result = self.more_then_connect(msg)
            else:
                print(Fore.GREEN + "Sending connection request" + Style.RESET_ALL)
                send_result = self.send_connection_request(msg)
            
            # 验证发送结果
            if send_result:
                # 二次确认：检查是否变为 pending 状态
                time.sleep(1)
                if self.is_pending():
                    result["success"] = True
                    result["status"] = "sent"
                    result["message"] = "Connection request sent successfully"
                else:
                    result["success"] = True  # 函数返回 True，信任它
                    result["status"] = "sent"
                    result["message"] = "Connection request sent (unverified)"
            else:
                result["success"] = False
                result["status"] = "failed"
                result["message"] = "Failed to send connection request"
                
        except Exception as e:
            print(Fore.RED + f'Error: {e}' + Style.RESET_ALL)
            result["success"] = False
            result["status"] = "error"
            result["message"] = str(e)
        finally:
            time.sleep(random.uniform(1, 3))
        
        return result

    def send_multi_request(self, url_list: List[str], message: str):
        try:
            for url in url_list:
                self.send_single_request(url,message)
        except Exception as e:
            print(Fore.RED + f'Error: {e}' + Style.RESET_ALL)
        finally:
            self.close_driver()

    def is_msg_box_exist(self):
        try:
            self.driver.find_element(By.XPATH,
                                                '(//button[contains(@class,"msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted")])')
            return True
        except NoSuchElementException:
            return False

    def get_msg_box_count(self):
        try:
            elements = self.driver.find_elements(
                By.XPATH,
                '(//button[contains(@class,"msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted")])'
            )
            count = len(elements)
            if count == 0:
                print("No elements found matching the specified XPath.")
            return count  # 返回找到的元素数量
        except NoSuchElementException as e:
            print(f"Error: No elements found. Exception details: {e}")
            return 0

    def close_msg_box(self):
        try:
            while True:
                self.medium_wait()
                if self.is_msg_box_exist():
                    print(Fore.GREEN + "Locating and clicking the 'Close' button" + Style.RESET_ALL)
                    close_button = self.driver.find_element(By.XPATH,
                                                            '(//button[contains(@class, "msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted")])')
                    close_button.click()
                else:
                    break
                self.short_wait()
        except NoSuchElementException:
            print(Fore.RED + "Failed to close the message box" + Style.RESET_ALL)

    def find_last_message(self):
        try:
            messages = self.driver.find_elements(By.CSS_SELECTOR,'.msg-s-event__content')
            if messages:
                last_message = messages[-1].find_element(By.TAG_NAME, 'p').text
                return last_message.strip()
        except NoSuchElementException:
            return False

    def close_driver(self):
        self.driver.quit()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_driver()