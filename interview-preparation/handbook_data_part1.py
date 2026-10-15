"""Handbook Content Part 1: Chapters 1 to 6."""

CHAPTER_1 = {
    "title": "Chapter 1: Project Overview & Executive Summary",
    "sections": [
        {
            "heading": "1.1 What is Autonomous Web Agent?",
            "content": (
                "Autonomous Web Agent is an open-source, goal-driven AI agent that autonomously navigates the live web, "
                "interacts with dynamic web applications, and extracts structured data using natural language objectives. "
                "Instead of requiring hardcoded instructions or fragile XPath selectors, the agent inspects the rendered Document Object Model (DOM), "
                "extracts all visible interactive elements, formulates sequential action plans using a Large Language Model (LLM), "
                "and executes actions through a headless or visible Chromium browser powered by Playwright.\n\n"
                "The core application is located at `C:\\Users\\Prajwal\\.gemini\\antigravity\\scratch\\autonomous-web-agent` "
                "and pushed to GitHub under `prajwal0104/autonomous-web-agent` as an original, standalone repository (`isFork: false`)."
            )
        },
        {
            "heading": "1.2 The Problem It Solves",
            "content": (
                "Traditional web automation tools (like basic Selenium scripts or BeautifulSoup scrapers) suffer from three critical flaws:\n"
                "1. Fragility: If a website redesigns its layout, renames CSS classes, or changes button IDs, hardcoded automation scripts crash immediately.\n"
                "2. Dynamic Asynchrony: Modern web applications use Single Page Application (SPA) frameworks (React, Vue, Angular) that render content asynchronously. Static scrapers download initial HTML before client-side scripts run, resulting in empty or broken pages.\n"
                "3. Inability to Reason: If a website shows an unexpected cookie consent modal, a login prompt, or a paginated table, traditional scripts cannot adapt or decide what to do next.\n\n"
                "Autonomous Web Agent solves this by introducing an agentic closed-loop perception, planning, and execution cycle that evaluates the live DOM state at every step and recovers dynamically from unexpected layout changes."
            )
        },
        {
            "heading": "1.3 Comparison with Alternative Paradigms",
            "table": {
                "headers": ["Feature / Paradigm", "Traditional Scraper (BeautifulSoup)", "Scripted Automation (Selenium)", "Autonomous Web Agent"],
                "rows": [
                    ["Execution Method", "Static HTTP GET requests", "Hardcoded XPath / CSS scripts", "Goal-driven LLM cognitive loop"],
                    ["JavaScript Execution", "None (HTML only)", "Yes (Browser engine)", "Yes (Full Playwright Chromium context)"],
                    ["Adaptability to Layout Changes", "Zero (breaks on markup change)", "Low (relies on fixed selectors)", "High (evaluates semantic DOM in real time)"],
                    ["Error Recovery", "Fails on HTTP 4xx/5xx or missing tag", "Fails on NoSuchElementException", "Reflects on previous step failure & backtracks"],
                    ["Token Consumption", "Zero (no AI used)", "Zero (no AI used)", "Highly optimized (pruned interactive DOM tree)"],
                    ["Human Intervention", "High (requires rewriting code)", "High (requires updating selectors)", "Minimal (natural language goal specification)"]
                ]
            }
        },
        {
            "heading": "1.4 Natural Interview Elevator Pitches",
            "content": (
                "Use these tailored pitches depending on the interview context:\n\n"
                "--- 30-Second Elevator Pitch (HR & Recruiter Screen) ---\n"
                "\"I built Autonomous Web Agent, a Python-based autonomous AI application that allows language models to perceive and control live web browsers. "
                "Unlike traditional scrapers that break whenever a website updates its layout, my agent dynamically inspects the rendered web page, "
                "indexes interactive buttons and forms in real time, and uses an LLM reasoning loop to navigate, search, and extract data autonomously.\"\n\n"
                "--- 60-Second Explanation (Software Engineer & Technical Interviewer) ---\n"
                "\"My project is called Autonomous Web Agent. It bridges the gap between probabilistic LLM reasoning and deterministic web execution. "
                "The core engineering challenge in AI browser agents is token efficiency and selector reliability: raw web pages have tens of thousands of lines of HTML. "
                "I engineered an in-browser JavaScript parser that extracts only visible interactive elements, tagging each with a deterministic index attribute. "
                "This pruned tree is passed to a structured Pydantic planner that emits validated JSON action plans—such as clicks, text entry, and scrolling. "
                "The agent runs on Playwright Chromium, maintains an execution ledger for error recovery, and includes fallback heuristics so it can operate reliably even without active cloud APIs.\"\n\n"
                "--- 2-Minute Technical Deep Dive (AI Engineer & System Architect) ---\n"
                "\"Autonomous Web Agent is an end-to-end autonomous agentic system designed around an observation-thought-action-reflection loop. "
                "The architecture consists of four distinct layers:\n"
                "First, the Browser Layer: Built on Playwright async API, managing browser context, humanized delays, anti-bot flags, and viewport screenshot capture.\n"
                "Second, the Perception Engine: Instead of feeding raw HTML or expensive multimodal screenshots for every single step, we inject a custom DOM parser directly into the page execution context. It computes live bounding boxes and visibility styles, filters out invisible clutter, and dynamically binds indexed data attributes to valid interactive nodes. This reduces LLM context token usage by over 90%.\n"
                "Third, the Cognitive Planner: We enforce a strict JSON contract via Pydantic models. The planner supports OpenAI GPT-4o, Google Gemini 1.5, local Ollama models, and an offline deterministic heuristic fallback for offline testing.\n"
                "Fourth, the Memory and Reflection Ledger: Every interaction step is recorded into an append-only state history tracking URL, action type, reasoning, success status, and textual observations. When an action fails, the observation is fed into the next prompt, allowing the agent to detect the failure and formulate an alternative approach rather than looping indefinitely.\""
            )
        }
    ]
}

