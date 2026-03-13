---
name: recall-cursor-claudecode-codex
description: >
  Search past Cursor, Claude Code, and Codex sessions. Triggers: /recall, "search old conversations",
  "find a past session", "recall a previous conversation", "search session history",
  "what did we discuss", "remember when we", "search Cursor sessions"
metadata:
  author: DanWongAtDeliveroo
  version: "0.3.0"
  license: MIT
---

# /recall — Search Past Cursor, Claude Code & Codex Sessions

Search all past Cursor, Claude Code, and Codex sessions using full-text search with BM25 ranking.

## Usage

```bash
python3 ~/.claude/skills/recall/scripts/recall.py QUERY [--project PATH] [--days N] [--source claude|codex|cursor] [--limit N] [--reindex]
```

## Examples

```bash
# Simple keyword search
python3 ~/.claude/skills/recall/scripts/recall.py "bufferStore"

# Phrase search (exact match)
python3 ~/.claude/skills/recall/scripts/recall.py '"ACP protocol"'

# Boolean query
python3 ~/.claude/skills/recall/scripts/recall.py "rust AND async"

# Prefix search
python3 ~/.claude/skills/recall/scripts/recall.py "buffer*"

# Filter by project and recency
python3 ~/.claude/skills/recall/scripts/recall.py "state machine" --project ~/my-project --days 7

# Search only Claude Code sessions
python3 ~/.claude/skills/recall/scripts/recall.py "buffer" --source claude

# Search only Codex sessions
python3 ~/.claude/skills/recall/scripts/recall.py "buffer" --source codex

# Search only Cursor sessions
python3 ~/.claude/skills/recall/scripts/recall.py "sandbox" --source cursor

# Force reindex
python3 ~/.claude/skills/recall/scripts/recall.py --reindex "test"
```

## Query Syntax (FTS5)

- **Words**: `bufferStore` — matches stemmed variants (e.g., "discussing" matches "discuss")
- **Phrases**: `"ACP protocol"` — exact phrase match
- **Boolean**: `rust AND async`, `tauri OR electron`, `NOT deprecated`
- **Prefix**: `buffer*` — matches bufferStore, bufferMap, etc.
- **Combined**: `"state machine" AND test`

## After Finding a Match

To resume a session, `cd` into the project directory and use the appropriate command:

```bash
# Claude Code sessions [claude]
cd /path/to/project
claude --resume SESSION_ID

# Codex sessions [codex]
cd /path/to/project
codex resume SESSION_ID

# Cursor sessions [cursor]
# Cursor doesn't support CLI resume — open the project in Cursor
# and use the transcript file path to review the conversation.
```

Each result includes a `File:` path. Use it to read the raw transcript (auto-detects format):

```bash
python3 ~/.claude/skills/recall/scripts/read_session.py <File-path-from-result>
```

If results are missing `File:` paths, run `--reindex` to backfill.

## Notes

- Index is stored at `~/.recall.db` (SQLite FTS5, auto-migrated from `~/.claude/recall.db`)
- Indexes `~/.claude/projects/` (Claude Code), `~/.codex/sessions/` (Codex), and `~/.cursor/projects/` (Cursor)
- First run indexes all sessions (a few seconds); subsequent runs are incremental
- Only user and assistant messages are indexed (tool calls, thinking blocks, state snapshots skipped)
- Results show `[claude]`, `[codex]`, or `[cursor]` tags to indicate the source
- Cursor sessions derive timestamps from file modification time (no per-entry timestamps)
