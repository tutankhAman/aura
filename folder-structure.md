/aura
├── frontend/              # React + Tauri UI
├── backend/               # Python core: agents, supervisor, routing, compression
├── scripts/               # Automation scripts (setup, install, update)
├── .env                   # API keys, model paths, etc.
├── tauri.conf.json        # Tauri config
├── requirements.txt       # Python dependencies
├── package.json           # Frontend deps
└── README.md


/frontend
├── src/
│   ├── components/         # Chat UI, logs, modals
│   ├── pages/              # Home, Settings, Logs
│   ├── context/            # React context for MCP sync
│   ├── utils/              # Frontend helpers (formatting, etc.)
│   ├── hooks/              # Custom React hooks
│   └── main.tsx            # Entry point
├── public/
│   └── icons/              # App icons and tray icons
└── index.html


/backend
├── agents/                 # Specialized local agents (modular)
│   ├── speech/             # STT, TTS (Whisper, Coqui, pyttsx3)
│   ├── system/             # App launcher, volume, workspace
│   ├── web/                # Web scraping/research agents
│   ├── automation/         # PyAutoGUI scripts, reminders
│   └── memory.py           # Local JSON/SQLite memory manager

├── supervisor/             # Decision-maker + prompt routing
│   ├── router.py           # LLM selection logic
│   ├── input_classifier.py # Fast NLP-based routing
│   ├── command_map.json    # Fast fallback phrases
│   └── supervisor.py       # Core logic

├── mcp/                    # Memory & Context Pruner (MCP)
│   ├── mcp.py              # Shared context memory
│   ├── serializer.py       # Save/load snapshots
│   └── pruner.py           # Trim irrelevant history

├── compressor/             # Prompt compression pipeline
│   ├── phi2_compressor.py  # Run local Phi-2
│   └── cache.py            # Cache compressed prompts

├── embeddings/             # Briefings + Weaviate vector store
│   ├── briefing_gen.py     # Summarize + embed
│   ├── vector_search.py    # Search embeddings
│   └── store.py            # Interface to Weaviate

├── models/                 # API wrappers for cloud models
│   ├── gemini.py
│   ├── together_llama3.py
│   ├── scout_llama4.py
│   └── fallback.py         # Error-tolerant fallback runner

├── utils/                  # Generic backend utilities
│   ├── logger.py
│   ├── config.py
│   └── scheduler.py        # APScheduler wrapper

└── main.py                 # Entrypoint (backend API server)


/scripts
├── install.sh              # Install deps
├── start_dev.sh            # Start dev server (frontend + backend)
├── update_models.sh        # Pull LLM updates from Ollama
└── reset_context.sh        # Clears MCP + embeddings + cache


.env                       # Keys for Gemini, Together.ai, Weaviate
README.md                  # Setup, features, credits
tauri.conf.json            # Tauri builder config
requirements.txt           # Python deps
package.json               # React/Tauri deps
