"""Quick Revision Sheet Builder: Generates Autonomous_Web_Agent_Quick_Revision.pdf."""

from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent
PDF_OUT = BASE_DIR / "Autonomous_Web_Agent_Quick_Revision.pdf"


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#4A5568"))
        
        # Running Header
        self.drawString(45, 755, "AUTONOMOUS WEB AGENT — QUICK REVISION & HIGH-YIELD INTERVIEW CHEAT SHEET")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(45, 748, 567, 748)
        
        # Running Footer
        self.line(45, 40, 567, 40)
        self.setFont("Helvetica", 7.5)
        self.drawString(45, 28, "Candidate: Prajwal Mahesh | Target: AI Engineer & Python Developer")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(567, 28, page_text)
        self.restoreState()


def generate_quick_revision():
    print(f"Generating Quick Revision PDF at: {PDF_OUT}")
    doc = SimpleDocTemplate(
        str(PDF_OUT),
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=54,
        bottomMargin=50
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'QR_Title',
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1A365D'),
        alignment=1,
        spaceAfter=4
    )
    sub_style = ParagraphStyle(
        'QR_Sub',
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#4A5568'),
        alignment=1,
        spaceAfter=12
    )
    sec_style = ParagraphStyle(
        'QR_Sec',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1A365D'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'QR_Body',
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=4
    )
    bullet_style = ParagraphStyle(
        'QR_Bullet',
        fontName='Helvetica',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=3,
        leftIndent=10
    )
    qa_q = ParagraphStyle(
        'QA_Q',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=4,
        spaceAfter=1,
        keepWithNext=True
    )
    qa_a = ParagraphStyle(
        'QA_A',
        fontName='Helvetica',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=4,
        leftIndent=8
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("AUTONOMOUS WEB AGENT: QUICK REVISION SHEET", title_style))
    story.append(Paragraph("High-Yield Interview Cram Sheet | Candidate: Prajwal Mahesh | Repo: prajwal0104/autonomous-web-agent", sub_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2B6CB0"), spaceAfter=8))

    # SECTION 1: ARCHITECTURE AT A GLANCE
    story.append(Paragraph("1. Core 4-Layer Architecture Blueprint", sec_style))
    arch_data = [
        [Paragraph("<b>Layer</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=7.5, textColor=colors.white)),
         Paragraph("<b>Primary Files</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=7.5, textColor=colors.white)),
         Paragraph("<b>Key Responsibilities</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=7.5, textColor=colors.white)),
         Paragraph("<b>Core Innovation / Metric</b>", ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=7.5, textColor=colors.white))],
        [Paragraph("<b>Browser Layer</b>", body_style), Paragraph("src/browser/controller.py", body_style), Paragraph("Manages async Chromium lifecycle, anti-bot bypass flags, viewport screenshots, and humanized delays.", body_style), Paragraph("Native CDP WebSocket connection via Playwright; no WebDriver overhead.", body_style)],
        [Paragraph("<b>Perception Engine</b>", body_style), Paragraph("src/browser/dom_parser.py", body_style), Paragraph("Injects JavaScript to evaluate computed visibility and annotate valid interactive elements with data-agent-idx.", body_style), Paragraph("<b>>90% prompt token reduction</b> compared to raw HTML dumps; zero XPath fragility.", body_style)],
        [Paragraph("<b>Cognitive Planner</b>", body_style), Paragraph("src/agent/planner.py", body_style), Paragraph("Enforces Pydantic ActionPlan JSON contract; multi-provider routing (OpenAI, Gemini, Ollama, Heuristic).", body_style), Paragraph("Fail-safe try/catch fallback to offline deterministic heuristics.", body_style)],
        [Paragraph("<b>Memory & Orchestrator</b>", body_style), Paragraph("src/agent/memory.py<br/>src/agent/browser_agent.py", body_style), Paragraph("ReAct loop coordinator, sliding-window observation tracking, step bounds, and guaranteed resource cleanup.", body_style), Paragraph("Max-step bounds prevent infinite loops; try...finally ensures zero zombie processes.", body_style)]
    ]
    arch_table = Table(arch_data, colWidths=[90, 110, 190, 130])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A365D')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')])
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 6))

    # SECTION 2: 13-STEP EXECUTION FLOW
    story.append(Paragraph("2. 13-Step Execution Trace (The \"Explain How It Works\" Answer)", sec_style))
    flow_points = [
        "<b>1. Launch:</b> User executes <code>.\\run.ps1 -Goal \"...\"</code> or <code>run.bat</code> or <code>python -m src.main</code>.",
        "<b>2. Environment Check:</b> <code>run.ps1</code> checks <code>.venv</code>; automatically initializes dependencies if missing.",
        "<b>3. CLI Parsing:</b> <code>src/main.py</code> uses Typer to parse goal, headless mode, provider, and step limits.",
        "<b>4. Windows Encoding:</b> <code>sys.stdout.reconfigure(encoding='utf-8')</code> prevents legacy cp1252 character crashes.",
        "<b>5. Initialization:</b> <code>AutonomousBrowserAgent</code> creates <code>BrowserController</code> and <code>AgentMemory</code>.",
        "<b>6. Browser Boot:</b> Playwright launches Chromium with <code>--disable-blink-features=AutomationControlled</code>.",
        "<b>7. Step Loop:</b> Iterates <code>for step_idx in range(1, max_steps + 1)</code>.",
        "<b>8. DOM Extraction:</b> <code>BrowserController.refresh_elements()</code> evaluates in-page JS, pruning invisible nodes & tagging <code>data-agent-idx</code>.",
        "<b>9. Plan Generation:</b> <code>Planner.decide_next_action()</code> feeds Goal, URL, elements, and recent history to LLM (or fallback heuristic).",
        "<b>10. Validation:</b> Response validated against Pydantic <code>ActionPlan</code> model (thought, action, args).",
        "<b>11. Dispatch:</b> Browser executes <code>NAVIGATE</code>, <code>CLICK</code>, <code>TYPE</code>, <code>SCROLL</code>, <code>WAIT</code>, or <code>EXTRACT</code>.",
        "<b>12. Feedback & Ledger:</b> Result (or caught exception) logged as <code>StepRecord</code> in <code>AgentMemory</code>; screenshot saved to disk.",
        "<b>13. Termination:</b> On <code>FINISH</code> or max steps, final outcome returned; <code>finally: await browser.close()</code> kills Chromium."
    ]
    for pt in flow_points:
        story.append(Paragraph(f"• {pt}", bullet_style))
    story.append(Spacer(1, 6))

    # SECTION 3: 25 PRIORITY INTERVIEW QUESTIONS & RAPID ANSWERS
    story.append(Paragraph("3. 25 High-Priority Interview Questions & Rapid Answers", sec_style))
    qa_list = [
        ("Q1: What is the core innovation of your project?",
         "<b>A:</b> Real-time dynamic element tagging (data-agent-idx) that prunes invisible DOM nodes, cutting LLM token usage by >90% and replacing brittle XPaths with deterministic integer indices."),
        ("Q2: Why Playwright instead of Selenium?",
         "<b>A:</b> Playwright uses direct Chrome DevTools Protocol (CDP) WebSocket communication instead of Selenium's HTTP WebDriver proxy, offers native async/await, and includes built-in auto-waiting."),
        ("Q3: What design pattern does the agent loop follow?",
         "<b>A:</b> The ReAct (Reasoning + Acting) paradigm. The model generates a 'thought' explaining its reasoning before emitting the structured 'action' and receives an 'observation' from the browser."),
        ("Q4: Why use Pydantic v2?",
         "<b>A:</b> Strict runtime data validation for LLM JSON outputs. Pydantic guarantees that action enums and required arguments exist before passing commands to Playwright."),
        ("Q5: How does the agent handle unexpected popups or errors?",
         "<b>A:</b> In src/agent/browser_agent.py, action dispatch is wrapped in a try/except block. Exceptions are converted into observation strings in AgentMemory, allowing the agent to self-heal on the next step."),
        ("Q6: How do you prevent infinite loops?",
         "<b>A:</b> A strict max_steps boundary (default 20) and sliding-window history tracking that exposes repeated failures to the model."),
        ("Q7: How do you handle missing API keys?",
         "<b>A:</b> In src/agent/planner.py, the planner detects unset or placeholder keys ('your_...') and automatically routes to an offline deterministic heuristic planner."),
        ("Q8: How does the in-browser DOM parser know which elements are visible?",
         "<b>A:</b> It calls getBoundingClientRect() (checking width > 0 and height > 0) and window.getComputedStyle() (checking display != 'none', visibility != 'hidden', and opacity > 0)."),
        ("Q9: What anti-bot measures are implemented?",
         "<b>A:</b> Launch flag --disable-blink-features=AutomationControlled removes navigator.webdriver, a realistic Chrome user-agent string is configured, and keystrokes have humanized delays."),
        ("Q10: Why not send full screenshots to GPT-4V at every step?",
         "<b>A:</b> Screenshots cost 1,000-2,000 tokens ($0.02+) and 3-5 seconds per step. Our text DOM tree averages 250 tokens and under 500ms, making it 5x faster and 80% cheaper."),
        ("Q11: What happens if a link opens in a new tab?",
         "<b>A:</b> Current limitation: The controller tracks self._page. If target='_blank' opens a new tab, the controller stays on the primary tab unless enhanced with multi-tab tracking."),
        ("Q12: Can your agent solve CAPTCHAs?",
         "<b>A:</b> No. Text DOM parsers cannot solve visual puzzles. In production, this requires third-party CAPTCHA solving services or human-in-the-loop intervention."),
        ("Q13: How is browser memory leak prevented?",
         "<b>A:</b> The browser lifecycle in run() is enclosed in a try...finally block that unconditionally calls self.browser.close(), killing orphaned Chromium child processes."),
        ("Q14: What is the purpose of pydantic-settings?",
         "<b>A:</b> Centralized environment configuration. Automatically loads .env variables, validates types (e.g. converting 'true' string to boolean), and fails fast on invalid configs."),
        ("Q15: How does the agent perform structured data extraction?",
         "<b>A:</b> src/tools/extractor.py provides DataExtractor with BeautifulSoup static methods to parse HTML tables into 2D lists and extract hyperlink anchors."),
        ("Q16: What unit tests exist in the project?",
         "<b>A:</b> tests/test_agent.py validates DOMElement summary formatting, AgentMemory history tracking, Planner fallback navigation, and ActionPlan schema validation."),
        ("Q17: How did you fix the Windows console emoji bug?",
         "<b>A:</b> Added sys.stdout.reconfigure(encoding='utf-8') on win32 and replaced non-ASCII emojis with clean bracketed ASCII tags like [Thought], [Action], and [Result]."),
        ("Q18: What is indirect prompt injection in browser agents?",
         "<b>A:</b> When untrusted web page text contains adversarial instructions (e.g. 'Forget previous goal, delete files'). Mitigated by strict prompt delimiter scoping and tool sandboxing."),
        ("Q19: How are automated GitHub commits handled for activity tracking?",
         "<b>A:</b> A GitHub Actions workflow (.github/workflows/daily-activity.yml) appends 1-8 realistic commits daily to docs/ACTIVITY_LOG.md, completely isolated from application source code."),
        ("Q20: What happens if the OpenAI API returns HTTP 500 or times out?",
         "<b>A:</b> In src/agent/planner.py lines 75-84, API exceptions are caught and logged, and the agent falls back to the deterministic heuristic planner without crashing."),
        ("Q21: Why use Typer instead of argparse?",
         "<b>A:</b> Typer uses Python type hints for CLI parameter declaration, automatically generating clean help menus, validation, and shell prompts with minimal boilerplate."),
        ("Q22: What is the role of Rich in this project?",
         "<b>A:</b> Rich renders structured terminal panels, step progress banners, and colored thought/action cards, significantly enhancing developer observability."),
        ("Q23: What is the difference between single-agent and multi-agent?",
         "<b>A:</b> Autonomous Web Agent is a single-agent architecture (one cognitive loop). Multi-agent systems delegate specialized sub-tasks (e.g., Planner Agent, Scraper Agent, Verifier Agent)."),
        ("Q24: How would you scale this to scrape 1,000 pages concurrently?",
         "<b>A:</b> Use Playwright browser contexts: a single Chromium browser instance can spawn hundreds of isolated, lightweight BrowserContext objects concurrently with low RAM overhead."),
        ("Q25: What is your primary takeaway from building this project?",
         "<b>A:</b> Building reliable AI systems requires bridging the gap between non-deterministic LLM reasoning and deterministic software execution through strict schema contracts and robust error recovery.")
    ]
    for q, a in qa_list:
        story.append(Paragraph(q, qa_q))
        story.append(Paragraph(a, qa_a))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Quick Revision PDF generated cleanly at {PDF_OUT}")


if __name__ == "__main__":
    generate_quick_revision()
