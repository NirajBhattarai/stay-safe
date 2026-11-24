import json
import os
import re
import stat

from .codex import MAX_BYTES, Reader, exclude_account_files, open_input
from .codex_rules import PROGRAMS

MODES = {"default", "manual", "acceptEdits", "plan", "auto", "dontAsk", "bypassPermissions"}
PERMISSIONS = {"allow", "ask", "deny", "defaultMode"}
SANDBOX = {"enabled", "autoAllowBashIfSandboxed"}
PREFERENCES = {"$schema", "model", "theme", "language", "verbose", "outputStyle", "editorMode", "tui", "viewMode",
               "alwaysThinkingEnabled", "effortLevel", "autoUpdatesChannel", "cleanupPeriodDays", "timeFormat",
               "timeZone", "prefersReducedMotion", "showTurnDuration", "terminalProgressBarEnabled",
               "spinnerTipsEnabled", "autoCompactEnabled", "fastMode", "feedbackSurveyRate", "spellcheck",
               "syntaxHighlightingDisabled", "vimInsertModeRemaps", "keybindingFlavor", "maxProseWidth",
               "showThinkingSummaries", "autoScrollEnabled", "copyOnSelect", "emojiCompletionEnabled"}
NAMED = {"additionalDirectories", "agent", "allowedMcpServers", "apiKeyHelper", "awsAuthRefresh",
         "awsCredentialExport", "deniedMcpServers", "disableAllHooks", "disableAutoMode", "disabledMcpjsonServers",
         "enableAllProjectMcpServers", "enabledMcpjsonServers", "enabledPlugins", "env", "extraKnownMarketplaces",
         "gcpAuthRefresh", "hooks", "otelHeadersHelper", "pluginConfigs", "processWrapper", "skipAutoPermissionPrompt",
         "skipDangerousModePermissionPrompt", "sshConfigs", "sshHostCommands", "statusLine", "worktree"}
HOOK_FIELDS = {"command": ("command",), "http": ("url",), "mcp_tool": ("server", "tool"), "prompt": ("prompt",),
               "agent": ("prompt",)}
DECISION_EVENTS = {"PreToolUse", "PermissionRequest"}
PROGRAM_SETTINGS = {"hooks", "disableAllHooks"}
COMMAND = "command withheld"
DISABLED = "turned off by disableAllHooks in this file"
UNREAD_ENABLE = ("disableAllHooks turns off the hooks found, but .claude/settings.local.json, managed settings and "
                 "--settings were not read and could turn them back on.")
PROJECT = "project settings"
HTTP = "HTTP hook"
ADDRESS = "address withheld"
DECIDES = "on PreToolUse or PermissionRequest: can approve or change tool calls"
MODEL = "prompt or agent hook; prompt withheld"
RULE = re.compile(r"([A-Za-z][A-Za-z0-9_]*)(?:\((.*)\))?", re.DOTALL)
UNREADABLE = "Settings file is missing, unreadable, a symlink, or not a JSON object; raw errors were withheld."


AUTO_MODE_GAP = ("permissions.defaultMode is auto. Claude Code ignores auto in project and project-local settings. "
                 "Where auto applies, the classifier's decisions are not assessed.")
AUTO_APPROVAL_UNSET = ("sandbox.autoAllowBashIfSandboxed is unset. Its default changed from true to false in "
                      "v2.1.324. Check your Claude Code version to determine how sandboxed Bash approvals work.")


