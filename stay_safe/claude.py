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
SANDBOX = {"enabled"}
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
        if mode is None:
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
        rules = table.get("allow", [])
        if not isinstance(rules, list):
            self.gap("permissions.allow is not a list; its rules were not evaluated.")
            rules = []
        for number, rule in enumerate(rules, 1):
            self.allow(number, rule)
        if any(table.get(key) for key in ("ask", "deny")):
            self.gap("permissions.ask or permissions.deny contains rules; Claude Code checks them before allow "
                     "rules, and they were not inspected.")

    def allow(self, number, rule):
        found = RULE.fullmatch(rule) if isinstance(rule, str) else None
        keys = ["permissions", "allow", str(number)]
        if found and found[1] == "Bash":
            spec = (found[2] or "").strip()
            if spec in ("", "*"):  # `Bash` and `Bash(*)` match every command.
                self.add(keys, "allow rule", ["tool: Bash", "broad: every command"], {"saved_approval": True})
                return
            first = re.split(r"[\s:]", spec, maxsplit=1)[0]  # `Bash(git:*)` and `Bash(git push *)` start with git.
            observations = ["tool: Bash"] + [f"program: {first}" for name in PROGRAMS if name == first]
            self.add(keys, "allow rule", observations, {"saved_approval": True})
        elif found and found[1] == "WebFetch":
            scope = "every address" if found[2] is None else "addresses withheld"
            self.add(keys, "allow rule", ["tool: WebFetch", scope], {"network_access": True})
        else:
            self.gap("permissions.allow contains rules for tools outside reader coverage; they were not evaluated.")

    def sandbox(self, value):
        table = self.table(value, "sandbox")
        self.unknown(table, SANDBOX, "sandbox")
        enabled = table.get("enabled")
        if enabled is None:  # https://code.claude.com/docs/en/sandboxing: "The sandbox is off by default."
            self.add(["sandbox", "enabled"], "setting", ["false (default)"])
        elif type(enabled) is bool:
            self.add(["sandbox", "enabled"], "setting", [str(enabled).lower()])
        else:
            self.gap("sandbox.enabled has an invalid boolean; its behavior is unknown.")


def read_file(path, source, *, discovered=False):
    reader = SettingsReader(source)
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
