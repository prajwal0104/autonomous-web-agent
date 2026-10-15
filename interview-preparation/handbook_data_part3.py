"""Handbook Content Part 3: Chapters 13 to 17."""

CHAPTER_13 = {
    "title": "Chapter 13: Limitations & Future Architectural Roadmap",
    "sections": [
        {
            "heading": "13.1 Confirmed Current Limitations",
            "content": (
                "Being honest about project limitations demonstrates high technical maturity during interviews:\n\n"
                "1. Single Tab Only: The current `BrowserController` operates on a single active page (`self._page`). If a link opens in `target=\"_blank\"` (new tab), the agent does not automatically switch tabs.\n"
                "2. CAPTCHA Handling: Complex Cloudflare Turnstile or reCAPTCHA puzzles cannot be solved by the text DOM parser.\n"
                "3. Canvas and SVG Visuals: Graphical charts rendered purely inside HTML5 `<canvas>` elements lack DOM child nodes, so the DOM parser cannot extract internal labels.\n"
                "4. Pure Stateless Restarts: Once a run finishes, the session cookie and cache are discarded unless a persistent browser context directory is configured."
            )
        },
        {
            "heading": "13.2 Future Engineering Roadmap",
            "content": (
                "Realistic architectural enhancements to discuss in interviews:\n"
                "1. Hybrid Multimodal Vision: Combine the lightweight DOM element tree with visual bounding-box overlays (e.g. Set-of-Marks) using Gemini 1.5 Pro or GPT-4o Vision for canvas and map elements.\n"
                "2. Persistent User Context: Introduce Playwright `launch_persistent_context()` to store session cookies, allowing the agent to perform workflows requiring persistent logins.\n"
                "3. Multi-Tab Context Manager: Track open pages via `context.pages` and expose a `SWITCH_TAB` action primitive in `AgentActionType`."
            )
        }
    ]
}

