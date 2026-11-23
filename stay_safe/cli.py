"""The command line: read the selected Codex files and print the report."""
import argparse
import os
from pathlib import Path
import stat
import sys

from . import claude_report
from .report import inspect, render, render_all
from .save import NAME, save
from .provenance import INSTALLED

FEEDBACK = "Report a problem or suggest an idea: https://github.com/chalkbadger/stay-safe/issues/new/choose\n"
SAVE_FOLDER = "the current directory" if INSTALLED else "the stay-safe folder"
NOT_SAVED = f"Could not save {NAME} in {SAVE_FOLDER}; the full report follows.\n"


def open_command(path, platform=None):
    """The line `--save` ends with: a command the user can paste to open the page (archived issue #106).

    stay-safe doesn't run it. The plain path is put in single quotes, where the shell expands nothing, and each `'`
    in it is written as '"'"'; so spaces, double quotes, `$`, backticks and `!` reach the command unchanged.
    """
    opener = "open" if (platform or sys.platform) == "darwin" else "xdg-open"
    quoted = "'" + str(path).replace("'", "'\"'\"'") + "'"
    return f"Saved the formatted report. Open it with: {opener} {quoted}\n"

SYSTEM = Path("/etc/codex")
# Where Claude Code's managed settings live on macOS and on Linux (https://code.claude.com/docs/en/managed-settings,
# "Deploy a managed settings file").
MANAGED = (Path("/Library/Application Support/ClaudeCode"), Path("/etc/claude-code"))
AGENTS = ("codex", "claude")
# The command --help names: the same for `python3 -m stay_safe` and `python3 stay_safe` (issue #48), in the form
# Python 3.14's argparse gives `-m` itself.
PROG = (sys.executable.rsplit("/", 1)[-1] or "python3") + " -m stay_safe"


class Parser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        if status:
            message = (message or "") + FEEDBACK
        super().exit(status, message)

    def error(self, message):
        self.exit(2, "Invalid arguments. Use --help.\n")


def codex_home():
    """Select the directory Codex's find_codex_home selects, or return the gap that stops Codex."""
    value = os.environ.get("CODEX_HOME", "")
    if value:
        try:
            if Path(value).is_dir():
                return Path(value), None
        except OSError:
            pass
        return None, ("Codex home: CODEX_HOME is set but is missing, not a directory or cannot be checked; "
                      "Codex would not start, so no default files were inspected.")
    if os.environ.get("HOME") != "":
        try:
            return Path.home() / ".codex", None
        except RuntimeError:
            pass
    return None, ("Codex home: CODEX_HOME is unset and the home directory cannot be determined; "
                  "no default files were inspected.")


def hooks_json(home):
    """Codex loads hooks.json beside config.toml when Rust's Path::is_file is true; errors count as false."""
    try:
        return (home / "hooks.json").is_file()
    except OSError:
        return False


def plugins_cache(home):
    """Return the observed or unreadable cache gap, or no gap when no version folder is found."""
    def folders(path):
        return [path / name for name in os.listdir(path) if (path / name).is_dir()]
    try:
        if any(folders(plugin) for market in folders(home / "plugins" / "cache") for plugin in folders(market)):
            return "Codex home: plugins/cache holds Codex plugins that were not inspected."
    except FileNotFoundError:
        pass
    except OSError:
        return ("Codex home: Could not check the plugin cache. "
                "Check that you can open plugins/cache in your Codex folder.")
    return None


def skills(home):
    """Return the skills gap when Codex would find a skill in skills/, the unreadable gap, or no gap.

    Codex loads skills from $CODEX_HOME/skills:
    https://github.com/openai/codex/blob/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/ext/skills/src/host_roots.rs#L134-L140
    A skill is a file named SKILL.md anywhere in the walk:
    https://github.com/openai/codex/blob/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/ext/skills/src/loader/discovery.rs#L142-L154
    The walk follows folder links (ext/skills/src/loader/host.rs#L164-L167), skips file links and hidden
    folders, among them Codex's own skills/.system, and lists folders down to depth 6
    (ext/skills/src/loader/mod.rs#L24):
    https://github.com/openai/codex/blob/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/exec-server/src/local_file_system.rs#L837-L839
    https://github.com/openai/codex/blob/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/exec-server/src/local_file_system.rs#L860-L863
    """
    root = home / "skills"
    failed = False

    def mode(path, follow=True):
        """The path's file type, or None when it is absent; other errors, such as PermissionError, propagate.
        Path.is_dir() would report an unreadable folder as absent."""
        try:
            return stat.S_IFMT(path.stat(follow_symlinks=follow).st_mode)
        except (FileNotFoundError, NotADirectoryError):
            return None

    # Breadth-first, as Codex walks, so each folder is first reached by its shortest route and a longer link to it
    # can't hide the folders below it.
    try:
        if mode(root) != stat.S_IFDIR:
            return None
        seen = {root.resolve()}
        queue = [(root, 0)]
        for folder, depth in queue:  # the loop also reaches folders appended while it runs
            try:
                names = sorted(os.listdir(folder))
            except OSError:
                failed = True
                continue
            for name in names:
                path = folder / name
                try:
                    kind = mode(path)
                    if mode(path, follow=False) == stat.S_IFLNK and kind != stat.S_IFDIR:
                        continue  # a file link or a broken link: Codex skips it
                    if name == "SKILL.md" and kind == stat.S_IFREG:
                        return "Codex home: skills holds Codex skills that were not inspected."
                    if kind == stat.S_IFDIR and depth < 6 and not name.startswith(".") and path.resolve() not in seen:
                        seen.add(path.resolve())
                        queue.append((path, depth + 1))
                except OSError:
                    failed = True
    except OSError:
        failed = True
    if failed:
        return ("Codex home: Could not check the skills folder. "
                "Check that you can open skills in your Codex folder.")
    return None


