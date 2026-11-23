"""The Claude Code report: the same evidence chain as the Codex report, with Claude Code's own wording (issue #163)."""

import re

from .claude import read_file
from .provenance import GAP, REPOSITORY, fingerprints, identify, source_link
from .rules import evaluate

HARNESS = "Claude Code"
SCOPE = [
    "Only the user settings file, or the files selected with --config, are read; project settings "
    "(.claude/settings.json, .claude/settings.local.json), managed settings and command-line flags are not.",
    "Files are independent snapshots; Claude Code combines allow rules from every settings file it loads.",
    "Ask and deny rules, which Claude Code checks before allow rules, are not inspected.",
    "Commands, addresses, paths and other values in rules and settings are withheld, except a first word on "
    "stay-safe's program list.",
]
# Advice for a finding, by rule; {file} names the settings file and {number} the rule's position in
# permissions.allow. Each sentence follows a meaning in harnesses/claude-code.md.
WHAT = {
    ("commands_without_prompts", None):
        "Set `permissions.defaultMode` to `default`, so Claude Code asks before most edits, shell commands and network "
        "requests. Commands your allow rules match still run without asking.",
    ("saved_approval", "broad"):
        "Remove this rule and allow only the commands you run often, for example `Bash(npm run test *)`.",
    ("saved_approval", None):
        "Check that this rule covers only the commands you meant, and remove it if you no longer need it.",
    ("network_access", "broad"):
        "Remove this rule, or limit it to the domains you need, for example `WebFetch(domain:example.com)`.",
    ("network_access", None):
        "Check that you trust every page on that domain, and remove the rule if you no longer need it.",
}
HEADLINES = {
    ("commands_without_prompts", None): "With these settings, Claude Code runs commands and edits files without asking you.",
    ("saved_approval", "broad"): "An allow rule lets Claude Code run every shell command without asking you.",
    ("saved_approval", None): "An allow rule lets Claude Code run matching shell commands without asking you.",
    ("network_access", "broad"): "An allow rule lets Claude Code fetch any web address without asking you.",
    ("network_access", None): "An allow rule lets Claude Code fetch pages from a domain without asking you.",
}
WHY = {
    "commands_without_prompts": "`bypassPermissions` skips permission prompts, so injected or mistaken instructions "
                                "could make it run code you didn't want.",
    "saved_approval": "A rule can cover more than the command you remember: an approval for a program you used to "
                      "download a file can cover uploads too. A deny or ask rule can override it, and stay-safe "
                      "doesn't check whether one does.",
    "network_access": "Injected instructions could send your private data out in a request.",
}
NOTE = ("*Before you change anything:* Claude Code combines settings from several files, and a `--permission-mode` "
        "flag or managed settings can override yours. Change the file named in each finding, then run stay-safe again.")
NOT_CHECKED = ("stay-safe reads only Claude Code settings whose meaning it has checked against Claude Code's docs, and "
               "it skips anything it can't read or check rather than guess. Each item says what to do.")
