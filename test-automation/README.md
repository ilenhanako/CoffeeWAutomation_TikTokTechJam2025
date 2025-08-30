# AutoGUI_TecJam2025
# Mobile UI Automation Framework

A comprehensive mobile UI automation framework using Appium and Qwen AI for intelligent test execution on Android applications.

## Overview

This framework combines traditional mobile automation with AI-powered decision making to create robust, self-healing test scenarios. It features:

- **AI-Powered Planning**: Automatic scenario generation from business goals
- **Vision-Guided Actions**: Uses Qwen Vision models to understand UI state
- **Intelligent Recovery**: Handles interruptions, permissions, and UI changes
- **Multi-Strategy Execution**: XML-first approach with vision model fallback
- **Fuzzy Clicking**: Adaptive coordinate targeting for better reliability

## Architecture

```
mobile_ui_automation/
├── config/           # Configuration and settings
├── core/            # Core automation components
├── ai_agents/       # AI model integrations
├── automation/      # Action processing and execution
├── utils/           # Utility functions
├── models/          # Data structures and types
├── tools/           # Appium tool integrations
└── main.py         # Entry point
```

## Quick Start

### Prerequisites

- Python 3.8+
- Appium Server running on `http://127.0.0.1:4723`
- Android device/emulator with the target app installed
- Qwen API key (DashScope)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mobile_ui_automation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export DASHSCOPE_API_KEY="your-api-key-here"
# Optional: For auth scenarios
export APP_USERNAME="your-username"
export APP_PASSWORD="your-password"
```

### Configuration

Edit `config/settings.py` to match your setup:

```python
# Update device configuration
DEVICE_NAME = "your-device-name"
APP_PACKAGE = "your.app.package"
APP_ACTIVITY = "your.app.MainActivity"
```

### Running Tests

```bash
python main.py
```

## Key Components

### Core Components

- **DriverManager**: Manages Appium WebDriver lifecycle
- **ScreenshotManager**: Handles image capture and processing
- **ActionProcessor**: Processes and executes mobile actions

### AI Agents

- **QwenClient**: Interfaces with Qwen AI models
- **PlanningAgent**: Generates test scenarios from business goals  
- **AIEvaluator**: Evaluates step outcomes and suggests recovery

### Automation Components

- **StepExecutor**: Orchestrates step execution with guards and evaluation
- **InterruptionHandler**: Detects and handles UI interruptions

## Usage Examples

### Basic Scenario Execution

```python
from main import run_scenario_with_planning

business_goal = "Share a video on home page to a friend only"
run_scenario_with_planning(business_goal, step_executor, complexity="medium")
```

### Custom Action Processing

```python
from automation.action_processor import ActionProcessor
from core.driver_manager import DriverManager

driver_manager = DriverManager()
processor = ActionProcessor(driver_manager, mobile_use, qwen_client)

# Execute with XML-first approach
result = processor.execute_enhanced_xml_first(screenshot_path, "tap the like button")
```

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

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DASHSCOPE_API_KEY` | Qwen API key | Required |
| `APP_USERNAME` | App login username | Optional |
| `APP_PASSWORD` | App login password | Optional |

### Key Settings

Edit `config/settings.py`:

- **Appium Configuration**: Device, app package, server URL
- **AI Model Settings**: Model names, API endpoints
- **Action Parameters**: Retry counts, timeouts, delays
- **Image Processing**: Patch sizes, pixel limits

## Development

### Adding New Actions

1. Extend `ActionProcessor.VALID_MOBILE_ACTIONS`
2. Add mapping in `ActionProcessor.ACTION_MAPPINGS`
3. Implement action logic in `MobileUse` tool

### Custom Recovery Strategies

1. Add recovery type to `EvaluationResult`
2. Implement handler in `StepExecutor._handle_recovery`
3. Update AI evaluator prompts

## Acknowledgments

- Built with [Appium](http://appium.io/) for mobile automation
- Powered by [Qwen](https://dashscope.aliyun.com/) AI models
- Uses [qwen-agent](https://github.com/QwenLM/Qwen-Agent) framework