def environments_toml(home):
    """Return the gap for an environments.toml Codex would read, the unreadable gap, or no gap.

    Codex reads it with read_to_string: a missing file, or a broken link, is skipped and other failures are
    errors, so a folder by that name is an error, not a missing file:
    https://github.com/openai/codex/blob/086ccc833bc9cf01024ad2dd6af7dbd421b6bf9a/codex-rs/exec-server/src/environment_toml.rs#L330-L341
    """
    try:
        if not stat.S_ISREG((home / "environments.toml").stat().st_mode):
            return "Codex home: environments.toml is not a file; Codex fails to read it."
    except (FileNotFoundError, NotADirectoryError):
        return None
    except OSError:
        return ("Codex home: Could not check environments.toml. "
                "Check that you can open environments.toml in your Codex folder.")
    return "Codex home: environments.toml exists and was not inspected."


def system_config():
    """Whether Codex's system config folder holds a file Codex loads, or a rules/ folder it cannot list."""
    try:
        if not SYSTEM.is_dir():
            return False
        names = ("config.toml", "managed_config.toml", "requirements.toml")
        if hooks_json(SYSTEM) or any((SYSTEM / name).is_file() for name in names):
            return True
        return any(name.endswith(".rules") for name in os.listdir(SYSTEM / "rules"))
    except FileNotFoundError:
        return False
    except OSError:
        return True


def claude_home(chosen=True):
    """The folder Claude Code keeps user settings in, and how the report names it; None when it can't be found.

    CLAUDE_CONFIG_DIR moves it from ~/.claude (https://code.claude.com/docs/en/settings, "Find or create your
    settings files"). Unless Claude Code was chosen with --agent, a run looks for ~/.claude only through $HOME, so a
    run without HOME checks Codex alone, as it did before Claude Code support."""
    value = os.environ.get("CLAUDE_CONFIG_DIR", "")
    if value:
        home, label = Path(value), "$CLAUDE_CONFIG_DIR"
    elif os.environ.get("HOME") != "" and (chosen or os.environ.get("HOME")):
        try:
            home, label = Path.home() / ".claude", "~/.claude"
        except RuntimeError:
            return None, "~/.claude"
    else:
        return None, "~/.claude"
    try:
        return (home if home.is_dir() else None), label
    except OSError:
        return None, label


def claude_gaps(home, managed=MANAGED):
    """What Claude Code loads beside its user settings that stay-safe names without opening."""
    gaps = []
    try:
        account = [Path.home() / ".claude.json", home / ".claude.json"]
    except RuntimeError:
        account = [home / ".claude.json"]
    if any(path.is_file() for path in account):
        gaps.append("Claude Code home: ~/.claude.json exists and was not inspected; it holds MCP servers and "
                    "per-project trust decisions.")
    if (home / "remote-settings.json").is_file():
        gaps.append("Claude Code home: remote-settings.json exists; settings your organization manages remotely "
                    "were not inspected.")
    for name in ("agents", "commands", "plugins", "skills"):
        try:
            if any(not item.startswith(".") for item in os.listdir(home / name)):
                gaps.append(f"Claude Code home: {name} holds items that were not inspected.")
        except (FileNotFoundError, NotADirectoryError):
            pass
        except OSError:
            gaps.append(f"Claude Code home: Could not check {name}.")
    names = ("managed-settings.json", "managed-settings.d", "managed-mcp.json")
    if any((folder / name).is_file() or (folder / name).is_dir() for folder in managed for name in names):
        gaps.append("Managed settings: a Claude Code managed settings file exists and was not inspected.")
    return gaps


