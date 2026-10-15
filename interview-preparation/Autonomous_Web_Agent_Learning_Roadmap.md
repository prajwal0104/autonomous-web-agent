# Autonomous Web Agent — Structured Learning Roadmap

## Overview & Progression Strategy

This roadmap is designed for a developer with foundational Python knowledge who wants to progress toward mastery of **Autonomous AI Agents**, **Playwright Browser Automation**, and **Modern LLM Architectures**.

The curriculum is structured into **5 Progressive Stages**, each with concrete prerequisites, hands-on repository exercises, and verification criteria.

---

## Stage 1: Repository Anatomy & Python Fundamentals (Days 1–3)

### Core Objective
Understand how the project boots up, how environment variables are parsed, and how Python classes interact.

### Topics to Master
1. **Virtual Environments & Packages**:
   - Why `.venv` is isolated (`pyproject.toml`, `requirements.txt`).
   - How `run.ps1` and `run.bat` automatically detect and initialize `.venv`.
2. **Pydantic v2 & Configuration**:
   - `pydantic-settings` in [`src/config.py`](file:///C:/Users/Prajwal/.gemini/antigravity/scratch/autonomous-web-agent/src/config.py#L9-L38).
   - Type annotations (`Literal`, `Field`, `Path`, `bool`, `int`).
3. **Command-Line Interfaces (CLI)**:
   - How `typer` parses CLI flags in [`src/main.py`](file:///C:/Users/Prajwal/.gemini/antigravity/scratch/autonomous-web-agent/src/main.py#L25-L55).
   - How Windows UTF-8 stdout encoding is handled.

### Hands-on Exercises
- [ ] **Exercise 1.1**: Run `.\run.ps1 -Goal "Test"` and trace which lines in `src/main.py` execute.
- [ ] **Exercise 1.2**: Open `src/config.py` and add a new setting `default_scroll_amount: int = 600`. Verify it loads with `python -c "from src.config import settings; print(settings.default_scroll_amount)"`.

### Exit Criteria
You can comfortably explain the relationship between `run.ps1` ➔ `src/main.py` ➔ `src/config.py` in under 60 seconds.

---

## Stage 2: Browser Automation & DOM Perception (Days 4–7)

### Core Objective
Master how Playwright controls Chromium and how the in-browser JavaScript extractor turns messy HTML into clean, token-efficient interactive element trees.

### Topics to Master
1. **Playwright Async Lifecycle**:
   - `async_playwright().start()` in [`src/browser/controller.py`](file:///C:/Users/Prajwal/.gemini/antigravity/scratch/autonomous-web-agent/src/browser/controller.py#L22-L45).
   - Anti-detection flags (`--disable-blink-features=AutomationControlled`).
   - Viewport emulation and user-agent customization.
2. **In-Browser JavaScript Injection**:
   - How `DOMParser.INTERACTIVE_EXTRACTOR_JS` runs inside Chromium's execution context.
   - Dynamic tagging with `data-agent-idx`.
   - Filtering invisible nodes (`getBoundingClientRect`, `window.getComputedStyle`).
3. **Deterministic Selectors vs Fragile XPaths**:
   - Why targeting `[data-agent-idx="3"]` avoids brittle hierarchy errors.

### Hands-on Exercises
- [ ] **Exercise 2.1**: Run unit tests with `pytest tests/test_agent.py -v` and inspect `test_dom_element_summary`.
- [ ] **Exercise 2.2**: Launch the agent with `--goal "Search Hacker News"` without headless mode and observe how `click_element` and `type_text` interact with input fields.

### Exit Criteria
You can draw the DOM extraction pipeline on a whiteboard and explain why raw HTML is never sent to the LLM.

---

## Stage 3: Cognitive Planning & Multi-Provider Architecture (Days 8–11)

### Core Objective
Understand how the agent reasons, generates structured JSON plans, and safely falls back when APIs are unreachable.

### Topics to Master
1. **Prompt Engineering & System Constraints**:
   - `Planner.SYSTEM_PROMPT` in [`src/agent/planner.py`](file:///C:/Users/Prajwal/.gemini/antigravity/scratch/autonomous-web-agent/src/agent/planner.py#L30-L60).
   - Why enforcing JSON schema via `response_format={"type": "json_object"}` prevents parsing failures.
2. **Action Contract & Action Enums**:
   - `AgentActionType`: `NAVIGATE`, `CLICK`, `TYPE`, `SCROLL`, `EXTRACT`, `WAIT`, `FINISH`.
   - Pydantic model validation on LLM output (`ActionPlan.model_validate_json`).
3. **Resilient Fallback Engine**:
   - How `Planner.decide_next_action()` detects placeholder keys (`your_openai_api_key_here`) and gracefully switches to `_fallback_heuristic_planner`.
   - Why try/catch wrappers around HTTP calls prevent unhandled crashes.

### Hands-on Exercises
- [ ] **Exercise 3.1**: Inspect `Planner._fallback_heuristic_planner()` and trace what action is emitted on Step 1 vs Step 2.
- [ ] **Exercise 3.2**: Add a new action type `REFRESH = "refresh"` to `AgentActionType` and handle it in `src/agent/browser_agent.py`.

### Exit Criteria
You can clearly explain the difference between a prompt-based chatbot and a structured-output agent loop to an interviewer.

---

## Stage 4: Memory, Execution Loops, & Error Recovery (Days 12–15)

### Core Objective
Understand how state is tracked across steps, how observations guide subsequent decisions, and how infinite loops are prevented.

### Topics to Master
1. **The Core Agent Loop**:
   - The `for step_idx in range(1, steps_limit + 1)` lifecycle in [`src/agent/browser_agent.py`](file:///C:/Users/Prajwal/.gemini/antigravity/scratch/autonomous-web-agent/src/agent/browser_agent.py#L52-L140).
2. **State & Observation Ledger**:
   - `AgentMemory` and `StepRecord` in [`src/agent/memory.py`](file:///C:/Users/Prajwal/.gemini/antigravity/scratch/autonomous-web-agent/src/agent/memory.py#L7-L42).
   - Sliding-window history (`format_history_for_llm(max_recent=5)`).
3. **Safety & Termination Guarantees**:
   - `FINISH` action stopping condition.
   - Max steps bound (`max_steps=20`) to prevent runaway API spend and browser hangs.
   - `finally: await self.browser.close()` ensuring no orphaned Chromium processes remain in memory.

### Hands-on Exercises
- [ ] **Exercise 4.1**: Examine `screenshots/` after a run and match each image to its corresponding `StepRecord`.
- [ ] **Exercise 4.2**: Modify `max_steps` to 3 and observe the exact termination response when the agent reaches the limit.

### Exit Criteria
You can articulate how the agent detects failure (e.g. an element not found) and communicates that observation back to the planner for the next step.

---

## Stage 5: Advanced Scenarios & Technical Interview Readiness (Days 16–20)

### Core Objective
Prepare to ace technical screening, system design, and coding rounds for AI Engineering and Software Development positions.

### Topics to Master
1. **Security & Prompt Injection**:
   - Indirect prompt injection via malicious web page text.
   - Restricting browser permissions and preventing arbitrary JavaScript execution.
2. **Trade-offs & Architecture Decisions**:
   - Playwright vs Selenium vs Puppeteer.
   - In-browser JS parser vs Vision-based VLM (e.g. OmniParser, GPT-4V).
   - Token efficiency vs full multimodal perception.
3. **Mock Interviews & Live Code Explanation**:
   - Answering the 25 Priority Interview Questions.
   - Delivering the 30-second, 60-second, and 2-minute elevator pitches.

### Hands-on Exercises
- [ ] **Exercise 5.1**: Complete the 5 Mock Interview Scenarios in Chapter 16 of the Handbook.
- [ ] **Exercise 5.2**: Conduct a timed 2-minute explanation of the architecture using the Mermaid sequence diagram.

### Exit Criteria
You can answer any Level 1 to Level 5 question from Chapter 14 with genuine technical depth and direct citations to the repository code.
