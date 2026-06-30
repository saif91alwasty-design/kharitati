# Kerykeion skill

A cross-platform [Agent Skill](https://agentskills.io/specification) that teaches AI agents to use
**[Kerykeion](https://github.com/g-battaglia/kerykeion)** — the Python astrology library — correctly:
building charts from birth data, computing aspects/synastry/returns/transits, rendering SVG charts,
and producing text reports or LLM-ready context. It documents the real, current API (verified against
the shipped package) so agents stop guessing method names.

Works with any skills-aware agent (Claude Code, Cursor, Codex, Copilot, Gemini, Windsurf, Cline, …).

## Install

```bash
npx skills add g-battaglia/kerykeion
```

Or copy the `kerykeion/` folder into your agent's skills directory (e.g. `skills/`,
`.agents/skills/`, or `.claude/skills/`).

## What's inside

```
kerykeion/
├── SKILL.md                      # entry point: mental model, setup, routing, pitfalls, licensing
├── references/
│   ├── subjects.md               # AstrologicalSubjectFactory, composite subjects, config, points
│   ├── charts.md                 # ChartDataFactory + ChartDrawer (all chart types & options)
│   ├── analysis.md               # aspects, compatibility, house comparison, distributions
│   ├── time-techniques.md        # returns, ephemeris, transits, moon phase
│   ├── reports-and-ai.md         # ReportGenerator + to_context (LLM XML)
│   └── reference-data.md         # every enum value, defaults, model fields
└── scripts/
    └── quickstart.py             # runnable offline example (subject → SVG + report + context)
```

The agent reads `SKILL.md` on activation and opens the `references/` files on demand.

## Requirements

`pip install kerykeion` (Python ≥ 3.10). The skill's examples run offline (no network) using explicit
coordinates.

## Licensing of Kerykeion

Kerykeion itself is **AGPL-3.0**. Importing it into your project triggers AGPL's copyleft (including
for SaaS/network use). For commercial or closed-source use, either buy a commercial license
(`kerykeion.astrology@gmail.com`) or consume the hosted
[Astrologer API](https://rapidapi.com/gbattaglia/api/astrologer) instead of importing the library —
`SKILL.md` explains this so agents surface it when the context is commercial.
