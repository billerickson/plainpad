#!/usr/bin/python3
"""A single, session-only plain-text scratchpad for Omarchy."""

import sys

VERSION = "0.1.0"

if __name__ == "__main__" and "--version" in sys.argv:
    print(f"Plainpad {VERSION}")
    raise SystemExit(0)

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, Gio, Gtk


class Plainpad(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="local.plainpad.Plainpad")
        self.window = None

    def do_activate(self):
        if self.window is None:
            # Keep the buffer and clipboard alive when Escape hides the window.
            self.hold()
            self.build_window()
        self.window.present()
        self.editor.grab_focus()

    def build_window(self):
        self.window = Gtk.ApplicationWindow(application=self, title="Plainpad")
        self.window.set_icon_name("local.plainpad.Plainpad")
        self.window.set_default_size(820, 460)
        self.window.set_hide_on_close(True)

        layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.window.set_child(layout)

        self.editor = Gtk.TextView()
        self.editor.set_monospace(True)
        self.editor.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.editor.set_top_margin(20)
        self.editor.set_bottom_margin(20)
        self.editor.set_left_margin(22)
        self.editor.set_right_margin(22)
        self.editor.set_input_hints(Gtk.InputHints.NO_SPELLCHECK)
        self.buffer = self.editor.get_buffer()
        self.buffer.set_enable_undo(True)

        scroll = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        scroll.set_child(self.editor)
        layout.append(scroll)

        footer = Gtk.Label(
            label="Plain text   ·   Ctrl+A select all   ·   Ctrl+C copy   ·   Esc dismiss"
        )
        footer.add_css_class("dim-label")
        footer.set_margin_top(9)
        footer.set_margin_bottom(9)
        layout.append(footer)

        for name, callback, keys in (
            ("dismiss", lambda *_: self.window.close(), ["Escape"]),
            (
                "undo",
                lambda *_: self.buffer.undo() if self.buffer.get_can_undo() else None,
                ["<Control>z"],
            ),
            (
                "redo",
                lambda *_: self.buffer.redo() if self.buffer.get_can_redo() else None,
                ["<Control><Shift>z", "<Control>y"],
            ),
            ("quit", lambda *_: self.quit(), ["<Control>q"]),
        ):
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", callback)
            self.add_action(action)
            self.set_accels_for_action("app." + name, keys)

        css = Gtk.CssProvider()
        css.load_from_string("textview { font-size: 16px; } label { font-size: 12px; }")
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )


if __name__ == "__main__":
    raise SystemExit(Plainpad().run(sys.argv))