CHAPTER_2 = {
    "title": "Chapter 2: Technology Stack & Architectural Dependencies",
    "sections": [
        {
            "heading": "2.1 Technology Stack Matrix",
            "content": "Every dependency in `requirements.txt` and `pyproject.toml` was selected to solve a concrete engineering problem:",
            "table": {
                "headers": ["Technology / Package", "Version", "Role in Project", "Code Evidence", "Trade-offs & Alternatives"],
                "rows": [
                    ["Python", ">=3.10 (3.13.3 tested)", "Core programming language", "pyproject.toml:9", "Python provides the premier ecosystem for AI/LLM tooling compared to Go or Node.js."],
                    ["Playwright", ">=1.49.0", "Async browser automation engine", "src/browser/controller.py:7", "Superior to Selenium due to native async architecture, auto-waiting, and fast CDP protocol."],
                    ["Pydantic", ">=2.9.0", "Data validation & JSON action schemas", "src/agent/planner.py:8", "Enforces strict type safety and structured JSON outputs from LLMs; much faster in v2 (written in Rust)."],
                    ["Pydantic-Settings", ">=2.5.0", "Environment configuration management", "src/config.py:6", "Automatically validates .env files; prevents silent runtime failures from missing settings."],
                    ["HTTPX", ">=0.27.0", "Async HTTP client for LLM APIs", "src/agent/planner.py:7", "Supports HTTP/2 and modern Python async/await; alternative to synchronous 'requests'."],
                    ["Rich", ">=13.9.0", "Terminal styling, panels & status logs", "src/agent/browser_agent.py:8", "Produces beautiful formatted console cards and logs; requires careful UTF-8 handling on Windows."],
                    ["Typer", ">=0.12.5", "CLI argument parser & entrypoint", "src/main.py:5", "Type-driven CLI builder on top of Click; reduces boilerplate argument parsing."],
                    ["BeautifulSoup4", ">=4.12.3", "HTML parsing & structured extraction", "src/tools/extractor.py:4", "Lightweight table and link parsing; avoids heavy browser DOM queries for simple HTML."],
                    ["Pytest", ">=8.3.0", "Unit and regression test framework", "tests/test_agent.py:3", "Standard test runner for Python; clean assert statements and fixture support."]
                ]
            }
        },
        {
            "heading": "2.2 Deep Dive: Playwright vs Selenium",
            "content": (
                "Why Playwright was chosen over Selenium:\n"
                "1. Protocol Efficiency: Selenium historically relied on the WebDriver HTTP protocol, where each command sends an HTTP request to an intermediary driver executable. Playwright communicates directly with Chromium via the Chrome DevTools Protocol (CDP) over a single WebSocket connection, resulting in lower latency.\n"
                "2. Native Auto-Waiting: In Selenium, developers frequently suffer from `StaleElementReferenceException` or `ElementNotInteractableException` unless manual explicit waits are configured. Playwright automatically waits for elements to become visible, enabled, and stable before issuing clicks or keystrokes.\n"
                "3. In-Browser JavaScript Evaluation: Playwright's `page.evaluate()` executes JavaScript directly inside the browser's V8 engine context with seamless bidirectional JSON serialization, which powers our DOMParser."
            )
        }
    ]
}

