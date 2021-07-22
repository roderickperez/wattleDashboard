import streamlit as st
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
from plotly import graph_objs as go
from PIL import *
import datetime
import warnings

warnings.simplefilter('ignore')


def app():
    st.markdown('# Production')
    st.markdown('## Declination Curve Analysis')
