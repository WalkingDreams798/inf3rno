"""Plugin system for Inf3rno."""

import os
import sys
import importlib
import inspect
from typing import Dict, List, Optional, Type
from abc import ABC, abstractmethod

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inf3rno.core.bruteforce import BaseBrute


class PluginBase(ABC):
    """Base class for all Inf3rno plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description."""
        pass

    @property
    def author(self) -> str:
        """Plugin author."""
        return "Unknown"

    @property
    def service(self) -> str:
        """Service name this plugin handles."""
        return ""

    @property
    def default_port(self) -> int:
        """Default port for this service."""
        return 0

    def on_attack_start(self, target: str, port: int, username: str):
        """Called when attack starts."""
        pass

    def on_attempt(self, username: str, password: str, success: bool):
        """Called on each attempt."""
        pass

    def on_attack_complete(self, found: list):
        """Called when attack completes."""
        pass

    def on_error(self, error: Exception):
        """Called on error."""
        pass


class BruteForcePlugin(PluginBase):
    """Base class for brute-force plugins."""

    @abstractmethod
    def create_module(self, target: str, port: int, username: str,
                      wordlist: str, **kwargs) -> BaseBrute:
        """Create a brute-force module instance."""
        pass


class WordlistPlugin(PluginBase):
    """Base class for wordlist generation plugins."""

    @abstractmethod
    def generate(self, target: str, username: str, **kwargs) -> List[str]:
        """Generate wordlist."""
        pass


class ReportPlugin(PluginBase):
    """Base class for report plugins."""

    @abstractmethod
    def export(self, credentials: list, output_file: str, **kwargs) -> str:
        """Export credentials to file."""
        pass


class PluginManager:
    """Manage Inf3rno plugins."""

    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, PluginBase] = {}
        self.brute_plugins: Dict[str, BruteForcePlugin] = {}
        self.wordlist_plugins: Dict[str, WordlistPlugin] = {}
        self.report_plugins: Dict[str, ReportPlugin] = {}

    def discover_plugins(self):
        """Discover and load all plugins from plugins directory."""
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)
            return

        for filename in os.listdir(self.plugins_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                plugin_name = filename[:-3]
                try:
                    self._load_plugin(plugin_name)
                except Exception as e:
                    print(f"[!] Failed to load plugin {plugin_name}: {e}")

    def _load_plugin(self, plugin_name: str):
        """Load a single plugin."""
        module_path = os.path.join(self.plugins_dir, f"{plugin_name}.py")
        if not os.path.exists(module_path):
            return

        # Add plugins directory to path
        plugins_dir = os.path.dirname(module_path)
        if plugins_dir not in sys.path:
            sys.path.insert(0, plugins_dir)

        # Import module
        spec = importlib.util.spec_from_file_location(plugin_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[plugin_name] = module
        spec.loader.exec_module(module)

        # Find plugin classes
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, PluginBase) and obj != PluginBase:
                try:
                    plugin_instance = obj()
                    self.register_plugin(plugin_instance)
                except Exception as e:
                    print(f"[!] Failed to instantiate plugin {name}: {e}")

    def register_plugin(self, plugin: PluginBase):
        """Register a plugin."""
        self.plugins[plugin.name] = plugin

        if isinstance(plugin, BruteForcePlugin):
            self.brute_plugins[plugin.service.lower()] = plugin
        elif isinstance(plugin, WordlistPlugin):
            self.wordlist_plugins[plugin.name] = plugin
        elif isinstance(plugin, ReportPlugin):
            self.report_plugins[plugin.name] = plugin

        print(f"[+] Registered plugin: {plugin.name} v{plugin.version}")

    def get_brute_plugin(self, service: str) -> Optional[BruteForcePlugin]:
        """Get brute-force plugin for service."""
        return self.brute_plugins.get(service.lower())

    def get_wordlist_plugin(self, name: str) -> Optional[WordlistPlugin]:
        """Get wordlist plugin by name."""
        return self.wordlist_plugins.get(name)

    def get_report_plugin(self, name: str) -> Optional[ReportPlugin]:
        """Get report plugin by name."""
        return self.report_plugins.get(name)

    def list_plugins(self) -> List[dict]:
        """List all loaded plugins."""
        return [
            {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description,
                "author": plugin.author,
                "type": type(plugin).__name__,
            }
            for plugin in self.plugins.values()
        ]


# Global plugin manager instance
plugin_manager = PluginManager()


def load_plugins(plugins_dir: str = "plugins"):
    """Load all plugins from directory."""
    plugin_manager.plugins_dir = plugins_dir
    plugin_manager.discover_plugins()
