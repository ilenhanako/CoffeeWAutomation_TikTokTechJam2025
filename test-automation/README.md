# AutoGUI_TecJam2025
# Mobile UI Automation Framework

A comprehensive mobile UI automation framework using Appium and Qwen AI for intelligent test execution on Android applications.

## Overview

This framework combines traditional mobile automation with AI-powered decision making to create robust, self-healing test scenarios. It features:

- **AI-Powered Planning**: Automatic scenario generation from business goals
- **Vision-Guided Actions**: Uses Qwen Vision models to understand UI state
- **Automated UI Interaction**: Automated UI interaction (click, type, swipe, etc.) with fallback to vision-based element detection.
- **Real Time Intelligent Recovery**: Handles interruptions, permissions, and UI changes using AI
- **Multi-Strategy Execution**: XML-first approach with vision model fallback
- **Fuzzy Clicking**: Adaptive coordinate targeting for better reliability
- FastAPI server for remote execution & WebSocket log streaming.

## Features

### Intelligent Action Processing

- **XML-First Strategy**: Prioritizes UI hierarchy analysis over vision
- **Vision Disambiguation**: Uses AI to choose between multiple candidates
- **Smart Coordinate Snapping**: Automatically adjusts coordinates to nearest tappable elements
- **Fuzzy Clicking**: Tries multiple points within bounding boxes

### Robust Error Handling

- **Interruption Detection**: Identifies ads, popups, permission dialogs
- **Recovery Strategies**: Multiple recovery approaches based on context
- **Evaluation Loop**: Continuous assessment of action outcomes
- **Adaptive Retries**: Context-aware retry mechanisms

### AI-Powered Planning

- **Business Goal Decomposition**: Breaks complex goals into actionable steps
- **Multi-Scenario Generation**: Creates alternative execution paths
- **Context-Aware Actions**: Understands app-specific UI patterns

### Knowledge-Graph Planning (RAG)
- **App-Specific Knowledge**: Retrieves UI patterns and flows from a knowledge graph.
- **Context-Aware Planning**: Generates steps that adapt to different apps (e.g., TikTok, Instagram).
- **Self-Healing Tests**: Plans update dynamically when UI changes are detected.


### Developer & Debug Features

- **Real-Time WebSocket Logs**: Stream execution logs & screenshots live.
- **Visual Debugging**: Annotated screenshots highlight action targets and detections.


## Architecture

```
test-automation/
├── ai_agents/           # AI agents: evaluator, action processor, planner, interruption handler
├── config/              # App + API config (Appium, model names, timeouts)
├── core/                # Driver & screenshot managers
├── graph/               # LangGraph workflow (perceive → execute → evaluate → recover → finish)
├── models/              # Execution dataclasses (steps, scenarios, results)
├── tools/               # Mobile interaction wrapper (`MobileUse`)
├── utils/               # Logging, knowledge blocks, XML parsing, YOLO client
├── yolo_detection/      # YOLO pre/post processing (optional, vision-based element detection)
├── api_server.py        # FastAPI server exposing `/run` + `/logs`
├── main.py              # CLI entry point for automation
├── requirements.txt     # Dependencies
└── .env                 # Secrets & config (API keys)
```
## How it Works
1. **Input**: Business goal + scenarios/steps (JSON or CLI).
2. **Execution**:
    - DriverManager launches app with Appium.
    - ActionProcessor tries XML-first selection → falls back to YOLO or Qwen vision.
    - MobileUse executes actions on device.

3. **Evaluation**: AIEvaluator verifies step success with screenshot + static hints.
4. **Recovery**: If failed, InterruptionGuard detects login/ads/permissions and resolves them.
5. **Loop**: Steps repeat until scenario is complete.

## Quick Start

### Prerequisites

- Python 3.9+
- Appium Server running on `http://127.0.0.1:4723`
- Android device/emulator with the target app installed
- Qwen API key (DashScope)
- YOLO Detection Service (FastAPI app under yolo_detection/) — must be running for vision-based element detection

### Installation

1. Clone the repository:
```bash
git clone <https://github.com/ilenhanako/CoffeeWAutomation_TikTokTechJam2025/>
cd test-automation
```

2. Install dependencies:
```bash
python -m venv venv
source venv/bin/activate

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export DASHSCOPE_API_KEY="your-api-key-here"
# Optional: For auth scenarios
export APP_USERNAME="your-username"
export APP_PASSWORD="your-password"
```
Or create a .env file in test-automation/ with at least
```python
DASHSCOPE_API_KEY=your_qwen_api_key
```

