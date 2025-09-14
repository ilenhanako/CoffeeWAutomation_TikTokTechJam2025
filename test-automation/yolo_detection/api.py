# yolo_detection/api.py
import os, io, re, time, base64, tempfile
from typing import List, Optional

#python -m yolo_detection.api

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
from inference_sdk import InferenceHTTPClient
from rapidfuzz import process, fuzz

# -------- Roboflow config --------
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
if not ROBOFLOW_API_KEY:
    raise RuntimeError("Set ROBOFLOW_API_KEY in the environment.")

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=ROBOFLOW_API_KEY
)

# -------- Query → classes mapping --------
INTENT_TO_CLASS = {
    "comment": ["comment", "comment_edit"],
    "reply": ["comment", "comment_edit"],
    "type": ["comment_edit", "send_comment"],
    "submit": ["send_comment"],
    "write": ["comment_edit"],
    "send": ["send_comment", "share"],
    "post": ["send_comment"],
    "like": ["like"],
    "heart": ["like"],
    "share": ["share"],
    "message": ["inbox"],
    "inbox": ["inbox"],
    "chat": ["inbox"],
    "profile": ["profile"],
    "upload": ["upload"],
    "friends": ["friends"],
    "explore": ["explore"],
    "search": ["search"],
    "magnifying": ["search"],
    "home": ["home"],
    "following": ["following"],
    "for you": ["for you"],
    "shop": ["shop"],
    "store": ["shop"],
}
YOLO_CLASSES = [
    "Following", "For you", "Friends", "comment", "comment_edit",
    "edit_profile", "home", "like", "name_edit", "profile",
    "save", "search", "send_comment", "share", "username_edit"
]

def _fuzzy(query: str, threshold: int = 70) -> List[str]:
    matches = process.extract(query, YOLO_CLASSES, scorer=fuzz.partial_ratio, limit=5)
    return [m[0] for m in matches if m[1] >= threshold]

def _targets_from_query(user_query: str) -> List[str]:
    q = user_query.lower()
    targets: List[str] = []
    for kw, classes in INTENT_TO_CLASS.items():
        if re.search(rf"\b{re.escape(kw)}\b", q):
            targets.extend(classes)
    if any(k in q for k in ["type", "write", "input", "text"]):
        targets.extend(["comment_edit", "username_edit", "name_edit"])
    if not targets:
        targets.extend(_fuzzy(q) or [])
    # dedupe, keep order
    seen = set()
    out = []
    for t in targets:
        k = t.lower()
        if k not in seen:
            seen.add(k)
            out.append(t)
    return out

def _predict(image_path: str, user_query: str, confidence_threshold: float):
    targets = _targets_from_query(user_query)
    if not targets:
        return None, {"reason": "no targets from query", "targets": []}

    result = client.run_workflow(
        workspace_name="tiktok-qz4gk",
        workflow_id="tiktokflutter",
        images={"image": image_path},
        use_cache=True,
    )

    # normalize
    if isinstance(result, list) and result:
        preds = result[0].get("predictions", {}).get("predictions", [])
    elif isinstance(result, dict):
        preds = result.get("predictions", {}).get("predictions", [])
    else:
        preds = []

    tlower = {t.lower() for t in targets}
    filtered = [
        p for p in preds
        if float(p.get("confidence", 0)) >= confidence_threshold
        and str(p.get("class", "")).lower() in tlower
    ]
    if not filtered:
        return None, {"reason": "no confident match", "targets": targets, "count": len(preds)}

    best = max(filtered, key=lambda x: float(x["confidence"]))
    return best, {"targets": targets, "count": len(preds)}

# -------- FastAPI --------
class PredictResponse(BaseModel):
    ok: bool
    match: bool
    x: Optional[int] = None
    y: Optional[int] = None
    cls: Optional[str] = None
    confidence: Optional[float] = None
    targets: List[str] = []
    reason: Optional[str] = None
    latency_ms: int

app = FastAPI(title="YOLO Intent Locator")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/predict", response_model=PredictResponse)
async def predict(
    user_query: str = Form(...),
    confidence_threshold: float = Form(0.90),
    image: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = Form(None),
):
    t0 = time.time()
    if not image and not image_base64:
        raise HTTPException(400, "Provide either file 'image' or 'image_base64'")

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
        if image:
            tmp.write(await image.read())
        else:
            try:
                b64 = image_base64.split(",")[-1]
                raw = base64.b64decode(b64)
                Image.open(io.BytesIO(raw)).verify()
                tmp.write(raw)
            except Exception as e:
                raise HTTPException(400, f"Invalid base64 image: {e}")

    try:
        best, meta = _predict(tmp_path, user_query, confidence_threshold)
        if not best:
            return PredictResponse(
                ok=True, match=False,
                reason=meta.get("reason"), targets=meta.get("targets", []),
                latency_ms=int((time.time() - t0) * 1000),
            )
        return PredictResponse(
            ok=True, match=True,
            x=int(best["x"]), y=int(best["y"]),
            cls=str(best["class"]), confidence=float(best["confidence"]),
            targets=meta.get("targets", []),
            latency_ms=int((time.time() - t0) * 1000),
        )
    finally:
        try: os.remove(tmp_path)
        except Exception: pass

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("YOLO_API_PORT", "8765"))
    uvicorn.run("yolo_detection.api:app", host="127.0.0.1", port=port, reload=False)
