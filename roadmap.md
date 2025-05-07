### **Libraries & Tools**

| **Category** | **Tools/Technologies** | **Purpose** |
| --- | --- | --- |
| **Core AI & NLP** | Hugging Face Transformers, LangChain Agents, spaCy, Hugging Face PEFT | Advanced NLP tasks, chaining LLM calls, and efficient model fine-tuning |
| **Speech Processing** | Whisper (STT), Coqui TTS, Porcupine | Convert speech to text, provide natural/emotional text-to-speech, and handle wake-word detection |
| **Vision & OCR** | LayoutLM, Microsoft gitai-text-screen, OpenCV, Tesseract OCR | Screen context awareness, UI parsing, and robust OCR capabilities |
| **Memory & Learning** | LangChain Memory, Redis Vector DB, SQLite/JSON | Persistent conversation history and long-term memory management |
| **Feature-Specific Tools** | Selenium WebDriver, PyAutoGUI, LangChain Metadata API + TinyDB, LangChain StatefulSequence, ChromaDB | UI automation, web scraping, state tracking, and logging/audit features |
| **UI & Interface** | Tauri, React, D3.js, Electron Forge | Building a cross-platform desktop UI with system tray support, smart overlays, and data visualization |
| **Infrastructure & Task Control** | Python 3.12, ONNX Runtime, APScheduler, Celery, FastAPI, LangChain Tools | Background task scheduling, API server integration, and multi-step workflow orchestration |
| **Critical Integrations** | Zapier Webhooks, GitHub Copilot, Codeium, Continue.dev | Automating third-party triggers and aiding in code generation and autocomplete |
| **Deployment & Updates** | Tauri Updater Plugin, Docker, Watchdog, Sentry AI | Packaging the app, containerization, auto-updates, and smart error reporting |

---

### **A.U.R.A. Agents**

| **Agent** | **Responsibilities** | **Key Technologies** |
| --- | --- | --- |
| **Supervisor Agent** | Central control: receives natural language input, delegates tasks to other agents, handles fallback conversation. | LangChain, GPT API, Python |
| **Automation Agent** | Manages system automation: opens/closes apps, file manipulation, workspace setup, and batch task execution. | PyAutoGUI, subprocess, APScheduler |
| **Speech Processing Agent** | Handles voice commands: converts speech-to-text (STT) and text-to-speech (TTS), detects wake-word. | Whisper, Coqui TTS, Porcupine |
| **Web Research Agent** | Conducts web searches, scrapes content, summarizes pages, and extracts UI context with OCR. | Selenium, OpenCV, BeautifulSoup, Tesseract OCR |
| **Communication Agent** | Automates messaging: types text, manages WhatsApp, email drafting, and fills in forms via automation. | Selenium, PyAutoGUI, FastAPI |
| **AI Processing Agent** | Generates natural, witty responses and handles conversational context and summarization using LLMs. | GPT API, LangChain Agents, spaCy |
| **Memory Agent** | Stores and retrieves past interactions and preferences; provides persistent context. | LangChain Memory, Redis, SQLite/JSON |
| **Scheduling Agent** | Manages task scheduling and reminders, executes tasks at specified times, and handles daily planning. | APScheduler, Celery, FastAPI |
| **System Control Agent** | Adjusts system settings (e.g., WiFi, Bluetooth, media control) and monitors system health for smart troubleshooting. | PyAutoGUI, psutil, subprocess |
| **Code Debugging Agent** | Assists with code debugging: identifies issues, suggests fixes, and helps improve code through AI-powered insights. | GPT API integration, Python debugging libraries |


## ✅ **Phase 1: Setup & Environment (Days 1–4)**

1. **Development Environment**
    - Install Python 3.12
    - Install Node.js & npm
    - Install Tauri CLI
    - Set up Git repo
2. **Tool Familiarization**
    - Read intro docs for Python, Tauri, React
    - Understand LangChain basics
    - Skim Together.ai & HuggingFace API usage
3. **Folder Structure**
    
    ```
    bash
    CopyEdit
    /aura
    ├── /frontend (React + Tauri)
    ├── /backend
    │   ├── /agents
    │   ├── /supervisor
    │   ├── /mcp (context mgmt)
    │   ├── /compressor (Phi-2 prompt reducer)
    │   ├── /router (task router)
    │   └── /embeddings (briefings + Weaviate)
    
    ```
    
4. **MCP Setup**
    - Lightweight context tracker
    - Shared access for agents
    - Integration with frontend for sync

---

## ✅ **Phase 2: Core Agents & Compressor (Days 5–12)**

1. **Build Key Agents**
    - Automation: PyAutoGUI, subprocess
    - Speech: Whisper STT, Coqui or pyttsx3
    - Web Research: Requests + BeautifulSoup/Selenium
    - Memory: SQLite or JSON for now
2. **Build Phi-2 Compressor Agent (via Ollama)**
    - Input: raw prompt
    - Output: optimized low-token prompt
    - Add pre-prompt rules for prompt safety/scope
3. **Test + Add MCP Integration**
    - Agents access/update shared context
    - Add fallback command responses via fuzzy NLP

---

## ✅ **Phase 3: Supervisor, Router & Reasoning Models (Days 13–18)**

1. **Supervisor Agent**
    - Central handler of user input
    - Classify request: low-level vs complex
    - Route to proper model (LLaMA 3.3 70B, Scout LLaMA 4 17B, Gemini)
2. **Multi-Tier Reasoning Router**
    - Step 1: Phi-2 compresses prompt
    - Step 2: Supervisor evaluates
        - Low-level? → Scout LLaMA 4 17B
        - Mid-to-heavy? → LLaMA 3.3 70B
        - Deep contextual / high reasoning? → Gemini 1.5 Pro
    - All via Together AI / HuggingFace APIs
3. **Performance Boosters Activated**
    - Fast Fallback Commands (local responses for known phrases)
    - Input classification for tiered routing
    - Background task prioritization (e.g., long prompts wait behind UI tasks)
    - Agent state snapshots (reuse past outputs if prompt is similar)

---

## ✅ **Phase 4: UI, Task Scheduling, and Context Sync (Days 19–24)**

1. **Tauri + React Frontend**
    - Command chat interface
    - Agent log viewer
    - Settings panel (e.g., model selector, compression toggle)
2. **System Tray**
    - Quick-launch interface
    - Lightweight command input
3. **Task Scheduler**
    - APScheduler + UI form for task mgmt
    - Sync with MCP to respect user preferences/context
4. **Frontend-Backend Bridge**
    - Use FastAPI for HTTP communication
    - Real-time state/response sync from MCP
5. **Context Sync + Optimization**
    - MCP serialized context saved/restored
    - Context pruning to avoid clutter
    - Fuzzy NLP fallbacks for command recovery

---

## ✅ **Phase 5: Embeddings, Briefings & Final Touches (Days 25–30)**

1. **Briefing Generator**
    - Summarize past sessions/interactions
    - Feed to LLM → get 5–10 key points
    - Save briefing + vector in Weaviate
2. **Weaviate Setup**
    - Local or free-tier deployment
    - Store interaction embeddings for search/history queries
3. **Final Integration**
    - Full multi-agent pipeline test
    - Prompt compression + routing validation
    - Check API quotas + error handling paths
4. **Optimization & Final Polish**
    - Minimize LLM calls
    - Async everything 🔥
    - Add error messages to guide users (“Try rephrasing”, etc.)
    - Add logs/metrics to track API costs, timings, decisions
5. **Docs & Packaging**
    - README, setup guide
    - CLI args for dev mode vs prod
    - Tauri build → Native app