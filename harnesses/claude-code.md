# Claude Code configuration meanings

Each report describes a settings file. Claude Code combines rules across its settings files and can apply session overrides. See [settings precedence] and [permission modes].

| Input | What the report can establish | Evidence |
|---|---|---|
| Settings file | The user settings file lives at `~/.claude/settings.json`. `CLAUDE_CONFIG_DIR` moves the folder. Explicitly selected settings are independent snapshots. The account and credential files are excluded. | [Settings locations], [account and credential files] |
| `permissions.defaultMode` | Lists the configured mode. `manual` is an alias for `default`. The built-in mode depends on surface and version. Project and project-local settings cannot enable `auto`. The reader leaves an absent mode and the decisions of the `auto` classifier unchecked. | [Modes], [starting mode], [Default mode] |
| `bypassPermissions` | Requests a mode that skips prompts. From v2.1.257, project and project-local settings cannot enable it. The file alone cannot establish the session mode. | [Default mode], [mode exceptions] |
| `permissions.allow` with `Bash` or `Bash(*)` | Both match all Bash commands. A more specific rule matches the commands covered by its pattern. A Bash allowance does not lift sandbox restrictions. | [Tool-wide rules], [Bash patterns], [sandbox and permissions] |
| Bare `WebFetch` | Covers all fetch requests. A bare allowance leaves the sandbox domain list unchanged. | [WebFetch rules] |
| `WebFetch(domain:…)` | Matches the specified domain pattern. `domain:*` covers every fetch domain from v2.1.172 and adds every host to the sandbox network allowlist from v2.1.186. Only the scope is shown. | [WebFetch rules], [sandbox network isolation] |
| `permissions.ask` and `permissions.deny` | A matching deny rule can block an allowed action. A matching ask rule can require approval. The report identifies the lists and leaves their matches unchecked. | [Rule order], [sandbox exceptions] |
| `sandbox.enabled` | A boolean configures Bash sandboxing. When omitted, the documented default is off. | [Sandbox default] |
| `sandbox.autoAllowBashIfSandboxed` | With sandboxing enabled, true requests automatic approval for eligible sandboxed Bash commands. False selects the regular permission flow. The omitted default changed from true to false in v2.1.324. | [Sandbox Bash approval] |
| Other fields | Settings that change only how Claude Code looks or which model it uses are skipped without a gap. Other unsupported settings are inspection gaps. Only documented field names appear in the report; other names are withheld. | [Settings index] |
| File format | Settings files are JSON. `NaN`, `Infinity` and `-Infinity`, which Python's JSON reader accepts, are invalid values. | [JSON settings] |

[Settings locations]: https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/settings.md#L21-L65
[account and credential files]: https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/sandboxing.md#L556
[settings precedence]: https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/settings.md#L211-L231
[permission modes]: https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/settings-reference.md#L1144-L1168
[Modes]: https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/permissions.md#L70-L84
[starting mode]: https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/permission-modes.md#L63-L87
[Default mode]: https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/settings-reference.md#L1144-L1168
[mode exceptions]: https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/permission-modes.md#L32-L46
[Tool-wide rules]: https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/permissions.md#L95-L105
[Bash patterns]: https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/permissions.md#L155-L183
[sandbox and permissions]: https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/sandboxing.md#L673-L705
[WebFetch rules]: https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/permissions.md#L544-L567
[sandbox network isolation]: https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/sandboxing.md#network-isolation
[Rule order]: https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/permissions.md#L52-L60
[sandbox exceptions]: https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/permissions.md#L764-L775
[Sandbox default]: https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/sandboxing.md#L21-L27
[Sandbox Bash approval]: https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/settings-reference.md#L1359-L1371
[Settings index]: https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/settings-reference.md
[JSON settings]: https://github.com/pleaseai/claude-code-docs/blob/161fdcbca8a503b16dbdc4e326dba95c8a5325dd/docs/settings.md#L132
