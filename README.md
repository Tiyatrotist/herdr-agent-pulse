# herdr-agent-pulse

A [herdr](https://github.com/herdrdev/herdr) plugin that makes coding-agent
activity visible at a glance: an animated pane-border title while an agent
works, a state icon on the tab label, and a one-line summary on the tab bar.
Works with any host terminal and needs no changes to herdr itself.

- An animated pane-border title while an agent is working (a spinner frame
  plus its current task text, read from the pane's own terminal title).
- A static "needs you" border label while an agent is blocked.
- A state icon prefixed onto a tab's label whenever any pane in that tab is
  working, blocked, or done; the tab's original label is restored once
  nothing in it is active.
- A one-line summary (e.g. `◐ 2 · ✋ 1`) written to a file for
  `ui.tab_bar_right` to display.

## Why

herdr's built-in agent state icon is a single static glyph, and the pane
border only changes color on focus, not on agent activity. If you run
several agent panes at once and want an iTerm2-like "this one is working /
this one needs you" signal without leaving herdr, this plugin adds it
entirely through herdr's existing plugin hooks and socket API.

## Themes

Two themes ship built in; an unknown theme name falls back to `iterm`.

| Theme | Working frames | Icons | Blocked label |
| --- | --- | --- | --- |
| `iterm` (default) | `◐ ◓ ◑ ◒` | working `◐` · blocked `✋` · done `✓` | `✋ needs you` |
| `naruto` | `🍥·· ·🍥· ··🍥 ·🍥·` (bouncing rasengan) | working `🍥` · blocked `🦊` · done `🎖` | `🦊 needs you` |

## Install

```sh
herdr plugin install Mozart2234/herdr-agent-pulse
```

For local development, or to run a checked-out copy instead of the
GitHub-managed one:

```sh
herdr plugin link .
```

`[[startup]]` only runs on herdr's own server boot or a live handoff, not on
`plugin link`/`enable` — the daemon starts the first time any pane's agent
status changes after linking. To start it immediately after linking into an
already-running herdr, trigger any agent status change (or restart herdr).

Requires herdr **0.9.1 or later**, macOS or Linux.

## Configure

Create `config.json` in the plugin's config directory (see
`config.default.json` in this repo for the documented defaults):

```json
{
  "theme": "iterm",
  "fps": 4,
  "tab_icons": true
}
```

| Key | Type | Default | Notes |
| --- | --- | --- | --- |
| `theme` | `"iterm"` \| `"naruto"` | `"iterm"` | Unknown values fall back to `iterm`. |
| `fps` | integer | `4` | Animation frame rate, clamped to 1-8. |
| `tab_icons` | boolean | `true` | Set `false` to disable tab-label renaming (border animation and the summary file are unaffected). |

A missing file, missing keys, or malformed JSON all fall back to the
defaults above rather than failing.

For this plugin's public id, `mozart2234.agent-pulse`, herdr resolves the
config directory to (verified against v0.9.1 `src/plugin_paths.rs`, which
percent-encodes anything outside `[a-z0-9._-]`; this id needs no encoding):

```
~/.config/herdr/plugins/config/mozart2234.agent-pulse/config.json
```

## Add the tab-bar-right summary

herdr passes each plugin its own `$HERDR_PLUGIN_STATE_DIR`, which for
`mozart2234.agent-pulse` resolves to:

```
~/.local/state/herdr/plugins/mozart2234.agent-pulse/
```

The daemon writes `summary.txt` there (atomically, only when it changes; the
last line is always the current summary, or an empty line when nothing is
active). Add this to `~/.config/herdr/config.toml`:

```toml
[[ui.tab_bar_right]]
type = "command"
command = "cat ~/.local/state/herdr/plugins/mozart2234.agent-pulse/summary.txt 2>/dev/null"
interval_seconds = 1
```

(herdr strips ANSI and shows the last completed output line, so a plain
`cat` is enough.)

## How it works

A small background daemon (`agent_pulse/daemon.py`) subscribes to herdr's
socket API for `pane.agent_status_changed`, tracks each pane's status, and
reports presentation-only metadata (`pane.report_metadata`, `tab.rename`)
back to herdr. `bin/ensure-daemon` is the plugin's `[[startup]]` and
`[[events]]` hook: it is invoked constantly (on every
`pane.agent_status_changed`, unsupervised, up to 32 concurrent), so it does
almost nothing — check whether the daemon's pidfile is alive, and if not,
launch `python3 -m agent_pulse.daemon` detached. The daemon itself owns the
socket connection, the animation loop, and its own singleton lock (a
`flock()` on its pidfile), so a burst of concurrent hook invocations is safe.
Tab renames only happen on a status *change*, not per animation frame, so a
working pane's per-frame border updates never touch the tab label.

All reported titles carry a short TTL, so if the daemon dies, any pane it
was animating returns to normal within 1-3 seconds on its own (the TTL is
three frame intervals, floored at one second). The next
`pane.agent_status_changed` event restarts it.

## Limitations

- **Tab renames are sticky.** herdr's `tab.rename` sets a permanent custom
  label (no clear option, and the tab turns bold and stops auto-following
  cwd/git) until renamed again. This plugin restores the original label once
  a tab goes idle, but while a tab has an icon, it behaves like any other
  manually-renamed tab.
- **Pane-border color is not configurable.** herdr's border color is
  focus-only; this plugin only changes the *title text* shown on the
  border, not its color.
- **New panes take up to a couple of animation ticks to appear live.** A
  brand-new pane's status is known immediately (from the `pane.created`
  event's own payload), but it only gets its own live status-change
  subscription after the daemon's next topology-triggered reconnect, which
  happens as soon as the daemon notices the new pane — not on a fixed
  delay, but not instantaneous either.
- Requires herdr ≥ 0.9.1; macOS or Linux only (no Windows support).

## Troubleshooting

The daemon logs to `daemon.log` in its state directory:

```
~/.local/state/herdr/plugins/mozart2234.agent-pulse/daemon.log
```

Check it first for connection errors, failed requests, or tick exceptions —
they are always logged there rather than swallowed silently.

To stop the plugin without removing it:

```sh
herdr plugin disable mozart2234.agent-pulse   # keeps it linked, stops running it
herdr plugin unlink mozart2234.agent-pulse    # removes it entirely
```

Disabling or unlinking does not by itself stop an already-running daemon
process. SIGTERM/SIGINT or a closed event subscription end the main loop and
run the cleanup that clears titles and restores tab labels. Individual request
failures are logged and ignored, so a failed report does not stop the daemon.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, running the
test suite, and a guide for adding a new theme.

## License

[MIT](LICENSE) © 2026 Alexei Mamani
