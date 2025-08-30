import logging
import asyncio

websockets = []
_loop: asyncio.AbstractEventLoop = None

def register_ws(ws):
    global _loop
    _loop = asyncio.get_event_loop()
    websockets.append(ws)

async def broadcast(event: dict):
    remove = []
    for ws in websockets:
        try:
            await ws.send_json(event)
        except Exception:
            remove.append(ws)
    for ws in remove:
        websockets.remove(ws)

def send_event(event: dict):

    if _loop and _loop.is_running():
        asyncio.run_coroutine_threadsafe(broadcast(event), _loop)

class StreamlitLogHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        send_event({"type": "log", "message": log_entry})

def setup_logger():
    logger = logging.getLogger("automation")
    logger.setLevel(logging.INFO)

    handler = StreamlitLogHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # add send_event convenience to logger
    logger.send_event = send_event  

    return logger
