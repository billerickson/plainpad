"""Real keyboard/clipboard smoke test; run inside Xvfb and dbus-run-session."""

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args, **kwargs):
    return subprocess.run(
        args, check=True, capture_output=True, timeout=10, **kwargs
    ).stdout


def windows():
    result = subprocess.run(
        ["xdotool", "search", "--onlyvisible", "--name", "^Plainpad$"],
        capture_output=True,
    )
    return result.stdout.decode().splitlines()


def wait_for(predicate):
    for _ in range(100):
        if predicate():
            return
        time.sleep(0.05)
    raise AssertionError("Timed out waiting for window state")


def key(*keys):
    run("xdotool", "key", "--clearmodifiers", *keys)
    time.sleep(0.15)


def clipboard():
    return run("xclip", "-selection", "clipboard", "-out").decode()


def copy_all():
    key("ctrl+a", "ctrl+c")
    return clipboard()


with tempfile.TemporaryDirectory(prefix="plainpad GUI ") as directory:
    env = {
        **os.environ,
        "HOME": directory,
        "XDG_CONFIG_HOME": directory + "/config",
        "XDG_DATA_HOME": directory + "/data",
        "GDK_BACKEND": "x11",
        "GTK_THEME": "Adwaita:dark",
        "GTK_A11Y": "none",
        "GSK_RENDERER": "cairo",
    }
    env.pop("HYPRLAND_INSTANCE_SIGNATURE", None)
    run(str(ROOT / "install.sh"), env=env)
    launcher = str(Path(directory) / ".local/bin/plainpad")
    app = subprocess.Popen([launcher], env=env)
    try:
        wait_for(windows)
        run("xdotool", "windowfocus", windows()[0])
        sample = "MAILGUN_API_KEY=example_only\n  literal **bold** `code` $HOME \\path\n\ttab stays\n"
        # Paste through the system clipboard, not the TextBuffer API.
        subprocess.run(
            ["xclip", "-selection", "clipboard", "-in"],
            input=sample.encode(),
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        key("ctrl+v")
        assert copy_all() == sample, "Clipboard round-trip changed literal text"
        key("ctrl+End")
        run("xdotool", "type", "--clearmodifiers", "!")
        key("ctrl+z")
        assert copy_all() == sample, "Undo failed"
        key("ctrl+shift+z")
        assert copy_all() == sample + "!", "Redo failed"
        key("Escape")
        wait_for(lambda: not windows())
        assert app.poll() is None, "Dismissal quit the app"
        assert clipboard() == sample + "!", "Dismissal lost the clipboard"
        run(launcher, env=env)
        wait_for(windows)
        run("xdotool", "windowfocus", windows()[0])
        assert copy_all() == sample + "!", "Reopening lost the draft"
        run(launcher, env=env)
        assert len(windows()) == 1, "Reopening created a duplicate window"
        key("ctrl+x")
        assert clipboard() == sample + "!", "Cut changed the text"
        key("ctrl+v")
        assert copy_all() == sample + "!", "Cut/paste changed the text"
        if len(sys.argv) == 2:
            key("ctrl+a")
            screenshot_text = 'MAILGUN_API_KEY=your_key_here\n\ncurl --header "Authorization: Bearer $API_TOKEN"\n\nUnderscores_stay_literal. So do **asterisks**.\n\nCopy. Edit. Paste. Escape.'
            subprocess.run(
                ["xclip", "-selection", "clipboard", "-in"],
                input=screenshot_text.encode(),
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            key("ctrl+v")
            key("ctrl+Home")
            time.sleep(0.5)
            run("import", "-window", windows()[0], sys.argv[1])
        key("ctrl+q")
        app.wait(timeout=5)
        assert app.returncode == 0, "Quit failed"
        print(
            "PASS: installed app, plain-text clipboard, undo/redo, cut/paste, Escape, retained draft/clipboard, single instance, quit"
        )
    finally:
        if app.poll() is None:
            app.terminate()
            app.wait(timeout=5)
