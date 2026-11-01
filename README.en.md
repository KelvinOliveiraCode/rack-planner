# rack-planner

**English** · [Português (Brasil)](README.md)

[![Python 3](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](#) [![PyYAML](https://img.shields.io/badge/PyYAML-only%20dep-3776AB?style=flat-square)](#) [![pytest](https://img.shields.io/badge/pytest-54%20tests-0A9EDC?style=flat-square&logo=pytest)](#) [![MIT License](https://img.shields.io/badge/License-MIT-f4c430?style=flat-square)](LICENSE)

## What it is

**A rack planner**: it sizes equipment placement (U slots, weight, power), checks electrical requirements (per-phase current, circuits), thermal (exhaust temperature, airflow), occupancy (best-fit allocation, overlap detection) and generates a visual rack report with violation warnings. It is an educational datacenter/infra lab.

## Status

An educational lab, working and tested (54 tests).

## Features

- **Model** (`modelo.py`): `Equipamento`, `Pdu`, `CapacidadeRack`, `carregar_equipamentos` and `carregar_capacidade` (YAML).
- **Sizing** (`dimensionamento.py`): `soma_u`, `soma_peso`, `soma_potencia`, `sobreposicoes`, `verifica_altura/peso`.
- **Electrical** (`eletrica.py`): `corrente_de_carga`, `corrente_por_fase`, `potencia_por_fase`, `circuitos_usados`, `verifica_corrente_por_fase/circuito/eletrica`.
- **Thermal** (`termica.py`): `temperatura_saida`, `temperatura_estimada`, `verifica_termica`, `alertas_de_fluxo`.
- **Occupancy** (`ocupacao.py`): `alocar` (best-fit), `verificar_folga_entre_fontes`, `resumo_de_ocupacao`.
- **Report** (`relatorio.py`): `_planta` (visual), `gerar_relatorio` with `Aviso` per violation, `tem_violacao`.
- **Warnings** (`aviso.py`): `Aviso` and `formatar`.
- **CLI** (`rackplan`).

## Architecture

A `rackplan` package with `modelo`, `dimensionamento`, `eletrica`, `termica`, `ocupacao`, `relatorio`, `aviso` and `cli`.

## Stack

- Python ≥ 3.10, PyYAML ≥ 6.0
- pytest (dev)

## Repository layout

```
rack-planner/
├── src/rackplan/    # modelo · dimensionamento · eletrica · termica · ocupacao · relatorio · aviso · cli
├── dados/
├── tests/           # 54 tests
└── LICENSE          # MIT
```

## Prerequisites and installation

```bash
pip install -e .
```

## How to run

```bash
rackplan <subcmd> dados/
```

## Tests and quality

```bash
PYTHONPATH=src python -m pytest tests/   # 54 passed
```

## Technical decisions

- Best-fit allocation: fits the largest-U equipment first.
- Per-phase electrical check (single/three-phase) + circuit count.

## Known limitations

- No liquid cooling (air only: exhaust temperature × airflow).
- Fixed voltage (127/220 V) — configurable in YAML.

## Development process

An individual project by Kelvin Oliveira, built with orchestrated AI agents and reviewed by the author.

## License and author

MIT — Copyright (c) 2026 Kelvin Rebelo de Oliveira. Author: [Kelvin Oliveira](https://github.com/KelvinOliveiraCode) · [Portfolio](https://kelvinoliveiracode.github.io/portfolio/)
