import streamlit as st
# import numpy as np
# from scipy.interpolate import griddata
# import pandas as pd
# import matplotlib.pyplot as plt
# from plotly import graph_objs as go
# import welleng as we
import folium
from streamlit_folium import folium_static
# # import ee
# # import geemap.eefolium as geemap


def app():

    st.markdown('# Viewer')

    viewer_params, viewer_plot = st.beta_columns(
        (1, 4))

    with viewer_params:
        viewer_Mode = ['Map View', '3D View']

    with viewer_plot:

        m = folium.Map(location=[8.3426, -73.6827],
                       zoom_start=13, tiles="cartodbpositron")

        # m = folium.Map(tiles="cartodbpositron")

        folium.CircleMarker(
            location=[8.33351075, -73.70513353],
            popup="Aguachica-2",
            radius=10,
            color="#3186cc",
            fill=True,
            fill_color="#3186cc"
        ).add_to(m)

        folium.CircleMarker(
            location=[8.33494223, -73.67233715],
            popup="Crisol-1",
            radius=10,
            color="#3186cc",
            fill=True,
            fill_color="#3186cc"
        ).add_to(m)

        folium.CircleMarker(
            location=[8.32586938, -73.68280489],
            popup="Crisol-2",
            radius=10,
            color="#3186cc",
            fill=True,
            fill_color="#3186cc"
        ).add_to(m)

        folium.CircleMarker(
            location=[8.35850098, -73.65913566],
            popup="Crisol-3",
            radius=10,
            color="#3186cc",
            fill=True,
            fill_color="#3186cc"
        ).add_to(m)

        folium.CircleMarker(
            location=[8.35838529, -73.67842751],
            popup="Norean-1",
            radius=10,
            color="#3186cc",
            fill=True,
            fill_color="#3186cc"
        ).add_to(m)

        folium.CircleMarker(
            location=[8.33577781, -73.70499465],
            popup="Pital-1",
            radius=10,
            color="#3186cc",
            fill=True,
            fill_color="#3186cc"
        ).add_to(m)

        folium.CircleMarker(
            location=[8.36888915, -73.6397439],
            popup="Eucalipto-1",
            radius=10,
            color="#3186cc",
            fill=True,
            fill_color="#3186cc"
        ).add_to(m)

        folium.CircleMarker(
            location=[8.34412715, -73.69961458],
            popup="Reposo-1",
            radius=10,
            color="#3186cc",
            fill=True,
            fill_color="#3186cc"
        ).add_to(m)

        folium.CircleMarker(
            location=[8.32381737, -73.66540851],
            popup="Toposi-2",
            radius=10,
            color="#3186cc",
            fill=True,
            fill_color="#3186cc"
        ).add_to(m)

        folium.CircleMarker(
            location=[8.33315358, -73.67215507],
            popup="Caramelo-2",
            radius=10,
            color="#3186cc",
            fill=True,
            fill_color="#3186cc"
        ).add_to(m)

        folium.CircleMarker(
            location=[8.33309645, -73.67208214],
            popup="Caramelo-1",
            radius=10,
            color="#3186cc",
            fill=True,
            fill_color="#3186cc"
        ).add_to(m)

        folium.CircleMarker(
            location=[8.33292278, -73.67201223],
            popup="Caramelo-3",
            radius=10,
            color="#3186cc",
            fill=True,
            fill_color="#3186cc"
        ).add_to(m)

        folium.CircleMarker(
            location=[8.33288558, -73.6719726],
            popup="Caramelo-5",
            radius=10,
            color="#3186cc",
            fill=True,
            fill_color="#3186cc"
        ).add_to(m)

        folium.CircleMarker(
            location=[8.35597644, -73.68249159],
            popup="Norean-1",
            radius=10,
            color="#3186cc",
            fill=True,
            fill_color="#3186cc"
        ).add_to(m)

        folium.CircleMarker(
            location=[8.34973363, -73.65764591],
            popup="Preludio-1",
            radius=10,
            color="#3186cc",
            fill=True,
            fill_color="#3186cc"
        ).add_to(m)

        folium.CircleMarker(
            location=[8.34545998, -73.66178435],
            popup="La Estancia-1",
            radius=10,
            color="#3186cc",
            fill=True,
            fill_color="#3186cc"
        ).add_to(m)

        folium.CircleMarker(
            location=[8.34545998, -73.66178435],
            popup="La Estancia-1",
            radius=10,
            color="#3186cc",
            fill=True,
            fill_color="#3186cc"
        ).add_to(m)

        folium.CircleMarker(
            location=[8.34022764, -73.65030377],
            popup="Bandera-1",
            radius=10,
            color="#3186cc",
            fill=True,
            fill_color="#3186cc"
        ).add_to(m)

        m.add_child(folium.LatLngPopup())

        ANHMapaTierras = 'data/surfaces/shapeFiles/Tierras_2021_06_01.json'
        ANHSeismic = 'data/surfaces/shapeFiles/Sísmica_3D.json'

        folium.GeoJson(ANHMapaTierras, name="ANH Mapa de Tierras").add_to(m)
        folium.GeoJson(ANHSeismic, name="ANH 3D Seismic").add_to(m)

        # folium.TopoJson(
        #     json.loads(requests.get(VMM-1_TopoJson).text),
        #     "objects.antarctic_ice_shelf",
        #     name="topojson",
        # ).add_to(m)

        folium.LayerControl().add_to(m)

        folium_static(m, width=1400, height=700)
