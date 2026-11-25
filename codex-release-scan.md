# Codex release scan

Scanned 8 stable releases: `rust-v0.167.0` → `rust-v0.172.0`.

Source drift only; behavior and uncited callers need review. Progress was not changed.

## rust-v0.167.0 → rust-v0.167.1

Commit: `0a94398fa60c4fac0e7659e4213a0a36e613dd46`

### codex-rs/core/config.schema.json — schema

```diff
--- rust-v0.167.0/codex-rs/core/config.schema.json
+++ rust-v0.167.1/codex-rs/core/config.schema.json
@@ -1132,6 +1132,9 @@
               "type": "boolean"
             },
             "incremental_tools": {
+              "type": "boolean"
+            },
+            "incremental_tools_legacy": {
               "type": "boolean"
             },
             "instant_interrupt": {
@@ -7845,6 +7848,9 @@
         "incremental_tools": {
           "type": "boolean"
         },
+        "incremental_tools_legacy": {
+          "type": "boolean"
+        },
         "instant_interrupt": {
           "type": "boolean"
         },
```

### Configuration fields

[Schema at this release](https://github.com/openai/codex/blob/0a94398fa60c4fac0e7659e4213a0a36e613dd46/codex-rs/core/config.schema.json)

- Added: `features.incremental_tools_legacy`
- Added: `profiles.*.features.incremental_tools_legacy`

## rust-v0.167.1 → rust-v0.167.2

Commit: `ce21072c90d32c40af7a55b60b2fb35c84a43a6a`

### codex-rs/core/config.schema.json — schema

```diff
--- rust-v0.167.1/codex-rs/core/config.schema.json
+++ rust-v0.167.2/codex-rs/core/config.schema.json
@@ -1135,6 +1135,9 @@
               "type": "boolean"
             },
             "incremental_tools_legacy": {
+              "type": "boolean"
+            },
+            "incremental_tools_legacy_gcp": {
               "type": "boolean"
             },
             "instant_interrupt": {
@@ -7851,6 +7854,9 @@
         "incremental_tools_legacy": {
           "type": "boolean"
         },
+        "incremental_tools_legacy_gcp": {
+          "type": "boolean"
+        },
         "instant_interrupt": {
           "type": "boolean"
         },
```

### Configuration fields

[Schema at this release](https://github.com/openai/codex/blob/ce21072c90d32c40af7a55b60b2fb35c84a43a6a/codex-rs/core/config.schema.json)

- Added: `features.incremental_tools_legacy_gcp`
- Added: `profiles.*.features.incremental_tools_legacy_gcp`

## rust-v0.167.2 → rust-v0.168.0

Commit: `9480ec100c3edee9fc69172e8e80a4730444094d`

### codex-rs/config/src/types.rs — apps

```diff
--- rust-v0.167.2/codex-rs/config/src/types.rs
+++ rust-v0.168.0/codex-rs/config/src/types.rs
@@ -744,6 +744,7 @@
     #[default]
     Auto,
     Osc9,
+    Osc777,
     Bel,
 }
 
@@ -752,6 +753,7 @@
         match self {
             NotificationMethod::Auto => write!(f, "auto"),
             NotificationMethod::Osc9 => write!(f, "osc9"),
+            NotificationMethod::Osc777 => write!(f, "osc777"),
             NotificationMethod::Bel => write!(f, "bel"),
         }
     }
@@ -872,6 +874,11 @@
 #[derive(Serialize, Deserialize, Debug, Clone, PartialEq, Default, JsonSchema)]
 #[schemars(deny_unknown_fields)]
 pub struct Tui {
+    /// Preferred hosts for new conversations, indexed by project and local user identity.
+    /// Read from the user configuration only; values are never endpoints or credentials.
+    #[serde(default)]
+    pub default_hosts: BTreeMap<String, BTreeMap<String, String>>,
+
     #[serde(default, flatten)]
     pub notification_settings: TuiNotificationSettings,
 
@@ -930,6 +937,11 @@
     /// Defaults to `true`; alternate-screen restrictions take precedence.
     #[serde(default = "default_true")]
     pub fullscreen_transcript: bool,
+
+    /// Preferred docked sidebar width as a percentage of the terminal. Defaults to one third.
+    #[serde(default)]
+    #[schemars(range(min = 1, max = 99))]
+    pub sidebar_width_percent: Option<u8>,
 
     /// Mouse wheel speed multiplier for transcript scrolling, based on one row per event.
     /// Defaults to `1.0`. Positive fractional values slow scrolling; values above `1.0` speed it up.
```

### codex-rs/core/config.schema.json — schema

```diff
--- rust-v0.167.2/codex-rs/core/config.schema.json
+++ rust-v0.168.0/codex-rs/core/config.schema.json
@@ -839,6 +839,9 @@
             "agent_message_board": {
               "type": "boolean"
             },
+            "agent_message_board_mcp": {
+              "type": "boolean"
+            },
             "analytics_plan_history": {
               "type": "boolean"
             },
@@ -888,6 +891,9 @@
             "async_compaction": {
               "$ref": "#/definitions/FeatureToml_for_AsyncCompactionConfigToml"
             },
+            "async_compaction_root_only": {
+              "type": "boolean"
+            },
             "auth_elicitation": {
               "type": "boolean"
             },
@@ -913,6 +919,9 @@
               "type": "boolean"
             },
             "cli_daybreak": {
+              "type": "boolean"
+            },
+            "cli_resume_account_check": {
               "type": "boolean"
             },
             "code_mode": {
@@ -961,6 +970,9 @@
               "type": "boolean"
             },
             "collaboration_modes": {
+              "type": "boolean"
+            },
+            "command_sessions_world_state": {
               "type": "boolean"
             },
             "compaction_image_budget": {
@@ -1062,10 +1074,16 @@
             "guardian_conversation_history_tools": {
               "type": "boolean"
             },
+            "guardian_denial_reconsideration": {
+              "type": "boolean"
+            },
             "guardian_enhanced_node_repl_transcripts": {
               "type": "boolean"
             },
             "guardian_ext": {
+              "type": "boolean"
+            },
+            "guardian_include_additional_context": {
               "type": "boolean"
             },
             "guardian_native_multi_agent_history": {
@@ -1098,10 +1116,16 @@
             "hooks": {
               "type": "boolean"
             },
+            "hosted_search_policy": {
+              "type": "boolean"
+            },
             "image_detail_original": {
               "type": "boolean"
             },
             "image_generation": {
+              "type": "boolean"
+            },
+            "image_generation_animation": {
               "type": "boolean"
             },
             "image_resize_notice": {
@@ -1132,12 +1156,6 @@
               "type": "boolean"
             },
             "incremental_tools": {
-              "type": "boolean"
-            },
-            "incremental_tools_legacy": {
-              "type": "boolean"
-            },
-            "incremental_tools_legacy_gcp": {
               "type": "boolean"
             },
             "instant_interrupt": {
@@ -1417,6 +1435,9 @@
               "type": "boolean"
             },
             "tui_multi_backend": {
+              "type": "boolean"
+            },
+            "tui_workspace": {
               "type": "boolean"
             },
             "ultrafast_mode": {
@@ -2144,7 +2165,7 @@
           "type": "boolean"
         },
         "sandbox_approval": {
-          "description": "Whether to allow shell command approval requests, including inline `with_additional_permissions` and `require_escalated` requests.",
+          "description": "Whether to allow sandbox escalation approval requests, including inline `with_additional_permissions` and `require_escalated` requests. Dangerous commands can still request approval within existing permissions.",
           "type": "boolean"
         },
         "skill_approval": {
@@ -2157,6 +2178,32 @@
         "mcp_elicitations",
         "rules",
         "sandbox_approval"
+      ],
+      "type": "object"
+    },
+    "GuardianElasticSectionConfigToml": {
+      "additionalProperties": false,
+      "properties": {
+        "max_section_entry_tokens": {
+          "format": "uint",
+          "minimum": 0.0,
+          "type": "integer"
+        },
+        "max_total_section_tokens": {
+          "description": "Upper bound for the section's allocation. Omit to use the global request budget as the upper bound.",
+          "format": "uint",
+          "minimum": 0.0,
+          "type": "integer"
+        },
+        "min_total_section_tokens": {
+          "format": "uint",
+          "minimum": 0.0,
+          "type": "integer"
+        }
+      },
+      "required": [
+        "max_section_entry_tokens",
+        "min_total_section_tokens"
       ],
       "type": "object"
     },
@@ -2229,6 +2276,17 @@
           "maximum": 1.0,
           "minimum": 0.0,
           "type": "number"
+        },
+        "sync_elastic_budgeting": {
+          "description": "Enable elastic allocation for synchronous Guardian requests. Defaults to false.",
+          "type": "boolean"
+        },
+        "sync_elastic_sections": {
+          "additionalProperties": {
+            "$ref": "#/definitions/GuardianElasticSectionConfigToml"
+          },
+          "description": "Named section limits, decoded and validated by Guardian when the switch is enabled.",
+          "type": "object"
         },
         "thread_context": {
           "description": "Deprecated and ignored; thread-owned Guardian context is always enabled.",
@@ -3725,6 +3783,7 @@
       "enum": [
         "auto",
         "osc9",
+        "osc777",
         "bel"
       ],
       "type": "string"
@@ -5053,6 +5112,14 @@
     "ToolsToml": {
       "additionalProperties": false,
       "properties": {
+        "client_search_provider": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/WebSearchProvider"
+            }
+          ],
+          "description": "Client provider preference when the model does not select a provider."
+        },
         "experimental_request_user_input": {
           "$ref": "#/definitions/ExperimentalRequestUserInput"
         },
@@ -5142,6 +5209,17 @@
           "default": false,
           "description": "Deselect read-only transcript or footer text after Copy on select confirms delivery. Editable composer selections remain visible. Defaults to `false` and has no effect when Copy on select is off.",
           "type": "boolean"
+        },
+        "default_hosts": {
+          "additionalProperties": {
+            "additionalProperties": {
+              "type": "string"
+            },
+            "type": "object"
+          },
+          "default": {},
+          "description": "Preferred hosts for new conversations, indexed by project and local user identity. Read from the user configuration only; values are never endpoints or credentials.",
+          "type": "object"
         },
         "disable_paste_burst": {
           "description": "When true, disables burst-paste detection for typed input entirely. All characters are inserted as they are received, and no buffering or placeholder replacement will occur for fast keypress bursts. Overrides the legacy top-level `disable_paste_burst` setting. Defaults to `false`.",
@@ -5239,18 +5317,31 @@
               "yank": null
             },
             "global": {
+              "change_host": null,
               "clear_terminal": null,
               "copy": null,
+              "equalize_pane_widths": null,
               "find_transcript": null,
               "focus_activity": null,
+              "focus_main_composer": null,
+              "focus_pane_left": null,
+              "focus_pane_right": null,
+              "focus_sidebar_content": null,
+              "hide_pane": null,
               "leader": null,
+              "maximize_pane_width": null,
+              "minimize_pane_width": null,
+              "move_divider_left": null,
+              "move_divider_right": null,
               "open_agents": null,
               "open_external_editor": null,
               "open_transcript": null,
               "queue": null,
+              "resize_panes": null,
               "select_transcript": null,
               "submit": null,
               "toggle_fast_mode": null,
+              "toggle_pane_zoom": null,
               "toggle_raw_output": null,
               "toggle_shortcuts": null,
               "toggle_side_conversation": null,
@@ -5490,6 +5581,14 @@
           "default": true,
           "description": "Show startup tooltips in the TUI welcome screen. Defaults to `true`.",
           "type": "boolean"
+        },
+        "sidebar_width_percent": {
+          "default": null,
+          "description": "Preferred docked sidebar width as a percentage of the terminal. Defaults to one third.",
+          "format": "uint8",
+          "maximum": 99.0,
+          "minimum": 1.0,
+          "type": "integer"
         },
         "status_line": {
           "default": null,
@@ -6032,6 +6131,14 @@
       "additionalProperties": false,
       "description": "Global keybindings. These are used when a context does not define an override.",
       "properties": {
+        "change_host": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Change where a new conversation runs."
+        },
         "clear_terminal": {
           "allOf": [
             {
@@ -6047,6 +6154,14 @@
             }
           ],
           "description": "Copy the last agent response to the clipboard."
+        },
+        "equalize_pane_widths": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Equalize visible pane widths."
         },
         "find_transcript": {
           "allOf": [
@@ -6064,6 +6179,46 @@
           ],
           "description": "Focus activity groups in the owned transcript to inspect their details."
         },
+        "focus_main_composer": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Focus the main conversation composer."
+        },
+        "focus_pane_left": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Focus the parent conversation."
+        },
+        "focus_pane_right": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Focus the open side conversation."
+        },
+        "focus_sidebar_content": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Focus the side conversation, or hide it when already focused."
+        },
+        "hide_pane": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Hide the focused sidebar pane."
+        },
         "leader": {
           "allOf": [
             {
@@ -6071,6 +6226,38 @@
             }
           ],
           "description": "Prefix for persistent, context-aware shortcut menus."
+        },
+        "maximize_pane_width": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Maximize the focused pane width."
+        },
+        "minimize_pane_width": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Minimize the focused pane width."
+        },
+        "move_divider_left": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Move the divider left when the side pane has focus."
+        },
+        "move_divider_right": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Move the divider right when the side pane has focus."
         },
         "open_agents": {
           "allOf": [
@@ -6104,6 +6291,14 @@
           ],
           "description": "Queue the current composer draft while a task is running."
         },
+        "resize_panes": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Enter keyboard resize mode for visible dividers."
+        },
         "select_transcript": {
           "allOf": [
             {
@@ -6127,6 +6322,14 @@
             }
           ],
           "description": "Toggle Fast mode."
+        },
+        "toggle_pane_zoom": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Zoom or restore the focused pane."
         },
         "toggle_raw_output": {
           "allOf": [
@@ -6272,18 +6475,31 @@
             }
           ],
           "default": {
+            "change_host": null,
             "clear_terminal": null,
             "copy": null,
+            "equalize_pane_widths": null,
             "find_transcript": null,
             "focus_activity": null,
+            "focus_main_composer": null,
+            "focus_pane_left": null,
+            "focus_pane_right": null,
+            "focus_sidebar_content": null,
+            "hide_pane": null,
             "leader": null,
+            "maximize_pane_width": null,
+            "minimize_pane_width": null,
+            "move_divider_left": null,
+            "move_divider_right": null,
             "open_agents": null,
             "open_external_editor": null,
             "open_transcript": null,
             "queue": null,
+            "resize_panes": null,
             "select_transcript": null,
             "submit": null,
             "toggle_fast_mode": null,
+            "toggle_pane_zoom": null,
             "toggle_raw_output": null,
             "toggle_shortcuts": null,
             "toggle_side_conversation": null,
@@ -7318,6 +7534,14 @@
       ],
       "type": "string"
     },
+    "WebSearchProvider": {
+      "description": "Provider preference selected by the resolved model catalog entry.",
+      "enum": [
+        "standalone",
+        "search_mcp"
+      ],
+      "type": "string"
+    },
     "WebSearchToolConfig": {
       "additionalProperties": false,
       "properties": {
@@ -7556,6 +7780,9 @@
         "agent_message_board": {
           "type": "boolean"
         },
+        "agent_message_board_mcp": {
+          "type": "boolean"
+        },
         "analytics_plan_history": {
           "type": "boolean"
         },
@@ -7605,6 +7832,9 @@
         "async_compaction": {
           "$ref": "#/definitions/FeatureToml_for_AsyncCompactionConfigToml"
         },
+        "async_compaction_root_only": {
+          "type": "boolean"
+        },
         "auth_elicitation": {
           "type": "boolean"
         },
@@ -7630,6 +7860,9 @@
           "type": "boolean"
         },
         "cli_daybreak": {
+          "type": "boolean"
+        },
+        "cli_resume_account_check": {
           "type": "boolean"
         },
         "code_mode": {
@@ -7678,6 +7911,9 @@
           "type": "boolean"
         },
         "collaboration_modes": {
+          "type": "boolean"
+        },
+        "command_sessions_world_state": {
           "type": "boolean"
         },
         "compaction_image_budget": {
@@ -7779,10 +8015,16 @@
         "guardian_conversation_history_tools": {
           "type": "boolean"
         },
+        "guardian_denial_reconsideration": {
+          "type": "boolean"
+        },
         "guardian_enhanced_node_repl_transcripts": {
           "type": "boolean"
         },
         "guardian_ext": {
+          "type": "boolean"
+        },
+        "guardian_include_additional_context": {
           "type": "boolean"
         },
         "guardian_native_multi_agent_history": {
@@ -7815,10 +8057,16 @@
         "hooks": {
           "type": "boolean"
         },
+        "hosted_search_policy": {
+          "type": "boolean"
+        },
         "image_detail_original": {
           "type": "boolean"
         },
         "image_generation": {
+          "type": "boolean"
+        },
+        "image_generation_animation": {
           "type": "boolean"
         },
         "image_resize_notice": {
@@ -7849,12 +8097,6 @@
           "type": "boolean"
         },
         "incremental_tools": {
-          "type": "boolean"
-        },
-        "incremental_tools_legacy": {
-          "type": "boolean"
-        },
-        "incremental_tools_legacy_gcp": {
           "type": "boolean"
         },
         "instant_interrupt": {
@@ -8134,6 +8376,9 @@
           "type": "boolean"
         },
         "tui_multi_backend": {
+          "type": "boolean"
+        },
+        "tui_workspace": {
           "type": "boolean"
         },
         "ultrafast_mode": {
```

### codex-rs/core/src/exec_policy.rs — rule-prompts, saved-runtime

```diff
--- rust-v0.167.2/codex-rs/core/src/exec_policy.rs
+++ rust-v0.168.0/codex-rs/core/src/exec_policy.rs
@@ -429,20 +429,35 @@
                 let prompt_is_rule = evaluation.matched_rules.iter().any(|rule_match| {
                     is_policy_match(rule_match) && rule_match.decision() == evaluation.decision
                 });
-                match prompt_is_rejected_by_policy(approval_policy, prompt_is_rule) {
+                let dangerous_command = dangerous_command_match_for_heuristics(
+                    &evaluation,
+                    Decision::Prompt,
+                    command_origin,
+                    command_platform,
+                );
+                // Reviewing a dangerous command does not grant additional permissions.
+                // Keep explicit rules, escalation requests, and unavailable Windows
+                // sandbox protection on their existing approval-policy paths.
+                let allow_dangerous_command_prompt = matches!(
+                    approval_policy,
+                    AskForApproval::Granular(config) if !config.sandbox_approval
+                ) && !prompt_is_rule
+                    && dangerous_command.is_some()
+                    && !sandbox_permissions.requests_sandbox_override()
+                    && !(command_platform == DangerousCommandPlatform::Windows
+                        && windows_sandbox_level == WindowsSandboxLevel::Disabled
+                        && profile_has_managed_filesystem_restrictions(&permission_profile));
+                let rejection = if allow_dangerous_command_prompt {
+                    None
+                } else {
+                    prompt_is_rejected_by_policy(approval_policy, prompt_is_rule)
+                };
+                match rejection {
                     Some(reason) if prompt_is_rule => ExecApprovalRequirement::Forbidden {
                         reason: reason.to_string(),
                     },
                     Some(reason) => ExecApprovalRequirement::Forbidden {
-                        reason: derive_rejected_prompt_reason(
-                            reason,
-                            dangerous_command_match_for_heuristics(
-                                &evaluation,
-                                Decision::Prompt,
-                                command_origin,
-                                command_platform,
-                            ),
-                        ),
+                        reason: derive_rejected_prompt_reason(reason, dangerous_command),
                     },
                     None if evaluation.decision == Decision::PromptUser => {
                         ExecApprovalRequirement::NeedsHumanApproval {
@@ -451,15 +466,21 @@
                     }
                     None => ExecApprovalRequirement::NeedsApproval {
                         reason: derive_prompt_reason(command, &evaluation),
-                        proposed_execpolicy_amendment: requested_amendment.or_else(|| {
-                            if auto_amendment_allowed {
-                                try_derive_execpolicy_amendment_for_prompt_rules(
-                                    &evaluation.matched_rules,
-                                )
-                            } else {
-                                None
-                            }
-                        }),
+                        // A reusable allow rule can bypass the sandbox on later calls.
+                        // This approval only authorizes execution with current permissions.
+                        proposed_execpolicy_amendment: if allow_dangerous_command_prompt {
+                            None
+                        } else {
+                            requested_amendment.or_else(|| {
+                                if auto_amendment_allowed {
+                                    try_derive_execpolicy_amendment_for_prompt_rules(
+                                        &evaluation.matched_rules,
+                                    )
+                                } else {
+                                    None
+                                }
+                            })
+                        },
                     },
                 }
             }
```

### codex-rs/core/src/mcp_tool_call.rs — full-access-tool-call

```diff
--- rust-v0.167.2/codex-rs/core/src/mcp_tool_call.rs
+++ rust-v0.168.0/codex-rs/core/src/mcp_tool_call.rs
@@ -1577,18 +1659,18 @@
     if !strict_auto_review
         && mcp_permission_prompt_is_auto_approved(
             config.approval_policy.value(),
-            permission_profile,
+            permission_source.profile(),
             McpPermissionPromptAutoApproveContext {
                 tool_approval_mode: Some(policy.mode),
             },
         )
     {
-        return None;
+        return McpToolApprovalRequirement::NotRequired;
     }
 
     let annotations = metadata.annotations.as_ref();
     if !strict_auto_review && !requires_mcp_tool_approval_for_mode(annotations, policy.mode) {
-        return None;
+        return McpToolApprovalRequirement::NotRequired;
     }
 
     let session_approval_key =
```

### codex-rs/ext/skills/src/host_roots.rs — skills-root

```diff
--- rust-v0.167.2/codex-rs/ext/skills/src/host_roots.rs
+++ rust-v0.168.0/codex-rs/ext/skills/src/host_roots.rs
@@ -123,38 +139,42 @@
 
         match &layer.name {
             ConfigLayerSource::Project { .. } => {
-                if let Some(repository_file_system) = &repository_file_system {
+                if let Some(repository_file_system) = repository_file_system {
                     roots.push(HostSkillRoot::host(
                         config_folder.join(SKILLS_DIR_NAME),
                         SkillScope::Repo,
-                        Arc::clone(repository_file_system),
+                        repository_file_system,
                     ));
                 }
             }
             ConfigLayerSource::User { .. } => {
                 // Deprecated user skills location (`$CODEX_HOME/skills`), kept for backward
                 // compatibility.
-                roots.push(local_root(
+                roots.push(HostSkillRoot::host(
                     config_folder.join(SKILLS_DIR_NAME),
                     SkillScope::User,
+                    host,
                 ));
 
                 if let Some(home_dir) = home_dir {
-                    roots.push(local_root(
+                    roots.push(HostSkillRoot::host(
                         home_dir.join(AGENTS_DIR_NAME).join(SKILLS_DIR_NAME),
                         SkillScope::User,
+                        host,
                     ));
                 }
 
-                roots.push(local_root(
+                roots.push(HostSkillRoot::host(
                     system_cache_root_dir(&config_folder),
                     SkillScope::System,
+                    host,
                 ));
             }
             ConfigLayerSource::System { .. } => {
-                roots.push(local_root(
+                roots.push(HostSkillRoot::host(
                     config_folder.join(SKILLS_DIR_NAME),
                     SkillScope::Admin,
+                    host,
                 ));
             }
             ConfigLayerSource::PackagedDefaults { .. }
```

### codex-rs/ext/skills/src/loader/mod.rs — skill-name

```diff
--- rust-v0.167.2/codex-rs/ext/skills/src/loader/mod.rs
+++ rust-v0.168.0/codex-rs/ext/skills/src/loader/mod.rs
@@ -11,11 +11,13 @@
 pub(crate) use environment::load_environment_skills_from_root;
 pub(crate) use host::HostSkillRoot;
 pub(crate) use host::HostSkillRootSnapshot;
+pub(crate) use host::canonicalize_for_skill_identity;
 pub(crate) use host::load_host_skill_root;
 pub(crate) use host_merge::load_and_merge_host_skill_roots;
 pub(crate) use host_merge::load_and_merge_host_skill_roots_with_request_snapshots;
 
 pub(crate) const MAX_CONCURRENT_ROOT_SCANS: usize = 8;
+pub(crate) use discovery::MAX_CONCURRENT_SKILL_LOADS;
 pub(super) const SKILLS_FILENAME: &str = "SKILL.md";
 pub(super) const SKILLS_METADATA_DIR: &str = "agents";
 pub(super) const SKILLS_METADATA_FILENAME: &str = "openai.yaml";
```

### codex-rs/protocol/src/permissions.rs — project-settings-write

```diff
--- rust-v0.167.2/codex-rs/protocol/src/permissions.rs
+++ rust-v0.168.0/codex-rs/protocol/src/permissions.rs
@@ -2643,2045 +2638,5 @@
 }
 
 #[cfg(test)]
-mod tests {
-    use super::*;
-    use pretty_assertions::assert_eq;
-    #[cfg(unix)]
-    use std::fs;
-    use std::path::Path;
-    use tempfile::TempDir;
-
-    #[cfg(unix)]
-    const SYMLINKED_TMPDIR_TEST_ENV: &str = "CODEX_PROTOCOL_TEST_SYMLINKED_TMPDIR";
-
-    #[cfg(unix)]
-    fn symlink_dir(original: &Path, link: &Path) -> std::io::Result<()> {
-        std::os::unix::fs::symlink(original, link)
-    }
-
-    #[cfg(any(target_os = "linux", target_os = "macos"))]
-    #[test]
-    fn writable_roots_protect_gitdir_target_outside_alias_root() {
-        let temp = TempDir::new().expect("tempdir");
-        let base = temp.path().canonicalize().expect("canonical tempdir");
-        let workspace = base.join("workspace");
-        let writable = base.join("writable");
-        let aliases = base.join("readonly-aliases");
-        let gitdir = writable.join("gitdir");
-        fs::create_dir(&workspace).expect("create workspace");
-        fs::create_dir_all(&gitdir).expect("create gitdir");
-        fs::create_dir(&aliases).expect("create aliases");
-        let alias = aliases.join("repo");
-        symlink_dir(&writable, &alias).expect("create alias");
-        fs::write(
-            workspace.join(".git"),
-            format!("gitdir: {}\n", alias.join("gitdir").display()),
-        )
-        .expect("write Git pointer");
-        let policy = FileSystemSandboxPolicy::restricted(
-            [&workspace, &writable]
-                .into_iter()
-                .map(|path| {
-                    FileSystemSandboxEntry::new(
-                        AbsolutePathBuf::from_absolute_path(path)
-                            .expect("absolute root")
-                            .into(),
-                        FileSystemAccessMode::Write,
-                    )
-                })
-                .collect(),
-        );
-        let roots = if cfg!(target_os = "macos") {
-            policy.get_writable_roots_with_cwd_preserving_mutable_paths(&workspace)
-        } else {
-            policy.get_writable_roots_with_cwd(&workspace)
-        };
-        let root = roots
-            .iter()
-            .find(|root| root.root.as_path() == writable)
-            .expect("additional writable root");
-        assert_eq!(
-            root.read_only_subpaths,
-            vec![AbsolutePathBuf::from_absolute_path(gitdir).expect("absolute gitdir")],
-        );
-    }
-
-    #[test]
-    fn permission_paths_preserve_native_strings_across_path_conventions() {
-        for path in [
-            "/workspace/src",
-            r"C:\workspace\src",
-            r"\\server\share\src",
-            r"\\localhost\share",
-        ] {
-            let expected = serde_json::json!({ "type": "path", "path": path });
-            let actual = serde_json::from_value::<RawFileSystemPath>(expected.clone())
-                .expect("valid raw permission path");
-            assert_eq!(
-                serde_json::to_value(actual).expect("lossless raw permission path"),
-                expected
-            );
-        }
-    }
-
-    #[test]
-    fn writable_root_presence_matches_materialized_roots() {
-        let cwd = TempDir::new().expect("tempdir");
-        let writable_root = AbsolutePathBuf::resolve_path_against_base("work", cwd.path());
-        let policies = [
-            FileSystemSandboxPolicy::read_only(),
-            FileSystemSandboxPolicy::unrestricted(),
-            FileSystemSandboxPolicy::external_sandbox(),
-            FileSystemSandboxPolicy::restricted(vec![FileSystemSandboxEntry::new(
-                FileSystemPath::Special {
-                    value: FileSystemSpecialPath::Root,
-                },
-                FileSystemAccessMode::Write,
-            )]),
-            FileSystemSandboxPolicy::restricted(vec![FileSystemSandboxEntry::new(
-                writable_root.clone().into(),
-                FileSystemAccessMode::Write,
-            )]),
-            FileSystemSandboxPolicy::restricted(vec![
-                FileSystemSandboxEntry::new(
-                    writable_root.clone().into(),
-                    FileSystemAccessMode::Write,
-                ),
-                FileSystemSandboxEntry::new(writable_root.into(), FileSystemAccessMode::Deny),
-            ]),
-            FileSystemSandboxPolicy::restricted(vec![FileSystemSandboxEntry::new(
-                FileSystemPath::Special {
-                    value: FileSystemSpecialPath::unknown(
-                        ":future_special_path",
-                        /*subpath*/ None,
-                    ),
-                },
-                FileSystemAccessMode::Write,
-            )]),
-        ];
-
-        for policy in policies {
-            assert_eq!(
-                policy.has_configured_writable_roots_with_cwd(cwd.path()),
-                !policy.get_writable_roots_with_cwd(cwd.path()).is_empty()
-            );
-        }
-    }
-
-    #[cfg(windows)]
-    #[test]
-    fn permission_paths_preserve_native_slash_unc_strings() {
-        for path in ["//server/share/src", r"/\server/share/src"] {
-            let expected = serde_json::json!({ "type": "path", "path": path });
-            let actual = serde_json::from_value::<RawFileSystemPath>(expected.clone())
-                .expect("valid raw slash UNC permission path");
-            assert_eq!(
-                serde_json::to_value(actual).expect("lossless raw slash UNC permission path"),
-                expected
-            );
-        }
-    }
-
-    #[cfg(unix)]
-    #[test]
-    fn native_ambiguous_permission_paths_keep_deny_semantics() {
-        let cwd = TempDir::new().expect("tempdir");
-        for path in ["//server/share/secret", "/C:/secret"] {
-            let denied_path = serde_json::from_value::<RawFileSystemPath>(serde_json::json!({
-                "type": "path",
-                "path": path,
-            }))
-            .expect("raw permission path")
-            .try_into()
-            .expect("runtime permission path");
-            let policy = FileSystemSandboxPolicy::restricted(vec![
-                FileSystemSandboxEntry::new(
-                    FileSystemPath::Special {
-                        value: FileSystemSpecialPath::Root,
-                    },
-                    FileSystemAccessMode::Read,
-                ),
-                FileSystemSandboxEntry::new(denied_path, FileSystemAccessMode::Deny),
-            ]);
-
-            assert!(
-                !policy.can_read_local_path_with_cwd(Path::new(path), cwd.path()),
-                "deny should apply to {path}"
-            );
-            assert!(
-                policy.can_read_local_path_with_cwd(&cwd.path().join("ordinary"), cwd.path()),
-                "opaque deny for {path} should not poison ordinary paths"
-            );
-        }
-    }
-
-    #[test]
-    fn uri_matcher_resolves_selected_executor_paths() {
-        let path = |path| PathUri::parse(path).expect("valid path URI");
-        let cwd = path("file:///C:/workspace");
-        let workspace_roots = [cwd.clone()];
-        let temporary_directories = [path("file:///C:/Temp")];
-        let context = FileSystemSandboxPolicyContext {
-            cwd: &cwd,
-            workspace_roots: &workspace_roots,
-            user_home_dir: None,
-            temporary_directories: Some(&temporary_directories),
-        };
-        let policy = FileSystemSandboxPolicy::restricted(vec![
-            FileSystemSandboxEntry::new(
-                FileSystemPath::Special {
-                    value: FileSystemSpecialPath::Root,
-                },
-                FileSystemAccessMode::Read,
-            ),
-            FileSystemSandboxEntry::new(
-                FileSystemPath::Special {
-                    value: FileSystemSpecialPath::project_roots(/*subpath*/ None),
-                },
-                FileSystemAccessMode::Write,
-            ),
-            FileSystemSandboxEntry::new(
-                path("file:///C:/workspace/private").into(),
-                FileSystemAccessMode::Deny,
-            ),
-            FileSystemSandboxEntry::new(
-                path("file:///C:/workspace/private/public").into(),
-                FileSystemAccessMode::Write,
-            ),
-            FileSystemSandboxEntry::new(
-                FileSystemPath::Special {
-                    value: FileSystemSpecialPath::Tmpdir,
-                },
-                FileSystemAccessMode::Write,
-            ),
-        ]);
-
-        for (candidate, expected) in [
-            (
-                "file:///C:/workspace/src/main.rs",
-                FileSystemAccessMode::Write,
-            ),
-            (
-                "file:///c:/WORKSPACE/private/key",
-                FileSystemAccessMode::Deny,
-            ),
-            (
-                "file:///C:/workspace/private/public/ok",
-                FileSystemAccessMode::Write,
-            ),
-            ("file:///C:/Temp/cache", FileSystemAccessMode::Write),
-            ("file:///C:/outside", FileSystemAccessMode::Read),
-            ("file:///tmp/cache", FileSystemAccessMode::Deny),
-        ] {
-            assert_eq!(
-                policy.resolve_access(&path(candidate), &context),
-                expected,
-                "resolving {candidate}"
-            );
-        }
-        assert!(!policy.can_write_path(&path("file:///c:/WORKSPACE/.git/config"), &context,));
-
-        let scoped = FileSystemSandboxPolicy::restricted(vec![FileSystemSandboxEntry::new(
-            FileSystemPath::Special {
-                value: FileSystemSpecialPath::project_roots(Some("docs/../public".to_string())),
-            },
-            FileSystemAccessMode::Write,
-        )]);
-        assert_eq!(
-            scoped.resolve_access(&path("file:///C:/workspace/public/file"), &context),
-            FileSystemAccessMode::Write
-        );
-        assert_eq!(
-            scoped.resolve_access(&path("file:///C:/outside/file"), &context),
-            FileSystemAccessMode::Deny
-        );
-    }
-
-    #[test]
-    fn uri_matcher_uses_validated_native_components_for_precedence() {
-        let path = |path| PathUri::parse(path).expect("valid path URI");
-        let cwd = path("file:///workspace");
-        let context = FileSystemSandboxPolicyContext {
-            cwd: &cwd,
-            workspace_roots: std::slice::from_ref(&cwd),
-            user_home_dir: None,
-            temporary_directories: None,
-        };
-        let candidate = path("file:///workspace/private/secret/key");
-
-        for (case, writable_path, denied_path) in [
-            (
-                "encoded component",
-                FileSystemPath::Special {
-                    value: FileSystemSpecialPath::Root,
-                },
-                path("file:///workspace/%70rivate").into(),
-            ),
-            (
-                "encoded separator",
-                FileSystemPath::Special {
-                    value: FileSystemSpecialPath::Root,
-                },
-                path("file:///workspace/private%2Fsecret").into(),
-            ),
-            (
-                "repeated separators",
-                path("file:///workspace////").into(),
-                path("file:///workspace/private").into(),
-            ),
-        ] {
-            let policy = FileSystemSandboxPolicy::restricted(vec![
-                FileSystemSandboxEntry::new(writable_path, FileSystemAccessMode::Write),
-                FileSystemSandboxEntry::new(denied_path, FileSystemAccessMode::Deny),
-            ]);
-
-            assert_eq!(
-                policy.resolve_access(&candidate, &context),
-                FileSystemAccessMode::Deny,
-                "resolving {case}"
-            );
-        }
-    }
-
-    #[test]
-    fn uri_matcher_fails_closed_without_executor_roots_or_lexical_paths() {
-        let path = |path| PathUri::parse(path).expect("valid path URI");
-        let cwd = path("file://server/share/workspace");
-        let context = FileSystemSandboxPolicyContext {
-            cwd: &cwd,
-            workspace_roots: &[],
-            user_home_dir: None,
-            temporary_directories: None,
-        };
-        let policy = FileSystemSandboxPolicy::restricted(vec![
-            FileSystemSandboxEntry::new(
-                FileSystemPath::Special {
-                    value: FileSystemSpecialPath::project_roots(/*subpath*/ None),
-                },
-                FileSystemAccessMode::Write,
-            ),
-            FileSystemSandboxEntry::new(
-                FileSystemPath::Special {
-                    value: FileSystemSpecialPath::Tmpdir,
-                },
-                FileSystemAccessMode::Write,
-            ),
-        ]);
-
-        assert_eq!(
-            policy.resolve_access(&cwd, &context),
-            FileSystemAccessMode::Deny
-        );
-        assert_eq!(
-            policy.resolve_access(&path("file:///tmp/cache"), &context),
-            FileSystemAccessMode::Deny
-        );
-
-        let opaque = path("file:///%00/bad/path/YQ");
-        let opaque_context = FileSystemSandboxPolicyContext {
-            cwd: &opaque,
-            workspace_roots: std::slice::from_ref(&opaque),
-            user_home_dir: None,
-            temporary_directories: None,
-        };
-        let opaque_policy = FileSystemSandboxPolicy::restricted(vec![FileSystemSandboxEntry::new(
-            opaque.clone().into(),
-            FileSystemAccessMode::Write,
-        )]);
-        assert_eq!(
-            opaque_policy.resolve_access(&opaque, &opaque_context),
-            FileSystemAccessMode::Deny
-        );
-    }
-
-    #[test]
-    fn uri_deny_and_metadata_matcher_use_executor_paths() {
-        let path = |path| PathUri::parse(path).expect("valid path URI");
-        let cwd = path("file:///C:/workspace");
-        let roots = [cwd.clone()];
-        let context = FileSystemSandboxPolicyContext {
-            cwd: &cwd,
-            workspace_roots: &roots,
-            user_home_dir: None,
-            temporary_directories: None,
-        };
-        let policy = FileSystemSandboxPolicy::restricted(vec![
-            FileSystemSandboxEntry::new(cwd.clone().into(), FileSystemAccessMode::Write),
-            FileSystemSandboxEntry::new(path("file:///C:/").into(), FileSystemAccessMode::Deny),
-            FileSystemSandboxEntry::new(
-                path("file:///C:/workspace/.codex").into(),
-                FileSystemAccessMode::Read,
-            ),
-            unreadable_glob_entry(r"C:\workspace\**\*.env".to_string()),
-        ]);
-        let prepared = policy
-            .prepare_deny_read_matcher(&context, InvalidDenyReadGlobBehavior::ReturnError)
-            .expect("remote deny matcher");
-
-        assert!(prepared.denied_roots.is_empty());
-        assert!(FileSystemSandboxPolicy::matches_prepared_read_deny(
-            &path("file:///c:/WORKSPACE/app/.ENV"),
-            &context,
-            &prepared,
-        ));
-        for candidate in ["file:///%00/bad/path/YQ", "file:///C:/workspace/%2Fsecret"] {
-            assert!(FileSystemSandboxPolicy::matches_prepared_read_deny(
-                &path(candidate),
-                &context,
-                &prepared,
-            ));
-        }
-        assert!(!policy.can_write_path(&path("file:///C:/workspace/.codex/config"), &context));
-        assert_eq!(
-            policy.metadata_write_denial(&path("file:///C:/workspace/.codex/config"), &context),
-            Some(".codex"),
-        );
-    }
-
-    #[test]
-    fn uri_deny_globs_use_executor_home() {
-        for (cwd, home, pattern, candidate) in [
-            (
-                "file:///workspace",
-                "file:///home/executor",
-                "~/private/*.env",
-                "file:///home/executor/private/secret.env",
-            ),
-            (
-                "file:///workspace",
-                "file:///home/executor",
-                "~//private/*.env",
-                "file:///home/executor/private/secret.env",
-            ),
-            (
-                "file:///C:/workspace",
-                "file:///C:/Users/executor",
-                r"~\private\*.env",
-                "file:///C:/Users/executor/private/secret.env",
-            ),
-            (
-                "file:///C:/workspace",
-                "file:///C:/Users/executor",
-                r"~\\private\*.env",
-                "file:///C:/Users/executor/private/secret.env",
-            ),
-        ] {
-            let cwd = PathUri::parse(cwd).expect("executor cwd");
-            let home = PathUri::parse(home).expect("executor home");
-            let candidate = PathUri::parse(candidate).expect("denied path");
-            let context = FileSystemSandboxPolicyContext {
-                cwd: &cwd,
-                workspace_roots: std::slice::from_ref(&cwd),
-                user_home_dir: Some(&home),
-                temporary_directories: None,
-            };
-            let policy = FileSystemSandboxPolicy::restricted(vec![unreadable_glob_entry(
-                pattern.to_string(),
-            )]);
-            let prepared = policy
-                .prepare_deny_read_matcher(&context, InvalidDenyReadGlobBehavior::ReturnError)
-                .expect("home-relative deny glob");
-
-            assert!(FileSystemSandboxPolicy::matches_prepared_read_deny(
-                &candidate, &context, &prepared,
-            ));
-
-            let without_home = FileSystemSandboxPolicyContext {
-                user_home_dir: None,
-                ..context
-            };
-            assert!(
-                policy
-                    .prepare_deny_read_matcher(
-                        &without_home,
-                        InvalidDenyReadGlobBehavior::ReturnError,
-                    )
-                    .is_err()
-            );
-            let prepared = policy
-                .prepare_deny_read_matcher(&without_home, InvalidDenyReadGlobBehavior::FailClosed)
-                .expect("missing executor home fails closed");
-            assert!(prepared.invalid_pattern);
-        }
-    }
-
-    #[test]
-    fn unknown_special_paths_are_ignored_by_legacy_bridge() -> std::io::Result<()> {
-        let policy = FileSystemSandboxPolicy::restricted(vec![
-            FileSystemSandboxEntry {
-                path: FileSystemPath::Special {
-                    value: FileSystemSpecialPath::Root,
-                },
-                access: FileSystemAccessMode::Read,
-                missing_path_behavior: None,
-            },
-            FileSystemSandboxEntry {
-                path: FileSystemPath::Special {
-                    value: FileSystemSpecialPath::unknown(
-                        ":future_special_path",
-                        /*subpath*/ None,
-                    ),
-                },
-                access: FileSystemAccessMode::Write,
-                missing_path_behavior: None,
-            },
-        ]);
-
-        let sandbox_policy = policy.to_legacy_sandbox_policy(
-            NetworkSandboxPolicy::Restricted,
-            Path::new("/tmp/workspace"),
-        )?;
-
-        assert_eq!(
-            sandbox_policy,
-            SandboxPolicy::ReadOnly {
-                network_access: false,
-            }
-        );
-        Ok(())
-    }
-
-    #[cfg(windows)]
-    #[test]
-    fn workspace_write_ignores_slash_tmp_special_path_but_preserves_literal_path() {
-        let cwd = TempDir::new().expect("tempdir");
-        let slash_tmp = AbsolutePathBuf::from_absolute_path("/tmp").expect("absolute tmp path");
-        let slash_tmp_only_policy = FileSystemSandboxPolicy::restricted(vec![
-            FileSystemSandboxEntry::new(
-                FileSystemPath::Special {
-                    value: FileSystemSpecialPath::Root,
-                },
-                FileSystemAccessMode::Read,
-            ),
-            FileSystemSandboxEntry::new(
-                FileSystemPath::Special {
-                    value: FileSystemSpecialPath::SlashTmp,
-                },
-                FileSystemAccessMode::Write,
-            ),
-        ]);
-        assert_eq!(
-            slash_tmp_only_policy
-                .to_legacy_sandbox_policy(NetworkSandboxPolicy::Restricted, cwd.path())
-                .expect("legacy sandbox policy"),
-            SandboxPolicy::ReadOnly {
-                network_access: false,
-            }
-        );
-        assert!(
-            !slash_tmp_only_policy
-                .needs_direct_runtime_enforcement(NetworkSandboxPolicy::Restricted, cwd.path())
-        );
-
-        for access in [FileSystemAccessMode::Read, FileSystemAccessMode::Deny] {
-            let policy = FileSystemSandboxPolicy::restricted(vec![
-                FileSystemSandboxEntry::new(
-                    FileSystemPath::Special {
-                        value: FileSystemSpecialPath::Root,
-                    },
-                    FileSystemAccessMode::Write,
-                ),
-                FileSystemSandboxEntry::new(
-                    FileSystemPath::Special {
-                        value: FileSystemSpecialPath::SlashTmp,
-                    },
-                    access,
-                ),
-            ]);
-            assert!(policy.has_full_disk_write_access());
-            assert!(policy.has_full_disk_read_access());
-        }
-
-        let legacy_policy = SandboxPolicy::new_workspace_write_policy();
-        assert_eq!(
-            FileSystemSandboxPolicy::from(&legacy_policy)
-                .to_legacy_sandbox_policy(NetworkSandboxPolicy::Restricted, cwd.path())
-                .expect("legacy workspace-write policy"),
-            legacy_policy
-        );
-        assert_eq!(
-            FileSystemSandboxPolicy::from(&legacy_policy)
-                .get_writable_roots_with_cwd(cwd.path())
-                .into_iter()
-                .map(|root| root.root)
-                .collect::<Vec<_>>(),
-            legacy_policy
-                .get_writable_roots_with_cwd(cwd.path())
-                .into_iter()
-                .map(|root| normalize_effective_absolute_path(root.root))
-                .collect::<Vec<_>>()
-        );
-        assert!(
-            FileSystemSandboxPolicy::workspace_write(
-                std::slice::from_ref(&slash_tmp),
-                /*exclude_tmpdir_env_var*/ true,
-                /*exclude_slash_tmp*/ false,
-            )
-            .can_write_local_path_with_cwd(slash_tmp.as_path(), cwd.path())
-        );
-    }
-
-    #[cfg(unix)]
-    #[test]
-    fn writable_roots_proactively_protect_missing_dot_codex() {
-        let cwd = TempDir::new().expect("tempdir");
-        let expected_root = AbsolutePathBuf::from_absolute_path(
-            cwd.path().canonicalize().expect("canonicalize cwd"),
-        )
-        .expect("absolute canonical root");
-        let expected_dot_codex = expected_root.join(".codex");
-
-        let policy = FileSystemSandboxPolicy::restricted(vec![FileSystemSandboxEntry {
-            path: FileSystemPath::Special {
-                value: FileSystemSpecialPath::project_roots(/*subpath*/ None),
-            },
-            access: FileSystemAccessMode::Write,
-            missing_path_behavior: None,
-        }]);
-
-        let writable_roots = policy.get_writable_roots_with_cwd(cwd.path());
-        assert_eq!(writable_roots.len(), 1);
-        assert_eq!(writable_roots[0].root, expected_root);
-        assert!(
-            writable_roots[0]
-                .read_only_subpaths
-                .contains(&expected_dot_codex)
-        );
-    }
-
-    #[cfg(target_os = "macos")]
-    #[test]
-    fn preserving_mutable_paths_normalizes_top_level_aliases_consistently() {
-        let root = TempDir::new_in("/tmp").expect("tempdir under /tmp");
-        let logical_root =
-            AbsolutePathBuf::from_absolute_path(root.path()).expect("absolute logical root");
-        let canonical_root = AbsolutePathBuf::from_absolute_path(
-            root.path().canonicalize().expect("canonicalize root"),
-        )
-        .expect("absolute canonical root");
-        let protected = canonical_root.join("protected");
-        fs::create_dir(&protected).expect("create protected path");
-        let policy = FileSystemSandboxPolicy::restricted(vec![
-            FileSystemSandboxEntry::new(logical_root.into(), FileSystemAccessMode::Write),
-            FileSystemSandboxEntry::new(protected.clone().into(), FileSystemAccessMode::Read),
-        ]);
-
-        let roots = policy.get_writable_roots_with_cwd_preserving_mutable_paths(root.path());
-
-        assert_eq!(roots.len(), 1);
-        assert_eq!(roots[0].root, canonical_root);
-        assert!(roots[0].read_only_subpaths.contains(&protected));
-    }
-
-    #[cfg(unix)]
-    #[test]
-    fn preserving_writable_roots_cannot_be_rebound_during_projection() {
-        use std::sync::Arc;
-        use std::sync::atomic::AtomicBool;
-        use std::sync::atomic::AtomicUsize;
-        use std::sync::atomic::Ordering;
-        use std::thread;
-
-        let tmp = TempDir::new().expect("tempdir");
-        let active_ancestor = tmp.path().join("active");
-        let parked_ancestor = tmp.path().join("parked");
-        let outside_ancestor = tmp.path().join("outside");
-        let writable_root = active_ancestor.join("workspace");
-        let outside_root = outside_ancestor.join("workspace");
-        fs::create_dir_all(&writable_root).expect("create writable root");
-        fs::create_dir_all(&outside_root).expect("create outside root");
-        let writable_root =
-            AbsolutePathBuf::from_absolute_path(writable_root).expect("absolute writable root");
-        let outside_root =
-            AbsolutePathBuf::from_absolute_path(outside_root).expect("absolute outside root");
-        let expected_writable_root = writable_root
-            .normalize_system_aliases()
-            .expect("normalize writable root");
-        let expected_outside_root = outside_root
-            .normalize_system_aliases()
-            .expect("normalize outside root");
-        let policy = FileSystemSandboxPolicy::restricted(vec![FileSystemSandboxEntry::new(
-            writable_root.into(),
-            FileSystemAccessMode::Write,
-        )]);
-
-        let stop = Arc::new(AtomicBool::new(false));
-        let swaps = Arc::new(AtomicUsize::new(0));
-        let racer_stop = Arc::clone(&stop);
-        let racer_swaps = Arc::clone(&swaps);
-        let racer = thread::spawn(move || {
-            while !racer_stop.load(Ordering::Relaxed) {
-                if fs::rename(&active_ancestor, &parked_ancestor).is_err() {
-                    thread::yield_now();
-                    continue;
-                }
-                if symlink_dir(&outside_ancestor, &active_ancestor).is_ok() {
-                    racer_swaps.fetch_add(1, Ordering::Relaxed);
-                    thread::yield_now();
-                    let _ = fs::remove_file(&active_ancestor);
-                }
-                fs::rename(&parked_ancestor, &active_ancestor).expect("restore writable ancestor");
-            }
-        });
-
-        let mut rebound_root = None;
-        for _ in 0..2_000 {
-            let roots = policy.get_writable_roots_with_cwd_preserving_mutable_paths(tmp.path());
-            if roots.len() != 1 || roots[0].root != expected_writable_root {
-                rebound_root = roots.first().map(|root| root.root.clone());
-                break;
-            }
-            assert_ne!(roots[0].root, expected_outside_root);
-            thread::yield_now();
-        }
-        stop.store(true, Ordering::Relaxed);
-        racer.join().expect("join path racer");
-
-        assert!(swaps.load(Ordering::Relaxed) > 0, "racer did not run");
-        assert_eq!(rebound_root, None);
-    }
-
-    #[test]
-    fn legacy_workspace_write_projection_preserves_symbolic_project_root() {
-        let policy = SandboxPolicy::WorkspaceWrite {
-            writable_roots: Vec::new(),
-            network_access: false,
-            exclude_tmpdir_env_var: true,
-            exclude_slash_tmp: true,
-        };
-
-        assert_eq!(
-            FileSystemSandboxPolicy::from(&policy),
-            FileSystemSandboxPolicy::restricted(vec![
-                FileSystemSandboxEntry {
-                    path: FileSystemPath::Special {
-                        value: FileSystemSpecialPath::Root,
-                    },
-                    access: FileSystemAccessMode::Read,
-                    missing_path_behavior: None,
-                },
-                FileSystemSandboxEntry {
-                    path: FileSystemPath::Special {
-                        value: FileSystemSpecialPath::project_roots(/*subpath*/ None),
-                    },
-                    access: FileSystemAccessMode::Write,
-                    missing_path_behavior: None,
-                },
-                FileSystemSandboxEntry::skip_missing_path(
-                    FileSystemPath::Special {
-                        value: FileSystemSpecialPath::project_roots(Some(".git".into())),
-                    },
-                    FileSystemAccessMode::Read,
-                ),
-                FileSystemSandboxEntry::skip_missing_path(
-                    FileSystemPath::Special {
-                        value: FileSystemSpecialPath::project_roots(Some(".agents".into())),
-                    },
-                    FileSystemAccessMode::Read,
-                ),
-                FileSystemSandboxEntry::skip_missing_path(
-                    FileSystemPath::Special {
-                        value: FileSystemSpecialPath::project_roots(Some(".codex".into())),
-                    },
-                    FileSystemAccessMode::Read,
-                ),
-                FileSystemSandboxEntry::skip_missing_path(
-                    FileSystemPath::Special {
-                        value: FileSystemSpecialPath::project_roots(Some(".aws".into())),
-                    },
-                    FileSystemAccessMode::Read,
-                ),
-            ])
-        );
-    }
-
-    #[test]
-    fn legacy_current_working_directory_special_path_deserializes_as_project_roots()
-    -> serde_json::Result<()> {
-        let value = serde_json::json!({
-            "kind": "current_working_directory",
-        });
-
-        let special_path = serde_json::from_value::<FileSystemSpecialPath>(value)?;
-        assert_eq!(
-            special_path,
-            FileSystemSpecialPath::project_roots(/*subpath*/ None)
-        );
-        assert_eq!(
-            serde_json::to_value(&special_path)?,
-            serde_json::json!({
-                "kind": "project_roots",
-            })
-        );
-        Ok(())
-    }
-
-    #[cfg(unix)]
-    #[test]
-    fn writable_roots_skip_default_metadata_when_explicit_user_rule_exists() {
-        for name in [".codex", ".aws"] {
-            let cwd = TempDir::new().expect("tempdir");
-            let expected_root = AbsolutePathBuf::from_absolute_path(
-                cwd.path().canonicalize().expect("canonicalize cwd"),
-            )
-            .expect("absolute canonical root");
-            let explicit_metadata = expected_root.join(name);
-            fs::create_dir(&explicit_metadata).expect("create metadata directory");
-
-            let policy = FileSystemSandboxPolicy::restricted(vec![
-                FileSystemSandboxEntry {
-                    path: FileSystemPath::Special {
-                        value: FileSystemSpecialPath::project_roots(/*subpath*/ None),
-                    },
-                    access: FileSystemAccessMode::Write,
-                    missing_path_behavior: None,
-                },
-                FileSystemSandboxEntry {
-                    path: FileSystemPath::Path {
-                        path: explicit_metadata.clone().into(),
-                    },
-                    access: FileSystemAccessMode::Write,
-                    missing_path_behavior: None,
-                },
-            ]);
-
-            let writable_roots = policy.get_writable_roots_with_cwd(cwd.path());
-            let workspace_root = writable_roots
-                .iter()
-                .find(|root| root.root == expected_root)
-                .expect("workspace writable root");
-            assert!(
-                !workspace_root
-                    .protected_metadata_names
-                    .contains(&name.to_string()),
-                "explicit {name} rule should remove the metadata-name protection"
-            );
-            assert!(
-                !workspace_root
-                    .read_only_subpaths
-                    .contains(&explicit_metadata),
-                "explicit {name} rule should win over the default protected carveout"
-            );
-            assert!(policy.can_write_local_path_with_cwd(
-                explicit_metadata.join("config.toml").as_path(),
-                cwd.path()
-            ));
-        }
-    }
-
-    #[test]
-    fn filesystem_policy_blocks_protected_metadata_path_writes_by_default() {
-        let cwd = TempDir::new().expect("tempdir");
-        let dot_git_config = cwd.path().join(".git").join("config");
-        let dot_agents_config = cwd.path().join(".agents").join("config");
-        let dot_codex_config = cwd.path().join(".codex").join("config.toml");
-        let dot_aws_config = cwd.path().join(".aws").join("config");
-        let root = AbsolutePathBuf::from_absolute_path(cwd.path()).expect("absolute cwd");
-        let file_system_policy =
-            FileSystemSandboxPolicy::restricted(vec![FileSystemSandboxEntry {
-                path: root.into(),
-                access: FileSystemAccessMode::Write,
-                missing_path_behavior: None,
-            }]);
-
-        assert!(!file_system_policy.can_write_local_path_with_cwd(&dot_git_config, cwd.path()));
-        assert!(!file_system_policy.can_write_local_path_with_cwd(&dot_agents_config, cwd.path()));
-        assert!(!file_system_policy.can_write_local_path_with_cwd(&dot_codex_config, cwd.path()));
-        assert!(!file_system_policy.can_write_local_path_with_cwd(&dot_aws_config, cwd.path()));
-
-        let writable_roots = file_system_policy.get_writable_roots_with_cwd(cwd.path());
-        assert_eq!(writable_roots.len(), 1);
-        assert_eq!(
-            writable_roots[0].protected_metadata_names,
-            vec![
-                ".git".to_string(),
-                ".agents".to_string(),
-                ".codex".to_string(),
-                ".aws".to_string(),
-            ]
-        );
-        assert!(!writable_roots[0].is_path_writable(&dot_git_config));
-        assert!(!writable_roots[0].is_path_writable(&dot_agents_config));
-        assert!(!writable_roots[0].is_path_writable(&dot_codex_config));
-        assert!(!writable_roots[0].is_path_writable(&dot_aws_config));
-    }
-
-    #[test]
-    fn legacy_workspace_write_projection_accepts_relative_cwd() {
-        let relative_cwd = Path::new("workspace");
-        let expected_root = AbsolutePathBuf::from_absolute_path(
-            std::env::current_dir()
-                .expect("current dir")
-                .join(relative_cwd),
-        )
-        .expect("absolute root");
-        let policy = SandboxPolicy::WorkspaceWrite {
-            writable_roots: vec![],
-            network_access: false,
-            exclude_tmpdir_env_var: true,
-            exclude_slash_tmp: true,
-        };
-
-        let file_system_policy =
-            FileSystemSandboxPolicy::from_legacy_sandbox_policy_for_cwd(&policy, relative_cwd);
-
-        let mut expected_entries = vec![
-            FileSystemSandboxEntry {
-                path: FileSystemPath::Special {
-                    value: FileSystemSpecialPath::Root,
-                },
-                access: FileSystemAccessMode::Read,
-                missing_path_behavior: None,
-            },
-            FileSystemSandboxEntry {
-                path: FileSystemPath::Special {
-                    value: FileSystemSpecialPath::project_roots(/*subpath*/ None),
-                },
-                access: FileSystemAccessMode::Write,
-                missing_path_behavior: None,
-            },
-        ];
-        expected_entries.extend(PROTECTED_METADATA_PATH_NAMES.iter().map(|name| {
-            FileSystemSandboxEntry::skip_missing_path(
-                FileSystemPath::Special {
-                    value: FileSystemSpecialPath::project_roots(Some((*name).into())),
-                },
-                FileSystemAccessMode::Read,
-            )
-        }));
-        expected_entries.extend(
-            default_read_only_subpaths_for_writable_root(
-                &expected_root,
-                /*protect_missing_dot_codex*/ true,
-            )
-            .into_iter()
-            .map(|path| {
-                FileSystemSandboxEntry::skip_missing_path(path.into(), FileSystemAccessMode::Read)
-            }),
-        );
-
-        assert_eq!(
-            file_system_policy,
-            FileSystemSandboxPolicy::restricted(expected_entries)
-        );
-        assert_eq!(
-            forbidden_agent_metadata_write(
-                Path::new(".git/config"),
-                relative_cwd,
-                &file_system_policy,
-            ),
-            Some(".git")
-        );
-        assert!(
-            file_system_policy
-                .can_write_local_path_with_cwd(Path::new("src/main.rs"), relative_cwd,)
-        );
-        assert!(
-            !file_system_policy
-                .can_write_local_path_with_cwd(Path::new(".codex/config.toml"), relative_cwd,)
-        );
-        assert!(!file_system_policy.can_write_local_path_with_cwd(
-            Path::new(".agents/skills/example/SKILL.md"),
-            relative_cwd,
-        ));
-    }
-
-    #[cfg(unix)]
-    #[test]
-    fn effective_runtime_roots_preserve_symlinked_paths() {
-        let cwd = TempDir::new().expect("tempdir");
-        let real_root = cwd.path().join("real");
-        let link_root = cwd.path().join("link");
-        let blocked = real_root.join("blocked");
-        let codex_dir = real_root.join(".codex");
-
-        fs::create_dir_all(&blocked).expect("create blocked");
-        fs::create_dir_all(&codex_dir).expect("create .codex");
-        symlink_dir(&real_root, &link_root).expect("create symlinked root");
-
-        let link_root =
-            AbsolutePathBuf::from_absolute_path(&link_root).expect("absolute symlinked root");
-        let link_blocked = link_root.join("blocked");
-        let expected_root = link_root.clone();
-        let expected_blocked = link_blocked.clone();
-        let expected_codex = link_root.join(".codex");
-
-        let policy = FileSystemSandboxPolicy::restricted(vec![
-            FileSystemSandboxEntry {
-                path: link_root.into(),
-                access: FileSystemAccessMode::Write,
-                missing_path_behavior: None,
-            },
-            FileSystemSandboxEntry {
-                path: link_blocked.into(),
-                access: FileSystemAccessMode::Deny,
-                missing_path_behavior: None,
-            },
-        ]);
-
-        assert_eq!(
-            policy.get_unreadable_roots_with_cwd(cwd.path()),
-            vec![expected_blocked.clone()]
-        );
-
-        let writable_roots = policy.get_writable_roots_with_cwd(cwd.path());
-        assert_eq!(writable_roots.len(), 1);
-        assert_eq!(writable_roots[0].root, expected_root);
-        assert!(
-            writable_roots[0]
-                .read_only_subpaths
-                .contains(&expected_blocked)
-        );
-        assert!(
-            writable_roots[0]
-                .read_only_subpaths
-                .contains(&expected_codex)
-        );
-    }
-
-    #[cfg(unix)]
-    #[test]
-    fn project_roots_special_path_preserves_symlinked_root() {
-        let cwd = TempDir::new().expect("tempdir");
-        let real_root = cwd.path().join("real");
-        let link_root = cwd.path().join("link");
-        let blocked = real_root.join("blocked");
-        let agents_dir = real_root.join(".agents");
-        let codex_dir = real_root.join(".codex");
-
-        fs::create_dir_all(&blocked).expect("create blocked");
-        fs::create_dir_all(&agents_dir).expect("create .agents");
-        fs::create_dir_all(&codex_dir).expect("create .codex");
-        symlink_dir(&real_root, &link_root).expect("create symlinked cwd");
-
-        let link_blocked =
-            AbsolutePathBuf::from_absolute_path(link_root.join("blocked")).expect("link blocked");
-        let expected_root =
-            AbsolutePathBuf::from_absolute_path(&link_root).expect("absolute symlinked root");
-        let expected_blocked = link_blocked.clone();
-        let expected_agents = expected_root.join(".agents");
-        let expected_codex = expected_root.join(".codex");
-
-        let policy = FileSystemSandboxPolicy::restricted(vec![
-            FileSystemSandboxEntry {
-                path: FileSystemPath::Special {
-                    value: FileSystemSpecialPath::Minimal,
-                },
-                access: FileSystemAccessMode::Read,
-                missing_path_behavior: None,
-            },
-            FileSystemSandboxEntry {
-                path: FileSystemPath::Special {
-                    value: FileSystemSpecialPath::project_roots(/*subpath*/ None),
-                },
-                access: FileSystemAccessMode::Write,
-                missing_path_behavior: None,
-            },
-            FileSystemSandboxEntry {
-                path: link_blocked.into(),
-                access: FileSystemAccessMode::Deny,
-                missing_path_behavior: None,
-            },
-        ]);
-
-        assert_eq!(
-            policy.get_readable_roots_with_cwd(&link_root),
-            vec![expected_root.clone()]
-        );
-        assert_eq!(
-            policy.get_unreadable_roots_with_cwd(&link_root),
-            vec![expected_blocked.clone()]
-        );
-
-        let writable_roots = policy.get_writable_roots_with_cwd(&link_root);
-        assert_eq!(writable_roots.len(), 1);
-        assert_eq!(writable_roots[0].root, expected_root);
-        assert!(
-            writable_roots[0]
-                .read_only_subpaths
-                .contains(&expected_blocked)
-        );
-        assert!(
-            writable_roots[0]
-                .read_only_subpaths
-                .contains(&expected_agents)
-        );
-        assert!(
-            writable_roots[0]
-                .read_only_subpaths
-                .contains(&expected_codex)
-        );
-    }
-
-    #[cfg(unix)]
-    #[test]
-    fn writable_roots_preserve_symlinked_protected_subpaths() {
-        let cwd = TempDir::new().expect("tempdir");
-        let root = cwd.path().join("root");
-        let decoy = root.join("decoy-codex");
-        let dot_codex = root.join(".codex");
-        fs::create_dir_all(&decoy).expect("create decoy");
-        symlink_dir(&decoy, &dot_codex).expect("create .codex symlink");
-
-        let root = AbsolutePathBuf::from_absolute_path(&root).expect("absolute root");
-        let expected_dot_codex = AbsolutePathBuf::from_absolute_path(
-            root.as_path()
-                .canonicalize()
-                .expect("canonicalize root")
-                .join(".codex"),
-        )
-        .expect("absolute .codex symlink");
-        let unexpected_decoy =
-            AbsolutePathBuf::from_absolute_path(decoy.canonicalize().expect("canonicalize decoy"))
-                .expect("absolute canonical decoy");
-
-        let policy = FileSystemSandboxPolicy::restricted(vec![FileSystemSandboxEntry {
-            path: root.into(),
-            access: FileSystemAccessMode::Write,
-            missing_path_behavior: None,
-        }]);
-
-        let writable_roots = policy.get_writable_roots_with_cwd(cwd.path());
-        assert_eq!(writable_roots.len(), 1);
-        assert_eq!(
-            writable_roots[0].read_only_subpaths,
-            vec![expected_dot_codex]
-        );
-        assert!(
-            !writable_roots[0]
-                .read_only_subpaths
-                .contains(&unexpected_decoy)
-        );
-    }
-
-    #[cfg(unix)]
-    #[test]
-    fn writable_roots_preserve_explicit_symlinked_carveouts_under_symlinked_roots() {
-        let cwd = TempDir::new().expect("tempdir");
-        let real_root = cwd.path().join("real");
-        let link_root = cwd.path().join("link");
-        let decoy = real_root.join("decoy-private");
-        let linked_private = real_root.join("linked-private");
-        fs::create_dir_all(&decoy).expect("create decoy");
-        symlink_dir(&real_root, &link_root).expect("create symlinked root");
-        symlink_dir(&decoy, &linked_private).expect("create linked-private symlink");
-
-        let link_root =
-            AbsolutePathBuf::from_absolute_path(&link_root).expect("absolute symlinked root");
-        let link_private = link_root.join("linked-private");
-        let expected_root = link_root.clone();
-        let expected_linked_private = link_private.clone();
-        let unexpected_decoy =
-            AbsolutePathBuf::from_absolute_path(decoy.canonicalize().expect("canonicalize decoy"))
-                .expect("absolute canonical decoy");
-
-        let policy = FileSystemSandboxPolicy::restricted(vec![
-            FileSystemSandboxEntry {
-                path: link_root.into(),
-                access: FileSystemAccessMode::Write,
-                missing_path_behavior: None,
-            },
-            FileSystemSandboxEntry {
-                path: link_private.into(),
-                access: FileSystemAccessMode::Deny,
-                missing_path_behavior: None,
-            },
-        ]);
-
-        let writable_roots = policy.get_writable_roots_with_cwd(cwd.path());
-        assert_eq!(writable_roots.len(), 1);
-        assert_eq!(writable_roots[0].root, expected_root);
-        assert_eq!(
-            writable_roots[0].read_only_subpaths,
-            vec![expected_linked_private]
-        );
-        assert!(
-            !writable_roots[0]
-                .read_only_subpaths
-                .contains(&unexpected_decoy)
-        );
-    }
-
-    #[cfg(unix)]
-    #[test]
-    fn writable_roots_preserve_explicit_symlinked_carveouts_that_escape_root() {
-        let cwd = TempDir::new().expect("tempdir");
-        let real_root = cwd.path().join("real");
-        let link_root = cwd.path().join("link");
-        let decoy = cwd.path().join("outside-private");
-        let linked_private = real_root.join("linked-private");
-        fs::create_dir_all(&decoy).expect("create decoy");
-        fs::create_dir_all(&real_root).expect("create real root");
-        symlink_dir(&real_root, &link_root).expect("create symlinked root");
-        symlink_dir(&decoy, &linked_private).expect("create linked-private symlink");
-
-        let link_root =
-            AbsolutePathBuf::from_absolute_path(&link_root).expect("absolute symlinked root");
-        let link_private = link_root.join("linked-private");
-        let expected_root = link_root.clone();
-        let expected_linked_private = link_private.clone();
-        let unexpected_decoy =
-            AbsolutePathBuf::from_absolute_path(decoy.canonicalize().expect("canonicalize decoy"))
-                .expect("absolute canonical decoy");
-
-        let policy = FileSystemSandboxPolicy::restricted(vec![
-            FileSystemSandboxEntry {
-                path: link_root.into(),
-                access: FileSystemAccessMode::Write,
-                missing_path_behavior: None,
-            },
-            FileSystemSandboxEntry {
-                path: link_private.into(),
-                access: FileSystemAccessMode::Deny,
-                missing_path_behavior: None,
-            },
-        ]);
-
-        let writable_roots = policy.get_writable_roots_with_cwd(cwd.path());
-        assert_eq!(writable_roots.len(), 1);
-        assert_eq!(writable_roots[0].root, expected_root);
-        assert_eq!(
-            writable_roots[0].read_only_subpaths,
-            vec![expected_linked_private]
-        );
-        assert!(
-            !writable_roots[0]
-                .read_only_subpaths
-                .contains(&unexpected_decoy)
-        );
-    }
-
-    #[cfg(unix)]
-    #[test]
-    fn writable_roots_preserve_explicit_symlinked_carveouts_that_alias_root() {
-        let cwd = TempDir::new().expect("tempdir");
-        let root = cwd.path().join("root");
-        let alias = root.join("alias-root");
-        fs::create_dir_all(&root).expect("create root");
-        symlink_dir(&root, &alias).expect("create alias symlink");
-
-        let root = AbsolutePathBuf::from_absolute_path(&root).expect("absolute root");
-        let alias = root.join("alias-root");
-        let expected_root = AbsolutePathBuf::from_absolute_path(
-            root.as_path().canonicalize().expect("canonicalize root"),
-        )
-        .expect("absolute canonical root");
-        let expected_alias = expected_root.join("alias-root");
-
-        let policy = FileSystemSandboxPolicy::restricted(vec![
-            FileSystemSandboxEntry {
-                path: root.into(),
-                access: FileSystemAccessMode::Write,
-                missing_path_behavior: None,
-            },
-            FileSystemSandboxEntry {
-                path: alias.into(),
-                access: FileSystemAccessMode::Deny,
-                missing_path_behavior: None,
-            },
-        ]);
-
-        let writable_roots = policy.get_writable_roots_with_cwd(cwd.path());
-        assert_eq!(writable_roots.len(), 1);
-        assert_eq!(writable_roots[0].root, expected_root);
-        assert_eq!(writable_roots[0].read_only_subpaths, vec![expected_alias]);
-    }
-
-    #[cfg(unix)]
-    #[test]
-    fn tmpdir_special_path_preserves_symlinked_tmpdir() {
-        if std::env::var_os(SYMLINKED_TMPDIR_TEST_ENV).is_none() {
-            let output = std::process::Command::new(std::env::current_exe().expect("test binary"))
-                .env(SYMLINKED_TMPDIR_TEST_ENV, "1")
-                .arg("--exact")
-                .arg("permissions::tests::tmpdir_special_path_preserves_symlinked_tmpdir")
-                .output()
-                .expect("run tmpdir subprocess test");
-
-            assert!(
-                output.status.success(),
-                "tmpdir subprocess test failed\nstdout:\n{}\nstderr:\n{}",
-                String::from_utf8_lossy(&output.stdout),
-                String::from_utf8_lossy(&output.stderr)
-            );
-            return;
-        }
-
-        let cwd = TempDir::new().expect("tempdir");
-        let real_tmpdir = cwd.path().join("real-tmpdir");
-        let link_tmpdir = cwd.path().join("link-tmpdir");
-        let blocked = real_tmpdir.join("blocked");
-        let codex_dir = real_tmpdir.join(".codex");
-
-        fs::create_dir_all(&blocked).expect("create blocked");
-        fs::create_dir_all(&codex_dir).expect("create .codex");
-        symlink_dir(&real_tmpdir, &link_tmpdir).expect("create symlinked tmpdir");
-
-        let link_blocked =
-            AbsolutePathBuf::from_absolute_path(link_tmpdir.join("blocked")).expect("link blocked");
-        let expected_root =
-            AbsolutePathBuf::from_absolute_path(&link_tmpdir).expect("absolute symlinked tmpdir");
-        let expected_blocked = link_blocked.clone();
-        let expected_codex = expected_root.join(".codex");
-
-        unsafe {
-            std::env::set_var("TMPDIR", &link_tmpdir);
-        }
-
-        let policy = FileSystemSandboxPolicy::restricted(vec![
-            FileSystemSandboxEntry {
-                path: FileSystemPath::Special {
-                    value: FileSystemSpecialPath::Tmpdir,
-                },
-                access: FileSystemAccessMode::Write,
-                missing_path_behavior: None,
-            },
-            FileSystemSandboxEntry {
-                path: link_blocked.into(),
-                access: FileSystemAccessMode::Deny,
-                missing_path_behavior: None,
-            },
-        ]);
-
-        assert_eq!(
-            policy.get_unreadable_roots_with_cwd(cwd.path()),
-            vec![expected_blocked.clone()]
-        );
-
-        let writable_roots = policy.get_writable_roots_with_cwd(cwd.path());
-        assert_eq!(writable_roots.len(), 1);
-        assert_eq!(writable_roots[0].root, expected_root);
-        assert!(
-            writable_roots[0]
-                .read_only_subpaths
-                .contains(&expected_blocked)
-        );
-        assert!(
-            writable_roots[0]
-                .read_only_subpaths
-                .contains(&expected_codex)
-        );
-    }
-
-    #[test]
-    fn resolve_access_for_local_path_with_cwd_uses_most_specific_entry() {
-        let cwd = TempDir::new().expect("tempdir");
-        let docs = AbsolutePathBuf::resolve_path_against_base("docs", cwd.path());
-        let docs_private = AbsolutePathBuf::resolve_path_against_base("docs/private", cwd.path());
-        let docs_private_public =
-            AbsolutePathBuf::resolve_path_against_base("docs/private/public", cwd.path());
-        let policy = FileSystemSandboxPolicy::restricted(vec![
-            FileSystemSandboxEntry {
-                path: FileSystemPath::Special {
-                    value: FileSystemSpecialPath::project_roots(/*subpath*/ None),
-                },
-                access: FileSystemAccessMode::Write,
-                missing_path_behavior: None,
-            },
-            FileSystemSandboxEntry {
-                path: docs.clone().into(),
-                access: FileSystemAccessMode::Read,
-                missing_path_behavior: None,
-            },
-            FileSystemSandboxEntry {
-                path: FileSystemPath::Path {
-                    path: docs_private.clone().into(),
-                },
-                access: FileSystemAccessMode::Deny,
-                missing_path_behavior: None,
-            },
-            FileSystemSandboxEntry {
-                path: FileSystemPath::Path {
-                    path: docs_private_public.clone().into(),
-                },
-                access: FileSystemAccessMode::Write,
-                missing_path_behavior: None,
-            },
-        ]);
-
-        assert_eq!(
-            policy.resolve_access_for_local_path_with_cwd(cwd.path(), cwd.path()),
-            FileSystemAccessMode::Write
-        );
-        assert_eq!(
-            policy.resolve_access_for_local_path_with_cwd(docs.as_path(), cwd.path()),
-            FileSystemAccessMode::Read
-        );
-        assert_eq!(
-            policy.resolve_access_for_local_path_with_cwd(docs_private.as_path(), cwd.path()),
-            FileSystemAccessMode::Deny
-        );
-        assert_eq!(
-            policy
-                .resolve_access_for_local_path_with_cwd(docs_private_public.as_path(), cwd.path()),
-            FileSystemAccessMode::Write
-        );
-    }
-
-    #[test]
-    fn split_only_nested_carveouts_need_direct_runtime_enforcement() {
-        let cwd = TempDir::new().expect("tempdir");
-        let docs = AbsolutePathBuf::resolve_path_against_base("docs", cwd.path());
-        let policy = FileSystemSandboxPolicy::restricted(vec![
-            FileSystemSandboxEntry {
-                path: FileSystemPath::Special {
-                    value: FileSystemSpecialPath::project_roots(/*subpath*/ None),
-                },
-                access: FileSystemAccessMode::Write,
-                missing_path_behavior: None,
-            },
-            FileSystemSandboxEntry {
-                path: docs.into(),
-                access: FileSystemAccessMode::Read,
-                missing_path_behavior: None,
-            },
-        ]);
-
-        assert!(
-            policy.needs_direct_runtime_enforcement(NetworkSandboxPolicy::Restricted, cwd.path(),)
-        );
-
-        let legacy_workspace_write = legacy_runtime_file_system_policy_for_cwd(
-            &SandboxPolicy::new_workspace_write_policy(),
-            cwd.path(),
-        );
-        assert!(
-            legacy_workspace_write
-                .needs_direct_runtime_enforcement(NetworkSandboxPolicy::Restricted, cwd.path(),),
-            "metadata-name protections must stay in the direct enforcement path even when legacy concrete read-only paths match"
-        );
-    }
-
-    #[test]
-    fn legacy_projection_runtime_enforcement_ignores_entry_order() {
-        let cwd = TempDir::new().expect("tempdir");
-        let legacy_policy = SandboxPolicy::WorkspaceWrite {
-            writable_roots: Vec::new(),
-            network_access: false,
-            exclude_tmpdir_env_var: true,
-            exclude_slash_tmp: true,
-        };
-        let legacy_order = legacy_runtime_file_system_policy_for_cwd(&legacy_policy, cwd.path());
-        let mut reordered_entries = legacy_order.entries.clone();
-        reordered_entries.reverse();
-        let reordered = FileSystemSandboxPolicy::restricted(reordered_entries);
-
-        assert!(
-            legacy_order.is_semantically_equivalent_to(&reordered, cwd.path()),
-            "entry order should not affect filesystem semantics"
-        );
-        assert_eq!(
-            legacy_order
-                .needs_direct_runtime_enforcement(NetworkSandboxPolicy::Restricted, cwd.path()),
-            reordered
-                .needs_direct_runtime_enforcement(NetworkSandboxPolicy::Restricted, cwd.path()),
-            "entry order should not affect direct-enforcement classification"
-        );
-    }
-
-    #[test]
-    fn missing_symbolic_metadata_carveouts_need_direct_runtime_enforcement() {
-        let cwd = TempDir::new().expect("tempdir");
-        let legacy_policy = SandboxPolicy::WorkspaceWrite {
-            writable_roots: Vec::new(),
-            network_access: false,
-            exclude_tmpdir_env_var: true,
-            exclude_slash_tmp: true,
-        };
-
-        let profile_projection =
-            FileSystemSandboxPolicy::from_legacy_sandbox_policy_for_cwd(&legacy_policy, cwd.path());
-        assert!(
-            profile_projection
-                .needs_direct_runtime_enforcement(NetworkSandboxPolicy::Restricted, cwd.path()),
-            "symbolic .git/.agents carveouts protect missing paths that legacy sandboxes cannot represent"
-        );
-
-        let legacy_runtime_projection =
-            legacy_runtime_file_system_policy_for_cwd(&legacy_policy, cwd.path());
-        assert!(
-            legacy_runtime_projection
-                .needs_direct_runtime_enforcement(NetworkSandboxPolicy::Restricted, cwd.path()),
-            "metadata-name protections are outside the legacy SandboxPolicy writable-root contract"
-        );
-    }
-
-    #[test]
-    fn root_write_with_read_only_child_is_not_full_disk_write() {
-        let cwd = TempDir::new().expect("tempdir");
-        let docs = AbsolutePathBuf::resolve_path_against_base("docs", cwd.path());
-        let policy = FileSystemSandboxPolicy::restricted(vec![
-            FileSystemSandboxEntry {
-                path: FileSystemPath::Special {
-                    value: FileSystemSpecialPath::Root,
-                },
-                access: FileSystemAccessMode::Write,
-                missing_path_behavior: None,
-            },
-            FileSystemSandboxEntry {
-                path: docs.clone().into(),
-                access: FileSystemAccessMode::Read,
-                missing_path_behavior: None,
-            },
-        ]);
-
-        assert!(!policy.has_full_disk_write_access());
-        assert_eq!(
-            policy.resolve_access_for_local_path_with_cwd(docs.as_path(), cwd.path()),
-            FileSystemAccessMode::Read
-        );
-        assert!(
-            policy.needs_direct_runtime_enforcement(NetworkSandboxPolicy::Restricted, cwd.path(),)
-        );
-        assert!(
-            policy
-                .to_legacy_sandbox_policy(NetworkSandboxPolicy::Restricted, cwd.path())
-                .is_err()
-        );
-    }
-
-    #[test]
-    fn root_deny_does_not_materialize_as_unreadable_root() {
-        let cwd = TempDir::new().expect("tempdir");
-        let docs = AbsolutePathBuf::resolve_path_against_base("docs", cwd.path());
-        let expected_docs = AbsolutePathBuf::from_absolute_path(
-            canonicalize_preserving_symlinks(cwd.path())
-                .expect("canonicalize cwd")
-                .join("docs"),
-        )
-        .expect("canonical docs");
-        let policy = FileSystemSandboxPolicy::restricted(vec![
-            FileSystemSandboxEntry {
-                path: FileSystemPath::Special {
-                    value: FileSystemSpecialPath::Root,
-                },
-                access: FileSystemAccessMode::Deny,
-                missing_path_behavior: None,
-            },
-            FileSystemSandboxEntry {
-                path: docs.clone().into(),
-                access: FileSystemAccessMode::Read,
-                missing_path_behavior: None,
-            },
-        ]);
-
-        assert_eq!(
-            policy.resolve_access_for_local_path_with_cwd(docs.as_path(), cwd.path()),
-            FileSystemAccessMode::Read
-        );
-        assert_eq!(
-            policy.get_readable_roots_with_cwd(cwd.path()),
-            vec![expected_docs]
-        );
-        assert!(policy.get_unreadable_roots_with_cwd(cwd.path()).is_empty());
-    }
-
-    #[test]
-    fn duplicate_root_deny_prevents_full_disk_write_access() {
-        let cwd = TempDir::new().expect("tempdir");
-        let root = AbsolutePathBuf::from_absolute_path(cwd.path())
-            .map(|cwd| absolute_root_path_for_cwd(&cwd))
-            .expect("resolve filesystem root");
-        let policy = FileSystemSandboxPolicy::restricted(vec![
-            FileSystemSandboxEntry {
-                path: FileSystemPath::Special {
-                    value: FileSystemSpecialPath::Root,
-                },
-                access: FileSystemAccessMode::Write,
-                missing_path_behavior: None,
-            },
-            FileSystemSandboxEntry {
-                path: FileSystemPath::Special {
-                    value: FileSystemSpecialPath::Root,
-                },
-                access: FileSystemAccessMode::Deny,
-                missing_path_behavior: None,
-            },
-        ]);
-
-        assert!(!policy.has_full_disk_write_access());
-        assert_eq!(
-            policy.resolve_access_for_local_path_with_cwd(root.as_path(), cwd.path()),
-            FileSystemAccessMode::Deny
-        );
-    }
-
-    #[test]
-    fn same_specificity_write_override_keeps_full_disk_write_access() {
-        let cwd = TempDir::new().expect("tempdir");
-        let docs = AbsolutePathBuf::resolve_path_against_base("docs", cwd.path());
-        let policy = FileSystemSandboxPolicy::restricted(vec![
-            FileSystemSandboxEntry {
-                path: FileSystemPath::Special {
-                    value: FileSystemSpecialPath::Root,
-                },
-                access: FileSystemAccessMode::Write,
-                missing_path_behavior: None,
-            },
-            FileSystemSandboxEntry {
-                path: docs.clone().into(),
-                access: FileSystemAccessMode::Read,
-                missing_path_behavior: None,
-            },
-            FileSystemSandboxEntry {
-                path: docs.clone().into(),
-                access: FileSystemAccessMode::Write,
-                missing_path_behavior: None,
-            },
-        ]);
-
-        assert!(policy.has_full_disk_write_access());
-        assert_eq!(
-            policy.resolve_access_for_local_path_with_cwd(docs.as_path(), cwd.path()),
-            FileSystemAccessMode::Write
-        );
-    }
-
-    #[test]
-    fn with_additional_readable_roots_skips_existing_effective_access() {
-        let cwd = TempDir::new().expect("tempdir");
-        let cwd_root = AbsolutePathBuf::from_absolute_path(cwd.path()).expect("absolute cwd");
-        let policy = FileSystemSandboxPolicy::restricted(vec![FileSystemSandboxEntry {
-            path: FileSystemPath::Special {
-                value: FileSystemSpecialPath::project_roots(/*subpath*/ None),
-            },
-            access: FileSystemAccessMode::Read,
-            missing_path_behavior: None,
-        }]);
-
-        let actual = policy
-            .clone()
-            .with_additional_readable_roots(cwd.path(), std::slice::from_ref(&cwd_root));
-
-        assert_eq!(actual, policy);
-    }
-
-    #[test]
-    fn with_additional_writable_roots_skips_existing_effective_access() {
-        let cwd = TempDir::new().expect("tempdir");
-        let cwd_root = AbsolutePathBuf::from_absolute_path(cwd.path()).expect("absolute cwd");
-        let policy = FileSystemSandboxPolicy::restricted(vec![FileSystemSandboxEntry {
-            path: FileSystemPath::Special {
-                value: FileSystemSpecialPath::project_roots(/*subpath*/ None),
-            },
-            access: FileSystemAccessMode::Write,
-            missing_path_behavior: None,
-        }]);
-
-        let actual = policy
-            .clone()
-            .with_additional_writable_roots(cwd.path(), std::slice::from_ref(&cwd_root));
-
-        assert_eq!(actual, policy);
-    }
-
-    #[test]
-    fn with_additional_writable_roots_adds_new_root() {
-        let temp_dir = TempDir::new().expect("tempdir");
-        let cwd = temp_dir.path().join("workspace");
-        let extra = AbsolutePathBuf::from_absolute_path(temp_dir.path().join("extra"))
-            .expect("resolve extra root");
-        let policy = FileSystemSandboxPolicy::restricted(vec![FileSystemSandboxEntry {
-            path: FileSystemPath::Special {
-                value: FileSystemSpecialPath::project_roots(/*subpath*/ None),
-            },
-            access: FileSystemAccessMode::Write,
-            missing_path_behavior: None,
-        }]);
-
-        let actual = policy.with_additional_writable_roots(&cwd, std::slice::from_ref(&extra));
-
-        assert_eq!(
-            actual,
-            FileSystemSandboxPolicy::restricted(vec![
-                FileSystemSandboxEntry {
-                    path: FileSystemPath::Special {
-                        value: FileSystemSpecialPath::project_roots(/*subpath*/ None),
-                    },
-                    access: FileSystemAccessMode::Write,
-                    missing_path_behavior: None,
-                },
-                FileSystemSandboxEntry {
-                    path: extra.into(),
-                    access: FileSystemAccessMode::Write,
-                    missing_path_behavior: None,
-                },
-            ])
-        );
-    }
-
-    #[test]
-    fn materialize_project_roots_with_workspace_roots_expands_exact_and_glob_entries() {
-        let temp_dir = TempDir::new().expect("tempdir");
-        let first = AbsolutePathBuf::from_absolute_path(temp_dir.path().join("first"))
-            .expect("resolve first root");
-        let second = AbsolutePathBuf::from_absolute_path(temp_dir.path().join("second"))
-            .expect("resolve second root");
-        let policy = FileSystemSandboxPolicy::restricted(vec![
-            FileSystemSandboxEntry {
-                path: FileSystemPath::Special {
-                    value: FileSystemSpecialPath::project_roots(/*subpath*/ None),
-                },
-                access: FileSystemAccessMode::Write,
-                missing_path_behavior: None,
-            },
-            FileSystemSandboxEntry {
-                path: FileSystemPath::Special {
-                    value: FileSystemSpecialPath::project_roots(Some(".git".into())),
-                },
-                access: FileSystemAccessMode::Read,
-                missing_path_behavior: None,
-            },
-            FileSystemSandboxEntry {
-                path: FileSystemPath::GlobPattern {
-                    pattern: project_roots_glob_pattern(Path::new("**/*.env")),
-                },
-                access: FileSystemAccessMode::Deny,
-                missing_path_behavior: None,
-            },
-        ]);
-
-        let actual =
-            policy.materialize_project_roots_with_workspace_roots(&[first.clone(), second.clone()]);
-
-        assert_eq!(
-            actual,
-            FileSystemSandboxPolicy::restricted(vec![
-                FileSystemSandboxEntry {
-                    path: FileSystemPath::Path {
-                        path: first.clone().into(),
-                    },
-                    access: FileSystemAccessMode::Write,
-                    missing_path_behavior: None,
-                },
-                FileSystemSandboxEntry {
-                    path: FileSystemPath::Path {
-                        path: second.clone().into(),
-                    },
-                    access: FileSystemAccessMode::Write,
-                    missing_path_behavior: None,
-                },
-                FileSystemSandboxEntry {
-                    path: FileSystemPath::Path {
-                        path: first.join(".git").into(),
-                    },
-                    access: FileSystemAccessMode::Read,
-                    missing_path_behavior: None,
-                },
-                FileSystemSandboxEntry {
-                    path: FileSystemPath::Path {
-                        path: second.join(".git").into(),
-                    },
-                    access: FileSystemAccessMode::Read,
-                    missing_path_behavior: None,
-                },
-                FileSystemSandboxEntry {
-                    path: FileSystemPath::GlobPattern {
-                        pattern: AbsolutePathBuf::resolve_path_against_base(
-                            "**/*.env",
-                            first.as_path(),
-                        )
-                        .to_string_lossy()
-                        .into_owned(),
-                    },
-                    access: FileSystemAccessMode::Deny,
-                    missing_path_behavior: None,
-                },
-                FileSystemSandboxEntry {
-                    path: FileSystemPath::GlobPattern {
-                        pattern: AbsolutePathBuf::resolve_path_against_base(
-                            "**/*.env",
-                            second.as_path(),
-                        )
-                        .to_string_lossy()
-                        .into_owned(),
-                    },
-                    access: FileSystemAccessMode::Deny,
-                    missing_path_behavior: None,
-                },
-            ])
-        );
-    }
-
-    #[test]
-    fn with_additional_legacy_workspace_writable_roots_protects_metadata() {
-        let temp_dir = TempDir::new().expect("tempdir");
-        let extra = AbsolutePathBuf::from_absolute_path(temp_dir.path().join("extra"))
-            .expect("resolve extra root");
-        std::fs::create_dir_all(extra.join(".git")).expect("create .git dir");
-        let policy = FileSystemSandboxPolicy::restricted(vec![FileSystemSandboxEntry {
-            path: FileSystemPath::Special {
-                value: FileSystemSpecialPath::project_roots(/*subpath*/ None),
-            },
-            access: FileSystemAccessMode::Write,
-            missing_path_behavior: None,
-        }]);
-
-        let actual =
-            policy.with_additional_legacy_workspace_writable_roots(std::slice::from_ref(&extra));
-
-        assert_eq!(
-            actual,
-            FileSystemSandboxPolicy::restricted(vec![
-                FileSystemSandboxEntry {
-                    path: FileSystemPath::Special {
-                        value: FileSystemSpecialPath::project_roots(/*subpath*/ None),
-                    },
-                    access: FileSystemAccessMode::Write,
-                    missing_path_behavior: None,
-                },
-                FileSystemSandboxEntry {
-                    path: FileSystemPath::Path {
-                        path: extra.clone().into()
-                    },
-                    access: FileSystemAccessMode::Write,
-                    missing_path_behavior: None,
-                },
-                FileSystemSandboxEntry::skip_missing_path(
-                    FileSystemPath::Path {
-                        path: extra.join(".git").into()
-                    },
-                    FileSystemAccessMode::Read,
-                ),
-            ])
-        );
-    }
-
-    #[test]
-    fn file_system_access_mode_orders_by_conflict_precedence() {
-        assert!(FileSystemAccessMode::Write > FileSystemAccessMode::Read);
-        assert!(FileSystemAccessMode::Deny > FileSystemAccessMode::Write);
-    }
-
-    #[test]
-    fn legacy_bridge_preserves_explicit_deny_entries() {
-        let denied = AbsolutePathBuf::try_from("/tmp/private").expect("absolute path");
-        let existing = FileSystemSandboxPolicy::restricted(vec![FileSystemSandboxEntry {
-            path: FileSystemPath::Path {
-                path: denied.clone().into(),
-            },
-            access: FileSystemAccessMode::Deny,
-            missing_path_behavior: None,
-        }]);
-
-        let rebuilt = FileSystemSandboxPolicy::from_legacy_sandbox_policy_preserving_deny_entries(
-            &SandboxPolicy::new_workspace_write_policy(),
-            Path::new("/tmp/workspace"),
-            &existing,
-        );
-
-        assert!(
-            rebuilt.entries.iter().any(|entry| {
-                entry.path
-                    == FileSystemPath::Path {
-                        path: denied.clone().into(),
-                    }
-                    && entry.access == FileSystemAccessMode::Deny
-            }),
-            "expected explicit deny entry to be preserved"
-        );
-    }
-
-    #[test]
-    fn preserving_deny_entries_keeps_unrestricted_policy_enforceable() {
-        let deny_entry = unreadable_glob_entry("/tmp/project/**/*.env".to_string());
-        let mut existing = FileSystemSandboxPolicy::restricted(vec![deny_entry.clone()]);
-        existing.glob_scan_max_depth = Some(2);
-        let mut replacement = FileSystemSandboxPolicy::unrestricted();
-
-        replacement.preserve_deny_read_restrictions_from(&existing);
-
-        let mut expected = FileSystemSandboxPolicy::restricted(vec![
-            FileSystemSandboxEntry {
-                path: FileSystemPath::Special {
-                    value: FileSystemSpecialPath::Root,
-                },
-                access: FileSystemAccessMode::Write,
-                missing_path_behavior: None,
-            },
-            deny_entry,
-        ]);
-        expected.glob_scan_max_depth = Some(2);
-        assert_eq!(replacement, expected);
-    }
-
-    fn deny_policy(path: &Path) -> FileSystemSandboxPolicy {
-        FileSystemSandboxPolicy::restricted(vec![FileSystemSandboxEntry {
-            path: FileSystemPath::Path {
-                path: AbsolutePathBuf::try_from(path)
-                    .expect("absolute deny path")
-                    .into(),
-            },
-            access: FileSystemAccessMode::Deny,
-            missing_path_behavior: None,
-        }])
-    }
-
-    fn unreadable_glob_entry(pattern: String) -> FileSystemSandboxEntry {
-        FileSystemSandboxEntry {
-            path: FileSystemPath::GlobPattern { pattern },
-            access: FileSystemAccessMode::Deny,
-            missing_path_behavior: None,
-        }
-    }
-
-    fn default_policy_with_unreadable_glob(pattern: String) -> FileSystemSandboxPolicy {
-        let mut policy = FileSystemSandboxPolicy::default();
-        policy.entries.push(unreadable_glob_entry(pattern));
-        policy
-    }
-
-    fn is_read_denied(
-        path: &Path,
-        file_system_sandbox_policy: &FileSystemSandboxPolicy,
-        cwd: &Path,
-    ) -> bool {
-        ReadDenyMatcher::try_new_for_local_paths(file_system_sandbox_policy, cwd)
-            .expect("valid deny-read globs")
-            .is_some_and(|matcher| matcher.is_local_path_read_denied(path))
-    }
-
-    #[test]
-    fn exact_path_and_descendants_are_denied() {
-        let temp = TempDir::new().expect("tempdir");
-        let denied_dir = temp.path().join("denied");
-        let nested = denied_dir.join("nested.txt");
-        std::fs::create_dir_all(&denied_dir).expect("create denied dir");
-        std::fs::write(&nested, "secret").expect("write secret");
-
-        let policy = deny_policy(&denied_dir);
-        assert!(is_read_denied(&denied_dir, &policy, temp.path()));
-        assert!(is_read_denied(&nested, &policy, temp.path()));
-        assert!(!is_read_denied(
-            &temp.path().join("other.txt"),
-            &policy,
-            temp.path()
-        ));
-    }
-
-    #[cfg(unix)]
-    #[test]
-    fn native_read_deny_matching_uses_uri_matcher_semantics() {
-        let temp = TempDir::new().expect("tempdir");
-        let real_dir = temp.path().join("real");
-        let alias_dir = temp.path().join("alias");
-        std::fs::create_dir_all(&real_dir).expect("create real dir");
-        symlink_dir(&real_dir, &alias_dir).expect("symlink alias");
-
-        let secret = real_dir.join("secret.txt");
-        std::fs::write(&secret, "secret").expect("write secret");
-        let alias_secret = alias_dir.join("secret.txt");
-
-        for (denied_root, candidate) in [(&real_dir, &alias_secret), (&alias_dir, &secret)] {
-            let policy = deny_policy(denied_root);
-            let denied_root_uri =
-                PathUri::from_host_native_path(denied_root).expect("deny root URI");
-            let candidate_uri = PathUri::from_host_native_path(candidate).expect("candidate URI");
-
-            assert_eq!(
-                is_read_denied(candidate, &policy, temp.path()),
-                candidate_uri.starts_with(&denied_root_uri)
-            );
-        }
-    }
-
-    #[test]
-    fn literal_patterns_and_globs_are_denied() {
-        let temp = TempDir::new().expect("tempdir");
-        let literal = temp.path().join("private");
-        let other = temp.path().join("notes.txt");
-        std::fs::create_dir_all(&literal).expect("create literal dir");
-        std::fs::write(&other, "notes").expect("write notes");
-
-        let mut policy = deny_policy(&literal);
-        policy.entries.push(unreadable_glob_entry(format!(
-            "{}/**/*.txt",
-            temp.path().display()
-        )));
-
-        assert!(is_read_denied(&literal, &policy, temp.path()));
-        assert!(is_read_denied(&other, &policy, temp.path()));
-    }
-
-    #[test]
-    fn glob_patterns_deny_matching_paths() {
-        let temp = TempDir::new().expect("tempdir");
-        let denied = temp.path().join("private").join("secret1.txt");
-        std::fs::create_dir_all(denied.parent().expect("parent")).expect("create parent");
-        std::fs::write(&denied, "secret").expect("write secret");
-
-        let policy = default_policy_with_unreadable_glob(format!(
-            "{}/private/secret?.txt",
-            temp.path().display()
-        ));
-
-        assert!(is_read_denied(&denied, &policy, temp.path()));
-
-        #[cfg(unix)]
-        {
-            use std::os::unix::ffi::OsStrExt;
-
-            let non_utf8 = denied
-                .parent()
-                .expect("parent")
-                .join(OsStr::from_bytes(b"secret\xff.txt"));
-            assert!(is_read_denied(&non_utf8, &policy, temp.path()));
-        }
-    }
-
-    #[test]
-    fn glob_patterns_do_not_cross_path_separators() {
-        let temp = TempDir::new().expect("tempdir");
-        let matching = temp.path().join("app").join("file42.txt");
-        let nested = temp.path().join("app").join("nested").join("file42.txt");
-        let short = temp.path().join("app").join("file4.txt");
-        let letters = temp.path().join("app").join("fileab.txt");
-        std::fs::create_dir_all(nested.parent().expect("parent")).expect("create parent");
-        std::fs::write(&matching, "secret").expect("write matching");
-        std::fs::write(&nested, "secret").expect("write nested");
-        std::fs::write(&short, "secret").expect("write short");
-        std::fs::write(&letters, "secret").expect("write letters");
-
-        let policy = default_policy_with_unreadable_glob(format!(
-            "{}/*/file[0-9]?.txt",
-            temp.path().display()
-        ));
-
-        assert!(is_read_denied(&matching, &policy, temp.path()));
-        assert!(!is_read_denied(&nested, &policy, temp.path()));
-        assert!(!is_read_denied(&short, &policy, temp.path()));
-        assert!(!is_read_denied(&letters, &policy, temp.path()));
-    }
-
-    #[test]
-    fn globstar_patterns_deny_root_and_nested_matches() {
-        let temp = TempDir::new().expect("tempdir");
-        let root_env = temp.path().join(".env");
-        let nested_env = temp.path().join("app").join(".env");
-        let other = temp.path().join("app").join("notes.txt");
-        std::fs::create_dir_all(nested_env.parent().expect("parent")).expect("create parent");
-        std::fs::write(&root_env, "secret").expect("write root env");
-        std::fs::write(&nested_env, "secret").expect("write nested env");
-        std::fs::write(&other, "notes").expect("write notes");
-
-        let policy =
-            default_policy_with_unreadable_glob(format!("{}/**/*.env", temp.path().display()));
-
-        assert!(is_read_denied(&root_env, &policy, temp.path()));
-        assert!(is_read_denied(&nested_env, &policy, temp.path()));
-        assert!(!is_read_denied(&other, &policy, temp.path()));
-    }
-
-    #[test]
-    fn unclosed_character_classes_match_literal_brackets() {
-        let temp = TempDir::new().expect("tempdir");
-        let bracket_file = temp.path().join("[");
-        let other = temp.path().join("notes.txt");
-        std::fs::write(&bracket_file, "secret").expect("write bracket file");
-        std::fs::write(&other, "notes").expect("write notes");
-        let policy = default_policy_with_unreadable_glob(format!("{}/[", temp.path().display()));
-
-        assert!(is_read_denied(&bracket_file, &policy, temp.path()));
-        assert!(!is_read_denied(&other, &policy, temp.path()));
-    }
-}
+#[path = "permissions_tests.rs"]
+mod tests;
```

### codex-rs/protocol/src/protocol.rs — approval, sandbox

```diff
--- rust-v0.167.2/codex-rs/protocol/src/protocol.rs
+++ rust-v0.168.0/codex-rs/protocol/src/protocol.rs
@@ -220,6 +220,15 @@
     /// Overrides the configured realtime protocol version for this session only.
     pub version: Option<RealtimeConversationVersion>,
     pub voice: Option<RealtimeVoice>,
+}
+
+/// A caller-owned realtime sideband. Dropping either direction seals input and ends
+/// the attachment after accepted messages drain. The caller supplies bounded channels
+/// and one complete JSON message per item.
+#[derive(Debug)]
+pub struct RealtimeSidebandTransport {
+    pub incoming: tokio::sync::mpsc::Receiver<String>,
+    pub outgoing: tokio::sync::mpsc::Sender<String>,
 }
 
 impl fmt::Debug for ConversationStartParams {
@@ -720,6 +729,13 @@
         reply: oneshot::Sender<CodexResult<()>>,
     },
 
+    /// Attach an existing call using caller-provided I/O without opening a socket.
+    RealtimeConversationAttachStream {
+        params: ConversationStartParams,
+        transport: RealtimeSidebandTransport,
+        reply: oneshot::Sender<CodexResult<()>>,
+    },
+
     /// Send audio input to the running realtime conversation stream.
     #[debug("RealtimeConversationAudio {{ item_id: {:?}, sample_rate: {}, num_channels: {}, samples_per_channel: {:?} }}", _0.frame.item_id, _0.frame.sample_rate, _0.frame.num_channels, _0.frame.samples_per_channel)]
     RealtimeConversationAudio(ConversationAudioParams),
@@ -1094,6 +1110,7 @@
             Self::CleanBackgroundTerminals => "clean_background_terminals",
             Self::RealtimeConversationStart(_) => "realtime_conversation_start",
             Self::RealtimeConversationAttach { .. } => "realtime_conversation_attach",
+            Self::RealtimeConversationAttachStream { .. } => "realtime_conversation_attach_stream",
             Self::RealtimeConversationAudio(_) => "realtime_conversation_audio",
             Self::RealtimeConversationText(_) => "realtime_conversation_text",
             Self::RealtimeConversationSpeech(_) => "realtime_conversation_speech",
@@ -1170,8 +1187,9 @@
 
 #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize, JsonSchema, TS)]
 pub struct GranularApprovalConfig {
-    /// Whether to allow shell command approval requests, including inline
+    /// Whether to allow sandbox escalation approval requests, including inline
     /// `with_additional_permissions` and `require_escalated` requests.
+    /// Dangerous commands can still request approval within existing permissions.
     pub sandbox_approval: bool,
     /// Whether to allow prompts triggered by execpolicy `prompt` rules.
     pub rules: bool,
@@ -2177,6 +2195,11 @@
     pub thread_id: ThreadId,
     pub turn_id: String,
     pub item: TurnItem,
+    /// Native tokens in the completed assistant message, including any sampled footer.
+    /// Completion telemetry only; absent for items without a producer-supplied count.
+    #[serde(default, skip_serializing_if = "Option::is_none")]
+    #[ts(optional)]
+    pub content_token_count: Option<u64>,
     #[serde(default, skip_serializing_if = "Option::is_none")]
     #[ts(optional)]
     pub started_at_ms: Option<i64>,
@@ -2308,6 +2331,11 @@
     pub message: String,
     #[serde(default)]
     pub codex_error_info: Option<CodexErrorInfo>,
+    /// Host-only file identities proven rejected against the submitted request.
+    #[serde(default, skip_serializing_if = "Vec::is_empty")]
+    #[schemars(skip)]
+    #[ts(skip)]
+    pub rejected_audio_file_ids: Vec<String>,
     /// Sensitive explanation and steering are delivered live but never enter rollout storage.
     #[serde(skip)]
     #[schemars(skip)]
@@ -2455,6 +2483,11 @@
     pub service_tier: Option<String>,
     pub approval_policy: AskForApproval,
     pub approvals_reviewer: ApprovalsReviewer,
+    /// Original selection before managed policy resolved the effective reviewer.
+    /// Older histories contain only `approvals_reviewer`.
+    #[serde(default, skip_serializing_if = "Option::is_none")]
+    #[ts(optional)]
+    pub requested_approvals_reviewer: Option<ApprovalsReviewer>,
     pub permission_profile: PermissionProfile,
     #[serde(default, skip_serializing_if = "Option::is_none")]
     #[ts(optional)]
@@ -3416,6 +3449,9 @@
 /// and should be used when there is no config override.
 #[derive(Serialize, Deserialize, Clone, Debug, JsonSchema, TS)]
 pub struct SessionMeta {
+    /// Scope discovery to the creator. Absent on threads created before account filtering.
+    #[serde(default, skip_serializing_if = "std::ops::Not::not")]
+    pub account_scoped: bool,
     /// ChatGPT user that created this thread; absent when unavailable or for older threads.
     #[serde(default, skip_serializing_if = "Option::is_none")]
     pub creator_user_id: Option<String>,
@@ -3499,6 +3535,7 @@
     fn default() -> Self {
         let id = ThreadId::default();
         SessionMeta {
+            account_scoped: false,
             creator_user_id: None,
             creator_account_id: None,
             session_id: id.into(),
@@ -3597,6 +3634,10 @@
     /// Root turn that owns this turn's attribution, retained across recovery.
     #[serde(default, skip_serializing_if = "Option::is_none")]
     pub root_turn_id: Option<String>,
+    /// Explicit routing for this turn. An empty list clears the thread's direct namespaces.
+    #[serde(default, skip_serializing_if = "Option::is_none")]
+    #[ts(optional)]
+    pub direct_only_tool_namespaces: Option<Vec<String>>,
     /// Plugin selection captured for this turn. Absent in older histories.
     #[serde(default, skip_serializing_if = "Option::is_none")]
     #[ts(optional)]
@@ -5742,6 +5783,7 @@
     #[test]
     fn item_completed_event_from_image_generation_emits_end_event() {
         let event = ItemCompletedEvent {
+            content_token_count: None,
             thread_id: ThreadId::new(),
             turn_id: "turn-1".into(),
             item: TurnItem::ImageGeneration(ImageGenerationItem {
@@ -5780,6 +5822,7 @@
     #[test]
     fn item_completed_event_from_file_change_emits_patch_end_event() {
         let event = ItemCompletedEvent {
+            content_token_count: None,
             thread_id: ThreadId::new(),
             turn_id: "turn-1".into(),
             started_at_ms: Some(0),
@@ -5819,6 +5862,7 @@
     #[test]
     fn item_completed_event_from_mcp_tool_call_emits_end_event() {
         let event = ItemCompletedEvent {
+            content_token_count: None,
             thread_id: ThreadId::new(),
             turn_id: "turn-1".into(),
             started_at_ms: Some(0),
@@ -5900,6 +5944,7 @@
             }),
         };
         let completed = ItemCompletedEvent {
+            content_token_count: None,
             thread_id: ThreadId::new(),
             turn_id: "turn-1".into(),
             started_at_ms: Some(10),
@@ -5978,6 +6023,7 @@
             }),
         };
         let completed = ItemCompletedEvent {
+            content_token_count: None,
             thread_id: ThreadId::new(),
             turn_id: "turn-1".into(),
             started_at_ms: Some(10),
@@ -6023,6 +6069,7 @@
     #[test]
     fn review_mode_item_completion_emits_legacy_events_with_ids() {
         let entered = ItemCompletedEvent {
+            content_token_count: None,
             thread_id: ThreadId::new(),
             turn_id: "turn-1".into(),
             started_at_ms: Some(0),
@@ -6036,6 +6083,7 @@
             }),
         };
         let exited = ItemCompletedEvent {
+            content_token_count: None,
             thread_id: ThreadId::new(),
             turn_id: "turn-1".into(),
             started_at_ms: Some(0),
@@ -6096,6 +6144,7 @@
     #[test]
     fn item_completed_event_defaults_missing_completed_at_ms() {
         let mut value = serde_json::to_value(ItemCompletedEvent {
+            content_token_count: None,
             thread_id: ThreadId::new(),
             turn_id: "turn-1".into(),
             item: TurnItem::UserMessage(UserMessageItem::new(&[])),
@@ -6137,6 +6186,7 @@
             misalignment: None,
             message: "rollback failed".into(),
             codex_error_info: Some(CodexErrorInfo::ThreadRollbackFailed),
+            rejected_audio_file_ids: Vec::new(),
         };
         assert!(!event.affects_turn_status());
     }
@@ -6149,6 +6199,7 @@
             codex_error_info: Some(CodexErrorInfo::ActiveTurnNotSteerable {
                 turn_kind: NonSteerableTurnKind::Review,
             }),
+            rejected_audio_file_ids: Vec::new(),
         };
         assert!(!event.affects_turn_status());
     }
@@ -6159,6 +6210,7 @@
             misalignment: None,
             message: "generic".into(),
             codex_error_info: Some(CodexErrorInfo::Other),
+            rejected_audio_file_ids: Vec::new(),
         };
         assert!(event.affects_turn_status());
     }
@@ -6168,6 +6220,7 @@
         let event = ErrorEvent {
             message: "This request violated the misalignment policy.".to_string(),
             codex_error_info: Some(CodexErrorInfo::MisalignmentPolicyViolation),
+            rejected_audio_file_ids: Vec::new(),
             misalignment: Some(MisalignmentErrorDetails {
                 error_type: Some("unauthorized_data_transfer".to_string()),
                 detailed_explanation: Some("Sensitive customer explanation".to_string()),
@@ -6194,6 +6247,22 @@
         assert!(!debug.contains("Sensitive customer explanation"));
         assert!(!debug.contains("Sensitive customer steering"));
         assert!(!debug.contains("sensitive-review-target"));
+    }
+
+    #[test]
+    fn rejected_audio_identity_round_trips_for_host_recovery() {
+        let event = ErrorEvent {
+            message: "invalid recording".to_string(),
+            codex_error_info: Some(CodexErrorInfo::BadRequest),
+            rejected_audio_file_ids: vec!["file_audio".to_string()],
+            misalignment: None,
+        };
+
+        let serialized = serde_json::to_value(&event).expect("serialize error event");
+        assert_eq!(serialized["rejected_audio_file_ids"], json!(["file_audio"]));
+        let restored: ErrorEvent =
+            serde_json::from_value(serialized).expect("deserialize error event");
+        assert_eq!(restored.rejected_audio_file_ids, vec!["file_audio"]);
     }
 
     #[test]
@@ -6529,6 +6598,7 @@
         let item = TurnContextItem {
             turn_id: None,
             root_turn_id: None,
+            direct_only_tool_namespaces: None,
             disabled_plugin_ids: None,
             cwd: test_path_buf("/tmp").abs(),
             approval_policy: AskForApproval::Never,
```

### Configuration fields

[Schema at this release](https://github.com/openai/codex/blob/9480ec100c3edee9fc69172e8e80a4730444094d/codex-rs/core/config.schema.json)

- Changed: `approval_policy.granular.sandbox_approval`
- Added: `features.agent_message_board_mcp`
- Added: `features.async_compaction_root_only`
- Added: `features.cli_resume_account_check`
- Added: `features.command_sessions_world_state`
- Added: `features.guardian_denial_reconsideration`
- Added: `features.guardian_include_additional_context`
- Added: `features.guardianv2.sync_elastic_budgeting`
- Added: `features.guardianv2.sync_elastic_sections`
- Added: `features.guardianv2.sync_elastic_sections.*`
- Added: `features.guardianv2.sync_elastic_sections.*.max_section_entry_tokens`
- Added: `features.guardianv2.sync_elastic_sections.*.max_total_section_tokens`
- Added: `features.guardianv2.sync_elastic_sections.*.min_total_section_tokens`
- Added: `features.hosted_search_policy`
- Added: `features.image_generation_animation`
- Removed: `features.incremental_tools_legacy`
- Removed: `features.incremental_tools_legacy_gcp`
- Added: `features.tui_workspace`
- Changed: `profiles.*.approval_policy.granular.sandbox_approval`
- Added: `profiles.*.features.agent_message_board_mcp`
- Added: `profiles.*.features.async_compaction_root_only`
- Added: `profiles.*.features.cli_resume_account_check`
- Added: `profiles.*.features.command_sessions_world_state`
- Added: `profiles.*.features.guardian_denial_reconsideration`
- Added: `profiles.*.features.guardian_include_additional_context`
- Added: `profiles.*.features.guardianv2.sync_elastic_budgeting`
- Added: `profiles.*.features.guardianv2.sync_elastic_sections`
- Added: `profiles.*.features.guardianv2.sync_elastic_sections.*`
- Added: `profiles.*.features.guardianv2.sync_elastic_sections.*.max_section_entry_tokens`
- Added: `profiles.*.features.guardianv2.sync_elastic_sections.*.max_total_section_tokens`
- Added: `profiles.*.features.guardianv2.sync_elastic_sections.*.min_total_section_tokens`
- Added: `profiles.*.features.hosted_search_policy`
- Added: `profiles.*.features.image_generation_animation`
- Removed: `profiles.*.features.incremental_tools_legacy`
- Removed: `profiles.*.features.incremental_tools_legacy_gcp`
- Added: `profiles.*.features.tui_workspace`
- Added: `profiles.*.tools.client_search_provider`
- Added: `tools.client_search_provider`
- Added: `tui.default_hosts`
- Added: `tui.default_hosts.*`
- Added: `tui.default_hosts.*.*`
- Changed: `tui.keymap`
- Changed: `tui.keymap.global`
- Added: `tui.keymap.global.change_host`
- Added: `tui.keymap.global.change_host[]`
- Added: `tui.keymap.global.equalize_pane_widths`
- Added: `tui.keymap.global.equalize_pane_widths[]`
- Added: `tui.keymap.global.focus_main_composer`
- Added: `tui.keymap.global.focus_main_composer[]`
- Added: `tui.keymap.global.focus_pane_left`
- Added: `tui.keymap.global.focus_pane_left[]`
- Added: `tui.keymap.global.focus_pane_right`
- Added: `tui.keymap.global.focus_pane_right[]`
- Added: `tui.keymap.global.focus_sidebar_content`
- Added: `tui.keymap.global.focus_sidebar_content[]`
- Added: `tui.keymap.global.hide_pane`
- Added: `tui.keymap.global.hide_pane[]`
- Added: `tui.keymap.global.maximize_pane_width`
- Added: `tui.keymap.global.maximize_pane_width[]`
- Added: `tui.keymap.global.minimize_pane_width`
- Added: `tui.keymap.global.minimize_pane_width[]`
- Added: `tui.keymap.global.move_divider_left`
- Added: `tui.keymap.global.move_divider_left[]`
- Added: `tui.keymap.global.move_divider_right`
- Added: `tui.keymap.global.move_divider_right[]`
- Added: `tui.keymap.global.resize_panes`
- Added: `tui.keymap.global.resize_panes[]`
- Added: `tui.keymap.global.toggle_pane_zoom`
- Added: `tui.keymap.global.toggle_pane_zoom[]`
- Changed: `tui.notification_method`
- Added: `tui.sidebar_width_percent`

## rust-v0.168.0 → rust-v0.169.0

Commit: `d32063f96c2dff1dc96af839b3952abb6acfeda4`

### codex-rs/config/src/config_toml.rs — legacy-profile

```diff
--- rust-v0.168.0/codex-rs/config/src/config_toml.rs
+++ rust-v0.169.0/codex-rs/config/src/config_toml.rs
@@ -881,37 +876,12 @@
                     .map(|_| SandboxMode::WorkspaceWrite)
             })
             .unwrap_or_default();
-        let effective_sandbox_mode = effective_sandbox_mode(
+        let permission_profile = crate::translate_legacy_permissions(
             resolved_sandbox_mode,
+            self.sandbox_workspace_write.as_ref(),
             Platform::native(),
             windows_sandbox_level,
         );
-
-        let permission_profile = match effective_sandbox_mode {
-            SandboxMode::ReadOnly => PermissionProfile::read_only(),
-            SandboxMode::WorkspaceWrite => match self.sandbox_workspace_write.as_ref() {
-                Some(SandboxWorkspaceWrite {
-                    writable_roots,
-                    network_access,
-                    exclude_tmpdir_env_var,
-                    exclude_slash_tmp,
-                }) => {
-                    let network_policy = if *network_access {
-                        NetworkSandboxPolicy::Enabled
-                    } else {
-                        NetworkSandboxPolicy::Restricted
-                    };
-                    PermissionProfile::workspace_write_with(
-                        writable_roots,
-                        network_policy,
-                        *exclude_tmpdir_env_var,
-                        *exclude_slash_tmp,
-                    )
-                }
-                None => PermissionProfile::workspace_write(),
-            },
-            SandboxMode::DangerFullAccess => PermissionProfile::Disabled,
-        };
         if configured_sandbox_mode.is_none()
             && let Some(constraint) = permission_profile_constraint
             && let Err(err) = constraint.can_set(&permission_profile)
```

### codex-rs/config/src/mcp_types.rs — mcp

```diff
--- rust-v0.168.0/codex-rs/config/src/mcp_types.rs
+++ rust-v0.169.0/codex-rs/config/src/mcp_types.rs
@@ -327,6 +327,12 @@
         } else {
             McpServerDisabledReason::Requirements { source }
         });
+    }
+
+    /// Whether a regular chat may defer this server when its tool catalog is cached.
+    pub fn can_defer_stdio_startup(&self) -> bool {
+        matches!(&self.transport, McpServerTransportConfig::Stdio { .. })
+            && (!self.required || self.startup_readiness == McpStartupReadiness::Catalog)
     }
 
     pub fn is_local_environment(&self) -> bool {
```

### codex-rs/config/src/types.rs — apps

```diff
--- rust-v0.168.0/codex-rs/config/src/types.rs
+++ rust-v0.169.0/codex-rs/config/src/types.rs
@@ -938,6 +938,10 @@
     #[serde(default = "default_true")]
     pub fullscreen_transcript: bool,
 
+    /// Summarize tool calls and collapse completed turns in the full-screen transcript. Defaults to `false`.
+    #[serde(default)]
+    pub collapse_turn_details: bool,
+
     /// Preferred docked sidebar width as a percentage of the terminal. Defaults to one third.
     #[serde(default)]
     #[schemars(range(min = 1, max = 99))]
```

### codex-rs/core/config.schema.json — schema

```diff
--- rust-v0.168.0/codex-rs/core/config.schema.json
+++ rust-v0.169.0/codex-rs/core/config.schema.json
@@ -442,14 +442,6 @@
           "description": "Experimental replacement for the history-retrieval instructions when history tools and Apps are enabled. Omitted or blank values use the built-in prompt.",
           "type": "string"
         },
-        "experimental_policy_template": {
-          "description": "Experimental full Guardian prompt template containing the tenant policy placeholder.",
-          "type": "string"
-        },
-        "extra_policy": {
-          "description": "Additional policy text inserted into the Guardian template's `{{ extra_policy }}` slot.",
-          "type": "string"
-        },
         "policy": {
           "description": "Additional policy instructions inserted into the guardian prompt.",
           "type": "string"
@@ -482,35 +474,6 @@
         "timeout_ms": {
           "default": 300000,
           "description": "Maximum time to wait for the refresh command to complete.",
-          "format": "uint64",
-          "minimum": 1.0,
-          "type": "integer"
-        }
-      },
-      "required": [
-        "command"
-      ],
-      "type": "object"
-    },
-    "AwsCredentialExportConfig": {
-      "additionalProperties": false,
-      "description": "Command used to export AWS signing credentials for a model provider.",
-      "properties": {
-        "args": {
-          "default": [],
-          "description": "Arguments passed to the credential export command.",
-          "items": {
-            "type": "string"
-          },
-          "type": "array"
-        },
-        "command": {
-          "description": "Executable to invoke directly, without a shell.",
-          "type": "string"
-        },
-        "timeout_ms": {
-          "default": 30000,
-          "description": "Maximum time to wait for the credential export command to complete.",
           "format": "uint64",
           "minimum": 1.0,
           "type": "integer"
@@ -1008,6 +971,9 @@
             "daemon_auto_start": {
               "type": "boolean"
             },
+            "daybreak_program_propagation": {
+              "type": "boolean"
+            },
             "default_mode_request_user_input": {
               "type": "boolean"
             },
@@ -1060,6 +1026,9 @@
               "type": "boolean"
             },
             "fast_mode": {
+              "type": "boolean"
+            },
+            "gateway_setup_wizard": {
               "type": "boolean"
             },
             "gcp_setup_wizard": {
@@ -1158,6 +1127,12 @@
             "incremental_tools": {
               "type": "boolean"
             },
+            "incremental_tools_legacy": {
+              "type": "boolean"
+            },
+            "incremental_tools_legacy_gcp": {
+              "type": "boolean"
+            },
             "instant_interrupt": {
               "type": "boolean"
             },
@@ -1186,6 +1161,9 @@
               "type": "boolean"
             },
             "mcp_connection_sharing": {
+              "type": "boolean"
+            },
+            "mcp_lazy_stdio_startup": {
               "type": "boolean"
             },
             "mcp_oauth_refresh_coordination": {
@@ -1652,6 +1630,35 @@
       ],
       "type": "string"
     },
+    "CredentialExportConfig": {
+      "additionalProperties": false,
+      "description": "Command used to export credentials for a model provider.",
+      "properties": {
+        "args": {
+          "default": [],
+          "description": "Arguments passed to the credential export command.",
+          "items": {
+            "type": "string"
+          },
+          "type": "array"
+        },
+        "command": {
+          "description": "Executable to invoke directly, without a shell.",
+          "type": "string"
+        },
+        "timeout_ms": {
+          "default": 30000,
+          "description": "Maximum time to wait for the credential export command to complete.",
+          "format": "uint64",
+          "minimum": 1.0,
+          "type": "integer"
+        }
+      },
+      "required": [
+        "command"
+      ],
+      "type": "object"
+    },
     "CredentialProviderConfig": {
       "additionalProperties": false,
       "description": "Declarative description of an environment-backed credential family.",
@@ -2016,60 +2023,40 @@
       "type": "string"
     },
     "GatewayOAuthConfig": {
-      "additionalProperties": false,
-      "properties": {
-        "authorization_url": {
-          "type": "string"
+      "anyOf": [
+        {
+          "$ref": "#/definitions/GatewayOAuthSettings"
         },
-        "client_id": {
-          "type": "string"
-        },
-        "credentials_store": {
-          "allOf": [
-            {
-              "$ref": "#/definitions/OAuthCredentialsStore"
+        {
+          "additionalProperties": false,
+          "properties": {
+            "credential_export": {
+              "allOf": [
+                {
+                  "$ref": "#/definitions/CredentialExportConfig"
+                }
+              ],
+              "description": "Command that prints a gateway access token."
+            },
+            "delivery": {
+              "allOf": [
+                {
+                  "$ref": "#/definitions/GatewayOAuthDelivery"
+                }
+              ],
+              "default": {
+                "kind": "header",
+                "name": "Authorization",
+                "scheme": "Bearer"
+              }
             }
+          },
+          "required": [
+            "credential_export"
           ],
-          "description": "Where Codex stores this gateway's OAuth credentials. Defaults to the keyring-backed store."
-        },
-        "delivery": {
-          "allOf": [
-            {
-              "$ref": "#/definitions/GatewayOAuthDelivery"
-            }
-          ],
-          "default": {
-            "kind": "header",
-            "name": "Authorization",
-            "scheme": "Bearer"
-          },
-          "description": "Omit to send the gateway token via the Authorization header"
-        },
-        "redirect_port": {
-          "format": "uint16",
-          "minimum": 0.0,
-          "type": "integer"
-        },
-        "resource": {
-          "type": "string"
-        },
-        "scopes": {
-          "default": [],
-          "items": {
-            "type": "string"
-          },
-          "type": "array"
-        },
-        "token_url": {
-          "type": "string"
+          "type": "object"
         }
-      },
-      "required": [
-        "authorization_url",
-        "client_id",
-        "token_url"
-      ],
-      "type": "object"
+      ]
     },
     "GatewayOAuthDelivery": {
       "oneOf": [
@@ -2116,6 +2103,66 @@
           "type": "object"
         }
       ]
+    },
+    "GatewayOAuthSettings": {
+      "additionalProperties": false,
+      "properties": {
+        "authorization_url": {
+          "type": "string"
+        },
+        "client_id": {
+          "type": "string"
+        },
+        "credentials_store": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/OAuthCredentialsStore"
+            }
+          ],
+          "description": "Where Codex stores this gateway's OAuth credentials. Defaults to the keyring-backed store."
+        },
+        "delivery": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/GatewayOAuthDelivery"
+            }
+          ],
+          "default": {
+            "kind": "header",
+            "name": "Authorization",
+            "scheme": "Bearer"
+          },
+          "description": "Omit to send the gateway token via the Authorization header"
+        },
+        "device_authorization_url": {
+          "description": "Optional device endpoint used when the terminal cannot open a browser for gateway sign-in.",
+          "type": "string"
+        },
+        "redirect_port": {
+          "format": "uint16",
+          "minimum": 0.0,
+          "type": "integer"
+        },
+        "resource": {
+          "type": "string"
+        },
+        "scopes": {
+          "default": [],
+          "items": {
+            "type": "string"
+          },
+          "type": "array"
+        },
+        "token_url": {
+          "type": "string"
+        }
+      },
+      "required": [
+        "authorization_url",
+        "client_id",
+        "token_url"
+      ],
+      "type": "object"
     },
     "GhostSnapshotToml": {
       "additionalProperties": false,
@@ -3100,7 +3147,7 @@
         "credential_export": {
           "allOf": [
             {
-              "$ref": "#/definitions/AwsCredentialExportConfig"
+              "$ref": "#/definitions/CredentialExportConfig"
             }
           ],
           "description": "Optional command whose exported credentials replace the AWS SDK credential chain."
@@ -3200,7 +3247,7 @@
               "$ref": "#/definitions/GatewayOAuthConfig"
             }
           ],
-          "description": "Secondary OAuth credentials required by the provider's gateway."
+          "description": "Gateway access token from OAuth or a credential export command."
         },
         "http_headers": {
           "additionalProperties": {
@@ -5196,6 +5243,11 @@
           "description": "Generate automatic conversation recaps when the terminal is unfocused. Defaults to `true`. Disabling this leaves `/recap` available on demand.",
           "type": "boolean"
         },
+        "collapse_turn_details": {
+          "default": false,
+          "description": "Summarize tool calls and collapse completed turns in the full-screen transcript. Defaults to `false`.",
+          "type": "boolean"
+        },
         "copy_on_select": {
           "allOf": [
             {
@@ -5319,6 +5371,7 @@
             "global": {
               "change_host": null,
               "clear_terminal": null,
+              "close_sidebar_tab": null,
               "copy": null,
               "equalize_pane_widths": null,
               "find_transcript": null,
@@ -5327,6 +5380,7 @@
               "focus_pane_left": null,
               "focus_pane_right": null,
               "focus_sidebar_content": null,
+              "focus_sidebar_tabs": null,
               "hide_pane": null,
               "leader": null,
               "maximize_pane_width": null,
@@ -5339,6 +5393,8 @@
               "queue": null,
               "resize_panes": null,
               "select_transcript": null,
+              "sidebar_down": null,
+              "sidebar_up": null,
               "submit": null,
               "toggle_fast_mode": null,
               "toggle_pane_zoom": null,
@@ -6147,6 +6203,14 @@
           ],
           "description": "Clear the terminal UI."
         },
+        "close_sidebar_tab": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Close the active sidebar tab."
+        },
         "copy": {
           "allOf": [
             {
@@ -6210,6 +6274,14 @@
             }
           ],
           "description": "Focus the side conversation, or hide it when already focused."
+        },
+        "focus_sidebar_tabs": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Open the sidebar tab chooser."
         },
         "hide_pane": {
           "allOf": [
@@ -6306,6 +6378,22 @@
             }
           ],
           "description": "Enter keyboard selection mode for the transcript."
+        },
+        "sidebar_down": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Switch to the next sidebar tab."
+        },
+        "sidebar_up": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Switch to the previous sidebar tab."
         },
         "submit": {
           "allOf": [
@@ -6477,6 +6565,7 @@
           "default": {
             "change_host": null,
             "clear_terminal": null,
+            "close_sidebar_tab": null,
             "copy": null,
             "equalize_pane_widths": null,
             "find_transcript": null,
@@ -6485,6 +6574,7 @@
             "focus_pane_left": null,
             "focus_pane_right": null,
             "focus_sidebar_content": null,
+            "focus_sidebar_tabs": null,
             "hide_pane": null,
             "leader": null,
             "maximize_pane_width": null,
@@ -6497,6 +6587,8 @@
             "queue": null,
             "resize_panes": null,
             "select_transcript": null,
+            "sidebar_down": null,
+            "sidebar_up": null,
             "submit": null,
             "toggle_fast_mode": null,
             "toggle_pane_zoom": null,
@@ -7949,6 +8041,9 @@
         "daemon_auto_start": {
           "type": "boolean"
         },
+        "daybreak_program_propagation": {
+          "type": "boolean"
+        },
         "default_mode_request_user_input": {
           "type": "boolean"
         },
@@ -8001,6 +8096,9 @@
           "type": "boolean"
         },
         "fast_mode": {
+          "type": "boolean"
+        },
+        "gateway_setup_wizard": {
           "type": "boolean"
         },
         "gcp_setup_wizard": {
@@ -8099,6 +8197,12 @@
         "incremental_tools": {
           "type": "boolean"
         },
+        "incremental_tools_legacy": {
+          "type": "boolean"
+        },
+        "incremental_tools_legacy_gcp": {
+          "type": "boolean"
+        },
         "instant_interrupt": {
           "type": "boolean"
         },
@@ -8127,6 +8231,9 @@
           "type": "boolean"
         },
         "mcp_connection_sharing": {
+          "type": "boolean"
+        },
+        "mcp_lazy_stdio_startup": {
           "type": "boolean"
         },
         "mcp_oauth_refresh_coordination": {
```

### codex-rs/core/src/config/mod.rs — sandbox-profile

```diff
--- rust-v0.168.0/codex-rs/core/src/config/mod.rs
+++ rust-v0.169.0/codex-rs/core/src/config/mod.rs
@@ -2713,66 +2729,14 @@
     fn profiles_are_active(
         &self,
         default_permissions_override: Option<&str>,
-        permission_config_syntax: Option<PermissionConfigSyntax>,
+        permission_config: Option<PermissionConfig<'_>>,
     ) -> bool {
         self.persisted_profile_id_was_provided
             || self.requirements_force_profile_selection
             || default_permissions_override.is_some()
-            || matches!(
-                permission_config_syntax,
-                Some(PermissionConfigSyntax::Profiles)
-            )
-            || permission_config_syntax.is_none()
+            || matches!(permission_config, Some(PermissionConfig::Named { .. }))
+            || permission_config.is_none()
     }
-}
-
-fn resolve_permission_config_syntax(
-    config_layer_stack: &ConfigLayerStack,
-    cfg: &ConfigToml,
-    sandbox_mode_override: Option<SandboxMode>,
-) -> Option<PermissionConfigSyntax> {
-    if sandbox_mode_override.is_some() {
-        return Some(PermissionConfigSyntax::Legacy);
-    }
-
-    let session_flags_select_profiles = config_layer_stack
-        .layers_high_to_low()
-        .find(|layer| matches!(layer.name, ConfigLayerSource::SessionFlags))
-        .and_then(|layer| {
-            layer
-                .config
-                .clone()
-                .try_into::<PermissionSelectionToml>()
-                .ok()
-        })
-        .is_some_and(|selection| selection.default_permissions.is_some());
-    if session_flags_select_profiles {
-        return Some(PermissionConfigSyntax::Profiles);
-    }
-
-    let mut selection = None;
-    for layer in config_layer_stack.layers_low_to_high() {
-        let Ok(layer_selection) = layer.config.clone().try_into::<PermissionSelectionToml>() else {
-            continue;
-        };
-
-        if layer_selection.sandbox_mode.is_some() {
-            selection = Some(PermissionConfigSyntax::Legacy);
-        }
-        if layer_selection.default_permissions.is_some() {
-            selection = Some(PermissionConfigSyntax::Profiles);
-        }
-    }
-
-    selection.or_else(|| {
-        if cfg.default_permissions.is_some() {
-            Some(PermissionConfigSyntax::Profiles)
-        } else if cfg.sandbox_mode.is_some() {
-            Some(PermissionConfigSyntax::Legacy)
-        } else {
-            None
-        }
-    })
 }
 
 /// Optional overrides for user configuration (e.g., from CLI flags).
```

### codex-rs/core/src/exec_policy.rs — saved-runtime

```diff
--- rust-v0.168.0/codex-rs/core/src/exec_policy.rs
+++ rust-v0.169.0/codex-rs/core/src/exec_policy.rs
@@ -12,14 +12,17 @@
 use codex_execpolicy::Error as ExecPolicyRuleError;
 use codex_execpolicy::Evaluation;
 use codex_execpolicy::MatchOptions;
-use codex_execpolicy::NetworkRuleProtocol;
 use codex_execpolicy::Policy;
 use codex_execpolicy::PolicyParser;
 use codex_execpolicy::RequirementsExecPolicy;
 use codex_execpolicy::RuleMatch;
 use codex_execpolicy::blocking_append_allow_prefix_rule;
 use codex_execpolicy::blocking_append_network_rule;
+use codex_network_proxy::NetworkProxy;
 use codex_protocol::approvals::ExecPolicyAmendment;
+use codex_protocol::approvals::NetworkApprovalContext;
+use codex_protocol::approvals::NetworkPolicyAmendment;
+use codex_protocol::approvals::NetworkPolicyRuleAction;
 use codex_protocol::config_types::WindowsSandboxLevel;
 use codex_protocol::models::PermissionProfile;
 use codex_protocol::permissions::FileSystemSandboxKind;
@@ -34,6 +37,8 @@
 use tracing::instrument;
 
 use crate::config::Config;
+use crate::network_policy_decision::ExecPolicyNetworkRuleAmendment;
+use crate::network_policy_decision::execpolicy_network_rule_amendment;
 use crate::sandboxing::SandboxPermissions;
 use crate::tools::sandboxing::ExecApprovalRequirement;
 use codex_shell_command::bash::parse_shell_lc_plain_commands;
@@ -558,14 +563,16 @@
         Ok(())
     }
 
-    pub(crate) async fn append_network_rule_and_update(
+    /// Keeps the policy used by subsequent calls in step with native enforcement and persistence.
+    pub(crate) async fn apply_network_rule_and_persist(
         &self,
         codex_home: &Path,
         host: &str,
-        protocol: NetworkRuleProtocol,
-        decision: Decision,
-        justification: Option<String>,
-    ) -> Result<(), ExecPolicyUpdateError> {
+        amendment: &NetworkPolicyAmendment,
+        approval_context: &NetworkApprovalContext,
+        proxy: Option<&NetworkProxy>,
+        on_policy_applied: impl FnOnce(),
+    ) -> anyhow::Result<()> {
         let _update_guard =
             self.update_lock
                 .acquire()
@@ -575,19 +582,48 @@
                         "exec policy update semaphore closed".to_string(),
                     ),
                 })?;
+        let ExecPolicyNetworkRuleAmendment {
+            protocol,
+            decision,
+            justification,
+        } = execpolicy_network_rule_amendment(amendment, approval_context, host);
+        let mut updated_policy = self.current().as_ref().clone();
+        updated_policy.add_network_rule(host, protocol, decision, Some(justification.clone()))?;
+        let updated_policy = Arc::new(updated_policy);
+        if let Some(proxy) = proxy {
+            match amendment.action {
+                NetworkPolicyRuleAction::Allow => proxy
+                    .add_allowed_domain(host)
+                    .await
+                    .map_err(|err| anyhow::anyhow!("failed to update runtime allowlist: {err}"))?,
+                NetworkPolicyRuleAction::Deny => proxy
+                    .add_denied_domain(host)
+                    .await
+                    .map_err(|err| anyhow::anyhow!("failed to update runtime denylist: {err}"))?,
+            }
+        }
+        // Explicit denials also apply to owner-routed calls without a shared proxy. Publish
+        // before the cancellable write. Grants become available to other calls only after a save.
+        if decision == Decision::Forbidden {
+            self.policy.store(Arc::clone(&updated_policy));
+        }
+        let notify_after_save = if proxy.is_some() {
+            on_policy_applied();
+            None
+        } else {
+            Some(on_policy_applied)
+        };
         let policy_path = default_policy_path(codex_home);
-        let host = host.to_string();
         spawn_blocking({
             let policy_path = policy_path.clone();
-            let host = host.clone();
-            let justification = justification.clone();
+            let host = host.to_owned();
             move || {
                 blocking_append_network_rule(
                     &policy_path,
                     &host,
                     protocol,
                     decision,
-                    justification.as_deref(),
+                    Some(&justification),
                 )
             }
         })
@@ -598,9 +634,10 @@
             source,
         })?;
 
-        let mut updated_policy = self.current().as_ref().clone();
-        updated_policy.add_network_rule(&host, protocol, decision, justification)?;
-        self.policy.store(Arc::new(updated_policy));
+        self.policy.store(updated_policy);
+        if let Some(notify) = notify_after_save {
+            notify();
+        }
         Ok(())
     }
 }
```

### codex-rs/core/src/mcp_tool_call.rs — tool-approval

```diff
--- rust-v0.168.0/codex-rs/core/src/mcp_tool_call.rs
+++ rust-v0.169.0/codex-rs/core/src/mcp_tool_call.rs
@@ -2742,11 +2755,6 @@
 }
 
 fn requires_mcp_tool_approval(annotations: Option<&ToolAnnotations>) -> bool {
-    let destructive_hint = annotations.and_then(|annotations| annotations.destructive_hint);
-    if destructive_hint == Some(true) {
-        return true;
-    }
-
     let read_only_hint = annotations
         .and_then(|annotations| annotations.read_only_hint)
         .unwrap_or(false);
@@ -2754,6 +2762,7 @@
         return false;
     }
 
+    let destructive_hint = annotations.and_then(|annotations| annotations.destructive_hint);
     destructive_hint.unwrap_or(true)
         || annotations
             .and_then(|annotations| annotations.open_world_hint)
```

### codex-rs/features/src/lib.rs — apps-feature-order

```diff
--- rust-v0.168.0/codex-rs/features/src/lib.rs
+++ rust-v0.169.0/codex-rs/features/src/lib.rs
@@ -770,7 +779,7 @@
                 "image_detail_original" | "resize_all_images" | "item_ids" => {
                     continue;
                 }
-                "personality" | "plugin_hooks" => {
+                "personality" | "plugin_discovery_prefetch" | "plugin_hooks" => {
                     continue;
                 }
                 "skill_env_var_dependency_prompt" => {
```

### codex-rs/model-provider-info/src/lib.rs — provider-auth

```diff
--- rust-v0.168.0/codex-rs/model-provider-info/src/lib.rs
+++ rust-v0.169.0/codex-rs/model-provider-info/src/lib.rs
@@ -176,7 +177,7 @@
     pub experimental_bearer_token: Option<RedactedString>,
     /// Command-backed bearer-token configuration for this provider.
     pub auth: Option<ModelProviderAuthInfo>,
-    /// Secondary OAuth credentials required by the provider's gateway.
+    /// Gateway access token from OAuth or a credential export command.
     pub gateway_oauth: Option<GatewayOAuthConfig>,
     /// AWS SigV4 auth configuration for this provider.
     pub aws: Option<ModelProviderAwsAuthInfo>,
@@ -249,30 +250,48 @@
     pub auth_refresh: Option<AwsAuthRefreshConfig>,
 }
 
-/// Command used to export AWS signing credentials for a model provider.
+/// Command used to export credentials for a model provider.
 #[derive(Debug, Clone, Deserialize, Serialize, PartialEq, Eq, JsonSchema)]
 #[schemars(deny_unknown_fields)]
-pub struct AwsCredentialExportConfig {
+pub struct CredentialExportConfig {
     /// Executable to invoke directly, without a shell.
     pub command: String,
     /// Arguments passed to the credential export command.
     #[serde(default)]
     pub args: Vec<RedactedString>,
     /// Maximum time to wait for the credential export command to complete.
-    #[serde(default = "default_aws_credential_export_timeout_ms")]
+    #[serde(default = "default_credential_export_timeout_ms")]
     pub timeout_ms: NonZeroU64,
 }
 
-impl AwsCredentialExportConfig {
+pub type AwsCredentialExportConfig = CredentialExportConfig;
+
+impl CredentialExportConfig {
+    pub fn validate(&self, field: &str) -> Result<(), String> {
+        if self.command.trim().is_empty() {
+            return Err(format!("provider {field}.command must not be empty"));
+        }
+        let path = Path::new(&self.command);
+        let mut components = path.components();
+        let bare = matches!((components.next(), components.next()),
+            (Some(Component::Normal(name)), None) if name == path.as_os_str());
+        if !path.is_absolute() && !bare {
+            return Err(format!(
+                "provider {field}.command must be an absolute path or a bare executable name"
+            ));
+        }
+        Ok(())
+    }
+
     pub fn timeout(&self) -> Duration {
         Duration::from_millis(self.timeout_ms.get())
     }
 }
 
-fn default_aws_credential_export_timeout_ms() -> NonZeroU64 {
-    match NonZeroU64::new(DEFAULT_AWS_CREDENTIAL_EXPORT_TIMEOUT_MS) {
+fn default_credential_export_timeout_ms() -> NonZeroU64 {
+    match NonZeroU64::new(DEFAULT_CREDENTIAL_EXPORT_TIMEOUT_MS) {
         Some(timeout_ms) => timeout_ms,
-        None => panic!("AWS credential export timeout must be non-zero"),
+        None => panic!("credential export timeout must be non-zero"),
     }
 }
```

### codex-rs/protocol/src/protocol.rs — approval, sandbox

```diff
--- rust-v0.168.0/codex-rs/protocol/src/protocol.rs
+++ rust-v0.169.0/codex-rs/protocol/src/protocol.rs
@@ -11,6 +11,7 @@
 use std::path::PathBuf;
 use std::str::FromStr;
 use std::time::Duration;
+use std::time::SystemTime;
 
 use strum_macros::EnumIter;
 
@@ -82,6 +83,7 @@
 use serde_with::serde_as;
 use strum_macros::Display;
 use tokio::sync::oneshot;
+use tokio::sync::watch;
 use tracing::error;
 use ts_rs::TS;
 
@@ -220,6 +222,16 @@
     /// Overrides the configured realtime protocol version for this session only.
     pub version: Option<RealtimeConversationVersion>,
     pub voice: Option<RealtimeVoice>,
+}
+
+/// Controls when an in-process realtime attachment may establish a connection.
+#[derive(Debug, Clone, Default)]
+pub struct RealtimeAttachmentOptions {
+    /// Set the watch to `true` to cancel a pending connection.
+    /// Dropping the sender while its value is `false` lets the attempt continue.
+    pub cancel: Option<watch::Receiver<bool>>,
+    /// Optional caller deadline for publishing the connection. Cleanup can finish later.
+    pub start_before: Option<SystemTime>,
 }
 
 /// A caller-owned realtime sideband. Dropping either direction seals input and ends
@@ -724,8 +736,10 @@
     RealtimeConversationStart(ConversationStartParams),
 
     /// Start a realtime conversation and report completion of the connection attempt.
+    /// If cancellation wins, completion acknowledges connection cleanup.
     RealtimeConversationAttach {
         params: ConversationStartParams,
+        options: RealtimeAttachmentOptions,
         reply: oneshot::Sender<CodexResult<()>>,
     },
 
@@ -838,6 +852,10 @@
         /// The user's decision in response to the request.
         decision: ReviewDecision,
     },
+
+    /// Cancel the file change approval issued by the named turn.
+    #[debug("CancelPatchApproval {{ id: {id:?}, turn_id: {turn_id:?} }}")]
+    CancelPatchApproval { id: String, turn_id: String },
 
     /// Resolve an MCP elicitation request.
     #[debug("ResolveElicitation {{ request_id: {request_id:?}, decision: {decision:?} }}")]
@@ -1125,7 +1143,7 @@
             Self::TurnSettings { .. } => "turn_settings",
             Self::InterAgentCommunication { .. } => "inter_agent_communication",
             Self::ExecApproval { .. } => "exec_approval",
-            Self::PatchApproval { .. } => "patch_approval",
+            Self::PatchApproval { .. } | Self::CancelPatchApproval { .. } => "patch_approval",
             Self::ResolveElicitation { .. } => "resolve_elicitation",
             Self::UserInputAnswer { .. } => "user_input_answer",
             Self::RequestPermissionsResponse { .. } => "request_permissions_response",
@@ -2088,6 +2106,8 @@
     ModelNotFound,
     /// Capacity is unavailable on a route restricted by server policy.
     PolicyCapacityUnavailable,
+    /// The workspace's inference hook explicitly denied this request.
+    InferenceHookDenied,
     CyberPolicy,
     BioPolicy,
     MisalignmentPolicyViolation,
@@ -2135,6 +2155,7 @@
             | Self::ServerOverloaded
             | Self::ModelNotFound
             | Self::PolicyCapacityUnavailable
+            | Self::InferenceHookDenied
             | Self::CyberPolicy
             | Self::BioPolicy
             | Self::MisalignmentPolicyViolation
@@ -2390,6 +2411,15 @@
 #[derive(Debug, Clone, Deserialize, Serialize, PartialEq, Eq, JsonSchema, TS)]
 pub struct ModelVerificationEvent {
     pub verifications: Vec<ModelVerification>,
+}
+
+#[derive(Debug, Clone, Deserialize, Serialize, PartialEq, JsonSchema, TS)]
+pub struct TargetedAnswerModeration {
+    pub item_id: String,
+    pub moderated: bool,
+    #[serde(default, skip_serializing_if = "Option::is_none")]
+    #[ts(optional)]
+    pub display: Option<crate::items::AgentMessageDisplay>,
 }
 
 #[derive(Debug, Clone, Deserialize, Serialize, PartialEq, JsonSchema, TS)]
@@ -2790,6 +2820,10 @@
 
 #[derive(Debug, Clone, Deserialize, Serialize, JsonSchema, TS)]
 pub struct AgentMessageEvent {
+    /// Legacy history assigns synthetic item IDs. Preserve the native ID for a moderated answer.
+    #[serde(default, skip_serializing_if = "Option::is_none")]
+    #[ts(optional)]
+    pub moderation: Option<TargetedAnswerModeration>,
     pub message: String,
     #[serde(default)]
     pub phase: Option<MessagePhase>,
@@ -3414,14 +3448,14 @@
     V2,
 }
 
-#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, Eq, JsonSchema, TS)]
+#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, Eq, JsonSchema)]
 pub struct SessionContextWindow {
     /// UUIDv7 identity of this context window.
-    pub window_id: String,
+    pub window_id: crate::ContextWindowId,
 }
 
 impl SessionContextWindow {
-    pub fn new(window_id: String) -> Self {
+    pub fn new(window_id: crate::ContextWindowId) -> Self {
         Self { window_id }
     }
 }
@@ -3447,7 +3481,7 @@
 /// NOTE: There used to be an `instructions` field here, which stored user_instructions, but we
 /// now save that on TurnContext. base_instructions stores the base instructions for the session,
 /// and should be used when there is no config override.
-#[derive(Serialize, Deserialize, Clone, Debug, JsonSchema, TS)]
+#[derive(Serialize, Deserialize, Clone, Debug, JsonSchema)]
 pub struct SessionMeta {
     /// Scope discovery to the creator. Absent on threads created before account filtering.
     #[serde(default, skip_serializing_if = "std::ops::Not::not")]
@@ -3479,7 +3513,6 @@
     /// An absent value means unknown; an empty list means no roots.
     /// Keep native paths parseable across hosts; validate them when restoring settings.
     #[serde(default, skip_serializing_if = "Option::is_none")]
-    #[ts(optional)]
     pub runtime_workspace_roots: Option<Vec<PathBuf>>,
     pub originator: String,
     pub cli_version: String,
@@ -3568,7 +3601,7 @@
     }
 }
 
-#[derive(Serialize, Debug, Clone, JsonSchema, TS)]
+#[derive(Serialize, Debug, Clone, JsonSchema)]
 pub struct SessionMetaLine {
     #[serde(flatten)]
     pub meta: SessionMeta,
@@ -3627,7 +3660,7 @@
 /// context updates, and again after mid-turn compaction when replacement
 /// history re-establishes full context, so resume/fork replay can recover the
 /// latest durable baseline.
-#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, JsonSchema, TS)]
+#[derive(Serialize, Clone, Debug, PartialEq, JsonSchema, TS)]
 pub struct TurnContextItem {
     #[serde(default, skip_serializing_if = "Option::is_none")]
     pub turn_id: Option<String>,
@@ -3646,15 +3679,11 @@
     pub approval_policy: AskForApproval,
     #[serde(default, skip_serializing_if = "Option::is_none")]
     pub approvals_reviewer: Option<ApprovalsReviewer>,
-    pub sandbox_policy: SandboxPolicy,
-    #[serde(default, skip_serializing_if = "Option::is_none")]
-    pub permission_profile: Option<PermissionProfile>,
+    pub permission_profile: PermissionProfile,
     /// Built-in or named profile that produced `permission_profile`, when known.
     #[serde(default, skip_serializing_if = "Option::is_none")]
     #[ts(optional)]
     pub active_permission_profile: Option<ActivePermissionProfile>,
-    #[serde(default, skip_serializing_if = "Option::is_none")]
-    pub file_system_sandbox_policy: Option<RawFileSystemSandboxPolicy>,
     pub model: String,
     #[serde(default, skip_serializing_if = "Option::is_none")]
     pub comp_hash: Option<String>,
@@ -3674,26 +3703,79 @@
     pub summary: Option<ReasoningSummaryConfig>,
 }
 
-impl TurnContextItem {
-    pub fn permission_profile(&self) -> PermissionProfile {
-        self.permission_profile.clone().unwrap_or_else(|| {
-            let file_system_sandbox_policy = self
-                .file_system_sandbox_policy
-                .clone()
-                .map(TryInto::try_into)
-                .transpose()
-                .unwrap_or_else(|_| Some(FileSystemSandboxPolicy::restricted(Vec::new())))
-                .unwrap_or_else(|| {
-                    FileSystemSandboxPolicy::from_legacy_sandbox_policy_for_cwd(
-                        &self.sandbox_policy,
-                        self.cwd.as_path(),
-                    )
-                });
-            PermissionProfile::from_runtime_permissions_with_enforcement(
-                SandboxEnforcement::from_legacy_sandbox_policy(&self.sandbox_policy),
-                &file_system_sandbox_policy,
-                NetworkSandboxPolicy::from(&self.sandbox_policy),
-            )
+impl<'de> Deserialize<'de> for TurnContextItem {
+    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
+    where
+        D: serde::Deserializer<'de>,
+    {
+        #[derive(Deserialize)]
+        struct Wire {
+            turn_id: Option<String>,
+            root_turn_id: Option<String>,
+            direct_only_tool_namespaces: Option<Vec<String>>,
+            disabled_plugin_ids: Option<Vec<String>>,
+            cwd: AbsolutePathBuf,
+            approval_policy: AskForApproval,
+            approvals_reviewer: Option<ApprovalsReviewer>,
+            // Older histories are normalized here; decoded items retain only the profile.
+            sandbox_policy: Option<SandboxPolicy>,
+            permission_profile: Option<PermissionProfile>,
+            active_permission_profile: Option<ActivePermissionProfile>,
+            file_system_sandbox_policy: Option<RawFileSystemSandboxPolicy>,
+            model: String,
+            comp_hash: Option<String>,
+            collaboration_mode: Option<CollaborationMode>,
+            multi_agent_version: Option<MultiAgentVersion>,
+            realtime_active: Option<bool>,
+            cyber_access_program: Option<CyberAccessProgram>,
+            effort: Option<ReasoningEffortConfig>,
+            summary: Option<ReasoningSummaryConfig>,
+        }
+
+        let wire = Wire::deserialize(deserializer)?;
+        let permission_profile = match wire.permission_profile {
+            Some(permission_profile) => permission_profile,
+            None => {
+                let sandbox_policy = wire
+                    .sandbox_policy
+                    .ok_or_else(|| serde::de::Error::missing_field("permission_profile"))?;
+                let file_system_sandbox_policy = wire
+                    .file_system_sandbox_policy
+                    .map(TryInto::try_into)
+                    .transpose()
+                    // Malformed historical split rules must not regain legacy grants.
+                    .unwrap_or_else(|_| Some(FileSystemSandboxPolicy::restricted(Vec::new())))
+                    .unwrap_or_else(|| {
+                        FileSystemSandboxPolicy::from_legacy_sandbox_policy_for_cwd(
+                            &sandbox_policy,
+                            wire.cwd.as_path(),
+                        )
+                    });
+                PermissionProfile::from_runtime_permissions_with_enforcement(
+                    SandboxEnforcement::from_legacy_sandbox_policy(&sandbox_policy),
+                    &file_system_sandbox_policy,
+                    NetworkSandboxPolicy::from(&sandbox_policy),
+                )
+            }
+        };
+        Ok(Self {
+            turn_id: wire.turn_id,
+            root_turn_id: wire.root_turn_id,
+            direct_only_tool_namespaces: wire.direct_only_tool_namespaces,
+            disabled_plugin_ids: wire.disabled_plugin_ids,
+            cwd: wire.cwd,
+            approval_policy: wire.approval_policy,
+            approvals_reviewer: wire.approvals_reviewer,
+            permission_profile,
+            active_permission_profile: wire.active_permission_profile,
+            model: wire.model,
+            comp_hash: wire.comp_hash,
+            collaboration_mode: wire.collaboration_mode,
+            multi_agent_version: wire.multi_agent_version,
+            realtime_active: wire.realtime_active,
+            cyber_access_program: wire.cyber_access_program,
+            effort: wire.effort,
+            summary: wire.summary,
         })
     }
 }
@@ -6573,7 +6655,7 @@
         }))?;
 
         assert_eq!(item.summary, None);
-        assert_eq!(item.file_system_sandbox_policy, None);
+        assert_eq!(item.permission_profile, PermissionProfile::Disabled);
         assert_eq!(item.comp_hash, None);
         assert_eq!(serde_json::to_value(item)?.get("summary"), None);
         Ok(())
@@ -6594,56 +6676,63 @@
     }
 
     #[test]
-    fn turn_context_item_serializes_split_policy_and_summary() -> Result<()> {
-        let item = TurnContextItem {
-            turn_id: None,
-            root_turn_id: None,
-            direct_only_tool_namespaces: None,
-            disabled_plugin_ids: None,
-            cwd: test_path_buf("/tmp").abs(),
-            approval_policy: AskForApproval::Never,
-            approvals_reviewer: None,
-            sandbox_policy: SandboxPolicy::DangerFullAccess,
-            permission_profile: None,
-            active_permission_profile: None,
-            file_system_sandbox_policy: Some(
-                FileSystemSandboxPolicy::restricted(vec![FileSystemSandboxEntry {
-                    path: FileSystemPath::GlobPattern {
-                        pattern: "/tmp/private/**/*.txt".to_string(),
-                    },
-                    access: FileSystemAccessMode::Deny,
-                    missing_path_behavior: None,
-                }])
-                .try_into()
+    fn turn_context_item_normalizes_legacy_permissions_and_writes_profile_only() -> Result<()> {
+        let cwd = test_path_buf("/tmp").abs();
+        let file_system = FileSystemSandboxPolicy::restricted(vec![FileSystemSandboxEntry {
+            path: FileSystemPath::GlobPattern {
+                pattern: "/tmp/private/**/*.txt".to_string(),
+            },
+            access: FileSystemAccessMode::Deny,
+            missing_path_behavior: None,
+        }]);
+        let mut legacy = json!({
+            "cwd": cwd,
+            "approval_policy": "never",
+            "sandbox_policy": { "type": "danger-full-access" },
+            "file_system_sandbox_policy": RawFileSystemSandboxPolicy::try_from(file_system.clone())
                 .expect("serializable split policy"),
-            ),
-            model: "gpt-5".to_string(),
-            comp_hash: None,
-            collaboration_mode: None,
-            multi_agent_version: None,
-            realtime_active: None,
-            cyber_access_program: None,
-            effort: None,
-            summary: Some(ReasoningSummaryConfig::None),
-        };
-
-        let value = serde_json::to_value(item)?;
+            "model": "gpt-5",
+            "summary": "none",
+        });
+        let item: TurnContextItem = serde_json::from_value(legacy.clone())?;
+        let profile = PermissionProfile::from_runtime_permissions(
+            &file_system,
+            NetworkSandboxPolicy::Enabled,
+        );
+        assert_eq!(item.permission_profile, profile);
+        let canonical = serde_json::to_value(&item)?;
         assert_eq!(
-            value["file_system_sandbox_policy"],
+            canonical,
             json!({
-                "kind": "restricted",
-                "entries": [{
-                    "path": {
-                        "type": "glob_pattern",
-                        "pattern": "/tmp/private/**/*.txt"
-                    },
-                    "access": "deny"
-                }]
+                "cwd": cwd,
+                "approval_policy": "never",
+                "permission_profile": profile,
+                "model": "gpt-5",
+                "summary": "none",
             })
         );
-        let legacy_summary: ReasoningSummaryConfig =
-            serde_json::from_value(value["summary"].clone())?;
-        assert_eq!(legacy_summary, ReasoningSummaryConfig::None);
+        assert_eq!(
+            serde_json::from_value::<TurnContextItem>(canonical.clone())?,
+            item
+        );
+
+        legacy["file_system_sandbox_policy"]["entries"][0]["path"] =
+            json!({ "type": "path", "path": "://" });
+        assert_eq!(
+            serde_json::from_value::<TurnContextItem>(legacy.clone())?.permission_profile,
+            PermissionProfile::from_runtime_permissions(
+                &FileSystemSandboxPolicy::restricted(Vec::new()),
+                NetworkSandboxPolicy::Enabled,
+            ),
+        );
+        legacy["permission_profile"] = serde_json::to_value(&profile)?;
+        assert_eq!(serde_json::from_value::<TurnContextItem>(legacy)?, item);
+        let mut missing_permissions = canonical;
+        missing_permissions
+            .as_object_mut()
+            .expect("context object")
+            .remove("permission_profile");
+        assert!(serde_json::from_value::<TurnContextItem>(missing_permissions).is_err());
         Ok(())
     }
```

### Configuration fields

[Schema at this release](https://github.com/openai/codex/blob/d32063f96c2dff1dc96af839b3952abb6acfeda4/codex-rs/core/config.schema.json)

- Removed: `auto_review.experimental_policy_template`
- Removed: `auto_review.extra_policy`
- Added: `features.daybreak_program_propagation`
- Added: `features.gateway_setup_wizard`
- Added: `features.incremental_tools_legacy`
- Added: `features.incremental_tools_legacy_gcp`
- Added: `features.mcp_lazy_stdio_startup`
- Changed: `model_providers.*.aws.credential_export`
- Changed: `model_providers.*.gateway_oauth`
- Added: `model_providers.*.gateway_oauth.credential_export`
- Added: `model_providers.*.gateway_oauth.credential_export.args`
- Added: `model_providers.*.gateway_oauth.credential_export.args[]`
- Added: `model_providers.*.gateway_oauth.credential_export.command`
- Added: `model_providers.*.gateway_oauth.credential_export.timeout_ms`
- Changed: `model_providers.*.gateway_oauth.delivery`
- Added: `model_providers.*.gateway_oauth.device_authorization_url`
- Added: `profiles.*.features.daybreak_program_propagation`
- Added: `profiles.*.features.gateway_setup_wizard`
- Added: `profiles.*.features.incremental_tools_legacy`
- Added: `profiles.*.features.incremental_tools_legacy_gcp`
- Added: `profiles.*.features.mcp_lazy_stdio_startup`
- Added: `tui.collapse_turn_details`
- Changed: `tui.keymap`
- Changed: `tui.keymap.global`
- Added: `tui.keymap.global.close_sidebar_tab`
- Added: `tui.keymap.global.close_sidebar_tab[]`
- Added: `tui.keymap.global.focus_sidebar_tabs`
- Added: `tui.keymap.global.focus_sidebar_tabs[]`
- Added: `tui.keymap.global.sidebar_down`
- Added: `tui.keymap.global.sidebar_down[]`
- Added: `tui.keymap.global.sidebar_up`
- Added: `tui.keymap.global.sidebar_up[]`

## rust-v0.169.0 → rust-v0.169.1

Commit: `c376cf7396eff83ce4c6ac61b9553df142e7a0be`

No changed cited ranges.

### Configuration fields

[Schema at this release](https://github.com/openai/codex/blob/c376cf7396eff83ce4c6ac61b9553df142e7a0be/codex-rs/core/config.schema.json)

No schema field changes.

## rust-v0.169.1 → rust-v0.170.0

Commit: `29eb79e9866b3262a777fdf8195c1b9e63684c91`

### codex-rs/config/src/types.rs — apps

```diff
--- rust-v0.169.1/codex-rs/config/src/types.rs
+++ rust-v0.170.0/codex-rs/config/src/types.rs
@@ -29,6 +29,7 @@
 use std::collections::BTreeMap;
 use std::collections::HashMap;
 use std::fmt;
+use std::num::NonZeroU64;
 
 use codex_utils_redacted_string::RedactedString;
 use schemars::JsonSchema;
@@ -637,6 +638,11 @@
 #[derive(Serialize, Deserialize, Debug, Clone, PartialEq, Default, JsonSchema)]
 #[schemars(deny_unknown_fields)]
 pub struct OtelConfigToml {
+    /// Command that prints a JSON object of HTTP headers for explicit OTLP HTTP exporters.
+    /// Runs from CODEX_HOME. Repository-local configuration cannot set OTel options.
+    pub headers_helper: Option<String>,
+    /// Interval between helper executions in milliseconds. Defaults to 29 minutes.
+    pub headers_helper_refresh_interval_ms: Option<NonZeroU64>,
     /// Byte limit for tool-result log output; independent of model-visible output.
     pub tool_result: Option<codex_protocol::config_types::ToolResultLogConfig>,
     /// Log successful SSE events whose kind ends in `.delta`. Defaults to true.
@@ -674,6 +680,8 @@
 /// Effective OTEL settings after defaults are applied.
 #[derive(Debug, Clone, PartialEq)]
 pub struct OtelConfig {
+    pub headers_helper: Option<String>,
+    pub headers_helper_refresh_interval_ms: Option<NonZeroU64>,
     pub tool_result: codex_protocol::config_types::ToolResultLogConfig,
     pub log_sse_deltas: bool,
     pub log_user_prompt: bool,
@@ -690,6 +698,8 @@
 impl Default for OtelConfig {
     fn default() -> Self {
         OtelConfig {
+            headers_helper: None,
+            headers_helper_refresh_interval_ms: None,
             tool_result: Default::default(),
             log_sse_deltas: true,
             log_user_prompt: false,
```

### codex-rs/core/config.schema.json — schema

```diff
--- rust-v0.169.1/codex-rs/core/config.schema.json
+++ rust-v0.170.0/codex-rs/core/config.schema.json
@@ -1199,6 +1199,9 @@
             "multi_env_copy_file": {
               "type": "boolean"
             },
+            "multi_environment_mcp": {
+              "type": "boolean"
+            },
             "network_proxy": {
               "$ref": "#/definitions/FeatureToml_for_NetworkProxyConfigToml"
             },
@@ -2246,6 +2249,13 @@
           "format": "uint",
           "minimum": 0.0,
           "type": "integer"
+        },
+        "nested_tool_names": {
+          "description": "Exact Code Mode tool names for the transcript_selected_exec_results section.",
+          "items": {
+            "type": "string"
+          },
+          "type": "array"
         }
       },
       "required": [
@@ -3925,6 +3935,16 @@
             }
           ],
           "description": "Optional log exporter"
+        },
+        "headers_helper": {
+          "description": "Command that prints a JSON object of HTTP headers for explicit OTLP HTTP exporters. Runs from CODEX_HOME. Repository-local configuration cannot set OTel options.",
+          "type": "string"
+        },
+        "headers_helper_refresh_interval_ms": {
+          "description": "Interval between helper executions in milliseconds. Defaults to 29 minutes.",
+          "format": "uint64",
+          "minimum": 1.0,
+          "type": "integer"
         },
         "log_agent_responses": {
           "description": "Opt in to logging final main-agent and spawned-subagent responses to an OTLP log exporter. Defaults to false. Response text can be sensitive and is capped at 64 KiB.",
@@ -8269,6 +8289,9 @@
         "multi_env_copy_file": {
           "type": "boolean"
         },
+        "multi_environment_mcp": {
+          "type": "boolean"
+        },
         "network_proxy": {
           "$ref": "#/definitions/FeatureToml_for_NetworkProxyConfigToml"
         },
```

### codex-rs/protocol/src/protocol.rs — approval, sandbox

```diff
--- rust-v0.169.1/codex-rs/protocol/src/protocol.rs
+++ rust-v0.170.0/codex-rs/protocol/src/protocol.rs
@@ -61,6 +61,7 @@
 use crate::request_permissions::RequestPermissionsEvent;
 use crate::request_permissions::RequestPermissionsResponse;
 use crate::request_user_input::RequestUserInputResponse;
+use crate::response_item_id::OptionalWireItemId;
 use crate::turn_input::CyberAccessProgram;
 use crate::turn_input::SuspendTurnOutcome;
 use crate::turn_input::TurnInputMode;
@@ -994,7 +995,8 @@
 #[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, JsonSchema, TS)]
 pub struct InterAgentCommunication {
     #[serde(default, skip_serializing_if = "Option::is_none")]
-    #[ts(optional)]
+    #[serde(with = "OptionalWireItemId")]
+    #[ts(optional, as = "Option<ResponseItemId>")]
     pub id: Option<ResponseItemId>,
     pub author: AgentPath,
     pub recipient: AgentPath,
@@ -2414,12 +2416,30 @@
 }
 
 #[derive(Debug, Clone, Deserialize, Serialize, PartialEq, JsonSchema, TS)]
+#[serde(from = "StoredTargetedModeration")]
 pub struct TargetedAnswerModeration {
     pub item_id: String,
     pub moderated: bool,
     #[serde(default, skip_serializing_if = "Option::is_none")]
     #[ts(optional)]
     pub display: Option<crate::items::AgentMessageDisplay>,
+}
+
+#[derive(Deserialize)]
+struct StoredTargetedModeration {
+    item_id: String,
+    #[serde(flatten)]
+    decision: crate::items::AgentMessageModeration,
+}
+
+impl From<StoredTargetedModeration> for TargetedAnswerModeration {
+    fn from(value: StoredTargetedModeration) -> Self {
+        Self {
+            item_id: value.item_id,
+            moderated: value.decision.moderated,
+            display: value.decision.display,
+        }
+    }
 }
 
 #[derive(Debug, Clone, Deserialize, Serialize, PartialEq, JsonSchema, TS)]
@@ -3450,7 +3470,7 @@
 
 #[derive(Serialize, Deserialize, Clone, Debug, PartialEq, Eq, JsonSchema)]
 pub struct SessionContextWindow {
-    /// UUIDv7 identity of this context window.
+    /// Persisted model-facing window identity.
     pub window_id: crate::ContextWindowId,
 }
```

### Configuration fields

[Schema at this release](https://github.com/openai/codex/blob/29eb79e9866b3262a777fdf8195c1b9e63684c91/codex-rs/core/config.schema.json)

- Added: `features.guardianv2.sync_elastic_sections.*.nested_tool_names`
- Added: `features.guardianv2.sync_elastic_sections.*.nested_tool_names[]`
- Added: `features.multi_environment_mcp`
- Added: `otel.headers_helper`
- Added: `otel.headers_helper_refresh_interval_ms`
- Added: `profiles.*.features.guardianv2.sync_elastic_sections.*.nested_tool_names`
- Added: `profiles.*.features.guardianv2.sync_elastic_sections.*.nested_tool_names[]`
- Added: `profiles.*.features.multi_environment_mcp`

## rust-v0.170.0 → rust-v0.171.0

Commit: `ccf9be8cc458bd6b8336fe84d68d8893f2691a5e`

### codex-rs/config/src/loader/mod.rs — roots-layer

```diff
--- rust-v0.170.0/codex-rs/config/src/loader/mod.rs
+++ rust-v0.171.0/codex-rs/config/src/loader/mod.rs
@@ -1653,7 +1658,11 @@
     }
     // The typed round trip resolves AbsolutePathBuf fields against this layer's directory.
     let _guard = AbsolutePathBufGuard::new(base_dir);
-    let Ok(resolved) = ConfigToml::try_from(value_from_config_toml.clone()) else {
+    // Provider identities contain no paths. An ignored malformed identity must not
+    // prevent an unrelated path in this layer from being resolved against its directory.
+    let path_input =
+        crate::config_layer_source::without_status_line_provider(&value_from_config_toml);
+    let Ok(resolved) = ConfigToml::try_from(path_input.into_owned()) else {
         return Ok(value_from_config_toml);
     };
     drop(_guard);
```

### codex-rs/config/src/mcp_types.rs — mcp

```diff
--- rust-v0.170.0/codex-rs/config/src/mcp_types.rs
+++ rust-v0.171.0/codex-rs/config/src/mcp_types.rs
@@ -206,7 +206,7 @@
     /// still fall back to stored OAuth credentials.
     #[serde(rename = "chatgpt")]
     ChatGpt,
-    /// Exchange an enterprise IdP refresh token for resource-specific authorization.
+    /// Exchange an enterprise IdP refresh token or, if none was issued, a current ID token for resource-specific authorization.
     /// Alternate credentials and ordinary OAuth fallback are not permitted.
     #[serde(rename = "ema_auth")]
     EmaAuth,
```

### codex-rs/config/src/types.rs — apps

```diff
--- rust-v0.170.0/codex-rs/config/src/types.rs
+++ rust-v0.171.0/codex-rs/config/src/types.rs
@@ -880,6 +880,28 @@
     }
 }
 
+/// The configured MCP server and advertised tool name identify a status line provider.
+#[derive(Serialize, Deserialize, Debug, Clone, PartialEq, Eq, JsonSchema)]
+#[serde(deny_unknown_fields)]
+pub struct StatusLineProviderId {
+    pub server: String,
+    pub tool: String,
+}
+
+/// An explicit default overrides an MCP provider from a lower configuration layer.
+#[derive(Serialize, Deserialize, Debug, Clone, PartialEq, Eq, JsonSchema)]
+#[serde(untagged)]
+pub enum StatusLineSelection {
+    Builtin(BuiltinStatusLine),
+    Mcp(StatusLineProviderId),
+}
+
+#[derive(Serialize, Deserialize, Debug, Clone, PartialEq, Eq, JsonSchema)]
+#[serde(rename_all = "lowercase")]
+pub enum BuiltinStatusLine {
+    Default,
+}
+
 /// Collection of settings that are specific to the TUI.
 #[derive(Serialize, Deserialize, Debug, Clone, PartialEq, Default, JsonSchema)]
 #[schemars(deny_unknown_fields)]
@@ -996,6 +1018,9 @@
     /// When unset, the TUI defaults to: `model-with-reasoning`, `current-dir`, and `thread-name`.
     #[serde(default)]
     pub status_line: Option<Vec<String>>,
+
+    /// Local status line selection. Set to "default" for built-in items or specify an MCP server and tool.
+    pub status_line_provider: Option<Box<StatusLineSelection>>,
 
     /// Color status line items with colors derived from the active syntax theme.
     /// Defaults to `true`.
@@ -1253,6 +1278,9 @@
 #[derive(Serialize, Deserialize, Debug, Clone, PartialEq, Eq, Default, JsonSchema)]
 #[schemars(deny_unknown_fields)]
 pub struct MarketplaceConfig {
+    /// Check for updates to installed Git plugins from this marketplace when plugins are listed.
+    #[serde(default)]
+    pub auto_update: bool,
     /// Last time Codex successfully added or refreshed this marketplace.
     #[serde(default)]
     pub last_updated: Option<String>,
```

### codex-rs/core/config.schema.json — schema

```diff
--- rust-v0.170.0/codex-rs/core/config.schema.json
+++ rust-v0.171.0/codex-rs/core/config.schema.json
@@ -609,6 +609,12 @@
       },
       "type": "object"
     },
+    "BuiltinStatusLine": {
+      "enum": [
+        "default"
+      ],
+      "type": "string"
+    },
     "BundledSkillsConfig": {
       "additionalProperties": false,
       "properties": {
@@ -700,6 +706,18 @@
         },
         "enabled": {
           "type": "boolean"
+        }
+      },
+      "type": "object"
+    },
+    "CodeModeToml": {
+      "additionalProperties": false,
+      "properties": {
+        "heartbeat_interval_s": {
+          "description": "Idle seconds between gRPC stream heartbeats. Zero (the default) disables them.",
+          "format": "uint32",
+          "minimum": 0.0,
+          "type": "integer"
         }
       },
       "type": "object"
@@ -878,6 +896,9 @@
             "browser_use_full_cdp_access": {
               "type": "boolean"
             },
+            "catalog_apps_instructions": {
+              "type": "boolean"
+            },
             "chronicle": {
               "type": "boolean"
             },
@@ -1028,6 +1049,9 @@
             "fast_mode": {
               "type": "boolean"
             },
+            "file_backed_tool_audio": {
+              "type": "boolean"
+            },
             "gateway_setup_wizard": {
               "type": "boolean"
             },
@@ -1056,6 +1080,9 @@
               "type": "boolean"
             },
             "guardian_native_multi_agent_history": {
+              "type": "boolean"
+            },
+            "guardian_nested_approval_context": {
               "type": "boolean"
             },
             "guardian_node_repl_transcript_images": {
@@ -1169,6 +1196,9 @@
             "mcp_oauth_refresh_coordination": {
               "type": "boolean"
             },
+            "mcp_shared_repl_cwd": {
+              "type": "boolean"
+            },
             "mcp_tool_list_changed": {
               "type": "boolean"
             },
@@ -1218,6 +1248,9 @@
               "type": "boolean"
             },
             "output_token_replay": {
+              "type": "boolean"
+            },
+            "per_environment_context": {
               "type": "boolean"
             },
             "personality": {
@@ -1292,6 +1325,9 @@
             "responses_websockets_v2": {
               "type": "boolean"
             },
+            "restored_history_prewarm": {
+              "type": "boolean"
+            },
             "retain_client_developer_messages": {
               "type": "boolean"
             },
@@ -1305,6 +1341,9 @@
               "$ref": "#/definitions/FeatureToml_for_RuntimeAgentInstancesConfigToml"
             },
             "runtime_metrics": {
+              "type": "boolean"
+            },
+            "safe_image_decoder": {
               "type": "boolean"
             },
             "search_tool": {
@@ -1458,6 +1497,9 @@
               "type": "boolean"
             },
             "use_xaa": {
+              "type": "boolean"
+            },
+            "utc_environment_date": {
               "type": "boolean"
             },
             "view_image": {
@@ -2282,6 +2324,17 @@
           ],
           "description": "Deprecated and ignored; asynchronous classification always uses conversations."
         },
+        "async_elastic_budgeting": {
+          "description": "Enable elastic allocation for asynchronous Guardian requests. Defaults to false.",
+          "type": "boolean"
+        },
+        "async_elastic_sections": {
+          "additionalProperties": {
+            "$ref": "#/definitions/GuardianElasticSectionConfigToml"
+          },
+          "description": "Section limits validated when asynchronous elastic budgeting is enabled.",
+          "type": "object"
+        },
         "classifier_instructions": {
           "type": "string"
         },
@@ -2739,6 +2792,11 @@
     "MarketplaceConfig": {
       "additionalProperties": false,
       "properties": {
+        "auto_update": {
+          "default": false,
+          "description": "Check for updates to installed Git plugins from this marketplace when plugins are listed.",
+          "type": "boolean"
+        },
         "last_revision": {
           "default": null,
           "description": "Git revision Codex last successfully activated for this marketplace.",
@@ -2845,7 +2903,7 @@
           "type": "string"
         },
         {
-          "description": "Exchange an enterprise IdP refresh token for resource-specific authorization. Alternate credentials and ordinary OAuth fallback are not permitted.",
+          "description": "Exchange an enterprise IdP refresh token or, if none was issued, a current ID token for resource-specific authorization. Alternate credentials and ordinary OAuth fallback are not permitted.",
           "enum": [
             "ema_auth"
           ],
@@ -3368,6 +3426,10 @@
         "hide_spawn_agent_metadata": {
           "type": "boolean"
         },
+        "interrupt_at_item_boundary": {
+          "description": "Let a subagent finish its current output item while cancelling tools immediately.",
+          "type": "boolean"
+        },
         "max_concurrent_threads_per_session": {
           "format": "uint",
           "minimum": 1.0,
@@ -3660,6 +3722,10 @@
         "socks_url": {
           "type": "string"
         },
+        "transparent_tcp": {
+          "description": "Route outbound TCP from managed Linux sandbox commands through the managed SOCKS5 proxy.",
+          "type": "boolean"
+        },
         "unix_sockets": {
           "additionalProperties": {
             "$ref": "#/definitions/NetworkProxyUnixSocketPermissionToml"
@@ -3729,6 +3795,10 @@
         },
         "socks_url": {
           "type": "string"
+        },
+        "transparent_tcp": {
+          "description": "Route outbound TCP from managed Linux sandbox commands through the managed SOCKS5 proxy.",
+          "type": "boolean"
         },
         "unix_sockets": {
           "$ref": "#/definitions/NetworkUnixSocketPermissionsToml"
@@ -4660,7 +4730,7 @@
     },
     "RemoteMessageBoardConfigToml": {
       "additionalProperties": false,
-      "description": "Connection to a board provisioned by the research host.",
+      "description": "Connection settings for a remote message board.",
       "properties": {
         "bearer_token": {
           "description": "Board credential supplied directly by a runtime config override.",
@@ -4677,6 +4747,38 @@
       "required": [
         "url"
       ],
+      "type": "object"
+    },
+    "ResponseProcessMode": {
+      "oneOf": [
+        {
+          "description": "Process items as they arrive. A tool can start before its response is complete.",
+          "enum": [
+            "streaming"
+          ],
+          "type": "string"
+        },
+        {
+          "description": "Process buffered items in order after the response completes, synchronous post-hooks finish, and any budget charges are posted.",
+          "enum": [
+            "after_complete_response"
+          ],
+          "type": "string"
+        }
+      ]
+    },
+    "ResponsesToml": {
+      "additionalProperties": false,
+      "properties": {
+        "process_mode": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/ResponseProcessMode"
+            }
+          ],
+          "description": "When to process response items, including text and tool calls. Defaults to `streaming`."
+        }
+      },
       "type": "object"
     },
     "ResumeCwdMode": {
@@ -4734,7 +4836,14 @@
           "description": "Stop when the shared budget is exhausted. Defaults to true.",
           "type": "boolean"
         },
+        "limit_budget": {
+          "description": "Positive, finite allowance in budget units. Set either limit_tokens or limit_budget. Spending exactly this amount is allowed.",
+          "exclusiveMinimum": 0.0,
+          "format": "double",
+          "type": "number"
+        },
         "limit_tokens": {
+          "description": "Positive whole-token allowance. Set either limit_tokens or limit_budget.",
           "format": "int64",
           "minimum": 1.0,
           "type": "integer"
@@ -4743,6 +4852,10 @@
           "format": "double",
           "minimum": 0.0,
           "type": "number"
+        },
+        "reminder_at_context_start": {
+          "description": "Restate the balance when a thread starts or its context is compacted. Defaults to true. Set false with an empty threshold list for no budget reminders.",
+          "type": "boolean"
         },
         "reminder_at_remaining_tokens": {
           "description": "Remaining weighted-token values that trigger reminders when crossed.",
@@ -4756,6 +4869,25 @@
           "format": "double",
           "minimum": 0.0,
           "type": "number"
+        }
+      },
+      "type": "object"
+    },
+    "RolloutTraceToml": {
+      "additionalProperties": false,
+      "description": "Storage budgets for one native rollout trace, shared by the root and its children.",
+      "properties": {
+        "max_bytes": {
+          "description": "Maximum bytes for the manifest, event log, and compressed payload shards. Defaults to 256 MiB.",
+          "format": "uint64",
+          "minimum": 0.0,
+          "type": "integer"
+        },
+        "max_payload_bytes": {
+          "description": "Maximum uncompressed bytes retained per new body or separated value. Defaults to 64 MiB.",
+          "format": "uint",
+          "minimum": 0.0,
+          "type": "integer"
         }
       },
       "type": "object"
@@ -5005,6 +5137,34 @@
         }
       ]
     },
+    "StatusLineProviderId": {
+      "additionalProperties": false,
+      "description": "The configured MCP server and advertised tool name identify a status line provider.",
+      "properties": {
+        "server": {
+          "type": "string"
+        },
+        "tool": {
+          "type": "string"
+        }
+      },
+      "required": [
+        "server",
+        "tool"
+      ],
+      "type": "object"
+    },
+    "StatusLineSelection": {
+      "anyOf": [
+        {
+          "$ref": "#/definitions/BuiltinStatusLine"
+        },
+        {
+          "$ref": "#/definitions/StatusLineProviderId"
+        }
+      ],
+      "description": "An explicit default overrides an MCP provider from a lower configuration layer."
+    },
     "ThreadStoreToml": {
       "oneOf": [
         {
@@ -5036,6 +5196,10 @@
           "description": "Developer message sampled before an automatic context-window rollover.",
           "maxLength": 2000,
           "type": "string"
+        },
+        "context_window_as_tool_output": {
+          "description": "Render the context window and its hints as an agent.thread_hint tool output.",
+          "type": "boolean"
         },
         "enabled": {
           "type": "boolean"
@@ -5366,8 +5530,10 @@
               "history_search_next": null,
               "history_search_previous": null,
               "queue": null,
+              "redo": null,
               "submit": null,
-              "toggle_shortcuts": null
+              "toggle_shortcuts": null,
+              "undo": null
             },
             "editor": {
               "delete_backward": null,
@@ -5390,6 +5556,7 @@
             },
             "global": {
               "change_host": null,
+              "choose_cloud_environment": null,
               "clear_terminal": null,
               "close_sidebar_tab": null,
               "copy": null,
@@ -5443,6 +5610,7 @@
               "half_page_up": null,
               "jump_bottom": null,
               "jump_top": null,
+              "mark_markdown": null,
               "page_down": null,
               "page_up": null,
               "scroll_down": null,
@@ -5673,6 +5841,14 @@
             "type": "string"
           },
           "type": "array"
+        },
+        "status_line_provider": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/StatusLineSelection"
+            }
+          ],
+          "description": "Local status line selection. Set to \"default\" for built-in items or specify an MCP server and tool."
         },
         "status_line_use_colors": {
           "default": true,
@@ -6004,6 +6180,14 @@
           ],
           "description": "Queue the current composer draft while a task is running."
         },
+        "redo": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Redo an undone composer edit."
+        },
         "submit": {
           "allOf": [
             {
@@ -6019,6 +6203,14 @@
             }
           ],
           "description": "Toggle the composer shortcut overlay."
+        },
+        "undo": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Undo the last edit to the composer draft."
         }
       },
       "type": "object"
@@ -6214,6 +6406,14 @@
             }
           ],
           "description": "Change where a new conversation runs."
+        },
+        "choose_cloud_environment": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Choose a saved environment for a new Cloud conversation."
         },
         "clear_terminal": {
           "allOf": [
@@ -6546,8 +6746,10 @@
             "history_search_next": null,
             "history_search_previous": null,
             "queue": null,
+            "redo": null,
             "submit": null,
-            "toggle_shortcuts": null
+            "toggle_shortcuts": null,
+            "undo": null
           }
         },
         "editor": {
@@ -6584,6 +6786,7 @@
           ],
           "default": {
             "change_host": null,
+            "choose_cloud_environment": null,
             "clear_terminal": null,
             "close_sidebar_tab": null,
             "copy": null,
@@ -6651,6 +6854,7 @@
             "half_page_up": null,
             "jump_bottom": null,
             "jump_top": null,
+            "mark_markdown": null,
             "page_down": null,
             "page_up": null,
             "scroll_down": null,
@@ -6911,6 +7115,14 @@
             }
           ],
           "description": "Jump to the beginning."
+        },
+        "mark_markdown": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Mark Markdown structure under the caret in transcript selection mode."
         },
         "page_down": {
           "allOf": [
@@ -7816,6 +8028,14 @@
       ],
       "description": "Cloud-owned feature settings."
     },
+    "code_mode": {
+      "allOf": [
+        {
+          "$ref": "#/definitions/CodeModeToml"
+        }
+      ],
+      "description": "Code Mode session settings."
+    },
     "compact_prompt": {
       "description": "Compact prompt used for history compaction.",
       "type": "string"
@@ -7968,6 +8188,9 @@
         "browser_use_full_cdp_access": {
           "type": "boolean"
         },
+        "catalog_apps_instructions": {
+          "type": "boolean"
+        },
         "chronicle": {
           "type": "boolean"
         },
@@ -8118,6 +8341,9 @@
         "fast_mode": {
           "type": "boolean"
         },
+        "file_backed_tool_audio": {
+          "type": "boolean"
+        },
         "gateway_setup_wizard": {
           "type": "boolean"
         },
@@ -8146,6 +8372,9 @@
           "type": "boolean"
         },
         "guardian_native_multi_agent_history": {
+          "type": "boolean"
+        },
+        "guardian_nested_approval_context": {
           "type": "boolean"
         },
         "guardian_node_repl_transcript_images": {
@@ -8259,6 +8488,9 @@
         "mcp_oauth_refresh_coordination": {
           "type": "boolean"
         },
+        "mcp_shared_repl_cwd": {
+          "type": "boolean"
+        },
         "mcp_tool_list_changed": {
           "type": "boolean"
         },
@@ -8308,6 +8540,9 @@
           "type": "boolean"
         },
         "output_token_replay": {
+          "type": "boolean"
+        },
+        "per_environment_context": {
           "type": "boolean"
         },
         "personality": {
@@ -8382,6 +8617,9 @@
         "responses_websockets_v2": {
           "type": "boolean"
         },
+        "restored_history_prewarm": {
+          "type": "boolean"
+        },
         "retain_client_developer_messages": {
           "type": "boolean"
         },
@@ -8395,6 +8633,9 @@
           "$ref": "#/definitions/FeatureToml_for_RuntimeAgentInstancesConfigToml"
         },
         "runtime_metrics": {
+          "type": "boolean"
+        },
+        "safe_image_decoder": {
           "type": "boolean"
         },
         "search_tool": {
@@ -8548,6 +8789,9 @@
           "type": "boolean"
         },
         "use_xaa": {
+          "type": "boolean"
+        },
+        "utc_environment_date": {
           "type": "boolean"
         },
         "view_image": {
@@ -8939,6 +9183,14 @@
       "default": null,
       "description": "Experimental / do not use. Realtime websocket session selection. `version` controls v1/v2 and `type` controls conversational/transcription."
     },
+    "responses": {
+      "allOf": [
+        {
+          "$ref": "#/definitions/ResponsesToml"
+        }
+      ],
+      "description": "Controls how Codex processes model responses."
+    },
     "responses_api_metadata": {
       "additionalProperties": {
         "type": "string"
@@ -8949,6 +9201,14 @@
     "review_model": {
       "description": "Review model override used by the `/review` feature.",
       "type": "string"
+    },
+    "rollout_trace": {
+      "allOf": [
+        {
+          "$ref": "#/definitions/RolloutTraceToml"
+        }
+      ],
+      "description": "Capture limits for local rollout traces when recording is enabled."
     },
     "sandbox_mode": {
       "allOf": [
```

### codex-rs/core/src/exec_policy.rs — saved-runtime

```diff
--- rust-v0.170.0/codex-rs/core/src/exec_policy.rs
+++ rust-v0.171.0/codex-rs/core/src/exec_policy.rs
@@ -276,10 +276,13 @@
     JoinBlockingTask { source: tokio::task::JoinError },
 
     #[error("failed to update in-memory rules: {source}")]
-    AddRule {
-        #[from]
-        source: ExecPolicyRuleError,
-    },
+    AddRule { source: ExecPolicyRuleError },
+}
+
+impl From<ExecPolicyRuleError> for ExecPolicyUpdateError {
+    fn from(source: ExecPolicyRuleError) -> Self {
+        Self::AddRule { source }
+    }
 }
 
 pub(crate) struct ExecPolicyManager {
```

### codex-rs/core/src/mcp.rs — apps-connection

```diff
--- rust-v0.170.0/codex-rs/core/src/mcp.rs
+++ rust-v0.171.0/codex-rs/core/src/mcp.rs
@@ -510,7 +512,7 @@
                 CODEX_APPS_MCP_SERVER_NAME.to_string(),
                 LEGACY_CODEX_APPS_REGISTRATION_ID,
                 codex_apps_mcp_server_config(
-                    &mcp_config.chatgpt_base_url,
+                    &mcp_config.client.chatgpt_base_url,
                     mcp_config.apps_mcp_product_sku.as_deref(),
                     originator,
                 ),
```

### codex-rs/hooks/src/engine/discovery.rs — hook-groups, hook-mcp-tool, hooks

```diff
--- rust-v0.170.0/codex-rs/hooks/src/engine/discovery.rs
+++ rust-v0.171.0/codex-rs/hooks/src/engine/discovery.rs
@@ -17,6 +17,7 @@
 use codex_config::TomlValue;
 use codex_config::version_for_toml;
 use codex_plugin::PluginHookSource;
+use codex_plugin::bundled_hook_app_connector_id;
 use codex_plugin::is_allowlisted_bundled_cleanup_hook;
 use codex_protocol::protocol::HookEventName;
 use codex_utils_absolute_path::AbsolutePathBuf;
@@ -648,6 +649,14 @@
             }
         };
         for (handler_index, handler) in group.hooks.iter().cloned().enumerate() {
+            let expected_app_connector_id = source.plugin_id.as_deref().and_then(|plugin_id| {
+                bundled_hook_app_connector_id(
+                    plugin_id,
+                    event_name,
+                    group.matcher.as_deref(),
+                    &handler,
+                )
+            });
             let normalized = match handler {
                 HookHandlerConfig::Command {
                     command,
@@ -770,6 +779,7 @@
                     NormalizedHandler {
                         config,
                         kind: ConfiguredHandlerKind::McpTool {
+                            expected_app_connector_id,
                             server,
                             tool,
                             input,
@@ -819,6 +829,7 @@
                     /*app_connector_id*/ None,
                 )
             });
+            let builtin = builtin || expected_app_connector_id.is_some();
             let plugin_content_hash = match source.plugin_content_hash {
                 Some(Ok(hash)) => Some(hash.as_str()),
                 Some(Err(err)) if !builtin && !source.bypass_hook_trust => {
```

### codex-rs/protocol/src/protocol.rs — approval, sandbox

```diff
--- rust-v0.170.0/codex-rs/protocol/src/protocol.rs
+++ rust-v0.171.0/codex-rs/protocol/src/protocol.rs
@@ -64,8 +64,6 @@
 use crate::response_item_id::OptionalWireItemId;
 use crate::turn_input::CyberAccessProgram;
 use crate::turn_input::SuspendTurnOutcome;
-use crate::turn_input::TurnInputMode;
-use crate::turn_input::TurnInputRequest;
 use crate::turn_input::TurnInputSubmission;
 use crate::turn_input::TurnStartOptions;
 use codex_extension_items::image_generation::GeneratedImageRef;
@@ -134,6 +132,8 @@
 pub const ENVIRONMENTS_INSTRUCTIONS_CLOSE_TAG: &str = "</environments_instructions>";
 pub const APPS_INSTRUCTIONS_OPEN_TAG: &str = "<apps_instructions>";
 pub const APPS_INSTRUCTIONS_CLOSE_TAG: &str = "</apps_instructions>";
+pub const CATALOG_APPS_INSTRUCTIONS_OPEN_TAG: &str = "<catalog_apps_instructions>";
+pub const CATALOG_APPS_INSTRUCTIONS_CLOSE_TAG: &str = "</catalog_apps_instructions>";
 pub const SKILLS_INSTRUCTIONS_OPEN_TAG: &str = "<skills_instructions>";
 pub const SKILLS_INSTRUCTIONS_CLOSE_TAG: &str = "</skills_instructions>";
 pub const PLUGINS_INSTRUCTIONS_OPEN_TAG: &str = "<plugins_instructions>";
@@ -222,10 +222,23 @@
     pub transport: Option<ConversationStartTransport>,
     /// Overrides the configured realtime protocol version for this session only.
     pub version: Option<RealtimeConversationVersion>,
-    pub voice: Option<RealtimeVoice>,
+    /// None inherits the thread setting; Some(None) selects the provider default.
+    pub voice: Option<Option<RealtimeVoice>>,
 }
 
-/// Controls when an in-process realtime attachment may establish a connection.
+/// Authentication selected by the embedding host for an existing call.
+#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
+pub enum RealtimeExistingCallAuth {
+    /// Use the model provider's authentication and runtime destination checks.
+    #[default]
+    ModelProvider,
+    /// Use the selected auth manager's external headers and the host's transport.
+    /// The trusted host must authorize the destination, call owner, and calling
+    /// workload before selecting this mode. Never derive it from a client URL.
+    ExternalHeaders,
+}
+
+/// Controls connection admission and authentication for an in-process attachment.
 #[derive(Debug, Clone, Default)]
 pub struct RealtimeAttachmentOptions {
     /// Set the watch to `true` to cancel a pending connection.
@@ -233,6 +246,8 @@
     pub cancel: Option<watch::Receiver<bool>>,
     /// Optional caller deadline for publishing the connection. Cleanup can finish later.
     pub start_before: Option<SystemTime>,
+    /// Applies only to existing calls; external headers require an explicit host-selected URL.
+    pub existing_call_auth: RealtimeExistingCallAuth,
 }
 
 /// A caller-owned realtime sideband. Dropping either direction seals input and ends
@@ -411,6 +426,7 @@
                 RealtimeVoice::Arbor,
                 RealtimeVoice::Sol,
                 RealtimeVoice::Cove,
+                RealtimeVoice::Marin,
                 RealtimeVoice::Aube,
                 RealtimeVoice::Bubbie,
                 RealtimeVoice::Haetsal,
@@ -556,6 +572,8 @@
 /// task kind. Child sessions and consumers of frozen initial settings are unchanged.
 #[derive(Debug, Clone, Default, PartialEq)]
 pub struct TurnSettingsUpdate {
+    /// Trusted host country. `None` preserves the current setting. Published for the named live turn's subsequent steps.
+    pub request_country: Option<crate::RequestCountry>,
     /// Changes the reviewer for subsequent approval requests, not pending reviews.
     pub approvals_reviewer: Option<ApprovalsReviewer>,
     /// Replaces the selection for subsequent steps, without changing future turns.
@@ -597,6 +615,8 @@
     }),
 )]
 pub struct ThreadSettingsOverrides {
+    /// Trusted host country. `None` preserves the current setting. Inherited by future turns on acceptance.
+    pub request_country: Option<crate::RequestCountry>,
     /// Updated fallback `cwd` and environments supplied together as a complete pair.
     pub environments: Option<TurnEnvironmentRequests>,
 
@@ -720,6 +740,9 @@
     /// This server sends [`EventMsg::TurnAborted`] in response.
     Interrupt,
 
+    /// Interrupt a spawned agent, respecting its configured sampling boundary.
+    InterruptAgent,
+
     /// Interrupt the named turn only if no input is queued for it.
     /// The decision is acknowledged before cancellation finishes.
     #[debug("InterruptIfNoPendingInput {{ turn_id: {turn_id:?} }}")]
@@ -774,14 +797,6 @@
 
     /// Request the list of voices supported by realtime conversation streams.
     RealtimeConversationListVoices,
-
-    /// Submit turn input using the requested routing behavior.
-    #[debug("TurnInput {{ requested_settings: {:?} }}", request.thread_settings)]
-    TurnInput {
-        request: Box<TurnInputRequest>,
-        mode: TurnInputMode,
-        reply: oneshot::Sender<CodexResult<TurnInputSubmission>>,
-    },
 
     /// Resume an interrupted regular turn.
     #[debug("RecoverTurn {{ requested_settings: {thread_settings:?} }}")]
@@ -1126,6 +1141,7 @@
     pub fn kind(&self) -> &'static str {
         match self {
             Self::Interrupt => "interrupt",
+            Self::InterruptAgent => "interrupt_agent",
             Self::InterruptIfNoPendingInput { .. } => "interrupt_if_no_pending_input",
             Self::CleanBackgroundTerminals => "clean_background_terminals",
             Self::RealtimeConversationStart(_) => "realtime_conversation_start",
@@ -1137,7 +1153,6 @@
             Self::RealtimeConversationClose => "realtime_conversation_close",
             Self::RealtimeConversationDetach { .. } => "realtime_conversation_detach",
             Self::RealtimeConversationListVoices => "realtime_conversation_list_voices",
-            Self::TurnInput { .. } => "turn_input",
             Self::RecoverTurn { .. } => "recover_turn",
             Self::SuspendTurnAndShutdown { .. } => "suspend_turn_and_shutdown",
             Self::ThreadSettings { .. } => "thread_settings",
@@ -1349,11 +1364,7 @@
             }
         }
 
-        if self.path_contains_protected_metadata_name(path) {
-            return false;
-        }
-
-        true
+        !self.path_contains_protected_metadata_name(path)
     }
 
     fn path_contains_protected_metadata_name(&self, path: &Path) -> bool {
@@ -2713,7 +2724,7 @@
 
 #[derive(Debug, Clone, PartialEq, Deserialize, Serialize, JsonSchema, TS)]
 pub struct RateLimitWindow {
-    /// Percentage (0-100) of the window that has been consumed.
+    /// Percentage of the allowance consumed during the window. Can exceed 100.
     pub used_percent: f64,
     /// Rolling window duration, in minutes.
     #[ts(type = "number | null")]
@@ -3032,6 +3043,10 @@
 pub struct McpInvocation {
     /// Name of the MCP server as defined in the config.
     pub server: String,
+    /// Registration scope, not necessarily the server's execution environment.
+    #[serde(default, skip_serializing_if = "Option::is_none")]
+    #[ts(optional)]
+    pub environment_id: Option<String>,
     /// Name of the tool as given by the MCP server.
     pub tool: String,
     /// Arguments to the tool call.
@@ -4197,6 +4212,10 @@
 pub struct McpStartupUpdateEvent {
     /// Server name being started.
     pub server: String,
+    /// Registration scope, not necessarily the server's execution environment.
+    #[serde(default, skip_serializing_if = "Option::is_none")]
+    #[ts(optional)]
+    pub environment_id: Option<String>,
     /// Current startup status.
     pub status: McpStartupStatus,
 }
@@ -5842,6 +5861,7 @@
             item: TurnItem::McpToolCall(McpToolCallItem {
                 id: "mcp-1".into(),
                 server: "server".into(),
+                environment_id: None,
                 tool: "tool".into(),
                 arguments: json!({"arg": "value"}),
                 connector_id: Some("connector".into()),
@@ -5972,6 +5992,7 @@
             item: TurnItem::McpToolCall(McpToolCallItem {
                 id: "mcp-1".into(),
                 server: "server".into(),
+                environment_id: None,
                 tool: "tool".into(),
                 arguments: json!({"arg": "value"}),
                 connector_id: Some("connector".into()),
@@ -6851,6 +6872,7 @@
             id: "init".to_string(),
             msg: EventMsg::McpStartupUpdate(McpStartupUpdateEvent {
                 server: "srv".to_string(),
+                environment_id: None,
                 status: McpStartupStatus::Failed {
                     error: "boom".to_string(),
                     reason: Some(McpStartupFailureReason::ReauthenticationRequired),
```

### codex-rs/protocol/src/shell_environment.rs — shell-launch

```diff
--- rust-v0.170.0/codex-rs/protocol/src/shell_environment.rs
+++ rust-v0.171.0/codex-rs/protocol/src/shell_environment.rs
@@ -18,6 +22,9 @@
     "CODEX_GUARDIAN_DECISIONS_API_KEY",
     OPENAI_FEDERATION_RULE_ID_ENV_VAR,
     OPENAI_IDENTITY_TOKEN_FILE_ENV_VAR,
+    OPENAI_IDENTITY_TOKEN_SOURCE_ENV_VAR,
+    OPENAI_SPIFFE_AUDIENCE_ENV_VAR,
+    OPENAI_SPIFFE_ID_ENV_VAR,
     OPENAI_WORKLOAD_IDENTITY_CONTEXT_ENV_VAR,
 ];
```

### codex-rs/rust-toolchain.toml — rust-toolchain

```diff
--- rust-v0.170.0/codex-rs/rust-toolchain.toml
+++ rust-v0.171.0/codex-rs/rust-toolchain.toml
@@ -1,3 +1,3 @@
 [toolchain]
-channel = "1.95.0"
+channel = "1.99.1"
 components = ["clippy", "rustfmt", "rust-src"]
```

### Configuration fields

[Schema at this release](https://github.com/openai/codex/blob/ccf9be8cc458bd6b8336fe84d68d8893f2691a5e/codex-rs/core/config.schema.json)

- Added: `code_mode`
- Added: `code_mode.heartbeat_interval_s`
- Added: `features.catalog_apps_instructions`
- Added: `features.file_backed_tool_audio`
- Added: `features.guardian_nested_approval_context`
- Added: `features.guardianv2.async_elastic_budgeting`
- Added: `features.guardianv2.async_elastic_sections`
- Added: `features.guardianv2.async_elastic_sections.*`
- Added: `features.guardianv2.async_elastic_sections.*.max_section_entry_tokens`
- Added: `features.guardianv2.async_elastic_sections.*.max_total_section_tokens`
- Added: `features.guardianv2.async_elastic_sections.*.min_total_section_tokens`
- Added: `features.guardianv2.async_elastic_sections.*.nested_tool_names`
- Added: `features.guardianv2.async_elastic_sections.*.nested_tool_names[]`
- Added: `features.mcp_shared_repl_cwd`
- Added: `features.multi_agent_v2.interrupt_at_item_boundary`
- Changed: `features.multi_agent_v2.message_board_remote`
- Added: `features.network_proxy.transparent_tcp`
- Added: `features.per_environment_context`
- Added: `features.restored_history_prewarm`
- Added: `features.rollout_budget.limit_budget`
- Changed: `features.rollout_budget.limit_tokens`
- Added: `features.rollout_budget.reminder_at_context_start`
- Added: `features.safe_image_decoder`
- Added: `features.token_budget.context_window_as_tool_output`
- Added: `features.utc_environment_date`
- Added: `marketplaces.*.auto_update`
- Changed: `mcp_servers.*.auth`
- Added: `profiles.*.features.catalog_apps_instructions`
- Added: `profiles.*.features.file_backed_tool_audio`
- Added: `profiles.*.features.guardian_nested_approval_context`
- Added: `profiles.*.features.guardianv2.async_elastic_budgeting`
- Added: `profiles.*.features.guardianv2.async_elastic_sections`
- Added: `profiles.*.features.guardianv2.async_elastic_sections.*`
- Added: `profiles.*.features.guardianv2.async_elastic_sections.*.max_section_entry_tokens`
- Added: `profiles.*.features.guardianv2.async_elastic_sections.*.max_total_section_tokens`
- Added: `profiles.*.features.guardianv2.async_elastic_sections.*.min_total_section_tokens`
- Added: `profiles.*.features.guardianv2.async_elastic_sections.*.nested_tool_names`
- Added: `profiles.*.features.guardianv2.async_elastic_sections.*.nested_tool_names[]`
- Added: `profiles.*.features.mcp_shared_repl_cwd`
- Added: `profiles.*.features.multi_agent_v2.interrupt_at_item_boundary`
- Changed: `profiles.*.features.multi_agent_v2.message_board_remote`
- Added: `profiles.*.features.network_proxy.transparent_tcp`
- Added: `profiles.*.features.per_environment_context`
- Added: `profiles.*.features.restored_history_prewarm`
- Added: `profiles.*.features.rollout_budget.limit_budget`
- Changed: `profiles.*.features.rollout_budget.limit_tokens`
- Added: `profiles.*.features.rollout_budget.reminder_at_context_start`
- Added: `profiles.*.features.safe_image_decoder`
- Added: `profiles.*.features.token_budget.context_window_as_tool_output`
- Added: `profiles.*.features.utc_environment_date`
- Added: `responses`
- Added: `responses.process_mode`
- Added: `rollout_trace`
- Added: `rollout_trace.max_bytes`
- Added: `rollout_trace.max_payload_bytes`
- Changed: `tui.keymap`
- Changed: `tui.keymap.composer`
- Added: `tui.keymap.composer.redo`
- Added: `tui.keymap.composer.redo[]`
- Added: `tui.keymap.composer.undo`
- Added: `tui.keymap.composer.undo[]`
- Changed: `tui.keymap.global`
- Added: `tui.keymap.global.choose_cloud_environment`
- Added: `tui.keymap.global.choose_cloud_environment[]`
- Changed: `tui.keymap.pager`
- Added: `tui.keymap.pager.mark_markdown`
- Added: `tui.keymap.pager.mark_markdown[]`
- Added: `tui.status_line_provider`
- Added: `tui.status_line_provider.server`
- Added: `tui.status_line_provider.tool`

## rust-v0.171.0 → rust-v0.172.0

Commit: `3d86e43b075adeba2193ec5c22ac92f55afd82e6`

### codex-rs/config/src/types.rs — apps

```diff
--- rust-v0.171.0/codex-rs/config/src/types.rs
+++ rust-v0.172.0/codex-rs/config/src/types.rs
@@ -499,6 +499,10 @@
     /// Approval mode for this tool.
     #[serde(default, skip_serializing_if = "Option::is_none")]
     pub approval_mode: Option<AppToolApproval>,
+
+    /// Reviewer for this tool's approval prompts, overriding link-level and app-level settings.
+    #[serde(default, skip_serializing_if = "Option::is_none")]
+    pub approvals_reviewer: Option<ApprovalsReviewer>,
 }
 
 /// Tool settings for a single app.
@@ -508,6 +512,15 @@
     /// Per-tool overrides keyed by tool name (for example `repos/list`).
     #[serde(default, flatten)]
     pub tools: HashMap<String, AppToolConfig>,
+}
+
+impl AppToolsConfig {
+    /// Match a tool by its raw name first and use its title as a fallback.
+    pub fn for_tool(&self, name: &str, title: Option<&str>) -> Option<&AppToolConfig> {
+        self.tools
+            .get(name)
+            .or_else(|| title.and_then(|title| self.tools.get(title)))
+    }
 }
 
 /// Approval settings for a connected account within an app.
```

### codex-rs/connectors/src/app_tool_policy_tests.rs — app-tool-policy-tests

```diff
--- rust-v0.171.0/codex-rs/connectors/src/app_tool_policy_tests.rs
+++ rust-v0.172.0/codex-rs/connectors/src/app_tool_policy_tests.rs
@@ -698,6 +700,7 @@
                         AppToolConfig {
                             enabled: Some(true),
                             approval_mode: None,
+                            approvals_reviewer: None,
                         },
                     )]),
                 }),
```

### codex-rs/core/config.schema.json — schema

```diff
--- rust-v0.171.0/codex-rs/core/config.schema.json
+++ rust-v0.172.0/codex-rs/core/config.schema.json
@@ -236,6 +236,14 @@
             }
           ],
           "description": "Approval mode for this tool."
+        },
+        "approvals_reviewer": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/ApprovalsReviewer"
+            }
+          ],
+          "description": "Reviewer for this tool's approval prompts, overriding link-level and app-level settings."
         },
         "enabled": {
           "description": "Whether this tool is enabled. `Some(true)` explicitly allows this tool.",
@@ -968,6 +976,9 @@
             "concurrent_reasoning_summaries": {
               "type": "boolean"
             },
+            "connector_tool_result_passthrough": {
+              "type": "boolean"
+            },
             "connectors": {
               "type": "boolean"
             },
@@ -1284,6 +1295,9 @@
               "type": "boolean"
             },
             "realtime_conversation": {
+              "type": "boolean"
+            },
+            "realtime_frames_local": {
               "type": "boolean"
             },
             "reasoning_effort_override": {
@@ -1702,6 +1716,11 @@
       "required": [
         "command"
       ],
+      "type": "object"
+    },
+    "CredentialPermissionsToml": {
+      "additionalProperties": false,
+      "description": "In `requirements.toml`, `[permissions.credentials]` sets shared credential policy and `[permissions.<profile>.credentials]` sets policy for a named profile. Omit the shared table until it contains a supported policy setting. In `config.toml`, credentials use the named-profile form alongside filesystem and network.",
       "type": "object"
     },
     "CredentialProviderConfig": {
@@ -2492,6 +2511,48 @@
       "properties": {
         "enabled": {
           "type": "boolean"
+        },
+        "housekeeper": {
+          "$ref": "#/definitions/GuardianV3HousekeeperConfigToml"
+        },
+        "max_instruction_tokens": {
+          "description": "Maximum estimated tokens per custom routing or retrieval prompt. Unset means uncapped. Ignored in project config.",
+          "format": "uint",
+          "minimum": 0.0,
+          "type": "integer"
+        },
+        "message_board_in_memory": {
+          "description": "Keep each fresh root's Guardian board in memory until the runtime closes. Defaults to false.",
+          "type": "boolean"
+        },
+        "reviewer": {
+          "$ref": "#/definitions/GuardianV3ReviewerConfigToml"
+        }
+      },
+      "type": "object"
+    },
+    "GuardianV3HousekeeperConfigToml": {
+      "additionalProperties": false,
+      "properties": {
+        "batch_timeout_ms": {
+          "description": "Time budget for routing one batch, in milliseconds. Defaults to 90,000.",
+          "format": "uint32",
+          "minimum": 1.0,
+          "type": "integer"
+        },
+        "routing_instructions": {
+          "description": "Guidance for grouping originals into channels and describing their topics. Ignored in project config.",
+          "type": "string"
+        }
+      },
+      "type": "object"
+    },
+    "GuardianV3ReviewerConfigToml": {
+      "additionalProperties": false,
+      "properties": {
+        "retrieval_instructions": {
+          "description": "Guidance for searching the Guardian board and managing channel subscriptions. Ignored in project config.",
+          "type": "string"
         }
       },
       "type": "object"
@@ -4200,6 +4261,9 @@
     "PermissionProfileToml": {
       "additionalProperties": false,
       "properties": {
+        "credentials": {
+          "$ref": "#/definitions/CredentialPermissionsToml"
+        },
         "description": {
           "type": "string"
         },
@@ -5496,6 +5560,8 @@
               "hide": null,
               "new_task": null,
               "new_worktree": null,
+              "next_group": null,
+              "previous_group": null,
               "rename": null,
               "resume": null,
               "search": null,
@@ -5934,6 +6000,22 @@
             }
           ],
           "description": "Open a new session in a worktree from the project default branch."
+        },
+        "next_group": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Select the first task in the next group."
+        },
+        "previous_group": {
+          "allOf": [
+            {
+              "$ref": "#/definitions/KeybindingsSpec"
+            }
+          ],
+          "description": "Select the first task in the previous group."
         },
         "rename": {
           "allOf": [
@@ -6691,6 +6773,8 @@
             "hide": null,
             "new_task": null,
             "new_worktree": null,
+            "next_group": null,
+            "previous_group": null,
             "rename": null,
             "resume": null,
             "search": null,
@@ -8260,6 +8344,9 @@
         "concurrent_reasoning_summaries": {
           "type": "boolean"
         },
+        "connector_tool_result_passthrough": {
+          "type": "boolean"
+        },
         "connectors": {
           "type": "boolean"
         },
@@ -8576,6 +8663,9 @@
           "type": "boolean"
         },
         "realtime_conversation": {
+          "type": "boolean"
+        },
+        "realtime_frames_local": {
           "type": "boolean"
         },
         "reasoning_effort_override": {
```

### codex-rs/core/src/connectors.rs — app-reviewer

```diff
--- rust-v0.171.0/codex-rs/core/src/connectors.rs
+++ rust-v0.172.0/codex-rs/core/src/connectors.rs
@@ -523,9 +526,13 @@
     let app_reviewer = if server_name == CODEX_APPS_MCP_SERVER_NAME {
         apps_config_from_layer_stack(config_layer_stack).and_then(|apps_config| {
             let app = connector_id.and_then(|connector_id| apps_config.apps.get(connector_id));
-            link_id
-                .and_then(|link_id| app?.links.as_ref()?.links.get(link_id))
-                .and_then(|link| link.approvals_reviewer)
+            tool.and_then(|(name, title)| app?.tools.as_ref()?.for_tool(name, title))
+                .and_then(|tool| tool.approvals_reviewer)
+                .or_else(|| {
+                    link_id
+                        .and_then(|link_id| app?.links.as_ref()?.links.get(link_id))
+                        .and_then(|link| link.approvals_reviewer)
+                })
                 .or_else(|| app.and_then(|app| app.approvals_reviewer))
                 .or_else(|| {
                     apps_config
```

### codex-rs/features/src/lib.rs — apps-feature-order

```diff
--- rust-v0.171.0/codex-rs/features/src/lib.rs
+++ rust-v0.172.0/codex-rs/features/src/lib.rs
@@ -769,6 +774,13 @@
                     );
                     continue;
                 }
+                "code_mode_host_grpc" => {
+                    self.record_legacy_usage_force(
+                        "features.code_mode_host_grpc",
+                        Feature::CodeModeHostGrpc,
+                    );
+                    continue;
+                }
                 "transcript_v2" => {
                     self.record_legacy_usage_force("features.transcript_v2", Feature::TranscriptV2);
                     continue;
```

### codex-rs/protocol/src/protocol.rs — approval, sandbox

```diff
--- rust-v0.171.0/codex-rs/protocol/src/protocol.rs
+++ rust-v0.172.0/codex-rs/protocol/src/protocol.rs
@@ -789,7 +789,13 @@
     /// Close the running realtime conversation stream.
     RealtimeConversationClose,
 
-    /// Close only the matching session after earlier start operations finish.
+    /// End the identified logical call, including after its transport owner is lost.
+    RealtimeConversationEnd {
+        realtime_session_id: String,
+        reply: oneshot::Sender<CodexResult<()>>,
+    },
+
+    /// Disconnect only the matching transport after earlier start operations finish.
     RealtimeConversationDetach {
         realtime_session_id: String,
         reply: oneshot::Sender<CodexResult<()>>,
@@ -1151,6 +1157,7 @@
             Self::RealtimeConversationText(_) => "realtime_conversation_text",
             Self::RealtimeConversationSpeech(_) => "realtime_conversation_speech",
             Self::RealtimeConversationClose => "realtime_conversation_close",
+            Self::RealtimeConversationEnd { .. } => "realtime_conversation_end",
             Self::RealtimeConversationDetach { .. } => "realtime_conversation_detach",
             Self::RealtimeConversationListVoices => "realtime_conversation_list_voices",
             Self::RecoverTurn { .. } => "recover_turn",
@@ -2113,6 +2120,9 @@
     ContextWindowExceeded,
     SessionBudgetExceeded,
     UsageLimitExceeded,
+    ApiKeySpendLimitExceeded,
+    ProjectSpendLimitExceeded,
+    OrganizationSpendLimitExceeded,
     RateLimitExceeded,
     FlexUnavailable,
     ServerOverloaded,
@@ -2156,6 +2166,16 @@
 }
 
 impl CodexErrorInfo {
+    pub fn is_usage_limit(&self) -> bool {
+        matches!(
+            self,
+            Self::UsageLimitExceeded
+                | Self::ApiKeySpendLimitExceeded
+                | Self::ProjectSpendLimitExceeded
+                | Self::OrganizationSpendLimitExceeded
+        )
+    }
+
     /// Whether this error should mark the current turn as failed when replaying history.
     pub fn affects_turn_status(&self) -> bool {
         match self {
@@ -2163,6 +2183,9 @@
             Self::ContextWindowExceeded
             | Self::SessionBudgetExceeded
             | Self::UsageLimitExceeded
+            | Self::ApiKeySpendLimitExceeded
+            | Self::ProjectSpendLimitExceeded
+            | Self::OrganizationSpendLimitExceeded
             | Self::RateLimitExceeded
             | Self::FlexUnavailable
             | Self::ServerOverloaded
```

### Configuration fields

[Schema at this release](https://github.com/openai/codex/blob/3d86e43b075adeba2193ec5c22ac92f55afd82e6/codex-rs/core/config.schema.json)

- Added: `apps.*.tools.*.approvals_reviewer`
- Added: `features.connector_tool_result_passthrough`
- Added: `features.guardianv3.housekeeper`
- Added: `features.guardianv3.housekeeper.batch_timeout_ms`
- Added: `features.guardianv3.housekeeper.routing_instructions`
- Added: `features.guardianv3.max_instruction_tokens`
- Added: `features.guardianv3.message_board_in_memory`
- Added: `features.guardianv3.reviewer`
- Added: `features.guardianv3.reviewer.retrieval_instructions`
- Added: `features.realtime_frames_local`
- Added: `plugins.*.apps.*.tools.*.approvals_reviewer`
- Added: `profiles.*.features.connector_tool_result_passthrough`
- Added: `profiles.*.features.guardianv3.housekeeper`
- Added: `profiles.*.features.guardianv3.housekeeper.batch_timeout_ms`
- Added: `profiles.*.features.guardianv3.housekeeper.routing_instructions`
- Added: `profiles.*.features.guardianv3.max_instruction_tokens`
- Added: `profiles.*.features.guardianv3.message_board_in_memory`
- Added: `profiles.*.features.guardianv3.reviewer`
- Added: `profiles.*.features.guardianv3.reviewer.retrieval_instructions`
- Added: `profiles.*.features.realtime_frames_local`
- Changed: `tui.keymap`
- Changed: `tui.keymap.agents`
- Added: `tui.keymap.agents.next_group`
- Added: `tui.keymap.agents.next_group[]`
- Added: `tui.keymap.agents.previous_group`
- Added: `tui.keymap.agents.previous_group[]`
