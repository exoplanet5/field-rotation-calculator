"""
Alt-Az Telescope Field Rotation Calculator

Computes parallactic angle and field rotation speed over an azimuth-altitude
grid, with overlaid hour-angle and declination contour lines.

Spherical astronomy (azimuth measured N-through-E, 0-360):
    sin(Dec) = sin(Alt)sin(φ) + cos(Alt)cos(φ)cos(Az)
    tan(HA)  = -sin(Az) / [tan(Alt)cos(φ) - sin(φ)cos(Az)]
    sin(q)   = sin(HA)cos(φ) / cos(Alt)          [parallactic angle]
    dq/dt    = -cos(φ)cos(Az) / cos(Alt) × ω_sid [rotation speed]
"""

import numpy as np
import matplotlib.pyplot as plt

SIDEREAL_RATE = 15.04107  # arcsec/s  (360° / 23h 56m 4.1s)


# ---------------------------------------------------------------------------
# Core transforms
# ---------------------------------------------------------------------------

def az_alt_to_hadec(az, alt, lat):
    """(Az, Alt, latitude) in degrees → (HA, Dec) in degrees."""
    a, e, phi = np.radians(az), np.radians(alt), np.radians(lat)
    sin_dec = np.sin(e) * np.sin(phi) + np.cos(e) * np.cos(phi) * np.cos(a)
    dec = np.arcsin(np.clip(sin_dec, -1, 1))
    ha = np.arctan2(-np.sin(a),
                    np.tan(e) * np.cos(phi) - np.sin(phi) * np.cos(a))
    return np.degrees(ha), np.degrees(dec)


def rotation_speed(az, alt, lat):
    """Field de-rotation speed in arcsec/s."""
    a, e, phi = np.radians(az), np.radians(alt), np.radians(lat)
    return -np.cos(phi) * np.cos(a) / np.cos(e) * SIDEREAL_RATE


def parallactic_angle(az, alt, lat):
    """Parallactic angle in degrees (full four-quadrant)."""
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
# Plotting
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


def make_plot(lat=38.6165, az_range=(0, 360), alt_range=(20, 85),
              ha_step_min=15, dec_step_deg=5,
              quantity='speed', n=500):
    """
    Build the field rotation contour plot.

    Parameters
    ----------
    lat          : float   Geographic latitude (deg)
    az_range     : tuple   Azimuth limits (deg)
    alt_range    : tuple   Altitude limits (deg)
    ha_step_min  : float   Hour-angle grid spacing (minutes of time)
    dec_step_deg : float   Declination grid spacing (deg)
    quantity     : str     'speed' | 'angle'
    n            : int     Grid resolution per axis

    Returns
    -------
    matplotlib.figure.Figure
    """
    az_1d = np.linspace(*az_range, n)
    alt_1d = np.linspace(*alt_range, n)
    Az, Alt = np.meshgrid(az_1d, alt_1d)

    HA, Dec = az_alt_to_hadec(Az, Alt, lat)

    # Quantity to contour
    if quantity == 'speed':
        Z = np.clip(rotation_speed(Az, Alt, lat), -360, 360)
        title = 'Field Rotation Speed (arcsec/s)'
        fmt = '%+.1f'
    else:
        Z = parallactic_angle(Az, Alt, lat)
        title = 'Parallactic Angle (°)'
        fmt = '%+.0f'

    fig, ax = plt.subplots(figsize=(14, 6))

    # --- main filled contour ---
    cf = ax.contourf(az_1d, alt_1d, Z, levels=24, cmap='RdBu_r', alpha=0.85)
    cs = ax.contour(cf, colors='k', linewidths=0.25, alpha=0.35)
    ax.clabel(cs, fmt=fmt, fontsize=7)
    fig.colorbar(cf, ax=ax, label=title, pad=0.02, shrink=0.95)

    # --- declination lines (solid black) ---
    dec_lo, dec_hi = np.nanmin(Dec), np.nanmax(Dec)
    dec_lvl = np.arange(np.ceil(dec_lo / dec_step_deg) * dec_step_deg,
                        dec_hi + 0.1, dec_step_deg)
    if dec_lvl.size:
        cd = ax.contour(az_1d, alt_1d, Dec, levels=dec_lvl,
                        colors='k', linestyles='-', linewidths=0.9, alpha=0.55)
        dec_labels = {v: f'δ={v:+.0f}°' for v in dec_lvl}
        ax.clabel(cd, fmt=dec_labels, fontsize=7, inline_spacing=3)

    # --- hour-angle lines (dashed green) ---
    ha_step_deg = ha_step_min / 60.0 * 15.0
    ha_lo, ha_hi = np.nanmin(HA), np.nanmax(HA)
    ha_lvl = np.arange(np.ceil(ha_lo / ha_step_deg) * ha_step_deg,
                       ha_hi + 0.1, ha_step_deg)
    if ha_lvl.size:
        ch = ax.contour(az_1d, alt_1d, HA, levels=ha_lvl,
                        colors='forestgreen', linestyles='--',
                        linewidths=0.65, alpha=0.6)
        ha_labels = {v: _ha_label(v) for v in ha_lvl}
        ax.clabel(ch, fmt=ha_labels, fontsize=7, inline_spacing=3)

    ax.set_title(f'{title}   (φ = {lat:.4f}°)', fontsize=13)
    ax.set_xlabel('Azimuth (°)', fontsize=11)
    ax.set_ylabel('Altitude (°)', fontsize=11)
    ax.grid(True, ls='--', alpha=0.15)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    fig = make_plot()
    plt.show()
