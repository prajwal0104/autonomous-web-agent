"""Application configuration and environment settings."""

from pathlib import Path
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    """Configuration settings for the Autonomous Web Agent."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM Settings
    llm_provider: Literal["openai", "gemini", "ollama", "mock"] = "openai"
    openai_api_key: str = Field(default="", description="OpenAI API Key")
    openai_model: str = "gpt-4o"

    gemini_api_key: str = Field(default="", description="Google Gemini API Key")
    gemini_model: str = "gemini-1.5-pro"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    # Browser Execution Settings
    headless: bool = False
    browser_timeout_ms: int = 30000
    viewport_width: int = 1280
    viewport_height: int = 800
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )

    # Agent Loop Settings
    max_steps: int = 25
    save_screenshots: bool = True
    screenshot_dir: Path = Path("./screenshots")
    verbose_logging: bool = True


settings = AgentSettings()
