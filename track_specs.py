"""
Az-Alt Track Specs — main page.
Three stacked panels: field rotation, elevation speed, azimuth speed.
"""

import io
import streamlit as st
import matplotlib
matplotlib.use('Agg')

from field_rotation import make_stack_plot

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

st.title('Alt-Az Telescope — Tracking Specs')

# ---- sidebar controls ----
with st.sidebar:
    st.header('Site')
    site_name = st.selectbox('Observatory', list(SITES.keys()))
    if SITES[site_name] is not None:
        lat = st.number_input('Latitude (°)', value=SITES[site_name],
                              format='%.4f', disabled=True)
    else:
        lat = st.number_input('Latitude (°)', value=0.0, format='%.4f',
                              min_value=-90.0, max_value=90.0, step=0.01)

    st.header('Sky Range')
    c1, c2 = st.columns(2)
    az_min = c1.number_input('Az min (°)', value=0.0,
                             min_value=0.0, max_value=360.0, step=5.0)
    az_max = c2.number_input('Az max (°)', value=360.0,
                             min_value=0.0, max_value=360.0, step=5.0)
    c3, c4 = st.columns(2)
    alt_min = c3.number_input('Alt min (°)', value=20.0,
                              min_value=0.0, max_value=89.0, step=5.0)
    alt_max = c4.number_input('Alt max (°)', value=85.0,
                              min_value=1.0, max_value=90.0, step=5.0)

    st.header('Grid Lines')
    ha_step = st.slider('HA spacing (min)', 5, 60, 15, 5)
    dec_step = st.slider('Dec spacing (°)', 1, 20, 5)

    st.header('Field Rotation Display')
    fr_quantity = st.radio(
        'Quantity (top panel)',
        ['speed', 'angle'],
        format_func=lambda x: ('Rotation Speed (″/s)' if x == 'speed'
                               else 'Parallactic Angle (°)'),
        horizontal=True,
    )

# ---- generate plot ----
fig = make_stack_plot(
    lat=lat,
    az_range=(az_min, az_max),
    alt_range=(alt_min, alt_max),
    ha_step_min=ha_step,
    dec_step_deg=dec_step,
    fr_quantity=fr_quantity,
)
st.pyplot(fig)

# ---- download buttons ----
tag = site_name.lower().replace(' ', '').replace('ó', 'o')
basename = (f'fieldrotation_{tag}'
            f'_az_{int(az_min)}to{int(az_max)}'
            f'_alt_{int(alt_min)}to{int(alt_max)}'
            f'_ha{int(ha_step)}_dec{int(dec_step)}_{fr_quantity}')

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

# ---- legend ----
st.caption(
    '**Top**: field rotation (speed or parallactic angle)  ·  '
    '**Middle**: elevation drive rate dE/dt  ·  '
    '**Bottom**: azimuth drive rate dA/dt  ·  '
    'Black solid = Dec lines, green dashed = HA lines'
)
