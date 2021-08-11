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
        viewer_Mode = ['Map View', 'Bubble Map - Time Line', '3D View']

        viewerMode = viewer_params.radio('Mode', viewer_Mode)

        if viewerMode == 'Map View':

            mapSettingExpander = viewer_params.expander('Map Settings')

            zoom = mapSettingExpander.slider('Map Zoom:',
                                             min_value=0, value=13, max_value=20)

            m = folium.Map(location=[8.3426, -73.6827],
                           zoom_start=zoom, tiles="cartodbpositron")

            showObject = viewer_params.multiselect(
                'Object', ['Wells', 'Seismic Polygon', 'Surfaces'], default=['Wells', 'Seismic Polygon'])

            if 'Wells' in showObject:

                viewer_params.markdown('#### Wells')

                wellsSettingExpander = viewer_params.expander(
                    'Well Settings')

                radius = wellsSettingExpander.slider('Radius:',
                                                     min_value=0, value=10, max_value=20)

                color = wellsSettingExpander.color_picker('Color:', '#00f900')

                fill = wellsSettingExpander.radio('Fill:', [True, False])

                wellList = ['Aguachica-2', 'Crisol-1', 'Crisol-2', 'Crisol-3', 'Norean-1', 'Pital-1', 'Eucalipto-1',
                            'Reposo-1', 'Toposi-2', 'Caramelo-1', 'Caramelo-2', 'Caramelo-3', 'Caramelo-5', 'Preludio-1', 'La Estancia-1', 'Bandera-1']

                wells = st.multiselect(
                    'Wells:', wellList, default=wellList)

                if 'Aguachica-2' in wells:

                    folium.CircleMarker(
                        location=[8.33351075, -73.70513353],
                        popup="Aguachica-2",
                        radius=radius,
                        color=color,
                        fill=fill,
                        fill_color=fill
                    ).add_to(m)

                if 'Crisol-1' in wells:
                    folium.CircleMarker(
                        location=[8.33494223, -73.67233715],
                        popup="Crisol-1",
                        radius=radius,
                        color=color,
                        fill=fill,
                        fill_color=fill
                    ).add_to(m)

                if 'Crisol-2' in wells:
                    folium.CircleMarker(
                        location=[8.32586938, -73.68280489],
                        popup="Crisol-2",
                        radius=radius,
                        color=color,
                        fill=fill,
                        fill_color=fill
                    ).add_to(m)

                if 'Crisol-3' in wells:
                    folium.CircleMarker(
                        location=[8.35850098, -73.65913566],
                        popup="Crisol-3",
                        radius=radius,
                        color=color,
                        fill=fill,
                        fill_color=fill
                    ).add_to(m)

                if 'Norean-1' in wells:
                    folium.CircleMarker(
                        location=[8.35838529, -73.67842751],
                        popup="Norean-1",
                        radius=radius,
                        color=color,
                        fill=fill,
                        fill_color=fill
                    ).add_to(m)

                if 'Pital-1' in wells:
                    folium.CircleMarker(
                        location=[8.33577781, -73.70499465],
                        popup="Pital-1",
                        radius=radius,
                        color=color,
                        fill=fill,
                        fill_color=fill
                    ).add_to(m)

                if 'Eucalipto-1' in wells:
                    folium.CircleMarker(
                        location=[8.36888915, -73.6397439],
                        popup="Eucalipto-1",
                        radius=radius,
                        color=color,
                        fill=fill,
                        fill_color=fill
                    ).add_to(m)

                if 'Reposo-1' in wells:
                    folium.CircleMarker(
                        location=[8.34412715, -73.69961458],
                        popup="Reposo-1",
                        radius=radius,
                        color=color,
                        fill=fill,
                        fill_color=fill
                    ).add_to(m)

                if 'Toposi-2' in wells:
                    folium.CircleMarker(
                        location=[8.32381737, -73.66540851],
                        popup="Toposi-2",
                        radius=radius,
                        color=color,
                        fill=fill,
                        fill_color=fill
                    ).add_to(m)

                if 'Caramelo-2' in wells:
                    folium.CircleMarker(
                        location=[8.33315358, -73.67215507],
                        popup="Caramelo-2",
                        radius=radius,
                        color=color,
                        fill=fill,
                        fill_color=fill
                    ).add_to(m)

                if 'Caramelo-1' in wells:
                    folium.CircleMarker(
                        location=[8.33309645, -73.67208214],
                        popup="Caramelo-1",
                        radius=radius,
                        color=color,
                        fill=fill,
                        fill_color=fill
                    ).add_to(m)

                if 'Caramelo-3' in wells:
                    folium.CircleMarker(
                        location=[8.33292278, -73.67201223],
                        popup="Caramelo-3",
                        radius=radius,
                        color=color,
                        fill=fill,
                        fill_color=fill
                    ).add_to(m)

                if 'Caramelo-5' in wells:
                    folium.CircleMarker(
                        location=[8.33288558, -73.6719726],
                        popup="Caramelo-5",
                        radius=radius,
                        color=color,
                        fill=fill,
                        fill_color=fill
                    ).add_to(m)

                if 'Preludio-1' in wells:
                    folium.CircleMarker(
                        location=[8.34973363, -73.65764591],
                        popup="Preludio-1",
                        radius=radius,
                        color=color,
                        fill=fill,
                        fill_color=fill
                    ).add_to(m)

                if 'La Estancia-1' in wells:
                    folium.CircleMarker(
                        location=[8.34545998, -73.66178435],
                        popup="La Estancia-1",
                        radius=radius,
                        color=color,
                        fill=fill,
                        fill_color=fill
                    ).add_to(m)

                if 'Bandera-1' in wells:
                    folium.CircleMarker(
                        location=[8.34022764, -73.65030377],
                        popup="Bandera-1",
                        radius=radius,
                        color=color,
                        fill=fill,
                        fill_color=fill
                    ).add_to(m)

            if 'Seismic Polygon' in showObject:
                viewer_params.markdown('#### Polygons')

                polygonSettingExpander = viewer_params.expander(
                    'Polygon Settings')

                pColor = polygonSettingExpander.color_picker(
                    'Polygon Color:', '#F90000')

                line_opacity = polygonSettingExpander.slider('Line Opacity:',
                                                             min_value=0.0, value=0.5, max_value=1.0)

                pFillColor = polygonSettingExpander.color_picker(
                    'Polygon Fill Color:', '#F90000')

                fill_opacity = polygonSettingExpander.slider('Fill Opacity:',
                                                             min_value=0.0, value=0.1, max_value=1.0)

                ANHSeismic = 'data/surfaces/shapeFiles/Sísmica_3D.json'

                style = {'fillColor': pFillColor,
                         'color': pColor, 'opacity': line_opacity, 'fillOpacity': fill_opacity}

                folium.GeoJson(ANHSeismic,
                               name="ANH 3D Seismic",
                               style_function=lambda x: style).add_to(m).add_to(m)

            if 'Surfaces' in showObject:
                viewer_params.markdown('#### Surfaces')

                surfacesSettingExpander = viewer_params.expander(
                    'Surface Settings')

                opacity = surfacesSettingExpander.slider('Surface Opacity:',
                                                         min_value=0.0, value=0.6, max_value=1.0)

                surfaces = viewer_params.multiselect('Surfaces:', [
                    'Real', 'Unconformity', 'La Luna', 'El Salto', 'Tablazo', 'Rosa Blanca', 'Rosa Blanca (Thin)'])

                if 'Real' in surfaces:

                    Real = r'data/surfaces/Real.png'

                    img_Real = folium.raster_layers.ImageOverlay(
                        name="Real",
                        image=Real,
                        bounds=[[8.247096, -73.748204],
                                [8.421736, -73.584173]],
                        opacity=opacity,
                        interactive=True,
                        cross_origin=False,
                        zindex=1)

                    img_Real.add_to(m)

                if 'Unconformity' in surfaces:

                    Unconformity = r'data/surfaces/unconformity.png'

                    img_Unconformity = folium.raster_layers.ImageOverlay(
                        name="Unconformity",
                        image=Unconformity,
                        bounds=[[8.247096, -73.748204],
                                [8.421736, -73.584173]],
                        opacity=opacity,
                        interactive=True,
                        cross_origin=False,
                        zindex=1)

                    img_Unconformity.add_to(m)

                if 'La Luna' in surfaces:

                    LaLuna = r'data/surfaces/LaLuna.png'

                    img_LaLuna = folium.raster_layers.ImageOverlay(
                        name="La Luna",
                        image=LaLuna,
                        bounds=[[8.247096, -73.748204],
                                [8.421736, -73.584173]],
                        opacity=opacity,
                        interactive=True,
                        cross_origin=False,
                        zindex=1)

                    img_LaLuna.add_to(m)

                if 'El Salto' in surfaces:

                    ElSalto = r'data/surfaces/ElSalto.png'

                    img_ElSalto = folium.raster_layers.ImageOverlay(
                        name="El Salto",
                        image=ElSalto,
                        bounds=[[8.247096, -73.748204],
                                [8.421736, -73.584173]],
                        opacity=opacity,
                        interactive=True,
                        cross_origin=False,
                        zindex=1)

                    img_ElSalto.add_to(m)

                if 'Tablazo' in surfaces:

                    Tablazo = r'data/surfaces/Tablazo.png'

                    img_Tablazo = folium.raster_layers.ImageOverlay(
                        name="Tablazo",
                        image=Tablazo,
                        bounds=[[8.247096, -73.748204],
                                [8.421736, -73.584173]],
                        opacity=opacity,
                        interactive=True,
                        cross_origin=False,
                        zindex=1)

                    img_Tablazo.add_to(m)

                if 'Rosa Blanca' in surfaces:

                    rosaBlanca = r'data/surfaces/RosaBlanca.png'

                    img_RosaBlanca = folium.raster_layers.ImageOverlay(
                        name="Rosa Blanca",
                        image=rosaBlanca,
                        bounds=[[8.247096, -73.748204],
                                [8.421736, -73.584173]],
                        opacity=opacity,
                        interactive=True,
                        cross_origin=False,
                        zindex=1)

                    img_RosaBlanca.add_to(m)

                if 'Rosa Blanca (Thin)' in surfaces:

                    rosaBlancaThin = r'data/surfaces/RosaBlancaFaultThin.png'

                    img_RosaBlancaThin = folium.raster_layers.ImageOverlay(
                        name="Rosa Blanca (Thin)",
                        image=rosaBlancaThin,
                        bounds=[[8.247096, -73.748204],
                                [8.421736, -73.584173]],
                        opacity=opacity,
                        interactive=True,
                        cross_origin=False,
                        zindex=1)

                    img_RosaBlancaThin.add_to(m)

            folium.LayerControl().add_to(m)

            m.add_child(folium.LatLngPopup())

            with viewer_plot:
                folium_static(m, width=1400, height=700)

        elif viewerMode == 'Bubble Map - Time Line':
            pass

        elif viewerMode == '3D View':
            pass
