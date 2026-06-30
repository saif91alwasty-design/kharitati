# Subjects — AstrologicalSubjectFactory & CompositeSubjectFactory

The astrological subject is the foundation of everything. Build it once with
`AstrologicalSubjectFactory`; it returns an `AstrologicalSubjectModel` (a Pydantic model) carrying
every planet, point, house, the lunar phase, and chart configuration.

## Table of contents
- [Three ways to create a subject](#three-ways-to-create-a-subject)
- [Full `from_birth_data` parameters](#full-from_birth_data-parameters)
- [What's on a subject (reading the data)](#whats-on-a-subject-reading-the-data)
- [Configuration: zodiac, houses, perspective](#configuration-zodiac-houses-perspective)
- [Active points, asteroids, fixed stars, Arabic parts](#active-points-asteroids-fixed-stars-arabic-parts)
- [JSON / dict export](#json--dict-export)
- [CompositeSubjectFactory (midpoint composite)](#compositesubjectfactory-midpoint-composite)
- [Legacy API](#legacy-api)

## Three ways to create a subject

All three are classmethods of `AstrologicalSubjectFactory` and return an `AstrologicalSubjectModel`.

```python
from kerykeion import AstrologicalSubjectFactory

# 1) From civil birth data (most common). Positional order:
#    name, year, month, day, hour, minute
s = AstrologicalSubjectFactory.from_birth_data(
    "John Lennon", 1940, 10, 9, 18, 30,
    city="Liverpool", nation="GB",
    lng=-2.9833, lat=53.4, tz_str="Europe/London",
    online=False,
)

# 2) From a UTC ISO-8601 instant (no local-time/DST ambiguity)
s = AstrologicalSubjectFactory.from_iso_utc_time(
    name="Johnny Depp",
    iso_utc_time="1963-06-09T05:00:00Z",
    city="Owensboro", nation="US",
    lng=-87.1112, lat=37.7719, tz_str="America/Chicago",
    online=False,
)

# 3) From the current moment at a location
s = AstrologicalSubjectFactory.from_current_time(
    name="Now", city="Rome", nation="IT", lng=12.4964, lat=41.9028, tz_str="Europe/Rome", online=False,
)
```

`month`/`day`/`hour`/`minute` are 1-based civil values in **local time at the birth place**; the
`tz_str` (an IANA name like `"Europe/Rome"`) converts to UTC internally. Use `from_iso_utc_time` when
you already have a UTC instant or want to sidestep historical DST edge cases.

## Full `from_birth_data` parameters

```python
AstrologicalSubjectFactory.from_birth_data(
    name="Now",
    year=None, month=None, day=None, hour=None, minute=None,
    city=None, nation=None,                 # display labels (default "Greenwich"/"GB"); + online geocoding
    lng=None, lat=None, tz_str=None,        # REQUIRED when online=False
    geonames_username=None,
    online=True,                            # ← set False for offline (see SKILL.md)
    zodiac_type="Tropical",                 # "Tropical" | "Sidereal"
    sidereal_mode=None,                     # required iff zodiac_type="Sidereal"; see reference-data.md
    houses_system_identifier="P",           # one letter; "P"=Placidus. Full map in reference-data.md
    perspective_type="Apparent Geocentric", # | "Heliocentric" | "Topocentric" | "True Geocentric"
    cache_expire_after_days=30,             # GeoNames HTTP cache TTL
    is_dst=None,                            # disambiguate a local time that falls in a DST fold
    altitude=None,                          # metres; used by Topocentric perspective
    active_points=None,                     # which points to activate; None = library default set
    calculate_lunar_phase=True,
    custom_ayanamsa_t0=None,                # with sidereal_mode="USER"
    custom_ayanamsa_ayan_t0=None,           # with sidereal_mode="USER"
    seconds=0,                              # keyword-only: seconds of birth time
    suppress_geonames_warning=False,        # keyword-only
)
```

`from_iso_utc_time` and `from_current_time` accept the same configuration keywords (zodiac, houses,
perspective, active_points, sidereal_mode, custom ayanamsa). `from_iso_utc_time` takes
`iso_utc_time` instead of the y/m/d/h/m fields; `from_current_time` takes neither.

## What's on a subject (reading the data)

Every celestial point and house is a `KerykeionPointModel` with these fields:

| field | meaning |
|---|---|
| `name` | e.g. `"Sun"`, `"First_House"` |
| `sign` | 3-letter sign, e.g. `"Lib"` (see reference-data.md for all 12) |
| `sign_num` | 0–11 index of the sign |
| `position` | degrees within the sign (0–30) |
| `abs_pos` | absolute ecliptic longitude (0–360) |
| `emoji` | sign emoji, e.g. `"♎️"` |
| `element` | `"Fire"`/`"Earth"`/`"Air"`/`"Water"` |
| `quality` | `"Cardinal"`/`"Fixed"`/`"Mutable"` |
| `house` | which house the point is in (planets only; `None` for houses) |
| `point_type` | `"AstrologicalPoint"` or `"House"` |
| `retrograde` | bool (planets) or `None` |
| `speed` | daily motion in degrees |
| `declination` | equatorial declination |
| `magnitude` | apparent visual magnitude (fixed stars) |

Access points and houses as attributes (snake_case):

```python
s.sun, s.moon, s.mercury, s.venus, s.mars, s.jupiter, s.saturn, s.uranus, s.neptune, s.pluto
s.ascendant, s.medium_coeli, s.descendant, s.imum_coeli      # the four angles
s.first_house ... s.twelfth_house                            # 12 house cusps
s.chiron, s.mean_lilith, s.true_lilith
s.mean_north_lunar_node, s.true_north_lunar_node, s.mean_south_lunar_node, s.true_south_lunar_node

print(s.sun.sign, s.sun.position, s.sun.house, s.sun.retrograde)
print(s.ascendant.sign)
print(s.moon.element)
```

The subject also exposes metadata and the lunar phase:

```python
s.name, s.city, s.nation, s.lng, s.lat, s.tz_str
s.year, s.month, s.day, s.hour, s.minute, s.day_of_week
s.iso_formatted_local_datetime, s.iso_formatted_utc_datetime, s.julian_day
s.zodiac_type, s.sidereal_mode, s.ayanamsa_value           # ayanamsa_value set on sidereal charts
s.houses_system_identifier, s.houses_system_name, s.perspective_type
s.is_diurnal, s.houses_names_list, s.active_points

lp = s.lunar_phase            # LunarPhaseModel
print(lp.moon_phase_name)     # e.g. "Waning Gibbous"
print(lp.moon_emoji)          # e.g. "🌖"
print(lp.moon_phase)          # phase index 1..28-ish
print(lp.degrees_between_s_m) # Sun→Moon separation in degrees
```

## Configuration: zodiac, houses, perspective

```python
# Sidereal / Vedic — must give a sidereal_mode (ayanamsa)
vedic = AstrologicalSubjectFactory.from_birth_data(
    "Sidereal", 1990, 7, 15, 10, 30, lng=12.5, lat=41.9, tz_str="Europe/Rome",
    online=False, zodiac_type="Sidereal", sidereal_mode="LAHIRI",
)
print(vedic.ayanamsa_value)   # offset in degrees

# Custom ayanamsa (USER mode)
AstrologicalSubjectFactory.from_birth_data(
    "Custom", 2000, 1, 1, 0, 0, lng=0.0, lat=51.5, tz_str="Etc/GMT", online=False,
    zodiac_type="Sidereal", sidereal_mode="USER",
    custom_ayanamsa_t0=2451545.0,     # reference Julian day (J2000.0)
    custom_ayanamsa_ayan_t0=23.5,     # ayanamsa offset at that epoch
)

# Different house system (e.g. "W" = Whole Sign, "K" = Koch, "R" = Regiomontanus)
AstrologicalSubjectFactory.from_birth_data(
    "Whole Sign", 1990, 7, 15, 10, 30, lng=12.5, lat=41.9, tz_str="Europe/Rome",
    online=False, houses_system_identifier="W",
)

# Heliocentric (or Topocentric — pass altitude in metres)
AstrologicalSubjectFactory.from_birth_data(
    "Helio", 1990, 7, 15, 10, 30, lng=12.5, lat=41.9, tz_str="Europe/Rome",
    online=False, perspective_type="Heliocentric",
)
```

All 48 sidereal modes, all 23 house-system letters with names, and the 4 perspectives are listed in
`references/reference-data.md`.

## Active points, asteroids, fixed stars, Arabic parts

A subject can carry up to 63 points: 10 planets, both Mean and True nodes, Chiron, both Liliths,
Earth, major asteroids `Ceres/Pallas/Juno/Vesta`, centaur `Pholus`, TNOs `Eris/Sedna/Haumea/
Makemake/Ixion/Orcus/Quaoar`, 23 fixed stars, Arabic parts `Pars_Fortunae/Pars_Spiritus/Pars_Amoris/
Pars_Fidei`, `Vertex`/`Anti_Vertex`, and the four angles.

**Important — only *active* points are populated.** A point's attribute is `None` unless that point
is in the subject's `active_points`. The default active set is the 10 planets + True nodes + Chiron +
Mean Lilith + 4 angles, so by default `s.ceres`, `s.sirius`, `s.mean_north_lunar_node`, etc. are
`None`. To read an asteroid, fixed star, or Mean node **off the subject**, activate it when you build
the subject:

```python
from kerykeion.settings.config_constants import DEFAULT_ACTIVE_POINTS

s = AstrologicalSubjectFactory.from_birth_data(
    "John Lennon", 1940, 10, 9, 18, 30, city="Liverpool", nation="GB",
    lng=-2.9833, lat=53.4, tz_str="Europe/London", online=False,
    active_points=list(DEFAULT_ACTIVE_POINTS) + ["Ceres", "Sirius", "Regulus",
                                                 "Mean_North_Lunar_Node", "Mean_South_Lunar_Node"],
)
print(s.sirius.abs_pos, s.sirius.magnitude, s.sirius.declination)   # now populated (e.g. magnitude -1.46)
print(s.ceres.sign, s.mean_north_lunar_node.sign)                  # also active here
# NB: s.vertex / s.pars_fortunae / s.pallas etc. stay None unless you add them to active_points too
```

The subject's `active_points` is the **source of truth**: it decides which points are computed/
populated on the subject *and* which are available to charts and aspects. The `active_points`
argument on `ChartDataFactory` / `AspectsFactory` can only **narrow** that set (pick a subset to
draw/aspect) — it **cannot add** a point the subject never computed. So passing
`active_points=[..., "Sirius"]` to `create_natal_chart_data` of a default subject silently does
nothing for Sirius. **If you want an asteroid / fixed star / Mean node anywhere — as an attribute, on
a chart, or in aspects — activate it on the subject** (as above). This is the single reliable rule.

Point names are exact strings (case- and underscore-sensitive). The complete 63-name list is in
`references/reference-data.md`.

## JSON / dict export

`AstrologicalSubjectModel` is a Pydantic model, so:

```python
print(s.model_dump_json(indent=2))        # full subject as JSON
print(s.sun.model_dump_json())            # a single point as JSON
data = s.model_dump()                     # plain dict
```

## CompositeSubjectFactory (midpoint composite)

A composite chart represents the *relationship itself* by taking the midpoints of two people's
points. The factory returns a `CompositeSubjectModel`, which behaves like a subject (same point/house
attributes). You can read its attributes directly, pass it to
`ChartDataFactory.create_composite_chart_data` and `AspectsFactory`, and serialize it with
`to_context`. **Note:** `ReportGenerator` does **not** accept a raw `CompositeSubjectModel` (it
raises `TypeError: Unsupported model type`) — to report a composite, wrap it first:
`ReportGenerator(ChartDataFactory.create_composite_chart_data(composite_model)).print_report()`.

```python
from kerykeion import AstrologicalSubjectFactory, CompositeSubjectFactory

a = AstrologicalSubjectFactory.from_birth_data("Angelina Jolie", 1975, 6, 4, 9, 9,
        city="Los Angeles", nation="US", lng=-118.2437, lat=34.0522, tz_str="America/Los_Angeles", online=False)
b = AstrologicalSubjectFactory.from_birth_data("Brad Pitt", 1963, 12, 18, 6, 31,
        city="Shawnee", nation="US", lng=-96.7069, lat=35.3273, tz_str="America/Chicago", online=False)

composite_model = CompositeSubjectFactory(a, b).get_midpoint_composite_subject_model()
print(composite_model.sun.sign)
```

Constructor: `CompositeSubjectFactory(first_subject, second_subject, chart_name=None)`. The only
method you need is `get_midpoint_composite_subject_model()`.

## Legacy API

`from kerykeion import AstrologicalSubject` is a v4-compatible wrapper that constructs by calling the
factory; prefer `AstrologicalSubjectFactory` in new code. `KerykeionChartSVG`, `NatalAspects`, and
`SynastryAspects` are legacy wrappers for `ChartDrawer` and `AspectsFactory` respectively — use the
modern factories instead.
