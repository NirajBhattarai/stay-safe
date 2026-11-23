"""Read selected Claude Code settings files without executing their configuration.

The meanings are in harnesses/claude-code.md; each one cites the Claude Code documentation it rests on.
"""

import json
import os
import re
import stat

from .codex import MAX_BYTES, Reader, open_input
from .codex_rules import PROGRAMS

# https://code.claude.com/docs/en/permissions, "Permission modes"; `manual` is the CLI's alias for `default`
# (https://code.claude.com/docs/en/permission-modes, "Available modes").
MODES = {"default", "manual", "acceptEdits", "plan", "auto", "dontAsk", "bypassPermissions"}
PERMISSIONS = {"allow", "ask", "deny", "defaultMode"}
SANDBOX = {"enabled", "autoAllowBashIfSandboxed"}
# Settings that change how Claude Code looks or which model it uses, not what it may do; skipped without a gap.
PREFERENCES = {"$schema", "model", "theme", "language", "verbose", "outputStyle", "editorMode", "tui", "viewMode",
               "alwaysThinkingEnabled", "effortLevel", "autoUpdatesChannel", "cleanupPeriodDays", "timeFormat",
               "timeZone", "prefersReducedMotion", "showTurnDuration", "terminalProgressBarEnabled",
               "spinnerTipsEnabled", "autoCompactEnabled", "fastMode", "feedbackSurveyRate", "spellcheck",
               "syntaxHighlightingDisabled", "vimInsertModeRemaps", "keybindingFlavor", "maxProseWidth",
               "showThinkingSummaries", "autoScrollEnabled", "copyOnSelect", "emojiCompletionEnabled"}
# Documented settings the report may name when they are outside reader coverage
# (https://code.claude.com/docs/en/settings-reference, "Settings index"). Other names are withheld.
NAMED = {"additionalDirectories", "agent", "allowedMcpServers", "apiKeyHelper", "awsAuthRefresh",
         "awsCredentialExport", "deniedMcpServers", "disableAllHooks", "disableAutoMode", "disabledMcpjsonServers",
         "enableAllProjectMcpServers", "enabledMcpjsonServers", "enabledPlugins", "env", "extraKnownMarketplaces",
         "gcpAuthRefresh", "hooks", "otelHeadersHelper", "pluginConfigs", "processWrapper", "skipAutoPermissionPrompt",
         "skipDangerousModePermissionPrompt", "sshConfigs", "sshHostCommands", "statusLine", "worktree"}
# A rule is a tool name with an optional specifier in parentheses (permissions page, "Permission rule syntax").
RULE = re.compile(r"([A-Za-z][A-Za-z0-9_]*)(?:\((.*)\))?", re.DOTALL)
UNREADABLE = "Settings file is missing, unreadable, a symlink, or not a JSON object; raw errors were withheld."


