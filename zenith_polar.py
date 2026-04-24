"""
Zenith polar sub-page — elevation & azimuth speeds / accelerations
plotted in polar coordinates around the zenith.
"""

import io
import streamlit as st
import matplotlib
matplotlib.use('Agg')

from field_rotation import make_zenith_polar_plot

SITES = {
    'Lenghu':        38.6165,
    'Mauna Kea':     19.8208,
    'La Palma':      28.7606,
    'Cerro Pachón': -30.2408,
    'Las Campanas':  -29.0146,
    'Paranal':      -24.6272,
    'La Silla':     -29.2567,
    'Sutherland':   -32.3792,
    'Siding Spring': -31.2754,
    'Custom':        None,
}

ALL_QUANTS = {
    'alt_speed': 'Elevation Speed (″/s)',
    'az_speed':  'Azimuth Speed (″/s)',
    'alt_accel': 'Elevation Accel (″/s²)',
    'az_accel':  'Azimuth Accel (″/s²)',
}

st.title('Zenith Polar View — Elevation & Azimuth Motion')

with st.sidebar:
    st.header('Site')
    site_name = st.selectbox('Observatory', list(SITES.keys()))
    if SITES[site_name] is not None:
        lat = st.number_input('Latitude (°)', value=SITES[site_name],
                              format='%.4f', disabled=True)
    else:
        lat = st.number_input('Latitude (°)', value=0.0, format='%.4f',
                              min_value=-90.0, max_value=90.0, step=0.01)

    st.header('Zenith Range')
    c1, c2 = st.columns(2)
    mask_inner = c1.number_input('Mask inner (°)', value=0.0,
                                 min_value=0.0, max_value=30.0, step=0.5)
    zen_max = c2.number_input('Zenith max (°)', value=5.0,
                              min_value=1.0, max_value=60.0, step=1.0)

    st.header('Panels')
    chosen = st.multiselect(
        'Quantities to show',
        list(ALL_QUANTS.keys()),
        default=list(ALL_QUANTS.keys()),
        format_func=lambda k: ALL_QUANTS[k],
    )

if not chosen:
    st.warning('Select at least one quantity to plot.')
    st.stop()

fig = make_zenith_polar_plot(
    lat=lat,
    zenith_range=(0, zen_max),
    mask_inner=mask_inner,
    quantities=tuple(chosen),
)
st.pyplot(fig)

# ---- downloads ----
tag = site_name.lower().replace(' ', '').replace('ó', 'o')
basename = (f'zenithpolar_{tag}'
            f'_zen0to{int(zen_max)}_mask{mask_inner:.1f}')

col_svg, col_pdf, col_png = st.columns(3)
buf_svg = io.BytesIO()
fig.savefig(buf_svg, format='svg', bbox_inches='tight', pad_inches=0.2)
col_svg.download_button('Download SVG', buf_svg.getvalue(),
                        file_name=f'{basename}.svg', mime='image/svg+xml')

buf_pdf = io.BytesIO()
fig.savefig(buf_pdf, format='pdf', bbox_inches='tight', pad_inches=0.2)
col_pdf.download_button('Download PDF', buf_pdf.getvalue(),
                        file_name=f'{basename}.pdf', mime='application/pdf')

buf_png = io.BytesIO()
fig.savefig(buf_png, format='png', dpi=300, bbox_inches='tight', pad_inches=0.2)
col_png.download_button('Download PNG', buf_png.getvalue(),
                        file_name=f'{basename}.png', mime='image/png')

st.caption(
    'Polar radius = zenith angle (°); angular = azimuth (N at top, '
    'clockwise through E/S/W). Inner mask hides the near-zenith singularity.'
)
