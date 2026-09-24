# Release verification

## Automated checks

- Installer: fresh temporary home with custom XDG paths containing spaces;
  installed executable runs independently of the checkout; desktop entry validates.
- Reinstall: no duplicate window rules; existing settings survive.
- Uninstall: removes only owned files and its exact config block, preserving later
  personal configuration edits and unrelated files.
- Conflicts: pre-existing executables, modified installed files, and modified
  config blocks stop the operation before any deletion or overwrite.
- GUI smoke: actual GTK window, keyboard input, literal text copy/paste, undo/redo,
  dismissal, retained clipboard and draft, single-instance reopening, and quit.

## Omarchy / Wayland

Verified on Omarchy 4.0.4, Hyprland 0.56.2 and GTK 4.22:

- Window opens centered and floating at 820 × 460 logical pixels.
- The dispatcher used by Super+T toggles floating/tiling.
- Dismissing and reopening retains the draft and opens floating again.
- Hyprland reload and config error checks pass after integration.

The isolated GUI smoke uses Ubuntu 24.04, GTK 4.14, Xvfb, and a private D-Bus
session. It exercises the real app without using the host clipboard.
It does not validate Hyprland behavior; those checks are performed on Omarchy.

## Before each release

Run the automated checks, test the install/uninstall workflow, and repeat the
Wayland checks if window behavior changes. Check multiple workspaces and display
scales when changing activation or sizing. Verify the README screenshot contains
only synthetic sample text.