# Gap message, without its source label -> (lead, what to do).
GAPS = {
    "permissions.defaultMode is absent; Claude Code's built-in mode depends on how it starts and its version, so it "
    "was not inferred.": (
        "**Not checked: which permission mode Claude Code starts in.** Your settings don't set "
        "`permissions.defaultMode`, so Claude Code uses its built-in mode, which depends on its version and how you "
        "start it.",
        "Set `permissions.defaultMode` to the mode you want, such as `default`, so the report can check it."),
    "permissions.defaultMode is auto; a classifier decides which actions run without asking, and its decisions are "
    "not assessed.": (
        "**Not checked: auto mode.** In `auto` mode Claude Code runs without routine prompts, and a classifier "
        "decides which actions may run. stay-safe can't assess those decisions.",
        "If you want to approve shell commands yourself, set `permissions.defaultMode` to `default`."),
    "permissions.defaultMode is unsupported or invalid; its value was withheld.": (
        "**Not checked: `permissions.defaultMode`.** Its value isn't one stay-safe recognizes.",
        "Set it to one of the modes in Claude Code's permission docs."),
    "permissions.allow contains rules for tools outside reader coverage; they were not evaluated.": (
        "**Not checked: some allow rules.** Rules for tools other than `Bash` and `WebFetch`, such as MCP tools, "
        "weren't evaluated.",
        "Review `permissions.allow` yourself."),
    "permissions.allow is not a list; its rules were not evaluated.": (
        "**Not checked: `permissions.allow`.** It isn't a list.",
        "Review `permissions.allow` yourself."),
    "permissions.ask or permissions.deny contains rules; Claude Code checks them before allow rules, and they were "
    "not inspected.": (
        "**Not checked: ask and deny rules.** Claude Code checks them before allow rules, so they can block or ask "
        "about commands an allow rule matches.",
        "Review `permissions.ask` and `permissions.deny` together with each allow-rule finding."),
    "permissions contains fields outside reader coverage; their values were withheld.": (
        "**Not checked: other `permissions` settings,** such as extra directories Claude Code may reach.",
        "Review the `permissions` block yourself."),
    "sandbox contains fields outside reader coverage; their values were withheld.": (
        "**Not checked: other `sandbox` settings,** such as commands excluded from the sandbox or allowed domains.",
        "Review the `sandbox` block yourself."),
    "sandbox.enabled has an invalid boolean; its behavior is unknown.": (
        "**Not checked: `sandbox.enabled`.** It isn't `true` or `false`.", "Set it to `true` or `false`."),
    "permissions must be a table.": (
        "**Not checked: `permissions`.** It isn't a JSON object.", "Review the `permissions` block yourself."),
    "sandbox must be a table.": (
        "**Not checked: `sandbox`.** It isn't a JSON object.", "Review the `sandbox` block yourself."),
    "Settings file exceeds the 1 MiB size limit.": (
        "**Not checked: the settings file.** It is larger than 1 MiB.", "Check the file yourself."),
    "Settings file is missing, unreadable, a symlink, or not a JSON object; raw errors were withheld.": (
        "**Not checked: the settings file.** stay-safe couldn't read it as a JSON object. It doesn't follow symlinks.",
        "Check that the file exists, is readable and holds a JSON object, or pass its target with `--config`."),
    "Claude Code home: ~/.claude.json exists and was not inspected; it holds MCP servers and per-project trust "
    "decisions.": (
        "**Not checked: `~/.claude.json`.** It holds your MCP servers, per-project trust decisions and account "
        "details, so stay-safe doesn't open it.",
        "Run `claude mcp list` to review your MCP servers."),
    "Claude Code home: remote-settings.json exists; settings your organization manages remotely were not inspected.": (
        "**Not checked: remotely managed settings.** Your organization's settings override yours.",
        "Ask your administrator what they allow."),
    "Managed settings: a Claude Code managed settings file exists and was not inspected.": (
        "**Not checked: managed settings.** Settings deployed to this computer override yours.",
        "Ask your administrator what they allow."),
}
FOLDERS = {"agents": "subagents", "commands": "custom commands", "plugins": "plugins", "skills": "skills"}
UNKNOWN = ("**Not checked:** {}", "Review this part of your setup yourself.")
WORDS = {"default": "`default` (asks before most actions)", "manual": "`manual` (asks before most actions)",
         "acceptEdits": "`acceptEdits` (accepts file edits without asking)", "plan": "`plan` (doesn't edit files)",
         "auto": "`auto` (a classifier decides what runs without asking)",
         "dontAsk": "`dontAsk` (refuses anything that would ask)",
         "bypassPermissions": "`bypassPermissions` (skips permission prompts)",
         "false (default)": "off (Claude Code's default)", "true": "on", "false": "off", "absent": "none found",
         "broad: every command": "every command", "every address": "every address",
         "addresses withheld": "some addresses (left out)"}


def inspect(paths, *, discovered=False, gaps=()):
    entries, gaps = [], list(gaps)
    hashes = fingerprints()
    provenance = identify(hashes=hashes)
    for index, path in enumerate(paths, 1):
        found, missing = read_file(path, f"settings-{index}", discovered=discovered)
        entries.extend(found)
        gaps.extend(missing)
    risks = evaluate(entries)
    revision = provenance["source_revision"]
    by_id = {entry["id"]: entry for entry in entries}
    for risk in risks:
        risk["configured_evidence"] = list(by_id[risk["entry"]]["observations"])
        risk["rule_source"] = source_link(revision, "stay_safe/rules.py")
        risk["interpretation_source"] = source_link(revision, "harnesses/claude-code.md")
    from .report import INCIDENT_STATUS, incident_links
    try:
        links = incident_links(revision=revision)
    except (OSError, UnicodeError):
        links = {}
    cited = sorted({i for risk in risks for i in risk["incidents"]}, key=lambda i: int(i[1:]))
    if any(identifier not in links for identifier in cited):
        gaps.append("Committed incident citations are incomplete; source links are unavailable.")
    gaps.extend(f"Incomplete fingerprint: {name} could not be read." for name, value in hashes.items() if value is None)
    if revision is None:
        gaps.append(GAP)
    return {"format_version": 3, "harness": HARNESS, "provenance": provenance, "scope": list(SCOPE),
            "file_inspection": "incomplete" if gaps else "complete for supported fields",
            "catalog": [{k: v for k, v in entry.items() if k != "facts"} for entry in entries],
            "risks": risks, "incident_status": INCIDENT_STATUS,
            "incident_links": {i: links[i] for i in cited if links.get(i)}, "inspection_gaps": gaps}


