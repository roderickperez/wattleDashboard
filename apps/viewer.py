import streamlit as st
import folium
from streamlit_folium import folium_static
from plotly import graph_objs as go
import pandas as pd


def app():

    wells = ("Crisol-1", "Crisol-2", "Crisol-3",
             "Norean-1", "Aguachica-2", "Bandera-1",
             "Eucalipto-1", "Caramelo-1", "Caramelo-2",
             "Caramelo-3", "Pital-1",
             "Toposi-2HST2", "La Estancia-1",
             "La Estancia-1H ST1", "La Estancia-1H ST2",
             "Norean-1", "Pital-1", "Preludio-1",
             "Reposo-1", "Sabal-1", "Toposi-1",
             "Toposi-2", "Toposi-2HST1")

    wellUndrilled = ["Toposi-Este 1 (A)", "Toposi-Este 1 (B)"]

    st.markdown('# Viewer')

    viewer_params, viewer_plot = st.columns(
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
                'Object', ['Wells', 'Seismic Polygon', 'Surfaces', 'Wells (Undrilled)'], default=['Wells', 'Seismic Polygon'])

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

            if 'Wells (Undrilled)' in showObject:
                viewer_params.markdown('#### Wells (Undrilled)')

                wellsSettingExpander = viewer_params.expander(
                    'Well (Undrilled) Settings')

                radius = wellsSettingExpander.slider('Radius (Undrilled):',
                                                     min_value=0, value=10, max_value=20)

                color = wellsSettingExpander.color_picker(
                    'Color (Undrilled):', '#1A00F9')

                fill = wellsSettingExpander.radio(
                    'Fill (Undrilled):', [True, False])

                wellUndrilledList = ["Toposi-Este 1 (A)", "Toposi-Este 1 (B)"]

                wellUndrilled = st.multiselect(
                    'Wells (Undrilled):', wellUndrilledList, default=wellUndrilledList)

                if 'Toposi-Este 1 (A)' in wellUndrilled:
                    folium.CircleMarker(
                        location=[8.321204, -73.65627],
                        popup="Toposi-Este 1 (A)",
                        radius=radius,
                        color=color,
                        fill=fill,
                        fill_color=fill
                    ).add_to(m)

                if 'Toposi-Este 1 (B)' in wellUndrilled:
                    folium.CircleMarker(
                        location=[8.324856, -73.658123],
                        popup="Toposi-Este 1 (B)",
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
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1]))

            fig.update_layout(
                xaxis=dict(range=[0, 5], autorange=False),
                yaxis=dict(range=[0, 5], autorange=False),
                title="Start Title",
                updatemenus=[dict(
                    type="buttons",
                    buttons=[dict(label="Play",
                                  method="animate",
                                  args=[None])])]
            )

            fig.frames = [go.Frame(data=[go.Scatter(x=[1, 2], y=[1, 2])]),
                          go.Frame(data=[go.Scatter(x=[1, 4], y=[1, 4])]),
                          go.Frame(data=[go.Scatter(x=[3, 4], y=[3, 4])],
                                   layout=go.Layout(title_text="End Title"))]
            # )
            fig.update_layout(title_text="End Title")
            viewer_plot.plotly_chart(fig)

        elif viewerMode == '3D View':

            fig = go.Figure()

            mapSettingExpander = viewer_params.expander('Map Settings')

            lineWidth = mapSettingExpander.slider('Line Width:',
                                                  min_value=0, value=10, max_value=20)

            showObject = viewer_params.multiselect(
                'Object', ['Wells', 'Polygons', 'Well Tops', 'Surfaces', 'Wells (Undrilled)'], default=['Wells', 'Polygons'])

            if 'Wells' in showObject:
                showWells = viewer_params.multiselect(
                    'Wells', wells, default=wells)

                if 'Aguachica-2' in showWells:
                    aguachica_2 = pd.read_csv(
                        "data/wellTrajectory/aguachica-2.csv")

                    fig.add_trace(go.Scatter3d(
                        x=aguachica_2['X'], y=aguachica_2['Y'], z=aguachica_2['Z'], name='Aguachica-2',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'Bandera-1' in showWells:
                    bandera_1 = pd.read_csv(
                        "data/wellTrajectory/bandera-1.csv")

                    fig.add_trace(go.Scatter3d(
                        x=bandera_1['X'], y=bandera_1['Y'], z=bandera_1['Z'], name='Bandera-1',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'Caramelo-1' in showWells:
                    caramelo_1 = pd.read_csv(
                        "data/wellTrajectory/caramelo-1.csv")

                    fig.add_trace(go.Scatter3d(
                        x=caramelo_1['X'], y=caramelo_1['Y'], z=caramelo_1['Z'], name='Caramelo-1',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'Caramelo-2' in showWells:
                    caramelo_2 = pd.read_csv(
                        "data/wellTrajectory/caramelo-2.csv")

                    fig.add_trace(go.Scatter3d(
                        x=caramelo_2['X'], y=caramelo_2['Y'], z=caramelo_2['Z'], name='Caramelo-2',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'Caramelo-3' in showWells:
                    caramelo_3 = pd.read_csv(
                        "data/wellTrajectory/caramelo-3.csv")

                    fig.add_trace(go.Scatter3d(
                        x=caramelo_3['X'], y=caramelo_3['Y'], z=caramelo_3['Z'], name='Caramelo-3',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'Caramelo-5' in showWells:
                    caramelo_5 = pd.read_csv(
                        "data/wellTrajectory/caramelo-3.csv")

                    fig.add_trace(go.Scatter3d(
                        x=caramelo_5['X'], y=caramelo_5['Y'], z=caramelo_5['Z'], name='Caramelo-5',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'Crisol-1' in showWells:
                    crisol_1 = pd.read_csv(
                        "data/wellTrajectory/caramelo-3.csv")

                    fig.add_trace(go.Scatter3d(
                        x=crisol_1['X'], y=crisol_1['Y'], z=crisol_1['Z'], name='Crisol-1',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'Crisol-2' in showWells:
                    crisol_2 = pd.read_csv(
                        "data/wellTrajectory/caramelo-2.csv")

                    fig.add_trace(go.Scatter3d(
                        x=crisol_2['X'], y=crisol_2['Y'], z=crisol_2['Z'], name='Crisol-2',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'Crisol-3' in showWells:
                    crisol_3 = pd.read_csv(
                        "data/wellTrajectory/caramelo-3.csv")

                    fig.add_trace(go.Scatter3d(
                        x=crisol_3['X'], y=crisol_3['Y'], z=crisol_3['Z'], name='Crisol-3',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'Eucalipto-1' in showWells:
                    eucalipto_1 = pd.read_csv(
                        "data/wellTrajectory/eucalipto-1.csv")

                    fig.add_trace(go.Scatter3d(
                        x=eucalipto_1['X'], y=eucalipto_1['Y'], z=eucalipto_1['Z'], name='Eucalipto-1',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'La Estancia-1' in showWells:
                    laEstancia_1 = pd.read_csv(
                        "data/wellTrajectory/laEstancia-1.csv")

                    fig.add_trace(go.Scatter3d(
                        x=laEstancia_1['X'], y=laEstancia_1['Y'], z=laEstancia_1['Z'], name='La Estancia-1',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'La Estancia-1H ST1' in showWells:
                    laEstancia_1H_ST1 = pd.read_csv(
                        "data/wellTrajectory/laEstancia-1H_ST1.csv")

                    fig.add_trace(go.Scatter3d(
                        x=laEstancia_1H_ST1['X'], y=laEstancia_1H_ST1['Y'], z=laEstancia_1H_ST1['Z'], name='La Estancia-1H ST1',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'La Estancia-1H ST2' in showWells:
                    laEstancia_1H_ST2 = pd.read_csv(
                        "data/wellTrajectory/laEstancia-1H_ST2.csv")

                    fig.add_trace(go.Scatter3d(
                        x=laEstancia_1H_ST2['X'], y=laEstancia_1H_ST2['Y'], z=laEstancia_1H_ST2['Z'], name='La Estancia-1H ST2',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'Norean-1' in showWells:
                    norean_1 = pd.read_csv(
                        "data/wellTrajectory/norean-1.csv")

                    fig.add_trace(go.Scatter3d(
                        x=norean_1['X'], y=norean_1['Y'], z=norean_1['Z'], name='Norean-1',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'Norean-1' in showWells:
                    norean_1 = pd.read_csv(
                        "data/wellTrajectory/norean-1.csv")

                    fig.add_trace(go.Scatter3d(
                        x=norean_1['X'], y=norean_1['Y'], z=norean_1['Z'], name='Norean-1',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'Pital-1' in showWells:
                    pital_1 = pd.read_csv(
                        "data/wellTrajectory/pital-1.csv")

                    fig.add_trace(go.Scatter3d(
                        x=pital_1['X'], y=pital_1['Y'], z=pital_1['Z'], name='Pital-1',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'Preludio-1' in showWells:
                    preludio_1 = pd.read_csv(
                        "data/wellTrajectory/preludio-1.csv")

                    fig.add_trace(go.Scatter3d(
                        x=preludio_1['X'], y=preludio_1['Y'], z=preludio_1['Z'], name='Preludio-1',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'Reposo-1' in showWells:
                    reposo_1 = pd.read_csv(
                        "data/wellTrajectory/reposo-1.csv")

                    fig.add_trace(go.Scatter3d(
                        x=reposo_1['X'], y=reposo_1['Y'], z=reposo_1['Z'], name='Reposo-1',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'Sabal-1' in showWells:
                    sabal_1 = pd.read_csv(
                        "data/wellTrajectory/sabal-1.csv")

                    fig.add_trace(go.Scatter3d(
                        x=sabal_1['X'], y=sabal_1['Y'], z=sabal_1['Z'], name='Sabal-1',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'Toposi-1' in showWells:
                    toposi_1 = pd.read_csv(
                        "data/wellTrajectory/toposi-1.csv")

                    fig.add_trace(go.Scatter3d(
                        x=toposi_1['X'], y=toposi_1['Y'], z=toposi_1['Z'], name='Toposi-1',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'Toposi-2' in showWells:
                    toposi_2 = pd.read_csv(
                        "data/wellTrajectory/toposi-2.csv")

                    fig.add_trace(go.Scatter3d(
                        x=toposi_2['X'], y=toposi_2['Y'], z=toposi_2['Z'], name='Toposi-2',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'Toposi-2HST1' in showWells:
                    toposi_2H = pd.read_csv(
                        "data/wellTrajectory/toposi-2H.csv")

                    fig.add_trace(go.Scatter3d(
                        x=toposi_2H['X'], y=toposi_2H['Y'], z=toposi_2H['Z'], name='Toposi-2HST1',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

            if 'Wells (Undrilled)' in showObject:
                showUndrilledWells = viewer_params.multiselect(
                    'Well (Undrilled)', wellUndrilled, default=wellUndrilled)

                if 'Toposi-Este 1 (A)' in showUndrilledWells:
                    toposi_este_1A = pd.read_csv(
                        "data/wellTrajectory/toposi_este_1A.csv")

                    fig.add_trace(go.Scatter3d(
                        x=toposi_este_1A['X'], y=toposi_este_1A['Y'], z=toposi_este_1A['Z'], name='Toposi Este-1A',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

                if 'Toposi-Este 1 (B)' in showUndrilledWells:
                    toposi_este_1B = pd.read_csv(
                        "data/wellTrajectory/toposi_este_1B.csv")

                    fig.add_trace(go.Scatter3d(
                        x=toposi_este_1B['X'], y=toposi_este_1B['Y'], z=toposi_este_1B['Z'], name='Toposi Este-1B',
                        mode='lines',
                        line=dict(
                            width=lineWidth
                        )
                    ))

            if 'Polygons' in showObject:
                showPolygons = viewer_params.multiselect(
                    'Polygons', ['Area', 'Seismic'], default=['Area', 'Seismic'])

                if 'Area' in showPolygons:
                    area_VMM1 = pd.read_csv(
                        "data/wellTrajectory/area_VMM1.csv")

                    fig.add_trace(go.Scatter3d(
                        x=area_VMM1['X'], y=area_VMM1['Y'], z=area_VMM1['Z'], name='Area',
                        mode='lines',
                        line=dict(
                            width=5
                        )
                    ))

                if 'Seismic' in showPolygons:
                    seismic_VMM1 = pd.read_csv(
                        "data/wellTrajectory/seismic_VMM1.csv")

                    fig.add_trace(go.Scatter3d(
                        x=seismic_VMM1['X'], y=seismic_VMM1['Y'], z=seismic_VMM1['Z'], name='Seismic',
                        mode='lines',
                        line=dict(
                            width=5
                        )
                    ))

            fig.update_scenes(xaxis_autorange="reversed",
                              yaxis_autorange="reversed",
                              zaxis_autorange="reversed")

            fig.update_layout(
                width=1300,
                height=700,
                showlegend=True,
                autosize=False,
                margin=dict(
                    l=0,
                    r=0,
                    b=0,
                    t=0,
                    pad=0),
                scene=dict(
                    camera=dict(
                        up=dict(
                            x=0,
                            y=0,
                            z=1
                        ),
                        eye=dict(
                            x=0,
                            y=1.0707,
                            z=1,
                        )
                    ),
                    aspectratio=dict(x=1, y=1, z=0.7),
                    aspectmode='manual'
                ),
            )

            viewer_plot.plotly_chart(fig)
