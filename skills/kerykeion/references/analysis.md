# Analysis — aspects, compatibility, house comparison, distributions

These tools turn one or two subjects into the relational data astrologers care about: aspects,
compatibility scores, where one chart's planets fall in another's houses, and elemental/modal balance.

## Table of contents
- [AspectsFactory](#aspectsfactory)
- [Customizing aspects: active_aspects, active_points, orbs](#customizing-aspects)
- [RelationshipScoreFactory (compatibility)](#relationshipscorefactory-compatibility)
- [HouseComparisonFactory](#housecomparisonfactory)
- [Element & quality distributions](#element--quality-distributions)

## AspectsFactory

All methods are classmethods; pass subjects (or composite/return models). Single-chart methods return
a `SingleChartAspectsModel`, dual-chart methods a `DualChartAspectsModel`; both expose `.aspects`
(a list of `AspectModel`).

```python
from kerykeion import AspectsFactory, AstrologicalSubjectFactory

jack = AstrologicalSubjectFactory.from_birth_data("Jack", 1990, 6, 15, 15, 15,
        city="Rome", nation="IT", lng=12.4964, lat=41.9028, tz_str="Europe/Rome", online=False)
jane = AstrologicalSubjectFactory.from_birth_data("Jane", 1991, 10, 25, 21, 0,
        city="Rome", nation="IT", lng=12.4964, lat=41.9028, tz_str="Europe/Rome", online=False)

# Within one chart (natal, return, composite):
res = AspectsFactory.single_chart_aspects(jack)        # alias: natal_aspects(...)
print(len(res.aspects), res.aspects[0])

# Between two charts (synastry / transits / comparisons):
res = AspectsFactory.dual_chart_aspects(jack, jane)    # alias: synastry_aspects(...)
print(len(res.aspects))
```

`natal_aspects` is a convenience alias of `single_chart_aspects`; `synastry_aspects` of
`dual_chart_aspects`. Each `AspectModel` carries:

| field | meaning |
|---|---|
| `p1_name`, `p2_name` | the two points, e.g. `"Sun"`, `"Moon"` |
| `p1_owner`, `p2_owner` | which subject each point belongs to (name string) |
| `aspect` | aspect type, e.g. `"trine"` (see reference-data.md for all 11) |
| `aspect_degrees` | exact angle of the aspect (0, 60, 90, 120, 180, …) |
| `orbit` | the actual orb (deviation from exact), in degrees |
| `diff` | absolute angular separation of the two points |
| `p1_abs_pos`, `p2_abs_pos` | absolute ecliptic longitudes |
| `p1_speed`, `p2_speed` | daily motion of each point |
| `aspect_movement` | `"Applying"`, `"Separating"`, or `"Static"` |

## Customizing aspects

Three keyword-only knobs. `active_points` and `active_aspects` are also accepted by the
`ChartDataFactory` helpers and `TransitsTimeRangeFactory`; `axis_orb_limit` is accepted by
`AspectsFactory`, `TransitsTimeRangeFactory`, and the generic `ChartDataFactory.create_chart_data`,
but **not** by the `create_*_chart_data` convenience helpers (see `references/charts.md`).

```python
# Narrow which points participate (subset of the subject's active points).
# NB: like everywhere, active_points can only narrow — to aspect an asteroid/fixed star, build the
# SUBJECT with it active first (see references/subjects.md); it cannot be added here.
res = AspectsFactory.single_chart_aspects(
    jack,
    active_points=["Sun", "Moon", "Venus", "Mars", "Ascendant", "Medium_Coeli"],
)

# Choose which aspects to detect and the orb for each (name + orb in degrees)
res = AspectsFactory.dual_chart_aspects(
    jack, jane,
    active_aspects=[
        {"name": "conjunction", "orb": 8},
        {"name": "opposition",  "orb": 8},
        {"name": "trine",       "orb": 6},
        {"name": "square",      "orb": 6},
        {"name": "sextile",     "orb": 4},
    ],
    axis_orb_limit=2.0,    # tighter cap for aspects to Asc/MC/Dsc/IC
)
```

The default active aspects are conjunction (10°), opposition (10°), trine (8°), sextile (6°), square
(5°), quintile (1°). Available aspect names and their exact degrees are in
`references/reference-data.md`. You can also start from the shipped default and tweak:

```python
from kerykeion.settings.config_constants import DEFAULT_ACTIVE_ASPECTS
custom = [dict(a) for a in DEFAULT_ACTIVE_ASPECTS] + [{"name": "semi-square", "orb": 2}]
```

## RelationshipScoreFactory (compatibility)

Computes a numeric synastry compatibility score using the method of Italian astrologer Ciro
Discepolo. Construct with two subjects, then call `get_relationship_score()` → `RelationshipScoreModel`.

```python
from kerykeion import AstrologicalSubjectFactory, RelationshipScoreFactory

a = AstrologicalSubjectFactory.from_birth_data("Alice", 1990, 3, 15, 14, 30,
        city="Rome", nation="IT", lng=12.4964, lat=41.9028, tz_str="Europe/Rome", online=False)
b = AstrologicalSubjectFactory.from_birth_data("Bob", 1988, 7, 22, 9, 0,
        city="Rome", nation="IT", lng=12.4964, lat=41.9028, tz_str="Europe/Rome", online=False)

result = RelationshipScoreFactory(a, b).get_relationship_score()
print(result.score_value)         # numeric total
print(result.score_description)   # "Minimal" | "Medium" | "Important" | "Very Important" | "Exceptional" | "Rare Exceptional"
print(result.is_destiny_sign)     # bool: Sun-sign "destiny" pairing
for item in result.score_breakdown:   # which aspects contributed how many points
    print(item)
```

Constructor: `RelationshipScoreFactory(first_subject, second_subject, use_only_major_aspects=True, *,
axis_orb_limit=None)`. The model also exposes `.aspects` and `.subjects`.

## HouseComparisonFactory

Shows which of subject A's points land in subject B's houses and vice-versa — the backbone of
synastry house overlays.

```python
from kerykeion import AstrologicalSubjectFactory, HouseComparisonFactory

cmp = HouseComparisonFactory(a, b).get_house_comparison()   # → HouseComparisonModel
# first_points_in_second_houses = subject A's points landing in subject B's houses.
# Mind the two owners: point_owner_name is whose PLANET it is (A);
# projected_house_owner_name is whose HOUSE it falls into (B) — use the latter for the overlay label.
for p in cmp.first_points_in_second_houses:
    print(f"{p.point_owner_name}'s {p.point_name} ({p.point_sign}) "
          f"→ house {p.projected_house_number} of {p.projected_house_owner_name}")
```

The model has `first_points_in_second_houses`, `second_points_in_first_houses`,
`first_cusps_in_second_houses`, `second_cusps_in_first_houses` (each a list of `PointInHouseModel`),
plus `first_subject_name` / `second_subject_name`. Each `PointInHouseModel` distinguishes
`point_owner_name` (owner of the planet) from `projected_house_owner_name` (owner of the house the
planet projects into) — don't confuse them when labelling. Optional constructor arg `active_points`
limits the points considered. (Dual `ChartDataFactory` results already include this as `data.house_comparison`
when `include_house_comparison=True`.)

## Element & quality distributions

`ChartDataFactory` attaches `element_distribution` (Fire/Earth/Air/Water) and `quality_distribution`
(Cardinal/Fixed/Mutable) to its result. Two strategies:

- `distribution_method="weighted"` (default) — core factors count more (Sun/Moon/Asc ≈ 2.0, angles
  ≈ 1.5, personal planets ≈ 1.5, social ≈ 1.0, outer ≈ 0.5, minor bodies 0.3–0.8).
- `distribution_method="pure_count"` — every active point counts equally.

Override individual weights with `custom_distribution_weights` (lowercase point names; the special
key `"__default__"` sets the fallback for unlisted points):

```python
from kerykeion import AstrologicalSubjectFactory, ChartDataFactory

s = AstrologicalSubjectFactory.from_birth_data("Sample", 1986, 4, 12, 8, 45,
        city="Bologna", nation="IT", lng=11.3426, lat=44.4949, tz_str="Europe/Rome", online=False)

pure = ChartDataFactory.create_natal_chart_data(s, distribution_method="pure_count")
weighted = ChartDataFactory.create_natal_chart_data(
    s, distribution_method="weighted",
    custom_distribution_weights={"sun": 3.0, "__default__": 0.75},
)

print(pure.element_distribution.fire, weighted.element_distribution.fire)
print(weighted.element_distribution.fire_percentage)          # also *_percentage fields
print(weighted.quality_distribution.cardinal,
      weighted.quality_distribution.cardinal_percentage)
```

`ElementDistributionModel` fields: `fire`, `earth`, `air`, `water` (+ each `*_percentage`).
`QualityDistributionModel` fields: `cardinal`, `fixed`, `mutable` (+ each `*_percentage`). The same
keyword options forward through every `create_*_chart_data` method, so you can keep one weighting
scheme across natal, synastry, transit, return, and composite charts.