def heading_id(heading):
    """The anchor GitHub gives a heading, as report.py's anchor() computes it."""
    return re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")


def scope(risk):
    observations = risk["configured_evidence"]
    return "broad" if {"broad: every command", "every address"} & set(observations) else None


def finding(risk, path, number):
    """Lead, What to do, Change it and Check for one finding."""
    from .report import FINDINGS
    rule, key = risk["rule"], (risk["rule"], None if risk["rule"] == "commands_without_prompts" else scope(risk))
    headline, what = HEADLINES.get(key), WHAT.get(key)
    if headline is None:
        return (risk["explanation"], "See the cited incidents.", "*What to do:* Review this setting yourself.")
    if rule == "commands_without_prompts":
        change = (f"*Change it:* `permissions.defaultMode` in {path}, or ask Claude Code: \"Edit {path} to set "
                  f"`permissions.defaultMode` to `default`; show only what you change.\"")
        check = (f"*Check:* Look for `defaultMode` under `permissions` in {path}. A `--permission-mode` flag or "
                 "managed settings can still choose another mode.")
    else:
        change = (f"*Change it:* rule {number} of `permissions.allow` in {path}, or ask Claude Code: \"Show me rule "
                  f"{number} of `permissions.allow` in {path} and remove it; show only what you change.\"")
        check = f"*Check:* Look at `permissions.allow` in {path}."
    return (f"**{headline}** {WHY[rule]}", FINDINGS[rule]["how"],
            "\n\n".join([f"*What to do:* {what}", change, check]))


def gap(text, files):
    source, separator, message = text.partition(": ")
    if not (separator and source.startswith("settings-")):
        source, message = None, text
    lead_step = GAPS.get(message)
    folder = message.removeprefix("Claude Code home: ").removesuffix(" holds items that were not inspected.")
    if lead_step is None and folder in FOLDERS:
        lead_step = (f"**Not checked: {FOLDERS[folder]}.** Your Claude Code folder has {FOLDERS[folder]} in "
                     f"`{folder}`, which Claude Code loads and stay-safe doesn't inspect.",
                     f"Review the {FOLDERS[folder]} you installed.")
    if lead_step is None and message.startswith("Settings outside reader coverage were not evaluated: "):
        names = message.removeprefix("Settings outside reader coverage were not evaluated: ").removesuffix(".")
        lead_step = (f"**Not checked: other settings.** stay-safe doesn't yet read these settings: {names}.",
                     "Review them yourself; settings such as `hooks`, `env` and `apiKeyHelper` can run programs or "
                     "pass values to them.")
    if lead_step is None and message.startswith("Claude Code home: ") and message.endswith(
            "was not found; no Claude Code files were inspected."):
        lead_step = (f"**Not checked: Claude Code.** {message.removeprefix('Claude Code home: ')}",
                     "Check that Claude Code is installed, or select a settings file with `--config`.")
    lead, step = lead_step or (UNKNOWN[0].format(message), UNKNOWN[1])
    return f"{lead}\n\n*What to do:* {step}" + (f"\n\n*File `{files.get(source, source)}`*" if source else "")


def setup_line(entry):
    keys = entry["name"].split(".")
    words = [WORDS.get(o, f"starts with `{o[9:]}`" if o.startswith("program: ") else o.removeprefix("tool: "))
             for o in entry["observations"]]
    if keys[:2] == ["permissions", "allow"]:
        tool, rest = words[0], words[1:]
        return f"- Allow rule {keys[2]}: `{tool}`" + (f", {', '.join(rest)}" if rest else " (details left out)")
    label = {"permissions.defaultMode": "Permission mode", "sandbox.enabled": "Sandbox",
             "settings": "Settings file"}.get(entry["name"], f"`{entry['name']}`")
    return f"- {label}: {', '.join(words)}"


