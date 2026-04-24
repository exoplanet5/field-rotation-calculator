---
title: Alt-Az Telescope Tracking Specs
emoji: "\U0001F52D"
colorFrom: blue
colorTo: red
sdk: streamlit
app_file: app.py
pinned: false
license: mit
short_description: Alt-Az mount tracking speed, acceleration, and field rotation
---

# Alt-Az Telescope Tracking Specs

Interactive calculator for alt-azimuth mount tracking: field rotation,
axis drive speeds, and drive accelerations. Two pages:

1. **Az-Alt Track Specs** — three stacked Az-Alt panels
   - Field rotation (switchable between rotation speed and parallactic angle)
   - Elevation angular velocity
   - Azimuth angular velocity
2. **Zenith Polar Specs** — polar zenith view with four panels
   - Elevation / azimuth speed and acceleration
   - Inner-ring saturation (configurable) suppresses the zenith singularity

## Features

- Observatory presets: Lenghu, Mauna Kea, La Palma, Cerro Pachon, Las Campanas,
  Paranal, La Silla, Sutherland, Siding Spring, or custom latitude
- Configurable Az/Alt range, HA time spacing, Dec spacing
- Configurable zenith range + inner mask + adaptive saturation
- Export as **SVG**, **PDF**, or **PNG** (300 dpi)

## Formulas

Azimuth N-through-E, 0-360°. Sidereal rate ω = 15.04107 arcsec/s.

| Quantity | Formula |
|---|---|
| Declination | sin(Dec) = sin(Alt)sin(φ) + cos(Alt)cos(φ)cos(Az) |
| Hour Angle | tan(HA) = −sin(Az) / [tan(Alt)cos(φ) − sin(φ)cos(Az)] |
| Parallactic Angle | tan(q) = sin(HA)cos(φ) / [cos(Dec)sin(φ) − sin(Dec)cos(φ)cos(HA)] |
| Field Rotation Speed | dq/dt = −cos(φ)cos(Az)/cos(Alt) × ω |
| Azimuth Drive Speed | dA/dt = [sin(φ) − tan(E)cos(φ)cos(A)] × ω |
| Elevation Drive Speed | dE/dt = cos(φ)sin(A) × ω |
| Azimuth Drive Accel | d²A/dt² = sin(A)cos(φ)·[tan(E)sin(φ) − cos(A)cos(φ)(tan²E + sec²E)] × ω² |
| Elevation Drive Accel | d²E/dt² = cos(A)cos(φ)·[sin(φ) − cos(A)cos(φ)tan(E)] × ω² |

### Polar plot colour handling

The zenith polar view uses adaptive colorbar scaling:
- **Bipolar quantities** (dE/dt, dA/dt, d²A/dt²) are centered at zero via `TwoSlopeNorm`.
- **Mono-signed quantities** (d²E/dt², which is nearly always negative near zenith)
  use their natural asymmetric range — symmetrizing would waste half the colorbar.
- For quantities that diverge at zenith (dA/dt, d²A/dt², d²E/dt²), the inner
  ring (radius = zenith_max / 10) is saturated to the percentile range computed
  from the outer annulus, so the singularity doesn't dominate the scale.

## Deploy to Hugging Face Spaces via GitHub

Every push to `main` on GitHub automatically syncs to HF Spaces via a GitHub Action.

### One-time setup

1. **Create a Hugging Face token**
   - Go to https://huggingface.co/settings/tokens
   - Click **Create new token**
   - Choose **Write** access (required to push to Spaces)
   - Copy the token

2. **Add the token to your GitHub repo**
   - Go to your repo **Settings** → **Secrets and variables** → **Actions**
   - Click **New repository secret**
   - Name: `HF_TOKEN`
   - Value: paste the token from step 1
   - Click **Add secret**

3. **Push to deploy** — every `git push origin main` will:
   - Trigger `.github/workflows/sync-to-hf.yml`
   - Mirror the repo to HF Spaces
   - HF builds and serves the Streamlit app automatically

### Verify

After pushing, check:
- GitHub Actions tab → "Sync to Hugging Face Spaces" workflow should show green
- App live https://huggingface.co/spaces/zhuoxiaowang/field-rotation-calculator

## Run Locally

```bash
pip install numpy matplotlib streamlit
streamlit run app.py
```