class SettingsReader(Reader):
    def read(self, data):
        self.permissions(data.get("permissions", {}))
        self.sandbox(data.get("sandbox", {}))
        others = set(data) - {"permissions", "sandbox"} - PREFERENCES
        if others:
            names = sorted(others & NAMED)
            if others - NAMED:
                names.append("other fields whose names were withheld")
            listed = ", ".join(names[:-1]) + (" and " if len(names) > 1 else "") + names[-1]
            self.gap(f"Settings outside reader coverage were not evaluated: {listed}.")
        return self.entries, sorted(self.gaps)

    def permissions(self, value):
        table = self.table(value, "permissions")
        self.unknown(table, PERMISSIONS, "permissions")
        mode = table.get("defaultMode")
        if "defaultMode" not in table:
            self.gap("permissions.defaultMode is absent; Claude Code's built-in mode depends on how it starts and its "
                     "version, so it was not inferred.")
        elif not isinstance(mode, str) or mode not in MODES:
            self.gap("permissions.defaultMode is unsupported or invalid; its value was withheld.")
        else:
            self.add(["permissions", "defaultMode"], "setting", [mode],
                     {"commands_without_prompts": mode == "bypassPermissions"})
            if mode == "auto":
                self.gap("permissions.defaultMode is auto; a classifier decides which actions run without asking, "
                         "and its decisions are not assessed.")
        overrides = []
        for key in ("deny", "ask"):
            value = table.get(key, [])
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                self.gap(f"permissions.{key} must be a list of rule strings. Its rules were not evaluated.")
            elif value:
                overrides.append(f"{key} rules present")
                self.gap(f"permissions.{key} contains rules that can take precedence over allow. "
                         "Their matches were not checked.")
        rules = table.get("allow", [])
        if not isinstance(rules, list):
            self.gap("permissions.allow is not a list; its rules were not evaluated.")
            rules = []
        for number, rule in enumerate(rules, 1):
            self.allow(number, rule, overrides)

    def allow(self, number, rule, overrides):
        found = RULE.fullmatch(rule) if isinstance(rule, str) else None
        keys = ["permissions", "allow", str(number)]
        if found and found[1] == "Bash":
            spec = (found[2] or "").strip()
            if spec in ("", "*"):  # `Bash` and `Bash(*)` match every command.
                self.add(keys, "allow rule", ["tool: Bash", "broad: every command", *overrides], {"saved_approval": True})
                return
            first = re.split(r"[\s:]", spec, maxsplit=1)[0]  # `Bash(git:*)` and `Bash(git push *)` start with git.
            observations = ["tool: Bash"]
            if first in PROGRAMS:
                observations.append(f"program: {first}")
            self.add(keys, "allow rule", [*observations, *overrides], {"saved_approval": True})
        elif found and found[1] == "WebFetch":
            spec = found[2]
            if spec is None:
                scope = "every address"
            elif spec == "domain:*":
                scope = "every domain"
            elif spec.startswith("domain:") and spec[7:]:
                scope = "addresses withheld"
            else:
                self.gap("permissions.allow contains an unsupported WebFetch specifier. Its value was withheld.")
                return
            self.add(keys, "allow rule", ["tool: WebFetch", scope, *overrides], {"network_access": True})
        else:
            self.gap("permissions.allow contains rules for tools outside reader coverage; they were not evaluated.")

    def sandbox(self, value):
        if not isinstance(value, dict):
            self.gap("sandbox must be a table.")
            return
        self.unknown(value, SANDBOX, "sandbox")
        enabled = self.boolean(value, "enabled", False, "sandbox.enabled")
        if enabled is not None:
            label = str(enabled).lower() if "enabled" in value else "false (default)"
            self.add(["sandbox", "enabled"], "setting", [label])
        key = "autoAllowBashIfSandboxed"
        if key in value:
            auto = self.boolean(value, key, None, f"sandbox.{key}")
            if auto is not None:
                self.add(["sandbox", key], "setting", [str(auto).lower()])
        elif enabled:
            self.gap("sandbox.autoAllowBashIfSandboxed is unset. Its default changed from true to false in "
                     "v2.1.324. Check your Claude Code version to determine how sandboxed Bash approvals work.")


def read_file(path, source, *, discovered=False):
    reader = SettingsReader(source)
    if path.name.casefold() in {".claude.json", ".credentials.json"}:
        reader.gap("Claude Code account and credential files are excluded. Select a settings file instead.")
        return [], sorted(reader.gaps)
    try:
        fd = open_input(path)
        with os.fdopen(fd, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ValueError("not a regular file")
            content = stream.read(MAX_BYTES + 1)
        if len(content) > MAX_BYTES:
            reader.gap("Settings file exceeds the 1 MiB size limit.")
            return [], sorted(reader.gaps)
        data = json.loads(content.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("not an object")
    except FileNotFoundError:
        if not discovered:
            reader.gap(UNREADABLE)
            return [], sorted(reader.gaps)
        reader.add(["settings"], "settings file", ["absent"])
        return reader.read({})
    except (OSError, RecursionError, ValueError):
        reader.gap(UNREADABLE)
        return [], sorted(reader.gaps)
    return reader.read(data)
