import streamlit as st
# import numpy as np
# from scipy.interpolate import griddata
# import pandas as pd
# import matplotlib.pyplot as plt
# from plotly import graph_objs as go
# # import welleng as we
# # import folium
# # from streamlit_folium import folium_static
# # import ee
# # import geemap.eefolium as geemap

# surfaceList = ['', 'Real', 'Unconformity', 'La Luna', 'El Salto', 'Rosablanca']


def app():

    # @st.cache
    # def loadSurface():
    #     surfacedata = pd.read_csv(
    #         'data/surfaces/surfaces.csv')

    #     surfacedata.columns = ['x', 'y', 'z', 'surface']

    #     return surfacedata

    #     def loadWellTrajectory():
    #         trajectorydata = pd.read_csv(
    #             'data/wellTrajectory/trajectory.csv')

    #         trajectorydata.columns = ['md', 'x', 'y', 'well']

    #         return trajectorydata

    st.markdown('# Viewer')

    # viewer_params, viewer_plot = st.beta_columns(
    #     (1, 4))

    # with viewer_params:
    #     viewer_Mode = ['Map View', '3D View']

    #     viewerMode = st.radio(
    #         'Viewer Mode', viewer_Mode)

    #     surfacedata = loadSurface()

    #     real = surfacedata[surfacedata['surface'] == "Real"]
    #     real = real.drop(['surface'], axis=1)
    #     real_x = real['x'].values
    #     real_y = real['y'].values
    #     real_z = real['z'].values

    #     pts = 1000000  # Input the desired number of points here

    #     [x, y] = np.meshgrid(np.linspace(np.min(real_y), np.max(real_y), np.sqrt(
    #         pts)), np.linspace(np.min(real_x), np.max(real_x), np.sqrt(pts)))
    #     z = griddata((real_y, real_x), real_z, (x, y), method='linear')

    #     x = np.matrix.flatten(x)  # Gridded longitude
    #     y = np.matrix.flatten(y)  # Gridded latitude
    #     z = np.matrix.flatten(z)  # Gridded elevation

    #     fig = go.Figure(data=[go.Surface(z=z, x=x, y=y)])
    #     viewer_plot.plotly_chart(fig)

    #     ###############################

    #     Unconformity = surfacedata[surfacedata['surface']
    #                                == "Unconformity"]
    #     Unconformity = Unconformity.drop(['surface'], axis=1)

    #     laLuna = surfacedata[surfacedata['surface'] == "La Luna"]
    #     laLuna = laLuna.drop(['surface'], axis=1)

    #     elSalto = surfacedata[surfacedata['surface'] == "El Salto"]
    #     elSalto = elSalto.drop(['surface'], axis=1)

    #     Rosablanca = surfacedata[surfacedata['surface']
    #                              == "Rosablanca"]
    #     Rosablanca = Rosablanca.drop(['surface'], axis=1)


#         if viewerMode == 'Map View':
#             pass

#         if viewerMode == '3D View':

#             wellTrajectoryCheck = viewer_params.checkbox(
#                 'Well Trajectory', value=False)

#             if wellTrajectoryCheck == True:

#                 trajectorydata = loadWellTrajectory()

#                 aguachica_2 = trajectorydata[trajectorydata['well']
#                                              == "Aguachica-2"]

#                 with viewer_plot:
#                     viewer_plot.write(aguachica_2)

#                     fig = go.Figure()
#                     fig.add_trace(go.Scatter3d(
#                         x=[1041013, 1041013], y=[1413348, 1413348], z=[0, 5750], mode='lines'))

#                     #fig.update_layout(scene=dict(zaxis=dict(range=[6000, 0])))

#                     viewer_plot.plotly_chart(fig)

#             else:
#                 pass

#             viewer_params.checkbox('Well Tops', value=False)
#             viewer_params.checkbox('Faults', value=False)

#             # if surface:
#             # surfacedata = loadSurface()


#             # surface = st.checkbox('Surface', value=True)
#             # st.multiselect('Select Surface: ', surfaceList)

#             # realOpacity = st.slider(
#             #     'Opacity:', min_value=0.0, value=0.9, max_value=1.0)
#             # realScaleShow = st.radio('Show Scale', [
#             #     True, False])

#             # with viewer_plot:
#             #     st.write(real)
#             #     x = real['x'].to_numpy()
#             #     y = real['y'].to_numpy()
#             #     z = real['z'].to_numpy()

#             #     st.write(type(x))
#             #     st.write(x)
#             #     st.write(type(y))
#             #     st.write(type(z))

