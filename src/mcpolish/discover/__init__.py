"""Source-to-IR pipeline."""

from mcpolish.discover.base import Discoverer
from mcpolish.discover.ir import build_registry, discover_path
from mcpolish.discover.python_ast import PythonDiscoverer

__all__ = ["Discoverer", "PythonDiscoverer", "build_registry", "discover_path"]