class SettingsReader(Reader):
    scope = None

    def read(self, data):
        self.permissions(data.get("permissions", {}))
        self.sandbox(data.get("sandbox", {}))
        self.programs(data)
        others = set(data) - {"permissions", "sandbox"} - PREFERENCES - PROGRAM_SETTINGS
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
            if self.scope != "project":
                self.gap("permissions.defaultMode is absent; Claude Code's built-in mode depends on how it starts "
                         "and its version, so it was not inferred.")
        elif not isinstance(mode, str) or mode not in MODES:
            self.gap("permissions.defaultMode is unsupported or invalid; its value was withheld.")
        else:
            self.add(["permissions", "defaultMode"], "setting", [mode],
                     {"commands_without_prompts": mode == "bypassPermissions"})
            if mode == "auto":
                self.gap(AUTO_MODE_GAP)
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
            if spec in ("", "*"):
                self.add(keys, "allow rule", ["tool: Bash", "broad: every command", *overrides], {"saved_approval": True})
                return
            first = re.split(r"[\s:]", spec, maxsplit=1)[0]
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

    def programs(self, data):
        disabled = False
        if "disableAllHooks" in data:
            disabled = self.boolean(data, "disableAllHooks", False, "disableAllHooks")
            if disabled is not None:
                self.add(["disableAllHooks"], "setting", [str(disabled).lower()])
        if "hooks" not in data:
            return
        found = self.hooks(data["hooks"])
        tail = ([DISABLED] if disabled else []) + ([PROJECT] if self.scope == "project" else [])
        for kind, name, observations, fact in (("command", ["hooks"], [COMMAND], "configured_program"),
                                                ("http", ["hooks", "http"], [HTTP, ADDRESS], "network_access")):
            if kind in found:
                decides = [DECIDES] if found[kind] & DECISION_EVENTS else []
                self.add(name, "hook", observations + decides + tail, {fact: not disabled})
        if "model" in found:
            self.add(["hooks", "prompt"], "hook", [MODEL] + tail)

    def hooks(self, value):
        if not isinstance(value, dict):
            self.gap("hooks is not an object of hook events; its hooks were not evaluated.")
            return {}
        found = {}
        for event, groups in value.items():
            if not isinstance(groups, list):
                self.gap("hooks contains an event that is not a list of matcher groups; it was not evaluated.")
                continue
            for group in groups:
                handlers = group.get("hooks") if isinstance(group, dict) else None
                if not isinstance(handlers, list):
                    self.gap("hooks contains a matcher group without a list of handlers; it was not evaluated.")
                    continue
                for handler in handlers:
                    kind = handler.get("type") if isinstance(handler, dict) else None
                    field = HOOK_FIELDS.get(kind) if isinstance(kind, str) else None
                    if field is None or not all(nonempty(handler.get(name)) for name in field):
                        self.gap("hooks contains a handler that is not a valid hook; it was not evaluated.")
                    elif kind == "mcp_tool":
                        self.gap("hooks contains MCP tool hooks, which call a tool on an MCP server without asking "
                                 "you; that server was not evaluated.")
                    else:
                        found.setdefault("model" if kind in ("prompt", "agent") else kind, set()).add(event)
        return found

    def sandbox(self, value):
        if not isinstance(value, dict):
            self.gap("sandbox must be a table.")
            return
        self.unknown(value, SANDBOX, "sandbox")
        enabled = self.boolean(value, "enabled", False, "sandbox.enabled")
        if enabled is not None and ("enabled" in value or self.scope != "project"):
            label = str(enabled).lower() if "enabled" in value else "false (default)"
            self.add(["sandbox", "enabled"], "setting", [label])
        key = "autoAllowBashIfSandboxed"
        if key in value:
            auto = self.boolean(value, key, None, f"sandbox.{key}")
            if auto is not None:
                self.add(["sandbox", key], "setting", [str(auto).lower()])
        elif enabled:
            self.gap(AUTO_APPROVAL_UNSET)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def invalid_json_constant(token):
    raise ValueError("Invalid JSON number")


def apply_disable(entries):
    flags = [entry for entry in entries if entry["kind"] == "setting" and entry["name"] == "disableAllHooks"]
    if not flags:
        return []
    winner = flags[-1]
    disabled = winner["observations"] == ["true"]
    for entry in flags[:-1]:
        if entry["observations"] != winner["observations"]:
            entry["observations"].append(f"overridden by {winner['source']}")
    hooks = [entry for entry in entries if entry["kind"] == "hook"]
    for entry in hooks:
        observations = [value for value in entry["observations"] if value != DISABLED]
        if disabled:
            label = (DISABLED if entry["source"] == winner["source"]
                     else f"turned off by disableAllHooks in {winner['source']}")
            observations.insert(len(observations) - (PROJECT in observations), label)
        entry["observations"] = observations
        entry["facts"] = {key: not disabled for key in entry["facts"]}
    return [UNREAD_ENABLE] if disabled and hooks else []


@exclude_account_files
def read_file(path, source, *, discovered=False, sources_read=None, scope=None):
    reader = SettingsReader(source)
    reader.scope = scope
    try:
        fd = open_input(path)
        with os.fdopen(fd, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ValueError("not a regular file")
            content = stream.read(MAX_BYTES + 1)
        if len(content) > MAX_BYTES:
            reader.gap("Settings file exceeds the 1 MiB size limit.")
            return [], sorted(reader.gaps)
        data = json.loads(content.decode("utf-8"), parse_constant=invalid_json_constant)
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
    if sources_read is not None:
        sources_read.append(source)
    return reader.read(data)
