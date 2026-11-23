# Claude Code configuration meanings

This is the interpretation table for the Claude Code reader (`stay_safe/claude.py`, issue #163). Like the
[Codex table](codex.md), it describes a selected settings-file snapshot. It does not establish a session's
effective permissions or whether an incident will occur. Command-line flags, project and local settings files,
managed and remotely managed settings, and runtime state are not inspected. Claude Code combines list settings such
as `permissions.allow` from every file it loads, so one file's rules are not the whole set.

`documented` means the meaning is supported by the linked Claude Code documentation, read on 2026-11-23. `open`
means the reader does not handle it; the report names it under Not checked.

## Files

| Setting | Meaning | Status | Source |
|---|---|---|---|
| `~/.claude/settings.json` | User settings, read by a default run. `CLAUDE_CONFIG_DIR` moves the folder. A run without `--agent` looks for it only through `$HOME` or `CLAUDE_CONFIG_DIR`. | documented | [settings], "Settings files and who they affect", "Find or create your settings files" |
| `~/.claude.json` | Holds account details, MCP server configurations and per-project trust decisions. Named, never opened. | documented; open | [settings], "Find or create your settings files" |
| Managed settings (`/Library/Application Support/ClaudeCode/`, `/etc/claude-code/`) | Organization settings that take precedence over user settings. Named when present, not read. | documented; open | [managed], "Deploy a managed settings file"; [settings], "Settings precedence" |
| `remote-settings.json`, `agents/`, `commands/`, `plugins/`, `skills/` in the Claude Code folder | Loaded by Claude Code; named when present, not read. | open | — |
| `.claude/settings.json`, `.claude/settings.local.json` | Project settings. Not read: stay-safe runs from its own folder, not your project. | documented; open | [settings], "Settings files and who they affect" |

## Settings

| Setting | Value | Meaning | Risk | Status | Source |
|---|---|---|---|---|---|
| `permissions.defaultMode` | `bypassPermissions` | Skips permission prompts, except for the actions no mode approves automatically. | `commands_without_prompts` | documented | [permissions], "Permission modes" |
| `permissions.defaultMode` | `default`, `manual`, `acceptEdits`, `plan`, `dontAsk` | Prompts, or refuses, before shell commands; `acceptEdits` accepts file edits and common filesystem commands only. `manual` is an alias for `default`. | none | documented | [permissions], "Permission modes"; [modes], "Available modes" |
| `permissions.defaultMode` | `auto` | Runs without routine prompts; a classifier checks each action. The classifier's decisions are a gap. | none; gap | documented; open | [permissions], "Permission modes" |
| `permissions.defaultMode` | absent | The built-in mode depends on the surface and version (`auto` in a terminal from v2.1.283). Not inferred; a gap. | none; gap | documented | [modes], "Which mode a session starts in" |
| `permissions.allow` | `Bash`, `Bash(*)` | Matches every Bash command. | `saved_approval` (broad) | documented | [permissions], "Match all uses of a tool" |
| `permissions.allow` | `Bash(<specifier>)` | Matches commands the specifier covers; `Bash(git:*)` and `Bash(git *)` match the same commands. Only a first word on the [program list](codex.md) is shown. | `saved_approval` | documented | [permissions], "Wildcard patterns" |
| `permissions.allow` | `WebFetch` | Matches all web fetch requests. | `network_access` | documented | [permissions], "Match all uses of a tool" |
| `permissions.allow` | `WebFetch(domain:<domain>)` | Matches fetch requests to that domain; the domain is withheld. | `network_access` | documented | [permissions], "Use specifiers for fine-grained control" |
| `permissions.allow` | other tools | Not evaluated; a gap. | none; gap | open | — |
| `permissions.ask`, `permissions.deny` | any rule | Checked before allow rules; the first match decides. Not evaluated; a gap. | none; gap | documented; open | [permissions], "Manage permissions" |
| `sandbox.enabled` | absent | The sandbox is off by default. | none | documented | [sandboxing], "What the sandbox restricts" |
| `sandbox.enabled` | `true`, `false` | Turns Bash sandboxing on or off. | none | documented | [reference], "Settings index" |
| other `permissions` and `sandbox` fields, other settings | any | Not evaluated; documented setting names are shown, others withheld. | none; gap | open | [reference], "Settings index" |

[settings]: https://code.claude.com/docs/en/settings
[permissions]: https://code.claude.com/docs/en/permissions
[modes]: https://code.claude.com/docs/en/permission-modes
[sandboxing]: https://code.claude.com/docs/en/sandboxing
[managed]: https://code.claude.com/docs/en/managed-settings
[reference]: https://code.claude.com/docs/en/settings-reference
