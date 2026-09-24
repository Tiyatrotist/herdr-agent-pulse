# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-24

Initial public release.

### Added

- Animated pane-border title while a coding agent is working (spinner frame
  plus its current task text), with a static "needs you" label while
  blocked.
- Tab-label state icon on any tab containing a working, blocked, or done
  pane; the original label is restored once nothing in the tab is active.
- `ui.tab_bar_right` summary file (e.g. `◐ 2 · ✋ 1`).
- Two built-in themes: `iterm` (default) and `naruto`.
- Configurable via `config.json` in the plugin's config directory: `theme`,
  `fps`, `tab_icons`.
- TTL-based self-healing: a dead daemon's reported titles clear within 1-3
  seconds depending on the configured frame rate, and the next
  `pane.agent_status_changed` event restarts it.
- 91 unit tests (pure core logic, socket client, config loading, daemon
  behavior against a fake Unix-socket server, and a manifest-id guard), plus
  a read-only live schema smoke test that skips cleanly when `herdr` is not
  on `PATH`.
