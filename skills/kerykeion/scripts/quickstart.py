#!/usr/bin/env python3
"""
Kerykeion quickstart — a known-good, offline, copy-pasteable starting point.

Run it to confirm the install works and to see the full subject → chart → report → context flow:

    python quickstart.py                # uses the built-in example
    python quickstart.py --svg out_dir  # also write an SVG to out_dir/

Everything here is offline (online=False with explicit coordinates), so it needs no network.
Swap the birth data for your own; keep online=False and provide lng/lat/tz_str.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from kerykeion import (
    AstrologicalSubjectFactory,
    ChartDataFactory,
    ReportGenerator,
    to_context,
)
from kerykeion.charts.chart_drawer import ChartDrawer


def build_subject():
    return AstrologicalSubjectFactory.from_birth_data(
        "Example Person",
        1990, 7, 15, 10, 30,            # year, month, day, hour, minute (local time)
        city="Rome", nation="IT",       # display labels in reports/to_context (default: Greenwich/GB)
        lng=12.4964, lat=41.9028,       # Rome
        tz_str="Europe/Rome",
        online=False,                   # offline: no GeoNames call
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Kerykeion quickstart")
    ap.add_argument("--svg", metavar="DIR", help="also render an SVG into DIR/")
    args = ap.parse_args()

    subject = build_subject()

    # 1) Read data straight off the subject
    print(f"Sun:  {subject.sun.sign} {subject.sun.position:.2f}°  (house {subject.sun.house})")
    print(f"Moon: {subject.moon.sign} {subject.moon.position:.2f}°  element {subject.moon.element}")
    print(f"Asc:  {subject.ascendant.sign} {subject.ascendant.position:.2f}°")
    print(f"Lunar phase: {subject.lunar_phase.moon_phase_name} {subject.lunar_phase.moon_emoji}")

    # 2) Precompute chart data (needed for charts, reports, distributions, aspects)
    chart_data = ChartDataFactory.create_natal_chart_data(subject)
    print(f"\nElement balance: fire={chart_data.element_distribution.fire:.1f} "
          f"earth={chart_data.element_distribution.earth:.1f} "
          f"air={chart_data.element_distribution.air:.1f} "
          f"water={chart_data.element_distribution.water:.1f}")
    print(f"Aspects found: {len(chart_data.aspects)}")

    # 3) Human-readable report
    print("\n--- REPORT ---")
    ReportGenerator(chart_data).print_report(max_aspects=8)

    # 4) LLM-ready context (inject into a prompt)
    print("\n--- LLM CONTEXT (truncated) ---")
    ctx = to_context(subject)
    print(ctx[:600] + ("…" if len(ctx) > 600 else ""))

    # 5) Optional SVG
    if args.svg:
        out = Path(args.svg)
        out.mkdir(parents=True, exist_ok=True)
        ChartDrawer(chart_data=chart_data).save_svg(output_path=out, filename="quickstart-natal")
        print(f"\nSVG written to {(out / 'quickstart-natal.svg').resolve()}")


if __name__ == "__main__":
    main()
