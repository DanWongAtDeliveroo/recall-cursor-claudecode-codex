# recall-cursor-claudecode-codex

Search across all your past Cursor, Claude Code, and Codex conversations with full-text search. Builds a SQLite FTS5 index over `~/.cursor/projects/`, `~/.claude/projects/`, and `~/.codex/sessions/` with BM25 ranking, Porter stemming, and incremental updates.

## Install

### Claude Code

```bash
npx skills add DanWongAtDeliveroo/recall-cursor-claudecode-codex
```

Then use `/recall` or ask "find a past session where we talked about foo".

### Codex

```bash
npx skills add DanWongAtDeliveroo/recall-cursor-claudecode-codex
```

### Cursor

Clone the repo and run the scripts directly:

```bash
git clone https://github.com/DanWongAtDeliveroo/recall-cursor-claudecode-codex.git ~/recall
python3 ~/recall/scripts/recall.py "your search query"
```

Or invoke via Shell tool in an agent chat.

## How it works

```
  ~/.claude/projects/**/*.jsonl ─────────────────┐
                                                  │
  ~/.codex/sessions/**/*.jsonl ──────────────────-┤
                                                  ├─▶ Index ──▶ ~/.recall.db (SQLite FTS5)
  ~/.cursor/projects/*/agent-transcripts/**/*.jsonl┘      │
                                                         │  incremental (mtime-based)
                                                         │
  Query ──▶ FTS5 Match ──▶ BM25 rank ──▶ Recency boost ──▶ Results
                │                    [half-life: 30 days]
                │  [Porter stemming
                │   phrase/boolean/prefix]
                ▼
         snippet extraction
         highlighted excerpts
```

- Indexes user/assistant messages into a SQLite FTS5 database at `~/.recall.db`
- First run indexes all sessions (a few seconds); subsequent runs only process new/modified files
- Skips tool_use, tool_result, thinking, and image blocks
- Results ranked by BM25 with a slight recency bias (recent sessions get up to a 20% boost, decaying with a 30-day half-life)
- Results tagged `[claude]`, `[codex]`, or `[cursor]` with highlighted excerpts
- No dependencies — Python 3.9+ stdlib only (sqlite3, json, argparse)

## Contributing

Found a bug or have an idea? [Open an issue](https://github.com/DanWongAtDeliveroo/recall-cursor-claudecode-codex/issues) or submit a pull request — contributions are welcome!

Fork of [arjunkmrm/recall](https://github.com/arjunkmrm/recall) with added Cursor support.