def markdown(report, files=None):
    from .report import GROUPS, PLACE, count, made_by, ordered
    files = {source: path for source, path in (files or {}).items() if path is not None}
    risks, gaps = ordered(report["risks"]), report["inspection_gaps"]
    sources = sorted({entry["source"] for entry in report["catalog"]} - {
        entry["source"] for entry in report["catalog"] if entry["kind"] == "settings file"})
    lines = [f"# {HARNESS} configuration diagnostic", "",
             f"{count(len(risks), 'finding', 'findings')}, {count(len(gaps), 'thing', 'things')} not checked.", ""]
    if sources:
        names = ", ".join(f"`{files.get(s) or s}`" for s in sources)
        lines += [f"stay-safe read your Claude Code settings ({names}). This report describes what "
                  f"{'that file says' if len(sources) == 1 else 'those files say'}, without running Claude Code.", ""]
    else:
        lines += ["stay-safe read no Claude Code settings file. See Not checked for the reason.", ""]
    blocks, titles = [], []
    for number, risk in enumerate(risks, 1):
        source, _, name = risk["entry"].partition(":")
        path = f"`{files[source]}`" if source in files else f"`<{source}>`"
        lead, how, step = finding(risk, path, name.rsplit(".", 1)[-1])
        titles.append(lead[2:].split("**", 1)[0] if lead.startswith("**") else lead)
        citations = ", ".join(f"[{i}]({report['incident_links'][i]})" if i in report["incident_links"] else i
                              for i in risk["incidents"])
        rule = f"`{risk['rule']}`"
        url = source_link(report["provenance"]["source_revision"], f"docs/rules.md#{risk['rule']}")
        if url:
            rule = f"[{rule}]({url})"
        blocks.append("\n\n".join([
            f"### {HARNESS} finding {number}", lead,
            f"*How it has gone wrong:* {how} {citations} ({report['incident_status']}).", step,
            f"*Rule {rule} · setting `{risk['entry']}` = `{'; '.join(risk['configured_evidence'])}`*"]))
    group = None
    for number, (risk, title) in enumerate(zip(risks, titles), 1):
        if PLACE[risk["rule"]][0] != group:
            group = PLACE[risk["rule"]][0]
            lines += [f"**{GROUPS[group][0]}**", ""]
        lines.insert(len(lines) - 1, f"{number}. [{title}](#{heading_id(f'{HARNESS} finding {number}')})")
    if gaps:
        lines += [f"{count(len(gaps), 'thing', 'things')} not checked: see [Not checked]"
                  f"(#{heading_id(f'{HARNESS} not checked')}).", ""]
    lines += [f"## {HARNESS} findings", ""]
    if risks:
        lines += [NOTE, "", "\n\n---\n\n".join(blocks), ""]
    else:
        lines += ["None of stay-safe's rules matched your Claude Code settings. That doesn't mean your setup is safe: "
                  "see what stay-safe didn't check and what this report can't see, below.", ""]
    lines += [f"## {HARNESS} not checked", ""]
    if gaps:
        lines += [NOT_CHECKED, "", "\n\n---\n\n".join(gap(text, files) for text in gaps), ""]
    else:
        lines += ["stay-safe checked every Claude Code setting it supports in the files it read.", ""]
    lines += [f"## {HARNESS} setup", ""]
    groups = {}
    for entry in report["catalog"]:
        groups.setdefault(entry["source"], []).append(setup_line(entry))
    for source, entries in groups.items():
        where = f"`{files[source]}` (`{source}`)" if source in files else f"`{source}`, the file you passed with `--config`"
        lines += [f"**Settings file {where}**", *entries, ""]
    if not groups:
        lines += ["stay-safe found no settings to list.", ""]
    revision = report["provenance"]["source_revision"]
    meanings = source_link(revision, "harnesses/claude-code.md")
    lines += [f"## {HARNESS} sources", "",
              f"- [What each Claude Code setting means, with official evidence]({meanings}) (`harnesses/claude-code.md`)"
              if meanings else "Source links are left out because stay-safe couldn't tell which commit it's running from.",
              "", f"## What the {HARNESS} report can't see", ""]
    lines += [f"- {line}" for line in SCOPE]
    lines += ["", "---", "",
              f"Made by stay-safe {made_by(report['provenance']) if meanings else '(commit unknown)'} · report format "
              f"{report['format_version']} · [Report a problem or suggest an idea]({REPOSITORY}/issues/new/choose)"]
    return "\n".join(lines) + "\n"
