import streamlit as st
import numpy as np
import pandas as pd
from plotly import graph_objs as go
from plotly.subplots import make_subplots

wells = ("Crisol-1", "Crisol-2", "Crisol-3",
         "Norean-1", "Aguachica-2", "Bandera-1", "Caramelo-1", "Caramelo-2", "Caramelo-3", "Pital-1", "Toposi-2HST1", "LaEstancia-1")

columns = ['SP', 'RD', 'RM', 'RS',
           'GR', 'NPHI', 'DT', 'RHOB']

##############


def app():
    st.markdown('# Well Logs')
    st.markdown('## Exploratory Data Analysis')
