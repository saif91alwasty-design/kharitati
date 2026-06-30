# Reference data — exact enum values, defaults, model fields

Authoritative vocabularies (from `kerykeion.schemas.kr_literals` and `settings.config_constants`,
v5.x). These strings must match exactly (case- and underscore-sensitive). **Important:** for
`active_points`, a name that doesn't match — wrong casing like `"sun"`, or a typo like `"Suun"` — is
**silently dropped, not rejected**. It raises no error; the point simply ends up inactive (e.g.
`active_points=["sun"]` leaves the subject with no active Sun and `subject.sun is None`). After
building a subject, sanity-check `subject.active_points` to confirm every name you intended is
present. Import these as `Literal` types from `kerykeion.kr_types` / `kerykeion.schemas.kr_literals`
to get static type-checker warnings for mistyped names.

## Signs, elements, qualities

| Sign (`Sign`) | Ari | Tau | Gem | Can | Leo | Vir | Lib | Sco | Sag | Cap | Aqu | Pis |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Emoji (`SignsEmoji`) | ♈️ | ♉️ | ♊️ | ♋️ | ♌️ | ♍️ | ♎️ | ♏️ | ♐️ | ♑️ | ♒️ | ♓️ |

- `Element`: `Fire`, `Earth`, `Air`, `Water`
- `Quality`: `Cardinal`, `Fixed`, `Mutable`
- `ZodiacType`: `Tropical` (default), `Sidereal`

## Houses

`Houses`: `First_House`, `Second_House`, `Third_House`, `Fourth_House`, `Fifth_House`,
`Sixth_House`, `Seventh_House`, `Eighth_House`, `Ninth_House`, `Tenth_House`, `Eleventh_House`,
`Twelfth_House`. (Subject attributes use lowercase: `s.first_house` … `s.twelfth_house`.)

## House systems (`HousesSystemIdentifier`)

Pass the **single letter** to `houses_system_identifier`. Default `P` (Placidus).

| Letter | System | Letter | System |
|---|---|---|---|
| `A` | Equal | `O` | Porphyry |
| `B` | Alcabitius | `P` | **Placidus** (default) |
| `C` | Campanus | `Q` | Pullen SR |
| `D` | Equal (MC) | `R` | Regiomontanus |
| `F` | Carter poli-equ. | `S` | Sripati |
| `H` | Horizon/Azimut | `T` | Polich/Page |
| `I` | Sunshine | `U` | Krusinski-Pisa-Goelzer |
| `i` | Sunshine/alt. | `V` | Equal/Vehlow |
| `K` | Koch | `W` | Whole Sign |
| `L` | Pullen SD | `X` | Axial rotation / Meridian |
| `M` | Morinus | `Y` | APC houses |
| `N` | Equal (1=Aries) | | |

(All Swiss-Ephemeris house systems except Gauquelin sectors. `i` and `I` are distinct.)

## Perspective (`PerspectiveType`)

`Apparent Geocentric` (default), `True Geocentric`, `Topocentric` (needs `altitude`), `Heliocentric`.

## Sidereal modes / ayanamsa (`SiderealMode`)

Required when `zodiac_type="Sidereal"`. 48 values:

- **Indian/Vedic**: `LAHIRI`, `LAHIRI_1940`, `LAHIRI_ICRC`, `LAHIRI_VP285`, `KRISHNAMURTI`,
  `KRISHNAMURTI_VP291`, `RAMAN`, `YUKTESHWAR`, `JN_BHASIN`, `USHASHASHI`, `DJWHAL_KHUL`,
  `ARYABHATA`, `ARYABHATA_522`, `ARYABHATA_MSUN`, `SURYASIDDHANTA`, `SURYASIDDHANTA_MSUN`,
  `SS_CITRA`, `SS_REVATI`, `TRUE_CITRA`, `TRUE_REVATI`, `TRUE_PUSHYA`, `TRUE_MULA`, `TRUE_SHEORAN`
- **Western sidereal**: `FAGAN_BRADLEY`, `DELUCE`, `HIPPARCHOS`, `SASSANIAN`, `ALDEBARAN_15TAU`,
  `VALENS_MOON`
