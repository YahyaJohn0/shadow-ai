# shadow_core/integrations.py
import webbrowser
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class Integrations:
    """
    Stubs for messaging integrations. For WhatsApp automation, opening WhatsApp Web and sending
    a message via selenium is a simple approach. Make sure to respect platform ToS.
    """
    def __init__(self, driver_path=None):
        self.driver_path = driver_path

    def open_in_browser(self, url):
        webbrowser.open(url)

    def send_whatsapp_web(self, phone_number, message, selenium_driver_path=None):
        """
        Very basic flow:
        - opens https://web.whatsapp.com/send?phone=<phone>&text=<message>
        - requires logged-in WhatsApp Web
        """
        msg = message.replace(" ", "%20")
        url = f"https://web.whatsapp.com/send?phone={phone_number}&text={msg}"
        webbrowser.open(url)
        # If you want to do with selenium for clicking send:
        if selenium_driver_path or self.driver_path:
            path = selenium_driver_path or self.driver_path
            options = webdriver.ChromeOptions()
            options.add_argument("--user-data-dir=./selenium-data")
            driver = webdriver.Chrome(executable_path=path, options=options)
            driver.get(url)
            time.sleep(10)  # wait for WhatsApp web to load & QR auth
            try:
                send_btn = driver.find_element(By.XPATH, '//button[@data-testid="compose-btn-send"]')
                send_btn.click()
                time.sleep(2)
            except Exception as e:
                print("Could not auto-send; you may need to press send manually:", e)
            # driver.quit()
