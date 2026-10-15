"""DOM parser and interactive element extraction."""

from typing import List, Optional
from pydantic import BaseModel, Field


class DOMElement(BaseModel):
    """Represents an interactive DOM element indexed for agent actions."""

    index: int = Field(description="Unique index of the interactive element")
    tag: str = Field(description="HTML tag name, e.g., 'button', 'input', 'a'")
    element_type: str = Field(default="", description="Input type if tag is input, e.g., 'text', 'password'")
    text: str = Field(default="", description="Visible text or inner content")
    aria_label: str = Field(default="", description="Accessibility aria-label if defined")
    placeholder: str = Field(default="", description="Input placeholder text")
    name: str = Field(default="", description="Element name attribute")
    href: Optional[str] = Field(default=None, description="Destination link if element is an anchor")
    selector: str = Field(description="CSS or XPath selector to target this element")
    is_visible: bool = Field(default=True, description="Whether the element is currently visible in viewport")

    def summary(self) -> str:
        """Render a concise, human and LLM-readable summary string."""
        desc = f"[{self.index}] <{self.tag}"
        if self.element_type:
            desc += f" type='{self.element_type}'"
        if self.name:
            desc += f" name='{self.name}'"
        if self.placeholder:
            desc += f" placeholder='{self.placeholder}'"
        if self.aria_label:
            desc += f" aria-label='{self.aria_label}'"
        desc += ">"
        if self.text:
            cleaned_text = " ".join(self.text.strip().split())
            if len(cleaned_text) > 40:
                cleaned_text = cleaned_text[:37] + "..."
            desc += f" \"{cleaned_text}\""
        if self.href:
            desc += f" -> {self.href}"
        return desc


class DOMParser:
    """Parses raw page content and extracts interactive candidate elements."""

    # JavaScript snippet injected into page to extract visible interactive DOM nodes
    INTERACTIVE_EXTRACTOR_JS = """
    () => {
        const interactiveSelectors = [
            'button',
            'a[href]',
            'input',
            'textarea',
            'select',
            '[role="button"]',
            '[role="link"]',
            '[role="checkbox"]',
            '[role="menuitem"]',
            '[tabindex]:not([tabindex="-1"])'
        ];
        
        const nodes = Array.from(document.querySelectorAll(interactiveSelectors.join(',')));
        const results = [];
        let idx = 1;
        
        for (const el of nodes) {
            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);
            
            // Filter out non-visible elements
            if (
                rect.width === 0 || 
                rect.height === 0 || 
                style.display === 'none' || 
                style.visibility === 'hidden' || 
                style.opacity === '0'
            ) {
                continue;
            }
            
            // Mark element with an agent attribute for rock-solid deterministic selector retrieval
            el.setAttribute('data-agent-idx', idx.toString());
            
            results.push({
                index: idx,
                tag: el.tagName.toLowerCase(),
                element_type: el.getAttribute('type') || '',
                text: (el.innerText || el.textContent || '').trim().slice(0, 80),
                aria_label: el.getAttribute('aria-label') || '',
                placeholder: el.getAttribute('placeholder') || '',
                name: el.getAttribute('name') || '',
                href: el.getAttribute('href') || null,
                selector: `[data-agent-idx="${idx}"]`,
                is_visible: true
            });
            idx++;
        }
        return results;
    }
    """

    @classmethod
    def format_elements_for_llm(cls, elements: List[DOMElement]) -> str:
        """Format list of interactive elements into LLM prompt text."""
        if not elements:
            return "No interactive elements detected on the current page."
        lines = ["--- Interactive Elements on Page ---"]
        for el in elements:
            lines.append(el.summary())
        return "\n".join(lines)
