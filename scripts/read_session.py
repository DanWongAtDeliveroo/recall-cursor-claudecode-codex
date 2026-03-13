#!/usr/bin/env python3
"""Pretty-print a Claude Code, Codex, or Cursor session transcript."""

import json
import sys

TEXT_BLOCK_TYPES = {"text", "input_text", "output_text"}

SKIP_MARKERS = (
    "<user_instructions>", "<environment_context>",
    "<permissions instructions>", "# AGENTS.md instructions",
)

CURSOR_SKIP_MARKERS = (
    "<user_info>", "<system_reminder>", "<agent_transcripts>",
    "<rules>", "<agent_skills>",
)


def extract_text(content):
    """Extract plain text from message content (string or array format)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type", "") in TEXT_BLOCK_TYPES
        ]
        return "\n".join(filter(None, parts))
    return ""


def iter_messages(path):
    """Yield (role, text) pairs from a session file, auto-detecting format."""
    fmt = detect_format(path)

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Skip Codex state snapshots (legacy)
            if entry.get("record_type") == "state":
                continue

            if fmt == "cursor":
                role = entry.get("role", "")
                if role not in ("user", "assistant"):
                    continue
                content = entry.get("message", {})
                if isinstance(content, dict):
                    content = content.get("content", "")
                elif not isinstance(content, str):
                    continue
                text = extract_text(content)
                if not text or any(marker in text for marker in CURSOR_SKIP_MARKERS):
                    continue
                yield role, text

            elif fmt == "claude":
                # Resolve role from type or role fields
                role = entry.get("role", "")
                if role not in ("user", "assistant"):
                    etype = entry.get("type", "")
                    if etype in ("user", "human"):
                        role = "user"
                    elif etype == "assistant":
                        role = "assistant"
                    else:
                        continue

                # Claude wraps in entry.message.content
                content = entry.get("message", {})
                if isinstance(content, dict):
                    content = content.get("content", "")
                elif not isinstance(content, str):
                    content = entry.get("content", "")

                text = extract_text(content)
                if not text or any(marker in text for marker in SKIP_MARKERS):
                    continue
                yield role, text

            else:
                # Codex — handle both legacy and current (wrapped payload) formats
                etype = entry.get("type", "")

                if etype in ("session_meta", "event_msg", "turn_context"):
                    continue

                if etype == "response_item":
                    payload = entry.get("payload", {})
                    role = payload.get("role", "")
                    content = payload.get("content", "")
                else:
                    role = entry.get("role", "")
                    content = entry.get("content", "")

                if role not in ("user", "assistant"):
                    continue

                text = extract_text(content)
                if not text or any(marker in text for marker in SKIP_MARKERS):
                    continue
                yield role, text


def detect_format(path):
    """Detect whether a session file is Claude Code, Codex, or Cursor format."""
    # Cursor transcripts live under agent-transcripts/ directories
    if "agent-transcripts" in path:
        return "cursor"
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("record_type") == "state":
                return "codex"
            # Claude entries have metadata fields that Cursor entries lack
            if "parentUuid" in entry or "cwd" in entry or "timestamp" in entry:
                return "claude"
            if "message" in entry and set(entry.keys()) == {"role", "message"}:
                return "cursor"
            if "message" in entry:
                return "claude"
            if "id" in entry and "instructions" in entry:
                return "codex"
            if entry.get("type") == "session_meta":
                return "codex"
    return "claude"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Pretty-print a Claude Code, Codex, or Cursor session transcript")
    parser.add_argument("path", help="Path to a session .jsonl file")
    parser.add_argument("--pretty", action="store_true", help="Human-readable output instead of JSON")
    args = parser.parse_args()

    if args.pretty:
        for role, text in iter_messages(args.path):
            print(f"--- {role} ---")
            print(text[:500])
            print()
    else:
        msgs = [{"role": role, "text": text} for role, text in iter_messages(args.path)]
        print(json.dumps(msgs, indent=2))


if __name__ == "__main__":
    main()