CHAPTER_14 = {
    "title": "Chapter 14: Comprehensive Interview Question Bank",
    "sections": [
        {
            "heading": "14.1 Level 1: HR & Behavioral Questions",
            "content": (
                "Q1: Tell me about yourself and your Autonomous Web Agent project.\n"
                "- What the interviewer assesses: Communication clarity, passion for AI, and ability to summarize technical concepts.\n"
                "- Beginner Explanation: Introduce who you are and why you built the project.\n"
                "- Natural Answer: \"I am a software developer with a strong focus on AI and automation. I developed Autonomous Web Agent to explore how LLMs can interact with live web applications. Traditional automation breaks when websites change layouts, so I built an agent that perceives web elements in real time and plans its own actions.\"\n"
                "- Deeper Technical Answer: Highlight the 4-layer architecture: Playwright browser control, in-browser JavaScript DOM indexing, Pydantic JSON action schemas, and memory-backed error recovery.\n"
                "- Common Trap: Claiming you developed the underlying LLM from scratch. Be clear that you built the agentic application, perception engine, and orchestration system."
            )
        },
        {
            "heading": "14.2 Level 2: Python & Code Implementation Questions",
            "content": (
                "Q2: How does your project use asynchronous Python (`async`/`await`) and why is it necessary?\n"
                "- What the interviewer assesses: Understanding of Python's concurrency model and non-blocking I/O.\n"
                "- Technical Answer: \"In `src/browser/controller.py`, all Playwright operations like `navigate()`, `click_element()`, and `refresh_elements()` are asynchronous coroutines. Web pages take hundreds of milliseconds to load, and LLM APIs take seconds to respond. Using `async`/`await` prevents the single-threaded Python event loop from freezing, allowing background tasks and clean timeout handling.\"\n"
                "- Code Evidence: `src/browser/controller.py` lines 48-60 and `src/main.py` line 54 (`asyncio.run(agent.run())`).\n\n"
                "Q3: Why did you use Pydantic models instead of plain Python dictionaries?\n"
                "- Technical Answer: \"In `src/agent/planner.py`, `ActionPlan` inherits from Pydantic's `BaseModel`. LLMs can produce malformed output. Pydantic automatically validates types, enforces that the action is a valid `AgentActionType` enum, and provides helpful errors if required arguments are missing, ensuring runtime type safety before passing commands to Playwright.\""
            )
        },
        {
            "heading": "14.3 Level 3: Architecture & System Design Questions",
            "content": (
                "Q4: How do you prevent the LLM from hallucinating invalid selectors or clicking elements that don't exist?\n"
                "- What the interviewer assesses: Selector reliability and grounding.\n"
                "- Technical Answer: \"We do not let the LLM generate arbitrary CSS or XPath selectors. Instead, our in-browser JavaScript parser tags all active elements with `data-agent-idx=\"N\"` and gives the LLM only the integer index (e.g. `[1]`, `[2]`). When the LLM decides to click, it only provides the integer index. In `click_element(index)`, Playwright queries `[data-agent-idx=\"{index}\"]`. This completely decouples the LLM from fragile DOM hierarchies.\"\n\n"
                "Q5: How does your agent handle infinite loops or repeated errors?\n"
                "- Technical Answer: \"First, `max_steps` (default 20) acts as a strict upper bound. Second, `AgentMemory` records the success status and observation of every step. When an action fails, the observation (e.g. 'Element not interactable') is injected into the next prompt, alerting the LLM to try an alternative approach.\""
            )
        },
        {
            "heading": "14.4 Level 4: Advanced AI & Agentic Reasoning Questions",
            "content": (
                "Q6: What is the difference between ReAct and your agent's execution loop?\n"
                "- Technical Answer: \"Our architecture is an implementation of the ReAct (Reasoning + Acting) paradigm. At each turn, the model generates a `thought` (reasoning trace) followed by an `action` with arguments. The browser executes the action and returns an `observation`. This explicit thought generation before action selection forces the model to deliberate on page state before emitting tool calls.\"\n\n"
                "Q7: How would you protect this agent against indirect prompt injection?\n"
                "- Technical Answer: \"Indirect prompt injection occurs when a target web page contains text designed to hijack the model's instructions. Safeguards include: 1) Strict delimiter isolation between user instructions and web text; 2) Limiting tool permissions so the agent cannot execute arbitrary bash commands or file deletions; 3) Requiring human confirmation for sensitive operations like financial transactions.\""
            )
        },
        {
            "heading": "14.5 Level 5: Expert Cross-Examination Questions",
            "content": (
                "Q8: Why did you choose a text-based DOM accessibility tree instead of pure vision with screenshots?\n"
                "- Technical Answer: \"It represents a deliberate engineering trade-off between latency, token cost, and accuracy. A high-resolution screenshot processed by GPT-4V costs ~1,000 to 2,000 tokens per step and takes 3-5 seconds. Our pruned interactive DOM tree averages only 200-400 tokens and processes in under 500ms. For standard form filling and text navigation, DOM indexing is 5x faster and 80% cheaper. However, for a production system, a hybrid approach (DOM first, vision fallback for canvas/visual elements) is optimal.\""
            )
        }
    ]
}

CHAPTER_15 = {
    "title": "Chapter 15: Practical Hands-On Exercises",
    "sections": [
        {
            "heading": "15.1 Exercise 1: Tracing Execution via CLI",
            "content": (
                "Task: Run the agent in visible browser mode with max steps set to 3.\n"
                "Command:\n"
                "`python -m src.main --goal \"Navigate to python.org and inspect the downloads page\" --max-steps 3`\n"
                "Questions to Answer:\n"
                "1. What URL did the agent start on?\n"
                "2. How many interactive elements were extracted on Step 1?\n"
                "3. Which element index did the agent choose to click?"
            )
        },
        {
            "heading": "15.2 Exercise 2: Implementing a New Action Primitive",
            "content": (
                "Task: Add a new action type `BACK = \"back\"` that tells the browser to navigate backwards in history.\n"
                "Steps:\n"
                "1. In `src/agent/planner.py`, add `BACK = \"back\"` to `AgentActionType`.\n"
                "2. In `src/browser/controller.py`, add `async def go_back(self): await self.page.go_back()`.\n"
                "3. In `src/agent/browser_agent.py`, add the handler in the action dispatch loop:\n"
                "   `elif plan.action == AgentActionType.BACK: await self.browser.go_back()`.\n"
                "4. Run `pytest` to ensure existing tests pass."
            )
        }
    ]
}

