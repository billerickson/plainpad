#!/usr/bin/python3
"""Install only user-owned Plainpad files; preserve edits and unrelated config."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

SOURCE = Path(__file__).resolve().parent
APP_ID = "local.plainpad.Plainpad"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def xdg(name, fallback):
    value = Path(os.environ.get(name) or fallback)
    if not value.is_absolute():
        raise ValueError(f"{name} must be an absolute path")
    return value


def desktop_quote(value):
    # Exec quoting is separate from Desktop Entry string escaping.
    value = value.replace("%", "%%")
    for char in ("\\", '"', "`", "$"):
        value = value.replace(char, "\\" + char)
    return '"' + value.replace("\\", "\\\\") + '"'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--omarchy",
        action="store_true",
        help="add floating rule to Omarchy 4 hyprland.lua (no keybinding)",
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="remove unmodified installed files and managed window rule",
    )
    args = parser.parse_args()
    home = Path.home()
    data = xdg("XDG_DATA_HOME", home / ".local/share")
    config = xdg("XDG_CONFIG_HOME", home / ".config")
    root = data / "plainpad"
    launcher = home / ".local/bin/plainpad"
    if any(c in str(data) + str(home) for c in "\n\r"):
        raise ValueError("Installation paths cannot contain newlines")
    manifest = root / "installation.json"
    hypr = config / "hypr/hyprland.lua"
    targets = {
        "app": root / "plainpad.py",
        "launcher": launcher,
        "desktop": data / f"applications/{APP_ID}.desktop",
        "icon": data / f"icons/hicolor/scalable/apps/{APP_ID}.svg",
        "rule": root / "plainpad.lua",
        "license": root / "LICENSE",
    }
    old = (
        json.loads(manifest.read_text())
        if manifest.exists()
        else {"files": {}, "config_block": ""}
    )
    for name, path in targets.items():
        if path.is_symlink():
            raise ValueError(f"Refusing symlink: {path}")
        if path.exists() and digest(path.read_bytes()) != old["files"].get(name):
            raise ValueError(
                f"Preserving existing or modified file: {path}. Move it aside before continuing."
            )
    if args.uninstall and not manifest.exists():
        print("Plainpad is not installed by this installer.")
        return

    before_config = hypr.read_bytes() if hypr.exists() else None
    config_text = before_config.decode() if before_config is not None else ""
    old_block = old.get("config_block", "")
    if old_block and config_text.count(old_block) != 1:
        raise ValueError(
            "The managed Plainpad config block changed. Restore it before updating or uninstalling."
        )
    new_block = old_block
    if args.omarchy and not args.uninstall and not old_block:
        if before_config is None or "omarchy" not in config_text.lower():
            raise ValueError(
                "--omarchy requires an existing Omarchy 4 hypr/hyprland.lua"
            )
        rule_path = json.dumps(str(targets["rule"]), ensure_ascii=False)
        new_block = f"\n-- BEGIN Plainpad (managed by installer)\ndofile({rule_path})\n-- END Plainpad\n"
    if args.uninstall:
        new_block = ""
    new_config = config_text.replace(old_block, "", 1) if old_block else config_text
    new_config += new_block
    config_changed = new_config != config_text

    content = {}
    if not args.uninstall:
        for name, source in [
            ("app", "plainpad.py"),
            ("icon", f"assets/{APP_ID}.svg"),
            ("rule", "omarchy/plainpad.lua"),
            ("license", "LICENSE"),
        ]:
            content[name] = (SOURCE / source).read_bytes()
        content["launcher"] = (
            "#!/usr/bin/python3\nimport runpy\nrunpy.run_path("
            + repr(str(targets["app"]))
            + ', run_name="__main__")\n'
        ).encode()
        desktop = (SOURCE / f"assets/{APP_ID}.desktop").read_text()
        content["desktop"] = desktop.replace(
            "Exec=plainpad", "Exec=" + desktop_quote(str(launcher))
        ).encode()

    # Preflight has completed. Keep rollback copies in memory for this operation.
    snapshots = {
        p: (p.read_bytes(), p.stat().st_mode & 0o777) if p.exists() else None
        for p in [*targets.values(), manifest]
    }
    if config_changed:
        backup = hypr.with_name(hypr.name + f".bak.plainpad-{time.time_ns()}")
        shutil.copy2(hypr, backup)
        print(f"Configuration backup: {backup}")
    try:
        if not args.uninstall:
            for name, payload in content.items():
                path = targets[name]
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
                path.chmod(0o755 if name == "launcher" else 0o644)
        if config_changed:
            hypr.write_text(new_config)
        # Validate both an added rule and removal while its source still exists.
        if (config_changed or new_block) and os.environ.get(
            "HYPRLAND_INSTANCE_SIGNATURE"
        ):
            subprocess.run(["hyprctl", "reload"], check=True, capture_output=True)
            errors = subprocess.check_output(
                ["hyprctl", "configerrors"], text=True
            ).strip()
            if errors:
                raise ValueError(f"Hyprland reported configuration errors: {errors}")
        if args.uninstall:
            for path in targets.values():
                path.unlink(missing_ok=True)
            manifest.unlink()
            try:
                root.rmdir()
            except OSError:
                pass  # Preserve anything the user put here.
        else:
            manifest.write_text(
                json.dumps(
                    {
                        "files": {k: digest(v) for k, v in content.items()},
                        "config_block": new_block,
                    },
                    indent=2,
                )
                + "\n"
            )
    except Exception:
        for path, snapshot in snapshots.items():
            if snapshot is None:
                path.unlink(missing_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(snapshot[0])
                path.chmod(snapshot[1])
        if config_changed:
            hypr.write_bytes(before_config)
            if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
                subprocess.run(["hyprctl", "reload"], capture_output=True)
        raise
    for command, directory in [
        ("update-desktop-database", data / "applications"),
        ("gtk-update-icon-cache", data / "icons/hicolor"),
    ]:
        if shutil.which(command):
            subprocess.run([command, str(directory)], capture_output=True)
    print(
        "Plainpad removed. Any manually added shortcut can now be removed."
        if args.uninstall
        else f"Installed Plainpad. Launch with {launcher} or your application menu."
    )
    if new_block and not os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
        print(
            "On your next Hyprland session, run: hyprctl reload && hyprctl configerrors"
        )


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"plainpad: {error}", file=sys.stderr)
        raise SystemExit(1)
