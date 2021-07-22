import streamlit as st
from multiapp import MultiApp
# import your app modules here
# , maps, logsEDA, logsML, productionEDA, seismic, economics, MLforecast, declinationCurve
from apps import home, productionEDA, declinationCurve
# from PIL import *
# import PIL.Image

st.set_page_config(
    page_title="VMM-1 | Wattle",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

app = MultiApp()

# image = Image.open('images\wattleLogo.png')
# st.sidebar.image(image, width=300)

st.sidebar.markdown("""
# VMM-1
""")

# Add all your application here
app.add_app("Home", home.app)
# app.add_app("Maps", maps.app)
# app.add_app("EDA Logs", logsEDA.app)
# app.add_app("ML Logs", logsML.app)
# app.add_app("Seismic", seismic.app)
app.add_app("EDA Production", productionEDA.app)
app.add_app("Declination Curve", declinationCurve.app)
# app.add_app("ML Production Forecast", MLforecast.app)
# app.add_app("Economics", economics.app)


# The main app
app.run()
