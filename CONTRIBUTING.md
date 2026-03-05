# Contributing to Radxa SOM Projects

Thank you for your interest in contributing to the Radxa Computer on Module projects database!
This repository relies heavily on structural accuracy and JSON schemas, ensuring that both human engineers and AI platforms (like LLMs, AI coding assistants) can parse the hardware data precisely.

## Adding a New SOM Board

To add a new SOM module to the database, please follow these structured steps:

1. **Create the Board Directory:** 
   Add a new folder under `hardware-db/boards/<your_board_id>` using a lowercase short ID. 
   *(Example: `hardware-db/boards/cm6`)*
   
2. **Setup the JSON Metadata Skeleton:**
   Populate the new directory with the following base metadata files:
   - `board.json`: Basic identifiers, SoC, framework dimensions, links.
   - `capabilities.json`: Tag lists, usage contexts, hardware constraints.
   - `interfaces.json`: Structural IO connectivity specs.
   - `power.json`: Minimum/maximum electrical power inputs.
   - `sources.yaml`: Origin of data (`extracted` or `human_entered`), tracking references (e.g. schematic PDF or internal XLSX paths).
   
   *(Optional)* `pinout.json`: A complete matrix of pins, voltages, and functions. This should be added if verification against full schematics is possible.
   
3. **Write the Board's Human README:**
   Ensure your physical documentation folder (e.g., `cm6/`) has a `README.md`. 
   Insert the snippet placeholder tags somewhere at the top where the specifications array should appear:
   ```markdown
   <!-- AGENT_SPEC_START -->
   <!-- AGENT_SPEC_END -->
   ```

## Pre-Commit Verification (Required)

To ensure the repository remains Agent-Friendly and Schema compliant, all contributions run a local `pre-commit` pipeline verification hook.

**1. Install `pre-commit` Local Hooks:**
Ensure you have `pre-commit` and `jsonschema` installed:
```bash
python3 -m pip install pre-commit jsonschema
pre-commit install
```

**2. What `pre-commit` Does:**
Before any git commit is accepted, the system automation will run:
- `python tools/validate_db.py`: Checking all `hardware-db/` dictionaries against JSON schema constraints.
- `python tools/generate_readme_snippets.py --check`: Ensuring that any JSON values modified have been properly regenerated into the markdown summaries. 

**Auto-Fixes:**
If your commit is rejected by `check-readme-snippets`, it means the README specs are out-of-sync. 
Fix it by running:
```bash
python tools/generate_readme_snippets.py
git add .
git commit 
```

*Note:* Never manually edit the spec tables sandwiched between `<!-- AGENT_SPEC_START -->` blocks. Let the generator script project the JSON content appropriately!
