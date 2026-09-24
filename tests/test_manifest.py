"""Guards the public plugin id declared in herdr-plugin.toml.

This is a standalone, community-installable plugin (`herdr plugin install
Mozart2234/herdr-agent-pulse`), distinct from any private single-machine dev
checkout it may have been copied from. A regression here would silently ship
the wrong id, which changes the resolved
HERDR_PLUGIN_STATE_DIR/HERDR_PLUGIN_CONFIG_DIR paths herdr computes from it
(see agent_pulse/config.py and README.md).

Stdlib-only: this repo supports Python 3.9+, and tomllib is 3.11+, so this
reads just the one `id = "..."` line instead of adding a TOML dependency.
"""

import os
import re
import unittest

MANIFEST_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "herdr-plugin.toml"
)
EXPECTED_PLUGIN_ID = "mozart2234.agent-pulse"


class ManifestPluginIdTests(unittest.TestCase):
    def test_manifest_declares_the_public_plugin_id(self):
        with open(MANIFEST_PATH, encoding="utf-8") as handle:
            content = handle.read()
        match = re.search(r'^id\s*=\s*"([^"]+)"', content, re.MULTILINE)
        self.assertIsNotNone(match, "herdr-plugin.toml must declare an id")
        self.assertEqual(match.group(1), EXPECTED_PLUGIN_ID)


if __name__ == "__main__":
    unittest.main()
