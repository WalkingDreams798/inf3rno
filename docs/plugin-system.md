# Plugin System

Inf3rno supports a plugin system for extending functionality.

## Plugin Types

### 1. BruteForcePlugin

Create custom brute-force modules for new protocols.

```python
from core.plugin import BruteForcePlugin
from core.bruteforce import BaseBrute

class MyBruteModule(BaseBrute):
    def __init__(self, target, port, username, wordlist, **kwargs):
        super().__init__(target, port, username, wordlist, **kwargs)
        self.service = "MyService"

    def try_login(self, username, password):
        # Implement your login logic here
        return False

class MyPlugin(BruteForcePlugin):
    @property
    def name(self):
        return "myplugin"

    @property
    def version(self):
        return "1.0.0"

    @property
    def description(self):
        return "My custom brute-force plugin"

    @property
    def service(self):
        return "MyService"

    @property
    def default_port(self):
        return 12345

    def create_module(self, target, port, username, wordlist, **kwargs):
        return MyBruteModule(target, port, username, wordlist, **kwargs)
```

### 2. WordlistPlugin

Create custom wordlist generators.

```python
from core.plugin import WordlistPlugin

class MyWordlistPlugin(WordlistPlugin):
    @property
    def name(self):
        return "mywordlist"

    @property
    def version(self):
        return "1.0.0"

    @property
    def description(self):
        return "My custom wordlist generator"

    def generate(self, target, username, **kwargs):
        # Generate and return wordlist
        return ["password1", "admin123", "test123"]
```

### 3. ReportPlugin

Create custom report exporters.

```python
from core.plugin import ReportPlugin

class MyReportPlugin(ReportPlugin):
    @property
    def name(self):
        return "myreport"

    @property
    def version(self):
        return "1.0.0"

    @property
    def description(self):
        return "My custom report exporter"

    def export(self, credentials, output_file, **kwargs):
        # Export credentials to file
        with open(output_file, "w") as f:
            for user, pwd in credentials:
                f.write(f"{user}:{pwd}\n")
        return output_file
```

## Plugin Hooks

Plugins can hook into the attack lifecycle:

```python
class MyPlugin(PluginBase):
    def on_attack_start(self, target, port, username):
        """Called when attack starts."""
        print(f"Attack started: {target}:{port}")

    def on_attempt(self, username, password, success):
        """Called on each attempt."""
        if success:
            print(f"Found: {username}:{password}")

    def on_attack_complete(self, found):
        """Called when attack completes."""
        print(f"Attack complete, found {len(found)} credentials")

    def on_error(self, error):
        """Called on error."""
        print(f"Error: {error}")
```

## Installing Plugins

1. Create a `.py` file in the `plugins/` directory
2. The plugin will be automatically discovered and loaded

## Creating a Plugin

1. Create a new file in `plugins/` directory
2. Import the base class:
   ```python
   from core.plugin import BruteForcePlugin
   ```
3. Implement the required properties and methods
4. Save the file - it will be auto-loaded

## Plugin Structure

```
plugins/
├── __init__.py
├── example.py
├── myplugin.py
└── custom.py
```

## API Usage

### List Plugins

```python
from core.plugin import plugin_manager

plugins = plugin_manager.list_plugins()
for plugin in plugins:
    print(f"{plugin['name']} v{plugin['version']}")
```

### Get Plugin

```python
from core.plugin import plugin_manager

# Get brute-force plugin
plugin = plugin_manager.get_brute_plugin("myservice")

# Get wordlist plugin
plugin = plugin_manager.get_wordlist_plugin("mywordlist")

# Get report plugin
plugin = plugin_manager.get_report_plugin("myreport")
```

## Example Plugin

See `plugins/example.py` for a complete working example.

## Best Practices

1. Keep plugins simple and focused
2. Handle errors gracefully
3. Use descriptive names
4. Document your plugin
5. Test thoroughly before deployment
