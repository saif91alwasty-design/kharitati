# Reports & AI context — ReportGenerator and to_context

Two ways to turn Kerykeion data into text: a human-readable `ReportGenerator` (tables for people) and
`to_context` (compact, non-interpretive XML for LLM prompts).

## ReportGenerator (human-readable text)

`ReportGenerator` mirrors the chart-type dispatch of `ChartDrawer`. It accepts a raw subject, any
`ChartDataModel` from `ChartDataFactory`, **or** a `MoonPhaseOverviewModel`, and renders the right
report automatically.

```python
from kerykeion import ReportGenerator, AstrologicalSubjectFactory, ChartDataFactory

subject = AstrologicalSubjectFactory.from_birth_data("Sample Natal", 1990, 7, 21, 14, 45,
        city="Rome", nation="IT", lng=12.4964, lat=41.9028, tz_str="Europe/Rome", online=False)

# Subject-only report (no aspects)
ReportGenerator(subject).print_report(include_aspects=False)

# Single-chart data (elements, qualities, aspects); cap how many aspects are listed
natal_data = ChartDataFactory.create_natal_chart_data(subject)
ReportGenerator(natal_data).print_report(max_aspects=10)

# Dual chart (synastry / transit / dual return) — includes house comparison + relationship score when present
partner = AstrologicalSubjectFactory.from_birth_data("Sample Partner", 1992, 11, 5, 9, 30,
        city="Rome", nation="IT", lng=12.4964, lat=41.9028, tz_str="Europe/Rome", online=False)
synastry_data = ChartDataFactory.create_synastry_chart_data(subject, partner)
ReportGenerator(synastry_data).print_report(max_aspects=12)
```

Two methods:

- `print_report(*, include_aspects=None, max_aspects=None)` — prints to stdout.
- `generate_report(*, include_aspects=None, max_aspects=None)` — returns the report as a string.

`include_aspects` / `max_aspects` may be set on the constructor
(`ReportGenerator(model, *, include_aspects=True, max_aspects=None)`) or per call (the call wins).
A report typically contains: a chart-aware title, birth/event metadata + configuration, celestial
points (sign, position, daily motion, declination, retrograde, house), house-cusp tables for each
subject, lunar phase, element/quality distributions, the aspect list, and — for dual charts — house
comparisons and the relationship score when the data carries them.

Grab sections by splitting the string output:

```python
report = ReportGenerator(natal_data)
sections = report.generate_report(max_aspects=5).split("\n\n")
for section in sections[:3]:
    print(section)
```

`ReportGenerator` also renders a `MoonPhaseOverviewModel` (see `references/time-techniques.md`):
`ReportGenerator(overview).print_report()` produces a formatted Moon-phase overview.

## to_context (LLM / prompt-ready XML)

`to_context` serializes a Kerykeion model into precise, **non-qualitative** XML — the raw "ground
truth" (positions, signs, houses, aspects, lunar phase) with no interpretation. It's designed to drop
straight into an LLM system prompt so the model interprets accurate data instead of hallucinating
positions.

```python
from kerykeion import AstrologicalSubjectFactory, to_context

subject = AstrologicalSubjectFactory.from_birth_data("John Doe", 1990, 1, 1, 12, 0,
        city="London", nation="GB", lng=-0.1278, lat=51.5074, tz_str="Europe/London", online=False)

context = to_context(subject)   # returns a str
print(context)
```

Output shape:

```xml
<chart name="John Doe">
  <birth_data date="1990-01-01" time="12:00" city="..." nation="..." ... />
  <config zodiac="Tropical" house_system="Placidus" perspective="Apparent Geocentric" />
  <planets>
    <point name="Sun" position="10.81" sign="Capricorn" element="Earth" quality="Cardinal" ... />
    ...
  </planets>
  <houses>...</houses>
  <lunar_phase name="Waning Gibbous" phase="20" degrees_between="254.32" emoji="🌖" />
</chart>
```

`to_context` accepts a wide range of models — not just subjects — so you can serialize whichever piece
of data you're feeding the LLM:

- subjects: `AstrologicalSubjectModel`, `CompositeSubjectModel`, `PlanetReturnModel`
- chart data: `SingleChartDataModel`, `DualChartDataModel`
- pieces: `KerykeionPointModel`, `LunarPhaseModel`, `AspectModel`,
  `ElementDistributionModel`, `QualityDistributionModel`, `PointInHouseModel`, `HouseComparisonModel`
- time: `TransitMomentModel`, `TransitsTimeRangeModel`, `MoonPhaseOverviewModel`

So a typical "build an interpretation" flow is: compute the chart data, pass it through `to_context`,
and inject the XML into your prompt:

```python
data = ChartDataFactory.create_synastry_chart_data(subject, partner)
prompt = f"Interpret this synastry. Use only this data:\n{to_context(data)}"
```

The serializer keeps the format consistent across natal, synastry, composite, and return charts,
escapes XML correctly, and omits empty fields — giving the model a clean, deterministic payload.
