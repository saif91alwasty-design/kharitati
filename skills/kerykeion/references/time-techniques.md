# Time techniques — returns, ephemeris, transits, moon phase

Predictive and time-based tools: where the sky returns to a natal position (returns), planetary
positions sampled across a span (ephemeris), sampled (within-orb) transit detection over a range, and
a rich Moon-phase overview.

## Table of contents
- [PlanetaryReturnFactory (solar / lunar returns)](#planetaryreturnfactory-solar--lunar-returns)
- [EphemerisDataFactory (positions over a date range)](#ephemerisdatafactory-positions-over-a-date-range)
- [TransitsTimeRangeFactory (sampled transit detection)](#transitstimerangefactory-sampled-transit-detection)
- [MoonPhaseDetailsFactory (lunar overview)](#moonphasedetailsfactory-lunar-overview)

## PlanetaryReturnFactory (solar / lunar returns)

A "return" is the moment a body comes back to its natal ecliptic longitude. Solar returns recur
yearly (around the birthday), lunar returns roughly monthly. The factory is constructed once with the
natal subject + the **location where the return is observed**, then queried for a return near a date.
Each query returns a `PlanetReturnModel` (a subject-like model). You can read its attributes, pass it
to `ChartDataFactory` and `AspectsFactory`, and serialize it with `to_context`. Like the composite
model, it is **not** accepted directly by `ReportGenerator` (raises `TypeError`) — to report a return,
wrap it through `ChartDataFactory` first (e.g.
`ReportGenerator(ChartDataFactory.create_return_chart_data(natal, return_subject)).print_report()`).

```python
from kerykeion import AstrologicalSubjectFactory, PlanetaryReturnFactory

natal = AstrologicalSubjectFactory.from_birth_data("John Lennon", 1940, 10, 9, 18, 30,
        city="Liverpool", nation="GB", lng=-2.9833, lat=53.4, tz_str="Europe/London", online=False)

rf = PlanetaryReturnFactory(
    natal,
    city="Liverpool", nation="GB",
    lng=-2.9833, lat=53.4, tz_str="Europe/London",   # where the return is cast
    online=False,
)

# return_type is keyword-only and required: "Solar" or "Lunar"
solar = rf.next_return_from_date(1964, 10, 1, return_type="Solar")   # first solar return on/after this date
lunar = rf.next_return_from_date(1964, 1, 1, return_type="Lunar")
print(solar.iso_formatted_utc_datetime, solar.sun.sign)
```

Query methods (all take `return_type="Solar"|"Lunar"`). **Prefer `next_return_from_date` or
`next_return_from_iso_formatted_time`** — the year / month-and-year variants are deprecated and emit a
`DeprecationWarning`:

| method | finds the next return… | status |
|---|---|---|
| `next_return_from_date(year, month, day=1, *, return_type)` | on/after a Y-M-D date | preferred |
| `next_return_from_iso_formatted_time(iso_formatted_time, return_type)` | on/after an ISO instant | preferred |
| `next_return_from_month_and_year(year, month, return_type)` | on/after the 1st of that month | deprecated |
| `next_return_from_year(year, return_type)` | on/after Jan 1 of that year | deprecated |

Constructor: `PlanetaryReturnFactory(subject, city=None, nation=None, lng=None, lat=None,
tz_str=None, online=True, geonames_username=None, *, cache_expire_after_days=30, altitude=None,
custom_ayanamsa_t0=None, custom_ayanamsa_ayan_t0=None)`. As always, pass `online=False` + coordinates
for offline use; use `city`/`nation` + `online=True` for geocoded locations.

To **chart** a return, feed it to `ChartDataFactory` (see `references/charts.md`):
`create_return_chart_data(natal, return_subject)` for a dual wheel, or
`create_single_wheel_return_chart_data(return_subject)` for the return alone.

## EphemerisDataFactory (positions over a date range)

Samples planetary positions at a fixed cadence between two datetimes. Useful for plotting movement,
feeding transit search, or exporting an ephemeris table.

```python
from datetime import datetime
from kerykeion import EphemerisDataFactory

factory = EphemerisDataFactory(
    start_datetime=datetime(2025, 1, 1),
    end_datetime=datetime(2025, 1, 31),
    step_type="days",      # "days" | "hours" | "minutes"
    step=1,                # one sample per step_type unit
    lat=51.4769, lng=0.0005, tz_str="Etc/UTC",
    # zodiac_type / sidereal_mode / houses_system_identifier / perspective_type also accepted
)

points = factory.get_ephemeris_data()                          # list of dicts: {"date", "planets", "houses"}
subjects = factory.get_ephemeris_data_as_astrological_subjects()  # list of AstrologicalSubjectModel
print(len(subjects), subjects[0].sun.abs_pos)
```

Guard rails: `max_days=730`, `max_hours=8760`, `max_minutes=525600` cap how many samples a single
range may produce (raise them via the constructor if you knowingly need more). Choose `step_type`/
`step` so the total count stays sensible — e.g. daily steps for a month, hourly only for short spans.

## TransitsTimeRangeFactory (sampled transit detection)

To track transiting planets aspecting a natal chart across time, combine the two factories: sample the
sky with `EphemerisDataFactory`, then pass those samples as `ephemeris_data_points`.

**What this gives you (and what it doesn't):** the result is a list of *sampled* moments — one per
ephemeris timestamp — each listing the aspects that are **within orb at that timestamp**. The dates
are your sampling cadence, **not** interpolated exact-hit times. With a daily/hourly step a fast
body (especially the Moon) can pass through exactness between samples, so an aspect may be reported a
bit before/after its true peak, or — if it tightens and loosens within one step — missed entirely.
Kerykeion does not root-find the exact instant for you. To approximate it: narrow `step`/`step_type`
(e.g. minute steps) around the window, and watch each aspect's `orbit` shrink toward 0 and its
`aspect_movement` flip from `"Applying"` to `"Separating"` — the crossover brackets the exact hit.

```python
from datetime import datetime
from kerykeion import AstrologicalSubjectFactory, EphemerisDataFactory, TransitsTimeRangeFactory

natal = AstrologicalSubjectFactory.from_birth_data("John Lennon", 1940, 10, 9, 18, 30,
        city="Liverpool", nation="GB", lng=-2.9833, lat=53.4, tz_str="Europe/London", online=False)

ephem = EphemerisDataFactory(
    start_datetime=datetime(2025, 1, 1), end_datetime=datetime(2025, 1, 10),
    step_type="days", step=1, lat=53.4, lng=-2.9833, tz_str="Europe/London",
).get_ephemeris_data_as_astrological_subjects()

tr = TransitsTimeRangeFactory(natal_chart=natal, ephemeris_data_points=ephem)
result = tr.get_transit_moments()        # → TransitsTimeRangeModel

for moment in result.transits:           # each is a TransitMomentModel
    print(moment.date, len(moment.aspects), "aspects")
    for asp in moment.aspects:
        print("  ", asp.p1_name, asp.aspect, asp.p2_name, "orb", round(asp.orbit, 2))
```

`TransitsTimeRangeFactory(natal_chart, ephemeris_data_points, active_points=<default set>,
active_aspects=<6 majors>, settings_file=None, *, axis_orb_limit=None)`. Tune `active_points` /
`active_aspects` / `axis_orb_limit` exactly as in `references/analysis.md`. The result model has
`transits` (list of `TransitMomentModel`, each with `date` + `aspects`), `subject`, and `dates`.

## MoonPhaseDetailsFactory (lunar overview)

A one-call, Swiss-Ephemeris-precise lunar overview for any subject: phase, illumination, the
surrounding major phases, next solar/lunar eclipses, sunrise/sunset, and apparent solar position.

```python
from kerykeion import AstrologicalSubjectFactory, MoonPhaseDetailsFactory, ReportGenerator

s = AstrologicalSubjectFactory.from_birth_data("Example", 2025, 4, 1, 7, 51,
        city="London", nation="GB", lng=-0.1276, lat=51.5074, tz_str="Europe/London", online=False)

overview = MoonPhaseDetailsFactory.from_subject(s)     # → MoonPhaseOverviewModel

print(overview.moon.phase_name, overview.moon.emoji)   # "Waxing Crescent 🌒"
print(overview.moon.illumination, overview.moon.stage) # "8%", "waxing"

if overview.moon.detailed and overview.moon.detailed.upcoming_phases:
    fm = overview.moon.detailed.upcoming_phases.full_moon
    if fm and fm.next:
        print("Next Full Moon:", fm.next.datestamp)

ReportGenerator(overview).print_report()               # formatted ASCII overview (see reports-and-ai.md)
print(overview.model_dump_json(exclude_none=True, indent=2))
```

`from_subject(subject, *, using_default_location=False, location_precision=0)`. The model's top level
is `timestamp`, `datestamp`, `sun`, `moon`, `location`; `overview.sun` carries sunrise/sunset/solar
noon/day length and the next solar eclipse, `overview.moon` the phase data, emoji, next lunar
eclipse, and a nested `detailed` block with `upcoming_phases` and `illumination_details`.
`MoonPhaseOverviewModel` is also one of the models accepted by `to_context` and `ReportGenerator`.
