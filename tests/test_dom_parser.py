"""Comprehensive unit and integration tests for DOMParser and in-browser JS extraction."""

import asyncio
import pytest
from playwright.async_api import async_playwright
from src.browser.dom_parser import DOMElement, DOMParser


def run_async(coro):
    """Helper to run async coroutines in synchronous pytest functions."""
    return asyncio.run(coro)


def test_dom_parser_extracts_interactive_elements():
    """Verify that buttons, inputs, links, textareas, and selects are detected."""
    async def _test():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            html = """
            <!DOCTYPE html>
            <html>
            <body>
                <h1>Welcome to Dashboard</h1>
                <p>This is static text that should NOT be indexed.</p>
                <button id="btn-login">Login</button>
                <input type="text" name="email" placeholder="Enter your email" />
                <textarea name="bio" placeholder="Short bio"></textarea>
                <select name="country">
                    <option value="US">United States</option>
                    <option value="IN">India</option>
                </select>
                <a href="https://example.com/docs">Documentation</a>
                <div role="button" tabindex="0">Custom Role Button</div>
            </body>
            </html>
            """
            await page.set_content(html)
            raw = await page.evaluate(DOMParser.INTERACTIVE_EXTRACTOR_JS)
            elements = [DOMElement(**item) for item in raw]
            await browser.close()
            return elements

    elements = run_async(_test())

    # Should detect: button, input, textarea, select, anchor, and role=button (total 6)
    assert len(elements) == 6

    # Verify tags and text
    tags = [e.tag for e in elements]
    assert "button" in tags
    assert "input" in tags
    assert "textarea" in tags
    assert "select" in tags
    assert "a" in tags
    assert "div" in tags

    # Verify specific element attributes
    btn = next(e for e in elements if e.tag == "button")
    assert btn.text == "Login"
    assert btn.index == 1

    input_el = next(e for e in elements if e.tag == "input")
    assert input_el.name == "email"
    assert input_el.placeholder == "Enter your email"

    link_el = next(e for e in elements if e.tag == "a")
    assert link_el.href == "https://example.com/docs"
    assert link_el.text == "Documentation"


def test_dom_parser_filters_invisible_elements():
    """Verify that display:none, visibility:hidden, and zero-dimension elements are excluded."""
    async def _test():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    .hidden-class { display: none; }
                    .invisible-class { visibility: hidden; }
                    .transparent-class { opacity: 0; }
                </style>
            </head>
            <body>
                <button id="visible-btn">Visible Button</button>
                <button class="hidden-class">Display None Button</button>
                <button class="invisible-class">Visibility Hidden Button</button>
                <button class="transparent-class">Opacity Zero Button</button>
                <div style="display: none;">
                    <a href="/hidden-link">Hidden Link inside Div</a>
                    <input type="text" name="hidden_input" />
                </div>
            </body>
            </html>
            """
            await page.set_content(html)
            raw = await page.evaluate(DOMParser.INTERACTIVE_EXTRACTOR_JS)
            elements = [DOMElement(**item) for item in raw]
            await browser.close()
            return elements

    elements = run_async(_test())

    # Only the visible button should pass the visibility heuristics
    assert len(elements) == 1
    assert elements[0].text == "Visible Button"
    assert elements[0].index == 1


def test_dom_parser_injects_data_agent_idx():
    """Verify that data-agent-idx attributes are stamped onto the live DOM nodes."""
    async def _test():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            html = """
            <!DOCTYPE html>
            <html>
            <body>
                <button id="b1">First</button>
                <button id="b2">Second</button>
                <button id="b3">Third</button>
            </body>
            </html>
            """
            await page.set_content(html)
            # Evaluate JS extractor
            await page.evaluate(DOMParser.INTERACTIVE_EXTRACTOR_JS)

            # Query DOM directly to verify attributes exist on actual nodes
            idx1 = await page.locator("#b1").get_attribute("data-agent-idx")
            idx2 = await page.locator("#b2").get_attribute("data-agent-idx")
            idx3 = await page.locator("#b3").get_attribute("data-agent-idx")

            await browser.close()
            return idx1, idx2, idx3

    i1, i2, i3 = run_async(_test())
    assert i1 == "1"
    assert i2 == "2"
    assert i3 == "3"


def test_dom_parser_empty_page_handling():
    """Verify that a page without interactive elements returns an empty list without errors."""
    async def _test():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            html = "<html><body><h1>Just a title</h1><p>No buttons or links here.</p></body></html>"
            await page.set_content(html)
            raw = await page.evaluate(DOMParser.INTERACTIVE_EXTRACTOR_JS)
            await browser.close()
            return raw

    raw = run_async(_test())
    assert raw == []

    # Verify formatting output
    summary = DOMParser.format_elements_for_llm([])
    assert "No interactive elements detected" in summary


def test_dom_parser_format_elements_for_llm():
    """Verify formatting of DOMElement objects into LLM prompt lines."""
    elements = [
        DOMElement(index=1, tag="button", text="Submit", selector='[data-agent-idx="1"]'),
        DOMElement(index=2, tag="input", element_type="text", placeholder="Search...", selector='[data-agent-idx="2"]'),
    ]
    formatted = DOMParser.format_elements_for_llm(elements)
    assert "--- Interactive Elements on Page ---" in formatted
    assert "[1] <button> \"Submit\"" in formatted
    assert "[2] <input type='text' placeholder='Search...'>" in formatted
