"""Typed exception tree. No bare except inside the package."""


class McpolishError(Exception):
    """Base class for every MCPolish failure."""


class DiscoveryError(McpolishError):
    """A source file couldn't be parsed or had no usable tool registrations."""


class ConfigError(McpolishError):
    """User config in pyproject.toml is invalid."""


class RegistryError(McpolishError):
    """The cross-server snapshot is missing or corrupt."""


class RuleError(McpolishError):
    """A rule itself threw. Caught by the runner so one bad rule never aborts a scan."""


class LLMError(McpolishError):
    """The optional LLM backend failed; we degrade gracefully."""
