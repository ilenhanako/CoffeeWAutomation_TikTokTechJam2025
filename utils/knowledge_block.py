from utils.statis_ui_knowledge import STATIC_UI_KB
from PIL import Image

def build_static_knowledge_block(app: str, screenshot_path: str, user_query: str) -> str:
    """Return a short text block with absolute coordinate hints + rules."""
    app = (app or "tiktok").lower()
    kb = STATIC_UI_KB.get(app, {})
    try:
        img = Image.open(screenshot_path)
        W, H = img.size
    except Exception:
        W, H = 1080, 1920

    # quick intent guess from user_query
    uq = user_query.lower()
    likely = []
    for k in ("comment","like","share","profile","mute","close"):
        if k in uq:
            likely.append(k)
    if not likely:
        # default to most common actions; still useful
        likely = ["comment","like","share","close"]

    lines = []
    lines.append(f"App={app} | Screen={W}x{H} px")
    lines.append("=== STATIC UI HINTS ===")
    for key in likely:
        if key in kb:
            desc = kb[key]["desc"]
            pos = kb[key]["pos"]
            abs_pts = [f"({int(x*W)},{int(y*H)})" for (x,y) in pos[:3]]
            lines.append(f"- {key}: {desc}. Likely around {', '.join(abs_pts)}")
    lines.append("")
    lines.append("=== INTERRUPTION HANDLING ===")
    lines.append("If a popup/banner/dialog blocks the UI: first tap its close affordance (X/Close/Cancel/Not now/Skip) at common spots,")
    lines.append("then continue the main task.")
    lines.append("")
    lines.append("=== OUTPUT RULES ===")
    lines.append("Return exactly ONE tool call (click/long_press/swipe/type/key/system_button/open/wait/terminate).")
    lines.append("For 'type', click the input first and include 'text'.")
    return "\n".join(lines)

def detect_app(app: str, package_name: str = "", hint: str = "") -> str:
    uq = f"{app} {hint} {package_name}".lower()
    if any(k in uq for k in ("tiktok", "douyin", "com.ss.android.ugc.trill")): return "tiktok"
    if any(k in uq for k in ("instagram", "com.instagram", "reels")): return "instagram"
    if any(k in uq for k in ("shorts", "youtube shorts", "com.google.android.youtube")): return "youtube_shorts"
    if any(k in uq for k in ("facebook", "fb reels", "com.facebook.katana", "com.facebook.lite")): return "facebook_reels"
    if any(k in uq for k in ("twitter", "x ", "com.twitter.android")): return "x"
    return "tiktok" 