# Diagnostic Playbook

Use these commands selectively. Avoid broad log dumps because Codex logs can include full prompts and tool schemas.

## Recent Errors

```bash
sqlite3 ~/.codex/logs_2.sqlite \
  "select datetime(ts,'unixepoch','localtime'), level, target, substr(coalesce(feedback_log_body,''),1,500)
   from logs
   where level in ('ERROR','WARN','error','warn')
   order by ts desc, ts_nanos desc
   limit 80;"
```

For a specific startup failure:

```bash
sqlite3 ~/.codex/logs_2.sqlite \
  "select datetime(ts,'unixepoch','localtime'), level, target, feedback_log_body
   from logs
   where level='ERROR'
   order by ts desc, ts_nanos desc
   limit 20;"
```

## Skill Frontmatter Failure

Log pattern:

```text
session_init: failed to load skill .../SKILL.md: missing YAML frontmatter delimited by ---
```

Fix pattern:

```markdown
---
name: skill-name
description: Clear trigger description.
---

# Skill Body
```

Validate:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.codex/skills/<skill-name>
```

## Reconnecting 2/5 Or Request Timeout

Useful checks:

```bash
codex doctor
scutil --proxy
env | rg -i '^(http|https|all|no)_proxy=' || true
```

If macOS system proxy is enabled but `codex doctor` says no proxy env vars, verify with temporary env vars:

```bash
HTTPS_PROXY=http://127.0.0.1:7897 \
HTTP_PROXY=http://127.0.0.1:7897 \
ALL_PROXY=socks5h://127.0.0.1:7897 \
codex doctor
```

Successful WebSocket result:

```text
websocket connected (HTTP 101 Switching Protocols)
proxy env vars present HTTP_PROXY, HTTPS_PROXY, ALL_PROXY
```

User-scope macOS GUI inheritance fix:

```bash
launchctl setenv HTTP_PROXY http://127.0.0.1:7897
launchctl setenv HTTPS_PROXY http://127.0.0.1:7897
launchctl setenv ALL_PROXY socks5h://127.0.0.1:7897
launchctl setenv NO_PROXY '127.0.0.1,localhost,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12,*.local'
```

For persistence after login, create a user LaunchAgent that runs a small script under `~/.codex/`. After loading it, fully quit and reopen Codex App so it inherits the new launchd environment.

## Plugin Manifest Warning

Log pattern:

```text
ignoring interface.defaultPrompt[0]: prompt must be at most 128 characters
```

Fix the plugin manifest only if this warning appears repeatedly during startup or causes visible slowdown. Keep `defaultPrompt` under 128 characters and valid JSON.

## Config Safety

Before editing global config:

```bash
cp ~/.codex/config.toml ~/.codex/config.toml.bak-$(date +%Y%m%d-%H%M%S)
```

Check current config:

```bash
codex doctor
codex features list
```

Do not modify:

```text
~/.codex/auth.json
```

unless the user explicitly requests auth reset or relogin.
