# Contributing to herdr-agent-pulse

Thanks for taking an interest in the plugin. This document covers dev setup,
running the tests, the project's testing philosophy, and how to add a theme.

## Dev setup

Clone the repo, then link it into your local herdr instead of installing the
GitHub-managed copy:

```sh
herdr plugin link .
```

`bin/ensure-daemon` needs to stay executable (`chmod +x bin/ensure-daemon`);
git preserves the executable bit on clone.

## Running the tests

```sh
python3 -m unittest discover -s tests -v
```

Requires **Python 3.9+, stdlib only** — no third-party dependencies, no
virtualenv, no `pip install`. This is a hard project rule: a plugin that
needs a package manager to run its hook script is a plugin that breaks on
someone else's machine.

One test module, `tests/test_schema_smoke.py`, talks to a real installed
`herdr` binary (read-only: `herdr api schema --json`) to catch upstream API
drift early. It skips cleanly via `unittest.skipUnless` when `herdr` is not
on `PATH` — CI runs without herdr installed, so expect it to report
`skipped` there, not `ok`.

## Strict TDD

This project expects a failing test before a behavior change, not after.
When you change behavior (fixing a bug, changing a default, adding a theme,
touching the manifest id, anything socket/daemon-facing):

1. Write or adjust the test first.
2. Run it and confirm it fails for the reason you expect (RED).
3. Make the change.
4. Run it again and confirm it passes (GREEN).

A pull request that adds behavior with no corresponding test, or that can't
show the RED step happened, will be asked to add one before merge.

## Adding a theme

Themes live in one place: the `_THEMES` dict in `agent_pulse/core.py`. Each
theme needs exactly these keys:

```python
"my-theme": {
    "working_frames": [...],   # non-empty list of glyphs, cycled by tick % len(frames)
    "icons": {
        "working": "...",
        "blocked": "...",
        "done": "...",
    },
    "blocked_label": "...",    # shown on the pane border while blocked
},
```

Nothing else in the codebase needs to change: `resolve_theme`, `frame`,
`tab_icon`, `border_title`, `summary`, and the tab-label icon-stripping logic
all read from `_THEMES` generically.

Add tests in `tests/test_core.py` alongside the existing theme tests,
covering at minimum:

- `resolve_theme("my-theme")` returns `"my-theme"`.
- `frame("my-theme", tick)` cycles through all of `working_frames` and wraps.
- `tab_icon("my-theme", status)` returns the right icon for each of
  `working`/`blocked`/`done`.
- `strip_known_prefix` correctly strips your theme's icons too (it derives
  its icon set from every theme in `_THEMES`, so a new theme is covered
  automatically, but add a test that exercises it explicitly).

Then document the theme in the README's theme table.

## Contract-test rule: fixtures must be real captures

`tests/fixtures/*.json` are **real, captured herdr responses** (`tab.get`,
`pane.get`, `pane.list`, `tab.list`), trimmed to what the test needs and
anonymized (no real tab names, cwd paths, or agent labels — replace with
placeholders).

Do not hand-write a fixture from what you assume the response shape looks
like. A hand-written fake once assumed `tab.get`/`pane.get` returned their
payload at the top level; the real herdr wraps it under `result.tab` /
`result.pane`. Every fixture-backed test passed against the fake shape,
and the bug shipped to a live tab bar (tab labels destroyed in a real
session before it was caught and fixed). Capture real output before writing
or changing a contract test:

```sh
herdr tab get <tab_id> --json    # or whichever method the test covers
```

Trim the result to the fields the test asserts on, replace anything
identifying with a placeholder, and use that as the fixture.

## Commit style

[Conventional Commits](https://www.conventionalcommits.org/): `feat:`,
`fix:`, `docs:`, `test:`, `ci:`, `chore:`, etc. Keep tests with the code
change they cover in the same commit.
