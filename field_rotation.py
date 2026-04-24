"""
Alt-Az Telescope Field Rotation Calculator — core module.

Computes (in arcsec/s and arcsec/s²):
    - field rotation speed dq/dt and parallactic angle q
    - azimuth & altitude drive speeds dA/dt, dE/dt
    - azimuth & altitude drive accelerations d²A/dt², d²E/dt²

Azimuth is measured N-through-E (0-360°).
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

SIDEREAL_RATE = 15.04107  # arcsec/s  (360° / 23 h 56 m 4.1 s)
_OMEGA2_ARCSEC = SIDEREAL_RATE ** 2 * np.pi / (180 * 3600)  # factor for accel


# ---------------------------------------------------------------------------
# Coordinate transforms
# ---------------------------------------------------------------------------

def az_alt_to_hadec(az, alt, lat):
    """(Az, Alt, latitude) in degrees → (HA, Dec) in degrees."""
    a, e, phi = np.radians(az), np.radians(alt), np.radians(lat)
    sin_dec = np.sin(e) * np.sin(phi) + np.cos(e) * np.cos(phi) * np.cos(a)
    dec = np.arcsin(np.clip(sin_dec, -1, 1))
    ha = np.arctan2(-np.sin(a),
                    np.tan(e) * np.cos(phi) - np.sin(phi) * np.cos(a))
    return np.degrees(ha), np.degrees(dec)


# ---------------------------------------------------------------------------
# Speeds
# ---------------------------------------------------------------------------

def rotation_speed(az, alt, lat):
    """Field rotation speed dq/dt in arcsec/s."""
    a, e, phi = np.radians(az), np.radians(alt), np.radians(lat)
    return -np.cos(phi) * np.cos(a) / np.cos(e) * SIDEREAL_RATE


def azimuth_speed(az, alt, lat):
    """Azimuth drive speed dA/dt in arcsec/s."""
    a, e, phi = np.radians(az), np.radians(alt), np.radians(lat)
    return (np.sin(phi) - np.tan(e) * np.cos(phi) * np.cos(a)) * SIDEREAL_RATE


def altitude_speed(az, alt, lat):
    """Altitude drive speed dE/dt in arcsec/s."""
    a, e, phi = np.radians(az), np.radians(alt), np.radians(lat)
    return np.cos(phi) * np.sin(a) * SIDEREAL_RATE


def parallactic_angle(az, alt, lat):
    """Parallactic angle in degrees (full 4-quadrant)."""
    a, e, phi = np.radians(az), np.radians(alt), np.radians(lat)
    ha = np.arctan2(-np.sin(a),
                    np.tan(e) * np.cos(phi) - np.sin(phi) * np.cos(a))
    sin_dec = np.sin(e) * np.sin(phi) + np.cos(e) * np.cos(phi) * np.cos(a)
    dec = np.arcsin(np.clip(sin_dec, -1, 1))
    q = np.arctan2(np.sin(ha) * np.cos(phi),
                   np.cos(dec) * np.sin(phi) -
                   np.sin(dec) * np.cos(phi) * np.cos(ha))
    return np.degrees(q)


# ---------------------------------------------------------------------------
# Accelerations (analytical d²A/dt², d²E/dt² in arcsec/s²)
# ---------------------------------------------------------------------------

def azimuth_accel(az, alt, lat):
    """Azimuth drive acceleration d²A/dt² in arcsec/s²."""
    a, e, phi = np.radians(az), np.radians(alt), np.radians(lat)
    term = np.sin(a) * np.cos(phi) * (
        np.tan(e) * np.sin(phi)
        - np.cos(a) * np.cos(phi) * (np.tan(e) ** 2 + 1.0 / np.cos(e) ** 2)
    )
    return term * _OMEGA2_ARCSEC


def altitude_accel(az, alt, lat):
    """Altitude drive acceleration d²E/dt² in arcsec/s²."""
    a, e, phi = np.radians(az), np.radians(alt), np.radians(lat)
    term = np.cos(a) * np.cos(phi) * (
        np.sin(phi) - np.cos(a) * np.cos(phi) * np.tan(e)
    )
    return term * _OMEGA2_ARCSEC


# ---------------------------------------------------------------------------
# Plotting helpers
# ---------------------------------------------------------------------------

def _ha_label(deg):
    """Format hour-angle degrees as ±Hh MMm."""
    h = deg / 15.0
    sign = '+' if h >= 0 else '-'
    h = abs(h)
    hh, mm = int(h), int(round((h % 1) * 60))
    if mm == 60:
        hh += 1
        mm = 0
    return f'{sign}{hh}h{mm:02d}m'


def _panel(ax, az_1d, alt_1d, Z, HA, Dec, title,
           ha_step_min, dec_step_deg, fmt='%+.1f', cmap='RdBu_r',
           clip=None, fig=None):
    """Draw one Az-Alt contour panel with HA/Dec overlays."""
    if clip is not None:
        Z = np.clip(Z, clip[0], clip[1])

    cf = ax.contourf(az_1d, alt_1d, Z, levels=24, cmap=cmap, alpha=0.85)
    cs = ax.contour(cf, colors='k', linewidths=0.25, alpha=0.35)
    ax.clabel(cs, fmt=fmt, fontsize=7)
    if fig is not None:
        fig.colorbar(cf, ax=ax, label=title, pad=0.02, shrink=0.95)

    # declination lines
    dec_lo, dec_hi = np.nanmin(Dec), np.nanmax(Dec)
    dec_lvl = np.arange(np.ceil(dec_lo / dec_step_deg) * dec_step_deg,
                        dec_hi + 0.1, dec_step_deg)
    if dec_lvl.size:
        cd = ax.contour(az_1d, alt_1d, Dec, levels=dec_lvl,
                        colors='k', linestyles='-', linewidths=0.9, alpha=0.55)
        ax.clabel(cd, fmt={v: f'δ={v:+.0f}°' for v in dec_lvl},
                  fontsize=7, inline_spacing=3)

    # hour-angle lines
    ha_step_deg = ha_step_min / 60.0 * 15.0
    ha_lo, ha_hi = np.nanmin(HA), np.nanmax(HA)
    ha_lvl = np.arange(np.ceil(ha_lo / ha_step_deg) * ha_step_deg,
                       ha_hi + 0.1, ha_step_deg)
    if ha_lvl.size:
        ch = ax.contour(az_1d, alt_1d, HA, levels=ha_lvl,
                        colors='forestgreen', linestyles='--',
                        linewidths=0.65, alpha=0.6)
        ax.clabel(ch, fmt={v: _ha_label(v) for v in ha_lvl},
                  fontsize=7, inline_spacing=3)

    ax.set_title(title, fontsize=12)
    ax.set_xlabel('Azimuth (°)', fontsize=10)
    ax.set_ylabel('Altitude (°)', fontsize=10)
    ax.grid(True, ls='--', alpha=0.15)


# ---------------------------------------------------------------------------
# Public plot builders
# ---------------------------------------------------------------------------

def make_plot(lat=38.6165, az_range=(0, 360), alt_range=(20, 85),
              ha_step_min=15, dec_step_deg=5, quantity='speed', n=500):
    """Single-panel field-rotation contour plot."""
    az_1d = np.linspace(*az_range, n)
    alt_1d = np.linspace(*alt_range, n)
    Az, Alt = np.meshgrid(az_1d, alt_1d)
    HA, Dec = az_alt_to_hadec(Az, Alt, lat)

    if quantity == 'speed':
        Z = rotation_speed(Az, Alt, lat)
        title = 'Field Rotation Speed (arcsec/s)'
        clip = (-360, 360)
    else:
        Z = parallactic_angle(Az, Alt, lat)
        title = 'Parallactic Angle (°)'
        clip = None

    fig, ax = plt.subplots(figsize=(14, 6))
    _panel(ax, az_1d, alt_1d, Z, HA, Dec, title=title,
           ha_step_min=ha_step_min, dec_step_deg=dec_step_deg,
           clip=clip, fig=fig)
    ax.set_title(f'{title}   (φ = {lat:.4f}°)', fontsize=13)
    fig.tight_layout()
    return fig


def make_stack_plot(lat=38.6165, az_range=(0, 360), alt_range=(20, 85),
                    ha_step_min=15, dec_step_deg=5,
                    fr_quantity='speed', n=500):
    """Three stacked panels: field rotation, alt speed, az speed."""
    az_1d = np.linspace(*az_range, n)
    alt_1d = np.linspace(*alt_range, n)
    Az, Alt = np.meshgrid(az_1d, alt_1d)
    HA, Dec = az_alt_to_hadec(Az, Alt, lat)

    if fr_quantity == 'speed':
        Z_fr = rotation_speed(Az, Alt, lat)
        fr_title = 'Field Rotation Speed (arcsec/s)'
        fr_clip = (-360, 360)
    else:
        Z_fr = parallactic_angle(Az, Alt, lat)
        fr_title = 'Parallactic Angle (°)'
        fr_clip = None

    Z_alt = altitude_speed(Az, Alt, lat)
    Z_az = azimuth_speed(Az, Alt, lat)

    fig, axes = plt.subplots(3, 1, figsize=(13, 16))
    _panel(axes[0], az_1d, alt_1d, Z_fr, HA, Dec, title=fr_title,
           ha_step_min=ha_step_min, dec_step_deg=dec_step_deg,
           clip=fr_clip, fig=fig)
    _panel(axes[1], az_1d, alt_1d, Z_alt, HA, Dec,
           title='Elevation Angular Velocity (arcsec/s)',
           ha_step_min=ha_step_min, dec_step_deg=dec_step_deg, fig=fig)
    _panel(axes[2], az_1d, alt_1d, Z_az, HA, Dec,
           title='Azimuth Angular Velocity (arcsec/s)',
           ha_step_min=ha_step_min, dec_step_deg=dec_step_deg,
           clip=(-360, 360), fig=fig)

    fig.suptitle(
        rf'$\mathbf{{Alt\!-\!Az\ Telescope\ Tracking\ Specs,\ '
        rf'for\ latitude\ \phi = {lat:.4f}^\circ}}$',
        fontsize=14, y=0.998,
    )
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Polar (zenith) plot
# ---------------------------------------------------------------------------

_POLAR_QUANTITIES = {
    'alt_speed': ('Elevation Angular Velocity (arcsec/s)', altitude_speed),
    'az_speed':  ('Azimuth Angular Velocity (arcsec/s)',  azimuth_speed),
    'alt_accel': ('Elevation Angular Acceleration (arcsec/s²)', altitude_accel),
    'az_accel':  ('Azimuth Angular Acceleration (arcsec/s²)',  azimuth_accel),
}


def _polar_panel(ax, Az_rad, Z, R_zen, title, mask_inner=0.0,
                 cmap='RdBu_r', fig=None, percentile=(2, 98), n_levels=60,
                 saturate_inner=None):
    """Draw one polar panel (zenith angle radial, az angular).

    Uses adaptive percentile clipping so near-zenith divergences
    don't blow out the colorbar.

    If `saturate_inner` is given, the colorbar range is derived from values
    OUTSIDE that zenith radius, and values inside are clipped to that range
    (producing solid-colour saturation rather than blown-out extremes).
    """
    Z = Z.copy()

    # Adaptive percentile range. If saturate_inner set, base it on the
    # outer annulus so the near-zenith singularity doesn't dominate.
    if saturate_inner and saturate_inner > 0:
        outer = R_zen >= saturate_inner
        vlo = np.nanpercentile(Z[outer], percentile[0])
        vhi = np.nanpercentile(Z[outer], percentile[1])
    else:
        vlo = np.nanpercentile(Z, percentile[0])
        vhi = np.nanpercentile(Z, percentile[1])
    if vlo == vhi:
        vlo, vhi = vlo - 1, vhi + 1

    if mask_inner > 0:
        Z = np.where(R_zen < mask_inner, np.nan, Z)

    # Saturate the inner ring to the outer colorbar range
    if saturate_inner and saturate_inner > 0:
        inner = R_zen < saturate_inner
        Z = np.where(inner & ~np.isnan(Z), np.clip(Z, vlo, vhi), Z)

    # Center diverging colormap at zero only if data is genuinely bipolar.
    # Mono-signed quantities (e.g. elevation acceleration near zenith) must
    # keep their asymmetric range so the full dynamic range is visible.
    if vlo < 0 < vhi:
        norm = TwoSlopeNorm(vmin=vlo, vcenter=0.0, vmax=vhi)
    else:
        norm = None

    levels = np.linspace(vlo, vhi, n_levels)
    cf = ax.contourf(Az_rad, R_zen, Z, levels=levels, cmap=cmap, norm=norm,
                     extend='both', antialiased=True)
    if fig is not None:
        cbar = fig.colorbar(cf, ax=ax, orientation='vertical',
                            pad=0.12, shrink=0.9)
        cbar.ax.tick_params(labelsize=8)
        # sparse ticks for readability
        cbar.set_ticks(np.linspace(vlo, vhi, 9))

    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)   # clockwise (N → E → S → W)
    ax.set_xticks(np.radians([0, 90, 180, 270]))
    ax.set_xticklabels(['N', 'E', 'S', 'W'], fontsize=9)
    ax.set_title(title, fontsize=11, pad=14)
    ax.grid(True, alpha=0.4)


def make_zenith_polar_plot(lat=38.6165, zenith_range=(0, 5), mask_inner=0.5,
                           quantities=('alt_speed', 'az_speed',
                                       'alt_accel', 'az_accel'),
                           n=400, percentile=(2, 98), n_levels=60):
    """
    Polar plot around zenith — up to 4 panels (speeds and accelerations).

    Parameters
    ----------
    lat : float         Geographic latitude (°)
    zenith_range : (zmin, zmax)  radial range in zenith angle (°)
    mask_inner : float  Blank out zenith angle < this (°), to hide singularity
    quantities : tuple  Subset of _POLAR_QUANTITIES keys (up to 4)
    n : int             Grid resolution per axis
    """
    z_min, z_max = zenith_range
    # convert zenith → altitude grid
    alt_1d = np.linspace(90 - z_max, 90 - max(z_min, 0.01), n)
    az_1d = np.linspace(0, 360, n)
    Az_rad, Alt_deg = np.meshgrid(np.radians(az_1d), alt_1d)
    Az_deg = np.degrees(Az_rad)
    R_zen = 90 - Alt_deg   # radial coord in degrees

    n_panels = len(quantities)
    ncols = 2 if n_panels > 1 else 1
    nrows = int(np.ceil(n_panels / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(7 * ncols, 6 * nrows),
                             subplot_kw={'projection': 'polar'})
    axes = np.atleast_1d(axes).ravel()

    # Elevation speed is bounded (±ω·cos φ); the others diverge at zenith
    # and benefit from saturating the innermost ring of the polar view.
    sat_radius = z_max / 10.0
    diverging = {'az_speed', 'az_accel', 'alt_accel'}

    for ax, qkey in zip(axes, quantities):
        title, func = _POLAR_QUANTITIES[qkey]
        Z = func(Az_deg, Alt_deg, lat)
        sat = sat_radius if qkey in diverging else None
        _polar_panel(ax, Az_rad, Z, R_zen, title=title,
                     mask_inner=mask_inner, fig=fig,
                     percentile=percentile, n_levels=n_levels,
                     saturate_inner=sat)
        ax.set_ylim(z_min, z_max)

    # hide any unused axes
    for ax in axes[n_panels:]:
        ax.set_visible(False)

    fig.suptitle(f'Zenith Polar View — φ = {lat:.4f}°,  '
                 f'zenith {z_min:.1f}°–{z_max:.1f}°,  '
                 f'inner mask = {mask_inner:.1f}°',
                 fontsize=13)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    fig = make_stack_plot()
    plt.show()
