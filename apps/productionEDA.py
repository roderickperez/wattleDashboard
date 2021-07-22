import streamlit as st
import numpy as np
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import seasonal_decompose
import pandas as pd
from plotly import graph_objs as go
import warnings

warnings.simplefilter('ignore')


def app():
    st.markdown('# Production')
    st.markdown('## Exploration Data Analysis')
