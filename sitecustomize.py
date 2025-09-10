"""Repository-local site customizations.

This file is automatically imported by Python at startup (if present on sys.path).
We use it to make the local developer/test environment deterministic across machines.
"""

import os

# Prevent third-party pytest plugins from auto-loading. This avoids flaky behaviors
# when developers have globally installed plugins that interfere with collection.
# Tests in this repo do not rely on external plugins.
os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