CHAPTER_3 = {
    "title": "Chapter 3: Python Fundamentals to Project-Level Understanding",
    "sections": [
        {
            "heading": "3.1 Python Concepts for Beginners",
            "content": (
                "Here are the core Python concepts used in this project, explained in plain English:\n\n"
                "1. Asynchronous Programming (`async` / `await`):\n"
                "- Simple English: Doing other tasks while waiting for slow operations (like loading web pages or waiting for API responses) instead of freezing the entire program.\n"
                "- Analogy: A chef who puts bread in the toaster and chops onions while waiting, rather than staring at the toaster until the bread pops up.\n"
                "- Code Evidence in Project: In `src/browser/controller.py` line 48:\n"
                "  `async def navigate(self, url: str) -> str:`\n"
                "  `    await self.page.goto(url, wait_until='domcontentloaded')`\n\n"
                "2. Type Annotations & Pydantic Models:\n"
                "- Simple English: Stating in advance what type of data (string, integer, boolean) a variable or function expects, preventing errors.\n"
                "- Code Evidence in Project: In `src/agent/planner.py` line 20:\n"
                "  `class ActionPlan(BaseModel):`\n"
                "  `    thought: str = Field(description='Reasoning about current state')`\n"
                "  `    action: AgentActionType = Field(description='Action to perform')`\n"
                "  `    args: Dict[str, Any] = Field(default_factory=dict)`\n\n"
                "3. Enums (`Enum`):\n"
                "- Simple English: A fixed list of valid allowed choices with readable names, preventing typo bugs.\n"
                "- Code Evidence in Project: In `src/agent/planner.py` line 12:\n"
                "  `class AgentActionType(str, Enum):`\n"
                "  `    NAVIGATE = 'navigate'`\n"
                "  `    CLICK = 'click'`\n"
                "  `    TYPE = 'type'`\n"
                "  `    SCROLL = 'scroll'`\n"
                "  `    EXTRACT = 'extract'`\n"
                "  `    WAIT = 'wait'`\n"
                "  `    FINISH = 'finish'`"
            )
        },
        {
            "heading": "3.2 Error Handling & Try-Except-Finally",
            "content": (
                "In `src/agent/browser_agent.py` lines 49-145, the entire browser execution is wrapped in a `try...finally` block:\n"
                "```python\n"
                "try:\n"
                "    await self.browser.start()\n"
                "    # ... run execution loop ...\n"
                "finally:\n"
                "    await self.browser.close()\n"
                "```\n"
                "- Why `finally` is critical: If an unhandled exception or crash happens in the middle of a web browsing session, the `finally` block is guaranteed to run. This closes the Chromium browser process so that orphaned background browser processes do not eat up the user's computer RAM."
            )
        }
    ]
}

CHAPTER_4 = {
    "title": "Chapter 4: LLM Fundamentals & Prompt Engineering",
    "sections": [
        {
            "heading": "4.1 How LLMs Work in Agentic Applications",
            "content": (
                "Large Language Models (LLMs) are probabilistic next-token predictors trained on vast corpora of text and code. "
                "In Autonomous Web Agent, the LLM is not used as a conversational chatbot; instead, it is used as a **Cognitive Policy Engine**.\n\n"
                "Key Concepts:\n"
                "1. Tokens: The fundamental text chunks processed by models (~4 characters per token). Long HTML pages consume tens of thousands of tokens, costing money and increasing latency.\n"
                "2. Context Window: The maximum number of tokens a model can accept in a single request. By pruning non-interactive HTML, we ensure the agent fits comfortably within context limits.\n"
                "3. Structured Outputs: Instructing the model to respond exclusively in machine-readable JSON matching our `ActionPlan` schema rather than conversational prose."
            )
        },
        {
            "heading": "4.2 Prompt Engineering in the Project",
            "content": (
                "In `src/agent/planner.py` lines 30-58, `Planner.SYSTEM_PROMPT` enforces strict operational constraints:\n"
                "1. Role Specification: \"You are an autonomous AI web browsing agent.\"\n"
                "2. Context Contract: Explains the 4 inputs provided at every step (Goal, Current URL, History, Interactive Elements).\n"
                "3. Schema Enforcement: Outlines the exact JSON structure for `thought`, `action`, and `args`.\n"
                "4. Constraint Directive: \"Do not include markdown code fence formatting outside the JSON.\""
            )
        }
    ]
}