- **Babylonian**: `BABYL_KUGLER1`, `BABYL_KUGLER2`, `BABYL_KUGLER3`, `BABYL_HUBER`, `BABYL_ETPSC`,
  `BABYL_BRITTON`
- **Galactic**: `GALCENT_0SAG`, `GALCENT_COCHRANE`, `GALCENT_MULA_WILHELM`, `GALCENT_RGILBRAND`,
  `GALEQU_FIORENZA`, `GALEQU_IAU1958`, `GALEQU_MULA`, `GALEQU_TRUE`, `GALALIGN_MARDYKS`
- **Astronomical epochs**: `J2000`, `J1900`, `B1950`
- **Custom**: `USER` (supply `custom_ayanamsa_t0` + `custom_ayanamsa_ayan_t0`)

## Chart styling

- `ChartType`: `Natal`, `Synastry`, `Transit`, `Composite`, `DualReturnChart`, `SingleReturnChart`
- `KerykeionChartTheme`: `classic` (default), `dark`, `light`, `dark-high-contrast`, `strawberry`,
  `black-and-white`
- `KerykeionChartStyle`: `classic` (default), `modern`
- `KerykeionChartLanguage`: `EN`, `FR`, `PT`, `IT`, `CN`, `ES`, `RU`, `TR`, `DE`, `HI`
- `CompositeChartType`: `Midpoint`
- `ReturnType`: `Solar`, `Lunar`

## Aspects

`AspectName` and their exact angles (★ = "major", on by default):

| Aspect | Degrees | Default? | Default orb |
|---|---|---|---|
| ★ conjunction | 0 | yes | 10 |
| semi-sextile | 30 | no | — |
| semi-square | 45 | no | — |
| ★ sextile | 60 | yes | 6 |
| quintile | 72 | yes (orb 1) | 1 |
| ★ square | 90 | yes | 5 |
| ★ trine | 120 | yes | 8 |
| sesquiquadrate | 135 | no | — |
| biquintile | 144 | no | — |
| quincunx | 150 | no | — |
| ★ opposition | 180 | yes | 10 |

`DEFAULT_ACTIVE_ASPECTS` (from `kerykeion.settings.config_constants`):

```python
[{"name": "conjunction", "orb": 10}, {"name": "opposition", "orb": 10},
 {"name": "trine", "orb": 8}, {"name": "sextile", "orb": 6},
 {"name": "square", "orb": 5}, {"name": "quintile", "orb": 1}]
```

`AspectMovementType`: `Applying`, `Separating`, `Static`.

## Lunar phases

- `LunarPhaseName`: `New Moon`, `Waxing Crescent`, `First Quarter`, `Waxing Gibbous`, `Full Moon`,
  `Waning Gibbous`, `Last Quarter`, `Waning Crescent`
- `LunarPhaseEmoji`: 🌑 🌒 🌓 🌔 🌕 🌖 🌗 🌘 (in the same order)

## Relationship score descriptions (`RelationshipScoreDescription`)

`Minimal`, `Medium`, `Important`, `Very Important`, `Exceptional`, `Rare Exceptional`.

## Astrological points (`AstrologicalPoint` / `Planet`) — all 63

Use these **exact** strings in `active_points`. They are also subject attributes in lowercase
(`True_North_Lunar_Node` → `s.true_north_lunar_node`).

- **Planets (10):** `Sun`, `Moon`, `Mercury`, `Venus`, `Mars`, `Jupiter`, `Saturn`, `Uranus`,
  `Neptune`, `Pluto`
- **Lunar nodes (4):** `Mean_North_Lunar_Node`, `True_North_Lunar_Node`, `Mean_South_Lunar_Node`,
  `True_South_Lunar_Node`
- **Lilith / other (3):** `Chiron`, `Mean_Lilith`, `True_Lilith`
- **Earth & centaurs:** `Earth`, `Pholus`
- **Asteroids (4):** `Ceres`, `Pallas`, `Juno`, `Vesta`
- **TNOs / dwarf planets (8):** `Eris`, `Sedna`, `Haumea`, `Makemake`, `Ixion`, `Orcus`, `Quaoar`
  (plus `Pholus` above)
