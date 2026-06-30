# Charts — ChartDataFactory + ChartDrawer

Rendering is always **two steps**: precompute a `ChartDataModel` with `ChartDataFactory`, then draw
it with `ChartDrawer`. The factory does the astrology (which points, which aspects, distributions,
house comparison); the drawer does the SVG.

## Table of contents
- [Step 1 — ChartDataFactory](#step-1--chartdatafactory)
- [Step 2 — ChartDrawer](#step-2--chartdrawer)
- [Output methods](#output-methods-save-vs-generate)
- [Chart-type recipes](#chart-type-recipes)
- [Styling: themes, modern style, language](#styling-themes-modern-style-language)
- [Layout variants: external, wheel-only, aspect-grid-only](#layout-variants-external-wheel-only-aspect-grid-only)
- [Output tuning: minify, no-CSS-variables, transparent, title](#output-tuning)

## Step 1 — ChartDataFactory

Each method returns a `SingleChartDataModel` (natal/composite/single-return) or `DualChartDataModel`
(synastry/transit/dual-return). Pick the method that matches the chart you want:

```python
from kerykeion import ChartDataFactory

ChartDataFactory.create_natal_chart_data(subject)                          # one subject
ChartDataFactory.create_synastry_chart_data(first, second)                 # two people
ChartDataFactory.create_transit_chart_data(natal, transit)                 # natal + transit moment
ChartDataFactory.create_composite_chart_data(composite_model)              # from CompositeSubjectFactory
ChartDataFactory.create_return_chart_data(natal, return_subject)           # dual wheel: natal + return
ChartDataFactory.create_single_wheel_return_chart_data(return_subject)     # return alone, one wheel
# Generic dispatcher (rarely needed):
ChartDataFactory.create_chart_data(chart_type, first_subject, second_subject=None, ...)
```

Keyword options — **not every method accepts every kwarg**; passing an unsupported one raises
`TypeError`. This matrix is exact:

| kwarg | natal | synastry | transit | return (dual) | single-return | composite | generic `create_chart_data` |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| `active_points` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `active_aspects` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `distribution_method` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `custom_distribution_weights` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `include_house_comparison` | — | ✓ | ✓ | ✓ | — | — | ✓ |
| `include_relationship_score` | — | ✓ | — | — | — | — | ✓ |
| `axis_orb_limit` | — | — | — | — | — | — | ✓ |

So `axis_orb_limit` is **only** on the generic `create_chart_data` (and on `AspectsFactory` /
`TransitsTimeRangeFactory` — see `references/analysis.md` / `references/time-techniques.md`), never on
the `create_*_chart_data` helpers. `include_relationship_score` is synastry-only; `include_house_
comparison` is dual-charts-only.

- `distribution_method` (`"weighted"` default / `"pure_count"`) and `custom_distribution_weights`
  (`{"sun": 3.0, "__default__": 0.75}`) — keyword-only — control element/quality totals.

**`active_points` here can only *narrow*, not extend.** It selects a subset of the points that are
already active on the subject; it cannot add a point the subject never computed. So
`create_natal_chart_data(subject, active_points=["Sun", "Moon", "Ascendant"])` works (narrows the
display), but `create_natal_chart_data(default_subject, active_points=[..., "Sirius"])` silently
drops `"Sirius"` because the subject's `sirius` is `None`. **To include asteroids, fixed stars, or
Mean nodes on a chart, build the *subject* with them in `active_points` first** (see
`references/subjects.md`), then they flow through automatically.

What the data model carries (handy when you read it back): `chart_type`, the subject(s), `aspects`
(list of `AspectModel`), `element_distribution`, `quality_distribution`, `active_points`,
`active_aspects`, and on dual charts `house_comparison` + `relationship_score`. Field lists are in
`references/reference-data.md`; aspect/distribution details in `references/analysis.md`.

## Step 2 — ChartDrawer

```python
from kerykeion.charts.chart_drawer import ChartDrawer

drawer = ChartDrawer(
    chart_data=chart_data,             # the model from step 1 (required, keyword)
    theme="classic",                   # classic|dark|light|dark-high-contrast|strawberry|black-and-white
    style="classic",                   # "classic" | "modern"
    chart_language="EN",               # EN FR PT IT CN ES RU TR DE HI
    external_view=False,               # put the zodiac ring on the outside (natal)
    double_chart_aspect_grid_type="list",   # dual charts: "list" or "table"
    transparent_background=False,
    custom_title=None,                 # override the chart title
    show_degree_indicators=True,       # classic style only
    show_aspect_icons=True,            # classic style only
    show_zodiac_background_ring=True,  # modern style only
    language_pack=None,                # dict of label overrides / a new language
)
```

`theme=None` emits an unstyled SVG so you can supply your own CSS variables. Constructor also accepts
advanced overrides (`colors_settings`, `celestial_points_settings`, `aspects_settings`,
`auto_size`, `padding`, `show_house_position_comparison`, `show_cusp_position_comparison`) — only
reach for these when the user wants fine-grained customization.

## Output methods (save vs. generate)

`ChartDrawer` writes files **or** returns an SVG string. The `style` and
`show_zodiac_background_ring` arguments may be set on the constructor *or* per-call on the `save_`/
`generate_` methods (per-call wins).

```python
# Write an .svg file to a directory
drawer.save_svg(output_path="charts_output", filename="my-chart")          # → charts_output/my-chart.svg
drawer.save_wheel_only_svg_file(output_path="charts_output", filename="wheel")   # wheel, no aspect grid
drawer.save_aspect_grid_only_svg_file(output_path="charts_output", filename="grid")  # just the aspect grid

# Or get the SVG as a string (no file written) — great for web responses
svg_text: str = drawer.generate_svg_string()
wheel_text: str = drawer.generate_wheel_only_svg_string()
grid_text: str = drawer.generate_aspect_grid_only_svg_string()
```

`save_*` signature: `(output_path=None, filename=None, minify=False, remove_css_variables=False, *, ...)`.
If `output_path` is omitted it falls back to a default location, so **always pass an explicit
`output_path`** (e.g. a `charts_output/` folder you created) to keep output predictable. The `.svg`
extension is added automatically.

## Chart-type recipes

Each recipe assumes subjects already built offline (see `references/subjects.md`).

```python
from pathlib import Path
from kerykeion import AstrologicalSubjectFactory, CompositeSubjectFactory, PlanetaryReturnFactory
from kerykeion import ChartDataFactory
from kerykeion.charts.chart_drawer import ChartDrawer

out = Path("charts_output"); out.mkdir(exist_ok=True)

john = AstrologicalSubjectFactory.from_birth_data("John Lennon", 1940, 10, 9, 18, 30,
        city="Liverpool", nation="GB", lng=-2.9833, lat=53.4, tz_str="Europe/London", online=False)
paul = AstrologicalSubjectFactory.from_birth_data("Paul McCartney", 1942, 6, 18, 15, 30,
        city="Liverpool", nation="GB", lng=-2.9833, lat=53.4, tz_str="Europe/London", online=False)

# Natal
nat = ChartDataFactory.create_natal_chart_data(john)
ChartDrawer(chart_data=nat).save_svg(output_path=out, filename="natal")

# Synastry (two people overlaid)
syn = ChartDataFactory.create_synastry_chart_data(john, paul)
ChartDrawer(chart_data=syn).save_svg(output_path=out, filename="synastry")

# Transit (current sky vs natal): second subject is the transit moment
transit_moment = AstrologicalSubjectFactory.from_birth_data("Transit", 2025, 6, 8, 8, 45,
        lng=-2.9833, lat=53.4, tz_str="Europe/London", online=False)
tr = ChartDataFactory.create_transit_chart_data(john, transit_moment)
ChartDrawer(chart_data=tr).save_svg(output_path=out, filename="transit")

# Solar / Lunar return (dual wheel = natal + return; see time-techniques.md for the factory)
rf = PlanetaryReturnFactory(john, city="Liverpool", nation="GB", lng=-2.9833, lat=53.4, tz_str="Europe/London", online=False)
sr = rf.next_return_from_date(1964, 10, 1, return_type="Solar")
ChartDrawer(chart_data=ChartDataFactory.create_return_chart_data(john, sr)).save_svg(
    output_path=out, filename="solar-return-dual")
# Single wheel of just the return:
ChartDrawer(chart_data=ChartDataFactory.create_single_wheel_return_chart_data(sr)).save_svg(
    output_path=out, filename="solar-return-single")

# Composite
comp = CompositeSubjectFactory(john, paul).get_midpoint_composite_subject_model()
ChartDrawer(chart_data=ChartDataFactory.create_composite_chart_data(comp)).save_svg(
    output_path=out, filename="composite")
```

## Styling: themes, modern style, language

```python
# Theme
ChartDrawer(chart_data=nat, theme="dark").save_svg(output_path=out, filename="dark")
ChartDrawer(chart_data=nat, theme="black-and-white").save_svg(output_path=out, filename="bw")

# Modern concentric-ring style (works with every theme; set on constructor or per-call)
ChartDrawer(chart_data=nat).save_svg(output_path=out, filename="modern", style="modern")
ChartDrawer(chart_data=nat, style="modern", theme="dark").save_svg(output_path=out, filename="modern-dark")

# Language (chart labels). Full list: EN FR PT IT CN ES RU TR DE HI
ChartDrawer(chart_data=nat, chart_language="IT").save_svg(output_path=out, filename="natal-it")

# Custom labels / a brand-new language — only the keys you supply are merged over the defaults
ChartDrawer(chart_data=nat, chart_language="PT",
            language_pack={"info": "Informações", "celestial_points": {"Sun": "Sol", "Moon": "Lua"}}
).save_svg(output_path=out, filename="natal-pt")
```

For dual charts in modern style, `double_chart_aspect_grid_type="table"` switches the aspect grid
from a vertical list to a cross-reference table.

## Layout variants: external, wheel-only, aspect-grid-only

```python
# External natal: zodiac wheel on the outer ring
ChartDrawer(chart_data=nat, external_view=True).save_svg(output_path=out, filename="external")

# Wheel only (no aspect grid) — available for every chart type
ChartDrawer(chart_data=nat).save_wheel_only_svg_file(output_path=out, filename="wheel-only")

# Aspect grid only (useful for custom layouts)
ChartDrawer(chart_data=syn, theme="dark").save_aspect_grid_only_svg_file(
    output_path=out, filename="aspect-grid")
```

## Output tuning

```python
# Minified SVG (smaller file)
drawer.save_svg(output_path=out, filename="min", minify=True)

# Inline all styles, drop CSS variables → maximises compatibility with non-browser SVG viewers
drawer.save_svg(output_path=out, filename="portable", remove_css_variables=True)

# Transparent background + custom title
ChartDrawer(chart_data=nat, transparent_background=True, custom_title="Natal — JL"
).save_svg(output_path=out, filename="transparent")
```

Tip: SVGs render best in a web browser. Use `remove_css_variables=True` when the SVG must open in
apps that don't support CSS custom properties.
