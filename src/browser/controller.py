"""Playwright browser controller and automation driver."""

import asyncio
from pathlib import Path
from typing import List, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from ..config import settings
from .dom_parser import DOMElement, DOMParser


class BrowserController:
    """Controls browser session, pages, and web interactions."""

    def __init__(self, headless: Optional[bool] = None):
        self.headless = settings.headless if headless is None else headless
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self.current_elements: List[DOMElement] = []

    async def start(self) -> None:
        """Launch the browser and prepare the main page."""
        if self._playwright is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-infobars",
                ],
            )
            self._context = await self._browser.new_context(
                viewport={
                    "width": settings.viewport_width,
                    "height": settings.viewport_height,
                },
                user_agent=settings.user_agent,
            )
            self._page = await self._context.new_page()
            self._page.set_default_timeout(settings.browser_timeout_ms)

    async def close(self) -> None:
        """Gracefully close browser resources."""
        if self._page and not self._page.is_closed():
            await self._page.close()
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None

    @property
    def page(self) -> Page:
        if self._page is None:
            raise RuntimeError("Browser has not been started. Call 'await start()' first.")
        return self._page

    async def navigate(self, url: str) -> str:
        """Navigate to a URL and wait for DOM load."""
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        await self.page.goto(url, wait_until="domcontentloaded")
        try:
            # Allow dynamic page scripts a brief window to settle without hanging on long-polling connections
            await self.page.wait_for_load_state("networkidle", timeout=2500)
        except Exception:
            pass
        return self.page.url

    async def refresh_elements(self) -> List[DOMElement]:
        """Extract all interactive elements currently in the DOM."""
        raw_elements = await self.page.evaluate(DOMParser.INTERACTIVE_EXTRACTOR_JS)
        self.current_elements = [DOMElement(**item) for item in raw_elements]
        return self.current_elements

    async def click_element(self, index: int) -> None:
        """Click an interactive element by its assigned index."""
        selector = f'[data-agent-idx="{index}"]'
        await self.page.wait_for_selector(selector, state="visible", timeout=7000)
        await self.page.click(selector)
        try:
            await self.page.wait_for_load_state("domcontentloaded", timeout=2000)
        except Exception:
            pass

    async def type_text(self, index: int, text: str, press_enter: bool = False) -> None:
        """Type text into an input or textarea element by index."""
        selector = f'[data-agent-idx="{index}"]'
        await self.page.wait_for_selector(selector, state="visible", timeout=7000)
        await self.page.fill(selector, "")
        await self.page.type(selector, text, delay=50)
        if press_enter:
            await self.page.press(selector, "Enter")
            try:
                await self.page.wait_for_load_state("domcontentloaded", timeout=2000)
            except Exception:
                pass

    async def scroll(self, direction: str = "down", amount: int = 500) -> None:
        """Scroll the page in the specified direction."""
        delta = amount if direction.lower() == "down" else -amount
        await self.page.evaluate(f"window.scrollBy(0, {delta})")
        await asyncio.sleep(0.1)

    async def take_screenshot(self, filepath: Path) -> Path:
        """Capture screenshot of the current page viewport."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        await self.page.screenshot(path=str(filepath), full_page=False)
        return filepath

    async def get_page_text(self) -> str:
        """Extract clean text content from the current page body."""
        return await self.page.evaluate("() => document.body ? document.body.innerText : ''")

    async def get_page_html(self) -> str:
        """Extract full HTML content from the current page."""
        return await self.page.content()