#             #     fig = go.Figure()
#             #     fig.add_trace(go.Surface(
#             #         z=z, x=x, y=y, showscale=realScaleShow, opacity=realOpacity))

#             #     viewer_plot.plotly_chart(fig)

#     # with viewer_plot:
#     #     viewer_plot.write(trajectorydata)
#         # # st.set_page_config(layout ="wide")

#         # m = folium.Map(location=[8.30844, -73.6166], zoom_start=12)

#         # folium.Marker(
#         #     location=[8.33351075, -73.70513353],
#         #     popup="AGUACHICA-2",
#         #     icon=folium.Icon(color="red", icon="info-sign"),
#         # ).add_to(m)

#         # folium.Marker(
#         #     location=[8.33494223, -73.67233715],
#         #     popup="CRISOL-1",
#         #     icon=folium.Icon(color="green", icon="info-sign"),
#         # ).add_to(m)

#         # folium.Marker(
#         #     location=[8.32586938, -73.68280489],
#         #     popup="CRISOL-2",
#         #     icon=folium.Icon(color="green", icon="info-sign"),
#         # ).add_to(m)

#         # folium.Marker(
#         #     location=[8.35850098, -73.65913566],
#         #     popup="CRISOL-3",
#         #     icon=folium.Icon(color="green", icon="info-sign"),
#         # ).add_to(m)

#         # folium.Marker(
#         #     location=[8.35838529, -73.67842751],
#         #     popup="NOREAN-1",
#         #     icon=folium.Icon(color="green", icon="info-sign"),
#         # ).add_to(m)

#         # folium.Marker(
#         #     location=[8.33577781, -73.70499465],
#         #     popup="PITAL-1",
#         #     icon=folium.Icon(color="green", icon="info-sign"),
#         # ).add_to(m)

#         # folium.Marker(
#         #     location=[8.33577781, -73.70499465],
#         #     popup="PITAL-1",
#         #     icon=folium.Icon(color="green", icon="info-sign"),
#         # ).add_to(m)

#         # folium.Marker(
#         #     location=[8.33577781, -73.70499465],
#         #     popup="PITAL-1",
#         #     icon=folium.Icon(color="green", icon="info-sign"),
#         # ).add_to(m)

#         # folium.Marker(
#         #     location=[8.31833502, -73.70499465],
#         #     popup="PITAL-2",
#         #     icon=folium.Icon(color="green", icon="info-sign"),
#         # ).add_to(m)

#         # folium.Marker(
#         #     location=[8.33577781, -73.70499465],
#         #     popup="PRELUDIO-1",
#         #     icon=folium.Icon(color="green", icon="info-sign"),
#         # ).add_to(m)

#         # folium.Marker(
#         #     location=[8.33577781, -73.70499465],
#         #     popup="PITAL-1",
#         #     icon=folium.Icon(color="green", icon="info-sign"),
#         # ).add_to(m)

#         # folium.Marker(
#         #     location=[8.33577781, -73.70499465],
#         #     popup="PITAL-1",
#         #     icon=folium.Icon(color="green", icon="info-sign"),
#         # ).add_to(m)

#         # folium.Marker(
#         #     location=[8.33577781, -73.70499465],
#         #     popup="PITAL-1",
#         #     icon=folium.Icon(color="green", icon="info-sign"),
#         # ).add_to(m)

#         # folium.Marker(
#         #     location=[8.33577781, -73.70499465],
#         #     popup="PITAL-1",
#         #     icon=folium.Icon(color="green", icon="info-sign"),
#         # ).add_to(m)

#         # folium.Marker(
#         #     location=[8.33577781, -73.70499465],
#         #     popup="PITAL-1",
#         #     icon=folium.Icon(color="green", icon="info-sign"),
#         # ).add_to(m)

#         # folium.Marker(
#         #     location=[8.33577781, -73.70499465],
#         #     popup="PITAL-1",
#         #     icon=folium.Icon(color="green", icon="info-sign"),
#         # ).add_to(m)

#         # folium.Marker(
#         #     location=[8.33577781, -73.70499465],
#         #     popup="PITAL-1",
#         #     icon=folium.Icon(color="green", icon="info-sign"),
#         # ).add_to(m)

#         # folium.Marker(
#         #     location=[8.33577781, -73.70499465],
#         #     popup="PITAL-1",
#         #     icon=folium.Icon(color="green", icon="info-sign"),
#         # ).add_to(m)

#         # folium_static(m)
