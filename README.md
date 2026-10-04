<img src="pouch.svg" alt="A purple pouch" width="120">

# Pouch

One little place for all my AI bits.

Edit `instructions/AGENTS.md` and `skills/` here. The symlinks use each change directly, including new skills.

```sh
uv run pouch.py install
uv run pouch.py status
uv run pouch.py uninstall
```

Install backs up existing paths under `~/.pouch/backups/`, then creates these links:

| Link | Source |
| --- | --- |
| `~/.agents/skills` | `skills/` |
| `~/.codex/AGENTS.md` | `instructions/AGENTS.md` |
| `~/.config/opencode/AGENTS.md` | `instructions/AGENTS.md` |

Uninstall removes only these links. It keeps the source files and backups.
Restore a backup manually if you need the previous files.

On Windows, enable Developer Mode if Windows denies the symlinks.
