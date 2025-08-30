from appium import webdriver
from appium.options.android import UiAutomator2Options
from typing import Optional
import time

from config.settings import config

class DriverManager:
    # manager for appium
    
    def __init__(self):
        self.driver: Optional[webdriver.Remote] = None
    
    def setup_driver(self) -> webdriver.Remote:
        
        options = UiAutomator2Options()
        options.platform_name = config.PLATFORM_NAME
        options.device_name = config.DEVICE_NAME
        options.automation_name = config.AUTOMATION_NAME
        options.app_package = config.APP_PACKAGE
        options.app_activity = config.APP_ACTIVITY
        options.new_command_timeout = config.NEW_COMMAND_TIMEOUT

        self.driver = webdriver.Remote(config.APPIUM_SERVER_URL, options=options)
        self.driver.implicitly_wait(config.IMPLICIT_WAIT)
        return self.driver
    
    def get_driver(self) -> webdriver.Remote:
        if self.driver is None:
            return self.setup_driver()
        return self.driver
    
    def get_screen_size(self) -> dict:
        if self.driver is None:
            raise RuntimeError("Driver not initialized")
        return self.driver.get_window_size()
    
    def get_page_source(self) -> str:
        if self.driver is None:
            raise RuntimeError("Driver not initialized")
        return self.driver.page_source
    
    def wait_for_app_launch(self, seconds: float = 4.0):
        time.sleep(seconds)
    
    def quit_driver(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Warning: Error quitting driver: {e}")
            finally:
                self.driver = None

    def reset_app(self, clear_data: bool = False):
        driver = self.get_driver()
        package = config.APP_PACKAGE 

        try:
            driver.terminate_app(package)
        except Exception:
            pass

        if clear_data:
            try:
                driver.execute_script("mobile: shell", {
                    "command": "pm",
                    "args": ["clear", package]
                })
            except Exception:
                pass

        # Relaunch
        driver.activate_app(package)
        driver.implicitly_wait(config.IMPLICIT_WAIT)
        
        