- **Fixed stars (23):** `Regulus`, `Spica`, `Aldebaran`, `Antares`, `Sirius`, `Fomalhaut`, `Algol`,
  `Betelgeuse`, `Canopus`, `Procyon`, `Arcturus`, `Pollux`, `Deneb`, `Altair`, `Rigel`, `Achernar`,
  `Capella`, `Vega`, `Alcyone`, `Alphecca`, `Algorab`, `Deneb_Algedi`, `Alkaid`
- **Arabic parts (4):** `Pars_Fortunae`, `Pars_Spiritus`, `Pars_Amoris`, `Pars_Fidei`
- **Other points:** `Vertex`, `Anti_Vertex`
- **Angles (4):** `Ascendant`, `Medium_Coeli`, `Descendant`, `Imum_Coeli`

`DEFAULT_ACTIVE_POINTS` (what charts/aspects use unless you override):

```python
["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto",
 "True_North_Lunar_Node","True_South_Lunar_Node","Chiron","Mean_Lilith",
 "Ascendant","Medium_Coeli","Descendant","Imum_Coeli"]
```

Everything else (Mean nodes, True Lilith, Earth, asteroids, TNOs, fixed stars, Arabic parts, Vertex)
is **not populated** — the corresponding subject attribute is `None` — until you name it in the
**subject's** `active_points` (the arg on `ChartDataFactory`/`AspectsFactory` only narrows, it can't
add points; see `references/subjects.md`).

`PointType`: `AstrologicalPoint`, `House`.

## Key model fields (quick reference)

- **`KerykeionPointModel`** (every planet/point/house): `name`, `quality`, `element`, `sign`,
  `sign_num`, `position`, `abs_pos`, `emoji`, `point_type`, `house`, `retrograde`, `speed`,
  `declination`, `magnitude`
- **`LunarPhaseModel`**: `degrees_between_s_m`, `moon_phase`, `moon_emoji`, `moon_phase_name`
- **`AspectModel`**: `p1_name`, `p1_owner`, `p1_abs_pos`, `p2_name`, `p2_owner`, `p2_abs_pos`,
  `aspect`, `orbit`, `aspect_degrees`, `diff`, `p1`, `p2`, `p1_speed`, `p2_speed`, `aspect_movement`
- **`SingleChartDataModel`**: `chart_type`, `subject`, `aspects`, `element_distribution`,
  `quality_distribution`, `active_points`, `active_aspects`
- **`DualChartDataModel`**: `chart_type`, `first_subject`, `second_subject`, `aspects`,
  `house_comparison`, `relationship_score`, `element_distribution`, `quality_distribution`,
  `active_points`, `active_aspects`
- **`ElementDistributionModel`**: `fire`, `earth`, `air`, `water` (+ each `*_percentage`)
- **`QualityDistributionModel`**: `cardinal`, `fixed`, `mutable` (+ each `*_percentage`)
- **`HouseComparisonModel`**: `first_subject_name`, `second_subject_name`,
  `first_points_in_second_houses`, `second_points_in_first_houses`, `first_cusps_in_second_houses`,
  `second_cusps_in_first_houses`
- **`PointInHouseModel`**: `point_name`, `point_degree`, `point_sign`, `point_owner_name`,
  `point_owner_house_number`, `point_owner_house_name`, `projected_house_number`,
  `projected_house_name`, `projected_house_owner_name`
- **`RelationshipScoreModel`**: `score_value`, `score_description`, `is_destiny_sign`, `aspects`,
  `score_breakdown`, `subjects`
- **`PlanetReturnModel`** / **`CompositeSubjectModel`**: subject-like — all planet/house attributes
  plus `return_type` / `composite_chart_type` respectively
- **`TransitMomentModel`**: `date`, `aspects` — **`TransitsTimeRangeModel`**: `transits`, `subject`,
  `dates`
- **`MoonPhaseOverviewModel`**: `timestamp`, `datestamp`, `sun`, `moon`, `location`

## Errors

`from kerykeion import KerykeionException` — the library's base exception. Catch it to handle
invalid configuration (bad coordinates, geocoding failures, out-of-range ephemeris dates).
