import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()
@dataclass
class AppConfig:
    
    DASHSCOPE_API_KEY: str = os.getenv('DASHSCOPE_API_KEY')
    DASHSCOPE_BASE_URL: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    
    # Models
    QWEN_VL_MODEL: str = "qwen2.5-vl-7b-instruct"
    QWEN_MODEL: str = "qwen2.5-7b-instruct"
    
    # Appium 
    APPIUM_SERVER_URL: str = "http://127.0.0.1:4723"
    DEVICE_NAME: str = "Pixel_3a_API_34_extension_level_7_arm64-v8a"
    PLATFORM_NAME: str = "Android"
    AUTOMATION_NAME: str = "UiAutomator2"
    # APP_PACKAGE: str = "com.example.hackathon_test_app"
    APP_PACKAGE: str = "com.lynx.explorer"
    # APP_ACTIVITY: str = "com.example.hackathon_test_app.MainActivity"
    APP_ACTIVITY = "com.lynx.explorer.LynxViewShellActivity"

    NEW_COMMAND_TIMEOUT: int = 300
    IMPLICIT_WAIT: int = 10
    
    
    SCREENSHOT_PATH: str = "test-automation/current_screen.png"
    
    
    PATCH_SIZE: int = 14
    MERGE_SIZE: int = 2
    MIN_PIXELS: int = 256 * 28 * 28
    MAX_PIXELS: int = 1280 * 28 * 28
    

    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_DELAY: float = 1.5
    DEFAULT_WAIT_TIME: float = 0.2
    ACTION_TIMEOUT: float = 3.0
    

config = AppConfig()