### Configuration

Edit `config/settings.py` to match your setup:

```python
# Update device configuration
DEVICE_NAME = "your-device-name"
APP_PACKAGE = "your.app.package"
APP_ACTIVITY = "your.app.MainActivity"
```

Ensure Appiu, server is running locally:
```
appium --address 127.0.0.1 --port 4723

```
### Running Tests

**Start YOLO Detection Service**
```bash
cd test-automation/yolo_detection
uvicorn yolo_api:app --host 0.0.0.0 --port 8765
```


**Local Run (CLI)**

```bash
cd test-automation
python main.py

```
**API Server**
Run with FastAPI + Uvicorn:
```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000
```
**Endpoints**:
- POST /run → start automation
- WS /logs → stream logs & screenshots

## 🔑 Key Components

### Core Components

- **DriverManager (`core/driver_manager.py`)**
    
    Manages the lifecycle of the Appium WebDriver (setup, quit, reset, screen size, page source).
    
- **ScreenshotManager (`core/screenshot_manager.py`)**
    
    Handles screenshot capture, base64 encoding, and visualization (points, click boxes).
    
- **MobileUse (`tools/mobile_tool.py`)**
    
    A LangChain-compatible tool for interacting with the mobile device (click, swipe, type, key events, system buttons).
    

---

### AI Agents

- **ActionProcessor (`ai_agents/action_processor.py`)**
    
    Executes mobile actions with a multi-strategy pipeline:
    
    - XML-first element matching
    - YOLO detection
    - Qwen Vision fallback
        
        Includes fuzzy-clicking, coordinate snapping, and demo mode support.
        
- **QwenClient (`ai_agents/qwen_agent.py`)**
    
    Wrapper for Qwen LLM APIs, supporting text, chat, and vision-based completions.
    
- **AIEvaluator (`ai_agents/evaluator.py`)**
    
    Evaluates whether a step was successful by analyzing screenshots, UI XML, and static UI hints.
    
- **InterruptionGuard (`ai_agents/interruption_handler.py`)**
    
    Detects and handles interruptions such as ads, login dialogs, and permission prompts. Provides safe dismissal or handling actions.
    
- **~~MultiScenarioPlannerAgent (`ai_agents/planning_agent.py`)~~***(deprecated)*

    - Scenario planning is now handled by the **Knowledge Graph RAG** in the```knowledge-graph/```folder.
    
    - Generates multiple possible execution scenarios for a given business goal.
    

---

### Workflow Engine

- **Graph Workflow (`graph/`)**
    
    Built with **LangGraph**:
    
    - `node_perceive` → capture screenshot & XML
    - `node_execute` → perform action
    - `node_evaluate` → AI evaluator checks success
    - `node_recover` → interruption handling & retries
    - `node_finish` → mark step/scenario complete
    
    The workflow loops until a step is successful or retry limits are hit.
    

---

### Models

- **Execution Models (`models/execution_models.py`)**
    
    Dataclasses for steps, scenarios, action results, evaluation results, and processor configs.
    

---

### Utilities

- **Knowledge Block (`utils/knowledge_block.py`)**
    
    Provides static UI hints (coordinates, heuristics) per app (TikTok, Instagram, YouTube, etc.).
    
- **YOLO Client (`utils/yolo_client.py`)**
    
    HTTP client for YOLO-based element detection.
    
- **Logging (`utils/logging.py`)**
    
    Centralized logger with WebSocket broadcasting for real-time log streaming.
    

---

### API Server

- **`api_server.py`**
    
    FastAPI server with:
    
    - `POST /run` → starts automation with provided scenarios
    - `WS /logs` → streams logs and screenshots in real time


## Development

### Adding New Actions

1. Extend `ActionProcessor.VALID_MOBILE_ACTIONS`.
2. Add a mapping in `ActionProcessor.ACTION_MAPPINGS`.
3. Implement the corresponding action logic in the `MobileUse` tool.

### Custom Recovery Strategies

1. Add a new recovery type to `EvaluationResult`.
2. Update recovery handling logic in `graph/nodes.py` (inside `node_recover`).
3. Adjust the AI evaluator prompt (`AIEvaluator.EVAL_SYSTEM_PROMPT`) to support the new recovery type.

## Acknowledgments

- Built with [Appium](http://appium.io/) for mobile automation
- Powered by [Qwen](https://dashscope.aliyun.com/) AI models
- Uses [qwen-agent](https://github.com/QwenLM/Qwen-Agent) framework