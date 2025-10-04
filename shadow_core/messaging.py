import asyncio
from asyncio.log import logger
from mailbox import Message
import pywhatkit
import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import platform

CHROME_DRIVER_PATH = "chromedriver.exe"  # adjust if needed
CHROME_PROFILE_PATH = r"C:\shadow_agent_profile"  # persistent profile folder


# --- Chrome Driver Helper ---
def get_chrome_driver():
    options = Options()
    options.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    service = Service(CHROME_DRIVER_PATH)
    return webdriver.Chrome(service=service, options=options)


class Messaging:
    """
    Messaging automation module for Shadow AI.
    Supports:
      - WhatsApp (via pywhatkit / web.whatsapp.com)
      - Messenger (via Selenium)
      - Instagram (via Selenium)
    """

    def __init__(self, voice_module=None):
        self.VOICE = voice_module
        # Make sure numbers have country code with + prefix
        self.CONTACTS = {
            "abbas": "+923090222132",
            "dad": "+19876543210",
            "john": "+1122334455"
        }
        self.driver = None  # Selenium driver placeholder

    # ------------------------------
    # WhatsApp messaging
    # ------------------------------
    async def send_whatsapp_message(self, contact_name_or_number, message, wait_time=15):
        number = self.CONTACTS.get(contact_name_or_number.lower(), contact_name_or_number)
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute + 2
      # schedule 1 min later
        try:
            pywhatkit.sendwhatmsg(number, message, hour, minute, wait_time=wait_time)
            reply = f"✅ WhatsApp message scheduled to {contact_name_or_number}."
            print(reply)
            if self.VOICE:
                self.VOICE.speak(reply)
            return reply
        except Exception as e:
            error_msg = f"[WhatsApp ERROR] {e}"
            print(error_msg)
            if self.VOICE:
                self.VOICE.speak("Sorry, I couldn't send the WhatsApp message.")
            return error_msg

    # ------------------------------
    # Messenger via Selenium
    # ------------------------------
    async def send_messenger_message(self, contact, message):
        try:
            driver = self._init_driver()
            driver.get("https://www.messenger.com/")
            time.sleep(5)  # wait for login (user must log in once)

            search_box = driver.find_element(By.XPATH, '//input[@placeholder="Search Messenger"]')
            search_box.send_keys(contact)
            search_box.send_keys(Keys.RETURN)
            time.sleep(2)

            msg_box = driver.find_element(By.XPATH, '//div[@aria-label="Type a message..."]')
            msg_box.send_keys(message)
            msg_box.send_keys(Keys.RETURN)

            reply = f"✅ Messenger message sent to {contact}."
            print(reply)
            if self.VOICE:
                self.VOICE.speak(reply)
            return reply
        except Exception as e:
            error_msg = f"[Messenger ERROR] {e}"
            print(error_msg)
            if self.VOICE:
                self.VOICE.speak("Sorry, I couldn't send the Messenger message.")
            return error_msg

    # ------------------------------
    # Instagram via Selenium
    # ------------------------------
    async def send_instagram_message(self, contact, message):
        try:
            driver = self._init_driver()
            driver.get("https://www.instagram.com/direct/inbox/")
            time.sleep(5)  # wait for login (user must log in once)

            search_box = driver.find_element(By.XPATH, '//input[@placeholder="Search..."]')
            search_box.send_keys(contact)
            search_box.send_keys(Keys.RETURN)
            search_box.send_keys(Keys.RETURN)
            time.sleep(2)

            msg_box = driver.find_element(By.TAG_NAME, 'textarea')
            msg_box.send_keys(message)
            msg_box.send_keys(Keys.RETURN)

            reply = f"✅ Instagram message sent to {contact}."
            print(reply)
            if self.VOICE:
                self.VOICE.speak(reply)
            return reply
        except Exception as e:
            error_msg = f"[Instagram ERROR] {e}"
            print(error_msg)
            if self.VOICE:
                self.VOICE.speak("Sorry, I couldn't send the Instagram message.")
            return error_msg

    # ------------------------------
    # Unified interface
    # ------------------------------
    async def send_message(self, platform, contact, message):
        platform = platform.lower()
        if platform == "whatsapp":
            return await self.send_whatsapp_message(contact, message)
        elif platform == "messenger":
            return await self.send_messenger_message(contact, message)
        elif platform == "instagram":
            return await self.send_instagram_message(contact, message)
        else:
            reply = f"⚠️ Platform '{platform}' not supported."
            print(reply)
            if self.VOICE:
                self.VOICE.speak(reply)
            return reply
        
