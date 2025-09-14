# services/yolo_client.py
from __future__ import annotations
import requests
from typing import Optional, Tuple, Dict

class YoloHTTPClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8765", timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def health(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            return r.ok and r.json().get("ok") is True
        except Exception:
            return False

    def predict(self, image_path: str, user_query: str, conf: float = 0.90
               ) -> Tuple[Optional[Tuple[int, int]], Dict]:
        """Returns ((x,y), meta) or (None, meta)."""
        files = {"image": open(image_path, "rb")}
        data = {"user_query": user_query, "confidence_threshold": str(conf)}
        try:
            r = requests.post(f"{self.base_url}/predict", data=data, files=files, timeout=self.timeout)
            r.raise_for_status()
            js = r.json()
            if js.get("ok") and js.get("match"):
                return (int(js["x"]), int(js["y"])), js
            return None, js
        finally:
            try: files["image"].close()
            except Exception: pass