def claude_run(args, chosen):
    """The Claude Code report and its file labels, or None when the default run finds no Claude Code folder."""
    if args.config:
        return claude_report.inspect([Path(p) for p in args.config]), {}
    home, label = claude_home(chosen)
    if home is None:
        if not chosen:
            return None
        return claude_report.inspect([], gaps=[
            f"Claude Code home: {label} was not found; no Claude Code files were inspected."]), {}
    result = claude_report.inspect([home / "settings.json"], discovered=True, gaps=claude_gaps(home))
    return result, {"settings-1": f"{label}/settings.json"}


def main(argv=None):
    parser = Parser(prog=PROG, description="Read Codex configuration files and print a shareable report.")
    parser.add_argument("--config", action="append", metavar="FILE", help="Inspect this file independently; repeat for more files.")
    parser.add_argument("--rules", action="append", metavar="FILE", help="Inspect one saved-rules file independently.")
    parser.add_argument("--agent", action="append", choices=AGENTS,
                        help="Check this coding agent; repeat for both. By default stay-safe checks Codex, and "
                             "Claude Code when its folder exists.")
    parser.add_argument("--format", choices=("markdown", "json"))
    parser.add_argument("--save", action="store_true",
                        help=f"Also save the report as a formatted page, {NAME}, in {SAVE_FOLDER}, and end with a command "
                             "that opens it. Not with --format json.")
    args, extra = parser.parse_known_args(argv)
    if args.save and len(extra) == 1 and not extra[0].startswith("-"):
        parser.exit(2, f"--save takes no path. It saves {NAME} in {SAVE_FOLDER}.\n")
    if extra:
        parser.error("Unexpected arguments.")
    if args.rules and len(args.rules) != 1:
        parser.error("Only one rules file may be selected.")
    if args.save and args.format == "json":
        # A fixed message: it names the options, never a value the user typed.
        parser.exit(2, "--save can't be combined with --format json. Use --help.\n")
    agents = list(dict.fromkeys(args.agent or []))
    if args.config and len(agents) > 1:
        parser.exit(2, "--config needs one --agent: choose codex or claude.\n")
    if args.rules and "claude" in agents:
        parser.exit(2, "--rules reads Codex files only.\n")
    if not agents:
        agents = ["codex"] if args.config or args.rules else ["codex", "claude"]
    runs = []
    if "codex" in agents:
        runs.append(codex_run(args))
    if "claude" in agents:
        run = claude_run(args, chosen="claude" in (args.agent or []))
        if run is not None:
            runs.append(run)
    status = 2 if any(result["inspection_gaps"] for result, _ in runs) else 0
    path = save(render_all(runs, "html")) if args.save else None
    if args.save and path is None:
        sys.stderr.write(NOT_SAVED)
        sys.stderr.flush()
    terminal = args.format is None and sys.stdout.isatty()
    sys.stdout.write(render_all(runs, args.format or ("plain" if terminal else "markdown")))
    if path is not None:
        sys.stdout.write(open_command(path))
    if terminal and not args.save:
        sys.stdout.flush()
        sys.stderr.write("Use --save to save a formatted HTML report.\n")
    if status == 2:
        sys.stdout.flush()
        sys.stderr.write("Inspection incomplete (exit 2). See the report for what wasn't checked.\n")
    return status


def codex_run(args):
    """The Codex report and its file labels, exactly as before --agent existed."""
    paths = [Path(p) for p in args.config or []]
    rules = Path(args.rules[0]) if args.rules else None
    defaults = not args.config and not args.rules
    gaps, files = [], {}
    if args.rules:
        files["rules-1"] = None  # Explicit selection has a source label, but no shareable path.
    if defaults:
        home, gap = codex_home()
        if home is None:
            paths, rules, gaps = [], None, [gap]
        else:
            paths = [home / "config.toml"]
            rules = home / "rules" / "default.rules"
            # The report names these files by where Codex keeps them, never by the expanded folder.
            base = "$CODEX_HOME" if os.environ.get("CODEX_HOME", "") else "~/.codex"
            files = {"config-1": f"{base}/config.toml", "rules-1": f"{base}/rules/default.rules"}
            if hooks_json(home):
                gaps.append("Codex home: hooks.json exists and was not inspected.")
            cache_gap = plugins_cache(home)
            if cache_gap:
                gaps.append(cache_gap)
            gaps.extend(gap for gap in (skills(home), environments_toml(home)) if gap)
            if system_config():
                gaps.append("System config folder: /etc/codex holds Codex configuration that was not inspected.")
    return inspect(paths, rules_path=rules, discovered=defaults, gaps=gaps), files
