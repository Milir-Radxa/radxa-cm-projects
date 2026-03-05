#!/usr/bin/env python3

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

try:
    import jsonschema
except ImportError as exc:
    raise SystemExit(
        "jsonschema is required. Install with: pip install jsonschema"
    ) from exc


SCHEMA_FILES = {
    "board.json": "board.schema.json",
    "interfaces.json": "interfaces.schema.json",
    "power.json": "power.schema.json",
    "capabilities.json": "capabilities.schema.json",
    "pinout.json": "pinout.schema.json",
}

REQUIRED_BOARD_FILES = [
    "board.json",
    "interfaces.json",
    "power.json",
    "capabilities.json",
    "sources.yaml",
]

ALLOWED_ORIGINS = {"human_entered", "extracted"}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_validators(schema_dir: Path) -> Dict[str, jsonschema.Draft202012Validator]:
    validators: Dict[str, jsonschema.Draft202012Validator] = {}
    for data_file, schema_file in SCHEMA_FILES.items():
        schema_path = schema_dir / schema_file
        if not schema_path.exists():
            raise FileNotFoundError(f"missing schema: {schema_path}")
        schema = load_json(schema_path)
        validators[data_file] = jsonschema.Draft202012Validator(schema)
    return validators


def parse_sources_yaml(path: Path) -> dict:
    data = {}
    current_list_key = None

    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            line = raw.rstrip("\n")
            stripped = line.strip()

            if not stripped or stripped.startswith("#"):
                continue

            if line.startswith("  - "):
                if current_list_key is None:
                    raise ValueError(f"{path}:{line_no}: list item without list key")
                value = line[4:].strip()
                if not value:
                    raise ValueError(f"{path}:{line_no}: empty list item")
                data.setdefault(current_list_key, []).append(value)
                continue

            if line.startswith(" "):
                raise ValueError(f"{path}:{line_no}: unsupported indentation")

            if ":" not in line:
                raise ValueError(f"{path}:{line_no}: missing key separator")

            key, raw_value = line.split(":", 1)
            key = key.strip()
            value = raw_value.strip()

            if not key:
                raise ValueError(f"{path}:{line_no}: empty key")

            if value == "":
                data[key] = []
                current_list_key = key
            else:
                data[key] = value
                current_list_key = None

    return data


def validate_sources_yaml(path: Path, repo_root: Path) -> List[str]:
    errors: List[str] = []

    try:
        parsed = parse_sources_yaml(path)
    except ValueError as exc:
        return [str(exc)]

    data_origin = parsed.get("data_origin")
    if data_origin not in ALLOWED_ORIGINS:
        errors.append(
            f"{path}: data_origin must be one of {sorted(ALLOWED_ORIGINS)}, got {data_origin}"
        )

    references = parsed.get("references")
    if not isinstance(references, list) or not references:
        errors.append(f"{path}: references must be a non-empty list")
    else:
        for ref in references:
            if not isinstance(ref, str) or not ref:
                errors.append(f"{path}: invalid reference value {ref!r}")
                continue
            if ref.startswith("http://") or ref.startswith("https://"):
                continue
            ref_path = repo_root / ref
            if not ref_path.exists():
                errors.append(f"{path}: reference path does not exist: {ref}")

    verified = parsed.get("last_verified_date")
    if not isinstance(verified, str):
        errors.append(f"{path}: last_verified_date must be YYYY-MM-DD")
    else:
        try:
            date.fromisoformat(verified)
        except ValueError:
            errors.append(f"{path}: invalid last_verified_date: {verified}")

    return errors


def board_ids(boards_root: Path, selected: Optional[List[str]]) -> List[str]:
    existing = sorted(entry.name for entry in boards_root.iterdir() if entry.is_dir())
    if selected is None:
        return existing
    selected_set = set(selected)
    missing = sorted(selected_set - set(existing))
    if missing:
        raise ValueError(f"unknown board ids: {', '.join(missing)}")
    return sorted(selected_set)


def validate_board(
    repo_root: Path,
    board_root: Path,
    validators: Dict[str, jsonschema.Draft202012Validator],
) -> List[str]:
    errors: List[str] = []
    board_id = board_root.name

    for required in REQUIRED_BOARD_FILES:
        if not (board_root / required).exists():
            errors.append(f"{board_root / required}: missing required file")

    for data_file, validator in validators.items():
        file_path = board_root / data_file
        if not file_path.exists():
            if data_file == "pinout.json":
                continue
            errors.append(f"{file_path}: missing")
            continue

        try:
            document = load_json(file_path)
        except json.JSONDecodeError as exc:
            errors.append(f"{file_path}: invalid JSON: {exc}")
            continue

        for issue in validator.iter_errors(document):
            field_path = "/".join(str(piece) for piece in issue.path)
            if field_path:
                errors.append(f"{file_path}: {field_path}: {issue.message}")
            else:
                errors.append(f"{file_path}: {issue.message}")

        if data_file == "board.json" and document.get("id") != board_id:
            errors.append(
                f"{file_path}: id field must match directory name {board_id}"
            )

    sources_path = board_root / "sources.yaml"
    if sources_path.exists():
        errors.extend(validate_sources_yaml(sources_path, repo_root))

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate hardware-db schemas and board data"
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
        help="Board id to validate, can be used multiple times",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    boards_root = repo_root / "hardware-db" / "boards"
    schema_root = repo_root / "hardware-db" / "schemas"

    if not boards_root.exists() or not schema_root.exists():
        print("hardware-db layout is incomplete", file=sys.stderr)
        return 2

    try:
        validators = load_validators(schema_root)
        ids = board_ids(boards_root, args.boards)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    all_errors = []
    for board_id in ids:
        all_errors.extend(validate_board(repo_root, boards_root / board_id, validators))

    if all_errors:
        for error in all_errors:
            print(f"ERROR: {error}")
        print(f"Validation failed with {len(all_errors)} error(s)")
        return 1

    print(f"Validated {len(ids)} board(s) successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
