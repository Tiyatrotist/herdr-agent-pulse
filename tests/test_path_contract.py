import re
from pathlib import Path

from agent_pulse import config, daemon


ROOT = Path(__file__).resolve().parents[1]
ENSURE_DAEMON = ROOT / "bin" / "ensure-daemon"


def test_ensure_daemon_fallback_state_dir_matches_python_config():
    script = ENSURE_DAEMON.read_text()
    match = re.search(r'STATE_DIR="\$HOME([^"]+)"', script)

    assert match is not None
    assert "~" + match.group(1) == config.DEFAULT_STATE_DIR


def test_ensure_daemon_pidfile_matches_daemon_constant():
    script = ENSURE_DAEMON.read_text()
    match = re.search(r'PID_FILE="\$STATE_DIR/([^"]+)"', script)

    assert match is not None
    assert match.group(1) == daemon.PID_FILE_NAME
