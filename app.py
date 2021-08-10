import streamlit as st
from multiapp import MultiApp
# import your app modules here
# , maps, logsEDA, logsML, productionEDA, seismic, economics, MLforecast, declinationCurve
from apps import home, productionEDA, declinationCurve, MLforecast, economics, viewer, logsEDA
from PIL import Image


st.set_page_config(
    page_title="VMM-1 | Wattle",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

app = MultiApp()

image = Image.open('images/wattleLogo.png')
st.sidebar.image(image, width=300)


st.sidebar.markdown("""
# VMM-1
""")


# Add all your application here
app.add_app("Home", home.app)
app.add_app("Viewer", viewer.app)
# app.add_app("Maps", maps.app)
app.add_app("Logs EDA", logsEDA.app)
# app.add_app("ML Logs", logsML.app)
# app.add_app("Seismic", seismic.app)
app.add_app("Production EDA", productionEDA.app)
app.add_app("Declination Curve", declinationCurve.app)
app.add_app("ML Production Forecast", MLforecast.app)
#app.add_app("Viewer)", viewer.app)
app.add_app("Economics", economics.app)

# The main app
app.run()

st.sidebar.write("Version: 0.2.3")
st.sidebar.write("Last Update: August, 10th, 2021")

st.sidebar.markdown("### Information")

st.sidebar.write(
    "Calle 100 #8A - 55 - Edificio World Trade Center - Torre C - Oficina 210 - Bogotá - Colombia")
st.sidebar.write("[Website](https://wattlepc.com/en/)")
st.sidebar.write("[Email](info@wattlepc.com)")
