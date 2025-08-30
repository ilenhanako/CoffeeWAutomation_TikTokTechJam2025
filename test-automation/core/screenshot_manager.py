import base64
from PIL import Image, ImageDraw, ImageColor
from pathlib import Path
from typing import List, Optional

from config.settings import config

class ScreenshotManager:
    
    @staticmethod
    def take_screenshot(driver, path: str = None) -> str:
        if path is None:
            path = config.SCREENSHOT_PATH
        
        driver.save_screenshot(path)
        # print(f"Screenshot saved: {path}")
        return path
    
    @staticmethod
    def encode_image(image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    @staticmethod
    def draw_point(image: Image.Image, point: List[int], color: str = "green") -> Image.Image:
        overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        x, y = point
        radius = min(image.size) * 0.02
        
        try:
            color_rgba = ImageColor.getrgb(color) + (200,)
        except:
            color_rgba = (0, 255, 0, 200)
        
        # Draw circle
        draw.ellipse([(x-radius, y-radius), (x+radius, y+radius)], fill=color_rgba)
        # Draw crosshair
        draw.line([(x-radius*1.5, y), (x+radius*1.5, y)], fill=color_rgba, width=3)
        draw.line([(x, y-radius*1.5), (x, y+radius*1.5)], fill=color_rgba, width=3)
        
        return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    
    @staticmethod
    def draw_click_box(image: Image.Image, bottom_right: List[int], 
                      box_size: int, color: str = "orange") -> Image.Image:
        overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        
        x2, y2 = bottom_right
        x1 = max(1, x2 - box_size)
        y1 = max(1, y2 - box_size)
        
        try:
            box_color = ImageColor.getrgb(color) + (120,)
        except:
            box_color = (255, 165, 0, 120)
        
        draw.rectangle([(x1, y1), (x2, y2)], fill=box_color, outline="red", width=3)
        return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    
    @staticmethod
    def ensure_directory_exists(file_path: str):
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)