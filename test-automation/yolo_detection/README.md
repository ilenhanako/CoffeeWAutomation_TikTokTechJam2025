# 📸 YOLO Detection Service

A FastAPI microservice that powers **vision-based element detection** for the AutoGUI_TecJam2025 Mobile UI Automation Framework.

It uses **Roboflow YOLO workflows** and **intent → class mappings** to locate UI elements in screenshots.

---

## 🚀 Features

- **Intent to UI Mapping**
    
    Natural-language queries like `"tap like button"` are mapped to YOLO classes (`like`).
    
- **YOLO Inference via Roboflow**
    
    Runs workflows hosted on [Roboflow](https://roboflow.com/) via `inference_sdk`.
    
- **Fuzzy Matching**
    
    Automatically expands queries to the closest YOLO classes (e.g., `"magnifying"` → `"search"`).
    
- **REST API**
    - `GET /health` → health check
    - `POST /predict` → detect UI element from image + query

---

## ⚙️ Prerequisites

- Python 3.9+
- A valid **Roboflow API key** (`ROBOFLOW_API_KEY`)
- Installed dependencies (`requirements.txt` in `test-automation/`)

---

## 🔧 Installation

```bash
cd test-automation/yolo_detection
python -m venv venv
source venv/bin/activate

pip install --upgrade pip setuptools wheel
pip install fastapi uvicorn pillow inference-sdk rapidfuzz

```

> Dependencies are already in the root test-automation/requirements.txt.
> 
> 
> You only need this if running YOLO separately.
> 

---

## 🔑 Environment Variables

Create a `.env` file in `test-automation/` or export directly:

```bash
export ROBOFLOW_API_KEY="your-roboflow-api-key"
export YOLO_API_PORT=8765   # optional (default: 8765)

```

---

## ▶️ Running the Server

From the root of `test-automation/`:

```bash
cd test-automation/yolo_detection
uvicorn yolo_api:app --host 0.0.0.0 --port 8765

```

Or with Python:

```bash
python -m yolo_detection.api

```

The server will be available at:

```
http://127.0.0.1:8765

```

---

## 📡 API Endpoints

### Health Check

```
GET /health

```

**Response**

```json
{ "ok": true }

```

---

### Predict

```
POST /predict
Content-Type: multipart/form-data

```

**Parameters**

- `user_query` *(form)* → natural language query (e.g. `"tap like button"`)
- `confidence_threshold` *(form, optional, default=0.90)*
- `image` *(file, optional)* → PNG/JPEG screenshot
- `image_base64` *(form, optional)* → base64-encoded image

**Example (cURL)**

```bash
curl -X POST "http://127.0.0.1:8765/predict" \
  -F "user_query=like" \
  -F "confidence_threshold=0.9" \
  -F "image=@screenshot.png"

```

**Success Response**

```json
{
  "ok": true,
  "match": true,
  "x": 512,
  "y": 1080,
  "cls": "like",
  "confidence": 0.95,
  "targets": ["like"],
  "latency_ms": 142
}

```

**Failure Response**

```json
{
  "ok": true,
  "match": false,
  "reason": "no confident match",
  "targets": ["like"],
  "latency_ms": 88
}

```

---

## 🧩 Integration

The main automation system (`test-automation/`) calls this service via HTTP at

`http://127.0.0.1:8765/predict`.

- If YOLO returns a match → automation clicks the detected coordinates.
- If not → fallback strategies are triggered (e.g., Qwen Vision).

---

## 📂 Folder Structure

```
yolo_detection/
├── api.py              # FastAPI app with /predict and /health
├── yolo_integration.py # Python helpers for direct YOLO calls
└── __init__.py

```

---

## 🛠 Development Notes

- Workflows are configured for **TikTok UI elements** (`workspace_name="tiktok-qz4gk"`, `workflow_id="tiktokflutter"`).
- To adapt to other apps:
    1. Update `YOLO_CLASSES` and `INTENT_TO_CLASS` mappings.
    2. Replace `workflow_id` in `api.py` and `yolo_integration.py`.