---
title: Field Rotation Calculator
emoji: "\U0001F52D"
colorFrom: blue
colorTo: red
sdk: streamlit
sdk_version: "1.44.1"
app_file: app.py
pinned: false
license: mit
short_description: Alt-Az telescope field rotation speed & parallactic angle
---

# Alt-Az Telescope Field Rotation Calculator

Interactive calculator for field (de-)rotation in alt-azimuth telescope mounts.

## Features

- **Field rotation speed** (arcsec/s) and **parallactic angle** contour maps over the full azimuth-altitude sky
- Overlaid **hour-angle** (dashed green) and **declination** (solid black) grid lines showing equatorial coordinate motion
- Preset observatory sites: Lenghu, Mauna Kea, La Palma, Cerro Pachon, Las Campanas, Paranal, La Silla, Sutherland, Siding Spring, or custom latitude
- Configurable HA time spacing, Dec spacing, Az/Alt range
- Export as **SVG**, **PDF**, or **PNG** (300 dpi)

## Spherical Astronomy

Azimuth measured North-through-East (0-360 deg).

| Quantity | Formula |
|---|---|
| Declination | sin(Dec) = sin(Alt)sin(phi) + cos(Alt)cos(phi)cos(Az) |
| Hour Angle | tan(HA) = -sin(Az) / [tan(Alt)cos(phi) - sin(phi)cos(Az)] |
| Parallactic Angle | tan(q) = sin(HA)cos(phi) / [cos(Dec)sin(phi) - sin(Dec)cos(phi)cos(HA)] |
| Rotation Speed | dq/dt = -cos(phi)cos(Az)/cos(Alt) x 15.041 arcsec/s |

## Run Locally

```bash
pip install numpy matplotlib streamlit
streamlit run app.py
```