CHAPTER_5 = {
    "title": "Chapter 5: Agentic AI Fundamentals & Architecture",
    "sections": [
        {
            "heading": "5.1 Chatbots vs Autonomous Agents",
            "content": (
                "Understanding the distinction is one of the most common interview questions:\n\n"
                "- Conventional Chatbot: Single-turn or multi-turn conversational interface. User inputs a prompt -> Model outputs text -> Process stops. The chatbot has no direct access to tools or external state.\n\n"
                "- Autonomous Agent: Operates in a continuous **Perception-Thought-Action-Observation Loop**:\n"
                "  1. Perceives the environment (web page DOM).\n"
                "  2. Formulates a plan towards an overarching objective.\n"
                "  3. Executes an action on external tools (clicks a button, types text).\n"
                "  4. Observes the resulting feedback (new URL, changed page state, or error message).\n"
                "  5. Reflects and adapts the next action until the termination condition (`FINISH`) is met."
            )
        },
        {
            "heading": "5.2 State Management & Stopping Conditions",
            "content": (
                "In `src/agent/memory.py` lines 15-42, `AgentMemory` maintains the state ledger:\n"
                "- Each step adds a `StepRecord` containing action, thought, observation, and success status.\n"
                "- Sliding Window: `format_history_for_llm(max_recent=5)` passes only the 5 most recent steps to the prompt to balance context awareness with token efficiency.\n"
                "- Stopping Conditions:\n"
                "  1. Explicit Goal Completion: When the planner emits `AgentActionType.FINISH`.\n"
                "  2. Max Steps Boundary: In `src/agent/browser_agent.py` line 52, `max_steps` (default 20) stops runaway execution, preventing infinite loops or unexpected billing charges."
            )
        }
    ]
}

CHAPTER_6 = {
    "title": "Chapter 6: Browser Automation & DOM Perception",
    "sections": [
        {
            "heading": "6.1 In-Browser DOM Parsing Architecture",
            "content": (
                "The core engineering innovation in this project is `DOMParser.INTERACTIVE_EXTRACTOR_JS` in `src/browser/dom_parser.py` lines 38-80.\n\n"
                "Step-by-Step Mechanism:\n"
                "1. Target Selectors: Queries buttons, anchor links with href, text inputs, textareas, selects, and role attributes (`button`, `link`, `checkbox`).\n"
                "2. Visibility Filtering: Evaluates `getBoundingClientRect()` and `window.getComputedStyle()`. If width/height is 0, or `display == 'none'`, or `visibility == 'hidden'`, or `opacity == '0'`, the element is pruned.\n"
                "3. Deterministic Annotation: Injects a custom attribute `data-agent-idx=\"1\"`, `data-agent-idx=\"2\"` into each valid element on the live DOM.\n"
                "4. Token-Efficient Formatting: Generates concise summaries like `[1] <input type='text' placeholder='Search'>` for the LLM prompt, reducing token consumption by 90% compared to raw HTML."
            )
        },
        {
            "heading": "6.2 Browser Reliability & Anti-Bot Protection",
            "content": (
                "In `src/browser/controller.py` lines 28-35, the Chromium instance is launched with custom flags:\n"
                "- `--disable-blink-features=AutomationControlled`: Removes the `navigator.webdriver` flag that websites check to block automated bots.\n"
                "- Real User-Agent: Configured with a realistic Windows Chrome user-agent string.\n"
                "- Humanized Typing: In `type_text()`, a 50ms character delay simulates human typing cadence, preventing anti-bot triggers on high-frequency form submissions."
            )
        }
    ]
}