class MockMessaging:
    """
    Mock messaging for testing without real API dependencies
    """
    
    def __init__(self, voice_module=None):
        self.VOICE = voice_module
        self.CONTACTS = {
            "abbas": "+923090222132",
            "dad": "+19876543210", 
            "john": "+1122334455"
        }
        logger.info("MockMessaging initialized - no real messages will be sent")
    
    async def send_whatsapp_message(self, contact_name_or_number, message, wait_time=15):
        """Mock WhatsApp message sending"""
        logger.info(f"[MOCK] Would send WhatsApp to {contact_name_or_number}: {message}")
        reply = f"✅ [MOCK] WhatsApp message would be sent to {contact_name_or_number}."
        print(reply)
        if self.VOICE:
            await self.VOICE.speak(reply)
        return reply
    
    async def send_messenger_message(self, contact, message):
        """Mock Messenger message sending"""
        logger.info(f"[MOCK] Would send Messenger to {contact}: {message}")
        reply = f"✅ [MOCK] Messenger message would be sent to {contact}."
        print(reply)
        if self.VOICE:
            await self.VOICE.speak(reply)
        return reply
    
    async def send_instagram_message(self, contact, message):
        """Mock Instagram message sending"""
        logger.info(f"[MOCK] Would send Instagram to {contact}: {message}")
        reply = f"✅ [MOCK] Instagram message would be sent to {contact}."
        print(reply)
        if self.VOICE:
            await self.VOICE.speak(reply)
        return reply
    
    async def send_message(self, platform, contact, message):
        """Mock unified message sending"""
        platform = platform.lower()
        logger.info(f"[MOCK] Would send {platform} message to {contact}: {message}")
        reply = f"✅ [MOCK] {platform.capitalize()} message would be sent to {contact}."
        print(reply)
        if self.VOICE:
            await self.VOICE.speak(reply)
        return reply
    
    @staticmethod
    def parse_command(command):
        """Parse command (same as real messaging)"""
        command = command.lower()
        platforms = ["whatsapp", "messenger", "instagram"]
        for plat in platforms:
            if plat in command and "to" in command:
                try:
                    parts = command.split("to", 1)[1].strip().split(" ", 1)
                    contact = parts[0].strip()
                    message = parts[1].strip() if len(parts) > 1 else ""
                    return plat, contact, message
                except:
                    return plat, None, None
        return None, None, None
    
    def add_contact(self, name, phone, platform="whatsapp", country_code="+1"):
        """Mock add contact"""
        logger.info(f"[MOCK] Would add contact: {name} ({phone})")
        self.CONTACTS[name.lower()] = phone
        return True
    
    def get_contacts(self):
        """Mock get contacts"""
        return [{"name": name, "phone": phone} for name, phone in self.CONTACTS.items()]

    # ------------------------------
    # Command parser
    # ------------------------------
    @staticmethod
    def parse_command(command):
        command = command.lower()
        platforms = ["whatsapp", "messenger", "instagram"]
        for plat in platforms:
            if plat in command and "to" in command:
                try:
                    parts = command.split("to", 1)[1].strip().split(" ", 1)
                    contact = parts[0].strip()
                    message = parts[1].strip() if len(parts) > 1 else ""
                    return plat, contact, message
                except:
                    return plat, None, None
        return None, None, None

    # ------------------------------
    # Selenium driver initializer
    # ------------------------------
    def _init_driver(self):
        if self.driver:
            return self.driver
        self.driver = get_chrome_driver()
        return self.driver
# Add this to the end of shadow_core/messaging.py

class MockMessaging(Messaging):
    """Mock messaging for testing without real API dependencies"""
    
    async def _send_whatsapp(self, message: Message) -> bool:
        logger.info(f"[WHATSAPP MOCK] Would send to {message.contact.name}: {message.content}")
        await asyncio.sleep(0.5)
        return True
    
    async def _send_sms(self, message: Message) -> bool:
        logger.info(f"[SMS MOCK] Would send to {message.contact.name}: {message.content}")
        await asyncio.sleep(0.5)
        return True
    
    async def _send_telegram(self, message: Message) -> bool:
        logger.info(f"[TELEGRAM MOCK] Would send to {message.contact.name}: {message.content}")
        await asyncio.sleep(0.5)
        return True
    
    async def _send_email(self, message: Message) -> bool:
        logger.info(f"[EMAIL MOCK] Would send to {message.contact.name}: {message.content}")
        await asyncio.sleep(0.5)
        return True