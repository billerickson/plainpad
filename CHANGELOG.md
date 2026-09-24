# Changelog

## 0.1.0 — 2026-09-24

Initial public release.

- Plain-text GTK scratchpad with clipboard editing and undo/redo.
- Escape dismisses the window and retains the draft in memory.
- Single-instance reopening; Ctrl+Q quits and discards the draft.
- Optional Omarchy 4 integration opens centered and floating; Super+T can tile.
- User-local installation, desktop entry, icon, and uninstall support.
- Installer preserves unrelated files, edited files, and personal configuration.

Verified with Omarchy 4.0.4 / Hyprland 0.56.2 / GTK 4.22 and isolated GTK 4.14
clipboard and keyboard checks on Ubuntu 24.04. Drafts are not saved across quit,
logout, or reboot. This is a standalone application, not an Omarchy shell plugin.
