#!/usr/bin/env python3

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def list_board_ids(boards_root: Path, selected: Optional[List[str]]) -> List[str]:
    existing = sorted(entry.name for entry in boards_root.iterdir() if entry.is_dir())
    if selected is None:
        return existing
    unknown = sorted(set(selected) - set(existing))
    if unknown:
        raise ValueError(f"unknown board ids: {', '.join(unknown)}")
    return sorted(set(selected))


def interface_summary(interfaces: List[Dict]) -> Tuple[int, str]:
    counts = Counter(interface["type"] for interface in interfaces)
    if not counts:
        return 0, "none"
    parts = [f"{interface_type}:{counts[interface_type]}" for interface_type in sorted(counts)]
    return sum(counts.values()), ", ".join(parts)


def power_summary(power_inputs: List[Dict]) -> str:
    if not power_inputs:
        return "none"
    parts = []
    for item in power_inputs:
        parts.append(
            f"{item.get('type', 'unknown')} {item.get('voltage_range', 'unknown')} via {item.get('connector', 'unknown')}"
        )
    return "; ".join(parts)


def build_snippet(board_id: str, board: dict, interfaces: dict, power: dict, caps: dict) -> str:
    iface_total, iface_breakdown = interface_summary(interfaces.get("interfaces", []))
    tags = caps.get("tags") or []
    tag_text = ", ".join(tags) if tags else "none"

    lines = [
        "### Agent Spec Summary",
        f"- Board: {board.get('name', 'unknown')} ({board_id})",
        f"- SoC: {board.get('soc', 'unknown')}",
        f"- Category: {board.get('category', 'unknown')}",
        f"- Form factor: {board.get('form_factor', 'unknown')}",
        f"- Interfaces total: {iface_total}",
        f"- Interface breakdown: {iface_breakdown}",
        f"- Capability tags: {tag_text}",
        f"- Power inputs: {power_summary(power.get('inputs', []))}",
        f"- Price tier: {caps.get('price_tier', 'unknown')}",
        f"- Compatible alternatives: {', '.join(caps.get('compatible_alternatives', [])) or 'none'}",
        f"- Open source level: {caps.get('open_source_level', 'unknown')}",
        f"- Data path: hardware-db/boards/{board_id}",
    ]

    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate agent spec snippets from hardware-db into tools/out"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root path",
    )
    parser.add_argument(
        "--board",
        action="append",
        dest="boards",
        help="Board id to generate, can be used multiple times",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if generated files are up-to-date without writing",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    boards_root = repo_root / "hardware-db" / "boards"
    out_root = repo_root / "tools" / "out"
    out_root.mkdir(parents=True, exist_ok=True)

    board_ids = list_board_ids(boards_root, args.boards)
    mismatched = []

    for board_id in board_ids:
        board_dir = boards_root / board_id
        board = load_json(board_dir / "board.json")
        interfaces = load_json(board_dir / "interfaces.json")
        power = load_json(board_dir / "power.json")
        capabilities = load_json(board_dir / "capabilities.json")

        expected = build_snippet(board_id, board, interfaces, power, capabilities)
        out_path = out_root / f"{board_id}.md"

        if args.check:
            current = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
            if current != expected:
                mismatched.append(str(out_path.relative_to(repo_root)))
            continue

        out_path.write_text(expected, encoding="utf-8")
        print(f"Generated {out_path.relative_to(repo_root)}")

    if args.check and mismatched:
        for path in mismatched:
            print(f"OUTDATED: {path}")
        return 1

    if args.check:
        print(f"Snippet files are up-to-date for {len(board_ids)} board(s)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