CHAPTER_16 = {
    "title": "Chapter 16: Mock Interview Practice Scenarios",
    "sections": [
        {
            "heading": "16.1 Scenario 1: The Junior Python Developer Round",
            "content": (
                "Interviewer: \"I see you used Pydantic Settings in your project. How does it work and why not just use `os.environ`?\"\n"
                "Candidate Model Answer: \"While `os.environ` returns raw strings and raises KeyError if a variable is missing, `pydantic-settings` provides automatic type conversion, validation, and default values. For example, in `src/config.py`, `headless: bool = False` automatically parses string 'true' or 'false' from `.env` into a real Python boolean. It also reads `.env` files automatically and guarantees that our application fails immediately with clear error messages at startup if required configurations are missing.\""
            )
        },
        {
            "heading": "16.2 Scenario 2: The Senior AI Architect Round",
            "content": (
                "Interviewer: \"Your agent relies on an LLM to choose actions. What happens when the model hallucinates an invalid action or produces invalid JSON?\"\n"
                "Candidate Model Answer: \"We employ a defense-in-depth approach. First, we use API-level constrained decoding (`response_format={'type': 'json_object'}` in OpenAI and `response_mime_type='application/json'` in Gemini) to force JSON output. Second, we parse the response through `ActionPlan.model_validate_json()`. If validation fails, or if the API call throws an error, our planner catches the exception and falls back to our deterministic heuristic planner. Furthermore, in the dispatch loop, if an action fails to execute, we catch the exception and log it into the memory ledger rather than letting the application crash, enabling the agent to self-heal.\""
            )
        }
    ]
}

CHAPTER_17 = {
    "title": "Chapter 17: Final Revision & Interview Readiness Checklist",
    "sections": [
        {
            "heading": "17.1 One-Page Project Summary Cheat Sheet",
            "content": (
                "* Project: Autonomous Web Agent (Public standalone repository: prajwal0104/autonomous-web-agent)\n"
                "* Core Architecture: 4 layers — Browser (Playwright), Perception (In-browser DOM tagger), Cognition (Pydantic Action Planner), Memory (StepRecord Ledger).\n"
                "* Key Innovation: Real-time dynamic element tagging (`data-agent-idx`) cutting token usage by 90% and eliminating fragile XPaths.\n"
                "* Multi-Provider: OpenAI GPT-4o, Google Gemini 1.5, Ollama, and offline Heuristic fallback.\n"
                "* Test Coverage: 4 unit test suites passing (`pytest tests/`)."
            )
        },
        {
            "heading": "17.2 The 10 Commandments of Your Interview",
            "content": (
                "1. Always cite exact file names (`controller.py`, `dom_parser.py`, `planner.py`).\n"
                "2. Emphasize why raw HTML is too expensive for LLMs.\n"
                "3. Explain the difference between an agent loop and a chatbot.\n"
                "4. Be honest about current limitations (single tab, no CAPTCHA solver).\n"
                "5. Highlight the `try...finally` browser cleanup ensuring zero zombie processes.\n"
                "6. Mention the Windows UTF-8 stdout encoding fix.\n"
                "7. Describe how `AgentMemory` enables self-healing on failure.\n"
                "8. Highlight that Pydantic v2 was chosen for speed and strict type enforcement.\n"
                "9. Discuss the offline heuristic planner that allows CI testing without API bills.\n"
                "10. Speak with confidence, calm pacing, and a problem-solving mindset."
            )
        }
    ]
}
