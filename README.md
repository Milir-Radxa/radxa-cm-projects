## About

[![Agentic Hardware Database](https://img.shields.io/badge/knowledge_graph-Agent_Friendly-blue.svg)](./hardware-db/)
[![LLMs.txt Ready](https://img.shields.io/badge/llms.txt-compliant-green.svg)](./llms.txt)

Welcome to the **Radxa Computer on Module (SoM)** projects. This repository contains the carrier board design files (PDF, DSN, PCB, DXF, XLSX) released by Radxa as well as community projects. 
For Large Language Models (LLMs) and autonomous engineering agents (like Cursor, GitHub Copilot), this repository acts as an **Agentic Hardware Knowledge Database**. By navigating to the `hardware-db` directory, agents can programmatically query JSON representations of board pinouts, interfaces, electrical domains, and hardware constraints without needing to parse complex schematic PDFs or unstructured markdown tables.

## CM Series

| CM Series                          | Description                                                                                     | Projects                          |
| ---------------------------------- | ----------------------------------------------------------------------------------------------- | --------------------------------- |
| [Radxa CM3](https://rock.sh/cm3)   | Computer on Module based on RK3566, compatible with Raspberry Pi CM4                            | [CM3 Projects](./cm3/README.md)   |
| [Radxa CM3I](https://rock.sh/cm3i) | Computer on Module based on RK3568(J) with industrial grade options                             | [CM3I Projects](./cm3i/README.md) |
| [Radxa CM4](https://rock.sh/cm4)   | Computer on Module based on RK3676(J), compatible with Raspberry Pi CM4                           | [CM4 Projects](./cm4/README.md)   |
| [Radxa CM5](https://rock.sh/cm5)   | Computer on Module based on RK3588S, compatible with Raspberry Pi CM4                           | [CM5 Projects](./cm5/README.md)   |

## NX Series

| NX Series                       | Description                                                                                     | Projects                          |
| ---------------------------------- | ----------------------------------------------------------------------------------------------- | --------------------------------- |
| [Radxa CM3S](https://rock.sh/cm3s) | Computer on Module based on RK3566 in SODIMM form factor, compatible with Raspberry Pi CM3/CM3+ | [CM3S Projects](./cm3s/README.md) |
| [Radxa NX5](https://rock.sh/nx5)   | Computer on Module based on RK3588S in SODIMM form factor                                       | [NX5 Projects](./nx5/README.md)   |
| [Radxa NX4](https://rock.sh/nx4)   | Computer on Module based on RK3557(J) in SODIMM form factor                                     | [NX4 Projects](./nx4/README.md) |
| [Orin NX](https://rock.sh/c200-orin) | Computer on Module based on NVIDIA Jetson Orin NX in SODIMM form factor                       | [Orin NX Projects](./c200/README.md) |

## Agent Friendly Hardware DB

This repository keeps all current hardware files and folder layout for human readers.

Machine readable hardware knowledge is added under `hardware-db` for agents and automation.

### New layout

- `hardware-db/schemas`: JSON Schema for board metadata and capability files
- `hardware-db/boards/<id>`: per board structured data and source tracking
- `tools/generate_readme_snippets.py`: generates `tools/out/<id>.md` summaries
- `tools/validate_db.py`: validates all board data against schema

### Why this matters (How it works)

To ensure both human documentation and machine-readable data never go out of sync, this repository operates under a unified **Single Source of Truth** pipeline:

```mermaid
graph TD
    A[(Raw Schematics / PDFs)] -->|Extract / Verify| B[hardware-db JSON Files]
    B -->|Verified Against| C{JSON Schemas}
    C -->|If Valid| D[tools/generate_readme_snippets.py]
    D -->|Injects / Updates| E[Human README.md Files]
    
    style B fill:#3498db,stroke:#2980b9,color:#fff
    style C fill:#f39c12,stroke:#d35400,color:#fff
    style E fill:#2ecc71,stroke:#27ae60,color:#fff
```

1. **Hardware Engineers/Contributors** write structured core data into `/hardware-db/` `.json`.
2. **Pre-commit Hooks & CI** validate that structure against `/schemas/`.
3. **Python Scripts** dynamically query the DB to print human-readable summary specs directly into each target documentation folder via `AGENT_SPEC_START` markdown blocks!

### Quick start

1. Create a Python virtual environment
2. Install dependency `jsonschema`
3. Run `python tools/validate_db.py`
4. Run `python tools/generate_readme_snippets.py`
5. Run `python tools/generate_readme_snippets.py --check` in CI or pre-commit

### Single source of truth

Board README files now include an `AGENT_SPEC_START` and `AGENT_SPEC_END` block at the top.

The content in this block is generated from `hardware-db/boards/<id>/*.json` through `tools/generate_readme_snippets.py`, with an explicit source path at the top of each block.

### Progressive migration

- Start from minimal known metadata with clear `sources.yaml` references
- Fill `interfaces.json`, `power.json`, and `capabilities.json` incrementally
- Add optional `pinout.json` when verifiable pin data is available
- Keep old docs and binary assets untouched during migration

### Contributing

If you'd like to help us add more SOM modules to the database, please check out our [Contribution Checklist](./CONTRIBUTING.md) to understand how to comply with schemas and install the mandated local `pre-commit` git hooks!
