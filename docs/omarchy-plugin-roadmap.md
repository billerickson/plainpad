# Omarchy plugin directory roadmap

Deferred work, recorded September 24, 2026. Plainpad 0.1.0 is a released
standalone GTK app. No plugin integration or directory submission has been
completed. Recheck the linked requirements before resuming this work.

## Already in place

- Public GitHub repository and release.
- README, MIT license, and documented dependencies.
- Application icon and screenshot (`docs/plainpad.png`).
- User-local installation/removal and optional Omarchy floating-window rules.
- Automated installer and GTK workflow checks.

## Remaining work

- [ ] **Investigate a thin QML integration around the existing GTK app.**
  This is the preferred starting point, not a verified implementation plan.
  Determine whether a launcher plugin can satisfy the shell lifecycle and
  marketplace requirements while keeping the existing editor. Confirm how
  dependencies, app launching, and window rules work when installed through
  `omarchy plugin add`; that command does not run our `install.sh` or arbitrary
  installation hooks. Document any separate setup that remains necessary.
- [ ] **Preserve the current workflow.** Open centered and floating, retain
  normal Super+T tiling, support literal text editing and clipboard operations,
  dismiss with Escape, and keep one session-only draft. If considering a QML
  rewrite, verify that its window type can still support normal tiling before
  committing to that approach.
- [ ] **Decide repository layout.** The submission expects one plugin with a
  manifest at the repository root. Decide whether to add integration here or
  create a separate companion repository, while preserving standalone installs.
- [ ] **Add the plugin manifest and working QML entry points.** Choose a plugin
  kind that matches the implementation. Include schema version, name, version,
  author, description, and a unique namespaced ID. A candidate is
  `io.github.billerickson.plainpad`; check availability before adopting it.
  Do not use the reserved `omarchy.*` namespace.
- [ ] **Validate and exercise the full plugin lifecycle.** Run
  `omarchy plugin validate <plugin-directory>` and `qmllint` with the installed
  shell imports. Test fresh installation, enable, open, close, Escape, reopen,
  disable, re-enable, shell restart, update, and removal. Preserve user settings
  and verify the editor behavior above. Use an isolated environment for
  clipboard checks; avoid launching another Hyprland instance on the host.
- [ ] **Prepare the listing assets and documentation.** Explain plugin
  installation/removal, dependencies, any manual setup, and draft lifetime.
  Add an optional root `preview.png` using the existing screenshot or a new
  screenshot of the final integration.
- [ ] **Prepare the submission.** Use the marketplace issue form or its
  documented CLI format. Suggested category: `Productivity`. Choose one to
  three currently supported tags that fit the implementation (for example,
  `launcher` for a launcher integration). Review the ownership and submission
  checklist with the owner and obtain approval for the completed submission.
- [ ] **Submit and follow through on review.** Automated compatibility and
  baseline checks run against the submitted commit. Address findings in the
  existing submission; publication requires explicit maintainer approval.
  Adding a manifest alone does not make the existing GTK app a working plugin.

## References

- [Marketplace publishing requirements](https://plugins.omarchy.org/publish.html)
- [Plugin development guide](https://plugins.omarchy.org/develop.html)
- [Omarchy shell plugin manual](https://omarchy.org/manual/shell-plugins/)
- [CLI submission guide and checklist](https://github.com/omacom/omarchy-plugin-marketplace/blob/main/SUBMISSION.md)
- [Submission form](https://github.com/omacom/omarchy-plugin-marketplace/issues/new?template=submit-plugin.yml)
