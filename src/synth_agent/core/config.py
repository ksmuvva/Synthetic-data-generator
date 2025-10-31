"""
Configuration management for Synthetic Data Generator.

Supports configuration via:
1. CLI flags (highest priority)
2. Environment variables
3. Config file (YAML)
4. Default values (lowest priority)
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigurationError(Exception):
    """Configuration error exception."""
    pass


class LLMConfig(BaseSettings):
    """LLM configuration settings."""

    provider: str = Field(default="openai", description="LLM provider: openai, anthropic")
    model: str = Field(default="gpt-4", description="Model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=1, le=100000)
    timeout: int = Field(default=30, ge=1, le=300)
    max_retries: int = Field(default=4, ge=0, le=10)
    retry_delays: List[int] = Field(default=[2, 4, 8, 16])
    enable_cache: bool = Field(default=True)
    cache_ttl: int = Field(default=3600)

    model_config = SettingsConfigDict(env_prefix="SYNTH_AGENT_LLM_", extra="ignore")


class GenerationConfig(BaseSettings):
    """Data generation configuration settings."""

    default_rows: int = Field(default=1000, ge=1, le=10000000)
    max_rows: int = Field(default=1000000, ge=1, le=10000000)
    quality_level: str = Field(default="high", pattern="^(low|medium|high)$")
    null_percentage: float = Field(default=0.05, ge=0.0, le=1.0)
    duplicate_percentage: float = Field(default=0.0, ge=0.0, le=1.0)
    outlier_percentage: float = Field(default=0.02, ge=0.0, le=1.0)
    use_semantic_analysis: bool = Field(default=True)
    infer_relationships: bool = Field(default=True)
    maintain_referential_integrity: bool = Field(default=True)
    batch_size: int = Field(default=10000, ge=100, le=1000000)
    parallel_generation: bool = Field(default=True)
    max_workers: int = Field(default=4, ge=1, le=32)

    model_config = SettingsConfigDict(env_prefix="SYNTH_AGENT_GENERATION_", extra="ignore")


class StorageConfig(BaseSettings):
    """Storage configuration settings."""

    default_output_dir: str = Field(default="./output")
    create_subdirs: bool = Field(default=True)
    timestamp_files: bool = Field(default=True)
    session_dir: str = Field(default="~/.synth-agent")
    session_db: str = Field(default="sessions.db")
    max_sessions: int = Field(default=100, ge=1, le=1000)
    enable_chunking: bool = Field(default=True)
    chunk_size_mb: int = Field(default=100, ge=1, le=1000)

    model_config = SettingsConfigDict(env_prefix="SYNTH_AGENT_STORAGE_", extra="ignore")


class ConversationConfig(BaseSettings):
    """Conversation configuration settings."""

    max_context_turns: int = Field(default=20, ge=1, le=100)
    context_window: int = Field(default=8000, ge=1000, le=100000)
    validate_before_generation: bool = Field(default=True)
    require_confirmation: bool = Field(default=True)
    show_progress: bool = Field(default=True)
    verbose_mode: bool = Field(default=False)

    model_config = SettingsConfigDict(env_prefix="SYNTH_AGENT_CONVERSATION_", extra="ignore")


class AnalysisConfig(BaseSettings):
    """Analysis configuration settings."""

    min_sample_size: int = Field(default=10, ge=1, le=10000)
    confidence_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    detect_distributions: bool = Field(default=True)
    infer_constraints: bool = Field(default=True)
    detect_relationships: bool = Field(default=True)
    ambiguity_threshold: float = Field(default=0.6, ge=0.0, le=1.0)
    max_clarification_questions: int = Field(default=5, ge=1, le=20)

    model_config = SettingsConfigDict(env_prefix="SYNTH_AGENT_ANALYSIS_", extra="ignore")


class LoggingConfig(BaseSettings):
    """Logging configuration settings."""

    level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    format: str = Field(default="json", pattern="^(json|text)$")
    console_output: bool = Field(default=True)
    file_output: bool = Field(default=True)
    log_dir: str = Field(default="~/.synth-agent/logs")
    max_file_size_mb: int = Field(default=10, ge=1, le=100)
    max_files: int = Field(default=5, ge=1, le=50)
    log_llm_interactions: bool = Field(default=True)
    log_api_calls: bool = Field(default=False)
    mask_sensitive_data: bool = Field(default=True)

    model_config = SettingsConfigDict(env_prefix="SYNTH_AGENT_LOGGING_", extra="ignore")


class SecurityConfig(BaseSettings):
    """Security configuration settings."""

    send_pattern_data_to_llm: bool = Field(default=False)
    anonymize_before_llm: bool = Field(default=True)
    local_only_mode: bool = Field(default=False)
    validate_file_paths: bool = Field(default=True)
    max_file_size_mb: int = Field(default=500, ge=1, le=10000)
    allowed_file_extensions: List[str] = Field(
        default=[".csv", ".json", ".xlsx", ".xml", ".parquet", ".txt"]
    )
    require_api_key: bool = Field(default=True)

    model_config = SettingsConfigDict(env_prefix="SYNTH_AGENT_SECURITY_", extra="ignore")


class UIConfig(BaseSettings):
    """UI configuration settings."""

    use_colors: bool = Field(default=True)
    show_spinner: bool = Field(default=True)
    show_progress_bar: bool = Field(default=True)
    max_table_rows: int = Field(default=20, ge=5, le=100)
    max_column_width: int = Field(default=50, ge=10, le=200)
    show_hints: bool = Field(default=True)
    show_examples: bool = Field(default=True)

    model_config = SettingsConfigDict(env_prefix="SYNTH_AGENT_UI_", extra="ignore")


class Config:
    """Main configuration class."""

    def __init__(self, config_path: Optional[Path] = None, **overrides: Any) -> None:
        """
        Initialize configuration with optional config file and overrides.

        Args:
            config_path: Path to YAML configuration file
            **overrides: Configuration overrides (highest priority)
        """
        self._config_data: Dict[str, Any] = {}

        # Load from config file if provided
        if config_path and config_path.exists():
            self._load_from_file(config_path)
        else:
            # Try default config location
            default_config = Path(__file__).parent.parent.parent.parent / "config" / "default_config.yaml"
            if default_config.exists():
                self._load_from_file(default_config)

        # Apply overrides (CLI flags)
        self._config_data.update(overrides)

        # Initialize subsections with filtered config data
        self.llm = LLMConfig(**self._filter_extra_keys(self._config_data.get("llm", {}), LLMConfig))
        self.generation = GenerationConfig(**self._filter_extra_keys(self._config_data.get("generation", {}), GenerationConfig))
        self.storage = StorageConfig(**self._filter_extra_keys(self._config_data.get("storage", {}), StorageConfig))
        self.conversation = ConversationConfig(**self._filter_extra_keys(self._config_data.get("conversation", {}), ConversationConfig))
        self.analysis = AnalysisConfig(**self._filter_extra_keys(self._config_data.get("analysis", {}), AnalysisConfig))
        self.logging = LoggingConfig(**self._filter_extra_keys(self._config_data.get("logging", {}), LoggingConfig))
        self.security = SecurityConfig(**self._filter_extra_keys(self._config_data.get("security", {}), SecurityConfig))
        self.ui = UIConfig(**self._filter_extra_keys(self._config_data.get("ui", {}), UIConfig))

        # Expand paths
        self._expand_paths()

    def _load_from_file(self, config_path: Path) -> None:
        """Load configuration from YAML file."""
        with open(config_path, "r") as f:
            self._config_data = yaml.safe_load(f) or {}

    def _filter_extra_keys(self, config_dict: Dict[str, Any], config_class: type) -> Dict[str, Any]:
        """Filter out extra keys that aren't part of the Pydantic model."""
        if not config_dict:
            return {}

        # Get the field names from the Pydantic model
        model_fields = config_class.model_fields.keys()

        # Filter to only include keys that are in the model
        filtered = {k: v for k, v in config_dict.items() if k in model_fields}

        return filtered

    def _expand_paths(self) -> None:
        """Expand user paths (~) in configuration."""
        self.storage.session_dir = os.path.expanduser(self.storage.session_dir)
        self.logging.log_dir = os.path.expanduser(self.logging.log_dir)

        # Ensure directories exist
        Path(self.storage.session_dir).mkdir(parents=True, exist_ok=True)
        if self.logging.file_output:
            Path(self.logging.log_dir).mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "llm": self.llm.model_dump(),
            "generation": self.generation.model_dump(),
            "storage": self.storage.model_dump(),
            "conversation": self.conversation.model_dump(),
            "analysis": self.analysis.model_dump(),
            "logging": self.logging.model_dump(),
            "security": self.security.model_dump(),
            "ui": self.ui.model_dump(),
        }

    def __repr__(self) -> str:
        return f"Config({self.to_dict()})"


# API Keys (from environment)
class APIKeys(BaseSettings):
    """API keys configuration."""

    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    aws_access_key_id: Optional[str] = Field(default=None, alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, alias="AWS_SECRET_ACCESS_KEY")
    aws_default_region: Optional[str] = Field(default="us-east-1", alias="AWS_DEFAULT_REGION")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


def get_config(config_path: Optional[Path] = None, **overrides: Any) -> Config:
    """
    Get configuration instance.

    Args:
        config_path: Optional path to config file
        **overrides: Configuration overrides

    Returns:
        Config instance
    """
    return Config(config_path=config_path, **overrides)


def get_api_keys() -> APIKeys:
    """
    Get API keys from environment.

    Returns:
        APIKeys instance
    """
    return APIKeys()
