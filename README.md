# ☕ Coffee with Automation

### AI-Powered GUI Testing for Real-World Mobile Apps

📺 **View product video & screenshots here:**  
👉 [Devpost Submission](https://devpost.com/software/bombotest)


## 🚨 The Problem
Modern GUI test automation is **fragile**.

- **5–10%** of test code constantly breaks.
- **60%** of failures come from minor UI changes (e.g., a button moves, a popup appears).
- Current tools like **Appium, Espresso, XCUITest, Katalon** depend on **brittle element locators**.
- Even newer AI approaches improve clicking flexibility — but **fail to validate business goals** (like “Did the purchase actually complete?”).

**Result:** Teams waste time fixing scripts instead of testing real functionality.


## 🔎 The Gap
- Tools focus on **element detection**, not **end-to-end business validation**.
- Static locators/scripts break in **dynamic UIs** (Android, iOS, Flutter, React Native, Hybrid).
- No resilience against **popups, ads, login walls, or app crashes**.


## 💡 The Opportunity
We’re building a **universal, vision-driven UI testing agent** that:

✅ Converts **natural language requirements** into test steps.  
✅ Uses **multimodal validation** (XML + vision + semantics).  
✅ **Handles anomalies** gracefully with AI recovery.  
✅ Validates **business outcomes**, not just clicks.  

**Outcome:** Scalable, resilient, business-aware test automation that **evolves as your app evolves**.


## 🚀 What It Does
The **Coffee with Automation** framework transforms business goals into executable test scenarios:

1. **Knowledge Graph + RAG**
    - Turns vague requirements into **precise, validated test flows**.
    - Maps business terms (“update username”) to app components/actions.
2. **Appium + Qwen AI**
    - Executes steps in **two modes**:
        - XML-based (fast, structured)
        - Vision-based (YOLO + Qwen-VL fallback)
    - Handles popups, dialogs, and interruptions automatically.
3. **Streamlit GUI**
    - Natural language input for test scenarios.
    - Run tests + view **logs, annotated screenshots, and results**.

## ✨ Key Differentiators
- **YOLO + Qwen-VL → Icon-Aware Testing**: Detects icons directly (not just OCR text). Perfect for TikTok-style apps.
    
- **Developer-Curated Knowledge Graph**: Devs co-define UI flows → agent tests with **business context**, not guesses.
    
- **XML-First + Vision Fallback**: Reliable structured parsing + resilient visual grounding.
    
- **AI Evaluator + Recovery**: Detects if each step worked. Recovers from dialogs, ads, errors.
    
- **Feature-Oriented Testing**: “Test the Like button” → agent retrieves real user paths from the Knowledge Graph.


<details>
<summary>
<img src="https://img.shields.io/badge/⚡_Why_It_Beats_AppAgentX_&_OmniParser-fff8c5?style=for-the-badge&labelColor=yellow&color=yellow" alt="Why It Beats AppAgentX & OmniParser"/>
</summary>

> **Better Perception, Better Planning, Better Reliability, Better Robustness, Better Relevance**

Other AI-driven test agents (like AppAgentX + OmniParser) showed what’s possible.  
We asked: **“What’s missing for real-world mobile testing?”**  
Here’s how we go beyond:


### 1. 🖼️ Icon Detection with YOLO + Qwen-VL
- **Problem with AppAgentX:** Relies heavily on OCR + text reasoning → fails on icon-only buttons.  
- **Our approach:** YOLO detects icons (even custom/unstyled ones) → Qwen-VL interprets meaning → Appium clicks it.  

✅ Works for **TikTok-style UIs** where icons > text.  
✅ Robust against design changes, dark mode, or missing labels.  

💡 *“We replace fragile OCR perception with icon detection (YOLO) + semantic grounding (Qwen-VL).”*


---

### 2. 🧩 Developer-Guided Knowledge Graph (Instead of Opaque AI Graphs)
- **Problem with AppAgentX:** AppAgentX **guesses the interaction graph dynamically**. → devs can’t guide or verify flows.  
    - It builds paths on the fly based on OCR/LLM interpretation.  
    - The result is opaque, unverified, and often wrong for edge cases.  

- **Our approach:** Developers define/edit the Knowledge Graph → agent uses it to plan.  

✅ Agent reasoning happens within a **verified structure**.  
✅ Easier to adapt for new features.  
✅ Paths reflect **real product logic** instead of one-off guesses.  
✅ Graph doubles as **living documentation** of user flows.  

💡 *“We let devs co-define interaction graphs → agent tests with verified business logic, not blind guesses.”*


---

### 3. 📱 Mobile-Native Focus: XML First, Vision Fallback
- **Problem with AppAgentX:** Treats apps like static screenshots, ignores XML structure. Vision-only parsing is brittle.  
- **Our approach:**  
    - Use **Appium XML trees** when available (fast, reliable).  
    - Fall back to **YOLO + vision** only when XML fails.  

✅ Optimized for **real mobile apps** (Android, Flutter, hybrid).  
✅ Outperforms vision-only systems in production environments.  

💡 *“We prioritize structured XML parsing → fallback to vision only when needed.”*


---

### 4. 🤖 AI Step Evaluator + Interrupt Recovery
- **Problem with AppAgentX:** AppAgentX assumes progress until final step → no mid-step validation, no recovery.  
- **Our approach:**  
    - **Evaluate each step** (did the UI update as expected?).  
    - Detect **interruptions** (dialogs, ads, errors).  
    - Auto-**recover** with dismissal, retries, or reroutes.  

✅ Reduces flaky tests from random popups.  
✅ Makes automation self-healing, not brittle.  

💡 *“We added a step-by-step evaluator that confirms subgoals, spots interruptions, and dynamically re-plans.”*


---

### 5. 🎯 Feature-Driven Testing via Knowledge Graph
- **AppAgentX:** Treats a prompt (“Log in to Gmail”) as one giant guess → builds a flat sequence, treats tasks as monolithic.  
- **Our system:** Retrieve realistic, developer-defined paths from the Knowledge Graph.  

🧪 Example: **“Test the Like Button”**  
- Path 1: Home → Feed → Scroll → Like Button  
- Path 2: Notifications → Post → Like Button  

✅ Covers **multiple real user journeys**, not just shortest paths.  
✅ Captures **business relevance** (not just clicks).  
✅ Automatically adapts when UI or flows change → just update the graph.  

💡 *“We don’t just test clicks. We test features the way real users reach them.”*


---

### 6. 🔁 Structured Execution Loop (LangGraph)
- **AppAgentX:** Linear execution → no mid-step checks, no recovery.  
- **Our system:** Every step follows **Perceive → Execute → Evaluate → Recover → Finish**.  

✅ Ensures **each action is verified** before moving on.  
✅ Guarantees recovery from errors, delays, or UI changes.  
✅ Turns automation into a **deterministic loop**, not a gamble.  

💡 *“We enforce a reliable execution cycle so every action is validated, recoverable, and stable.”*

---


</details>

    

## 🏗️ How We Built It
1. **Knowledge Graph + RAG**
    - Stores UI states, components, and flows.
    - Retrieval ensures contextually relevant tests.
2. **Qwen + Appium Execution**
    - XML-first interaction with AI-powered vision fallback.
    - AI evaluator checks subgoals, detects interruptions, and re-plans.
3. **LangGraph Execution Loop**
    - Every step follows:
        
        **Perceive → Execute → Evaluate → Recover → Finish**.
        
    - Ensures structured, resilient automation.
>
> ### 🧪 Example
>**Prompt:** “Test the Like button feature.”
>
>Our system:
>
>1. Finds realistic paths in the Knowledge Graph:
>    - Home → Feed → Post → Like Button
>    - Notifications → Post → Like Button
>2. Builds execution steps (swipe, tap, verify).
>3. Executes with **Appium + YOLO + Qwen-VL**.
>4. Evaluates: Did the Like action actually succeed?
>

✅ Multiple real-world flows, resilient execution, business outcome validation.


## 🏆 Accomplishments
- Recreated TikTok’s *For You* page in **Lynx (ByteDance’s Flutter-like framework)**.
- Built a **pipeline integrating KG + RAG + Qwen + Appium**.
- AppAgentX proved the concept; **we made it production-ready** and built a **vision-aware, interruption-resilient automation agent** designed for **real-world test automation, production-ready**:
    - Vision + XML hybrid
    - Developer-guided graphs
    - Step evaluators + recovery
    - Feature-aware, business-relevant testing

**Result →** Tests that **scale with the app**, adapt to UI changes, and validate **real user goals**.


## 📚 What We Learned
- **Multimodal validation matters:** XML + vision beats XML-only or vision-only.
- **Context is king:** RAG + KG reduces ambiguity from LLM-only prompts.
- **Real-world readiness:** Recovery strategies are critical for production apps.


## 🌱 What’s Next
Our roadmap pushes even further:

- **Cross-Platform Expansion** → Extend beyond Android to iOS and hybrid frameworks.
- **CI/CD Integration** → Seamless hooks into pipelines for regression coverage.
- **Reinforcement Learning** → Smarter anomaly recovery strategies that improve over time.
- **Collaborative Graph Editing** → Teams co-create and refine the Knowledge Graph as living test documentation.
- **AppAgentX Integration** → Today, AppAgentX tries to guess user flows by constructing graphs dynamically during execution.
> 
> Our vision is to **replace guessing with grounding**: combine YOLO + Qwen for perception, and reason over a **developer-defined Knowledge Graph** for explainable, reproducible testing.
>

## 📂 Repository Structure (See Quick Start Instructions in each folder)
- **knowledge-graph/** → KG + RAG for scenario planning
- **test-automation/** → Appium + Qwen AI execution engine
- **yolo_detection/** → YOLO FastAPI service for icon detection
- **tiktok-flutter-app/** → Demo app for testing (built with Lynx/Flutter)
- **streamlit-gui-app/** → Streamlit front-end for natural language testing


## ☕ Coffee with Automation
Building the future of **business-aware, vision-driven mobile test automation**.