# Hardware DB Migration Guide

## Goal

Migrate hardware knowledge from mixed human documents into `hardware-db` without breaking existing user experience.

All existing folders and files stay in place. New machine readable files are additive.

## Data flow

1. Keep original assets in board folders such as PDF, XLSX, DSN, PCB, and README
2. Add structured JSON under `hardware-db/boards/<id>`
3. Track evidence in `sources.yaml`
4. Generate board summary snippets with `tools/generate_readme_snippets.py`
5. Validate with `tools/validate_db.py`

## Pinout progressive plan

`pinout.json` is optional during early migration.

Use this staged approach:

1. Stage A
   - Do not create `pinout.json` when data quality is uncertain
   - Keep `sources.yaml` updated with current evidence
2. Stage B
   - Extract stable connector pin tables from PDF or XLSX
   - Normalize each pin with `number`, `name`, `functions`, `voltage`, `domain`
3. Stage C
   - Add `pinout.json`
   - Validate against `hardware-db/schemas/pinout.schema.json`
4. Stage D
   - Add constraints and cross references in `capabilities.json`
   - Keep source references and verification date current

## Extraction guidance from PDF and XLSX

1. Locate board evidence files from existing paths
2. Extract only verifiable facts with stable naming
3. Convert units and terms to normalized values
4. Preserve unknown values as `unknown` or `null` as allowed
5. Record every input source path or URL in `sources.yaml`

Recommended extraction targets:

- `board.json`: board identity and static product fields
- `interfaces.json`: interface list and optional version or lane width
- `power.json`: input power topology and optional power envelopes
- `capabilities.json`: agent retrieval tags, constraints, and use cases
- `pinout.json`: connector level pin map once verified

## Contributor checklist

- [ ] Keep existing folder structure and legacy docs untouched
- [ ] Update only the target board under `hardware-db/boards/<id>`
- [ ] Ensure required files exist: `board.json`, `interfaces.json`, `power.json`, `capabilities.json`, `sources.yaml`
- [ ] Ensure `sources.yaml` contains `data_origin`, `references`, `last_verified_date`
- [ ] Run `python tools/validate_db.py`
- [ ] Run `python tools/generate_readme_snippets.py`
- [ ] Confirm `tools/out/<id>.md` is updated
- [ ] Keep README marker blocks in board README files intact
- [ ] Run CI checks locally when possible before opening PR
