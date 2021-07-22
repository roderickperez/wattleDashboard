import streamlit as st
from statsmodels.tsa.seasonal import seasonal_decompose
import datetime

import pandas as pd
from prophet import Prophet
from prophet.diagnostics import cross_validation
from prophet.diagnostics import performance_metrics
from prophet.plot import plot_cross_validation_metric

from prophet.plot import plot_plotly, plot_components_plotly
from plotly import graph_objs as go
import warnings

# Kats Import
from kats.consts import TimeSeriesData
from kats.models.prophet import ProphetModel, ProphetParams


warnings.simplefilter('ignore')


def app():
    st.markdown('# Production')
    st.markdown('## Machine Learning (Beta)')

    @st.cache
    def load_data():
        # data = pd.read_csv(
        # 'C:\\Users\\RODERICK\\Documents\\ScientiaGROUP\\Wattle Petroleum SAS\\PythonProject\\StreamlitProject\\data\\Caramelo_2_Production.csv')
        data = pd.read_csv(
            'data/VMM1_AllWells_DetailedProduction_Updated.csv', header=None, infer_datetime_format=True)

        # data = pd.DataFrame(data).dropna()
        data.columns = ['Date', 'DP in H2O', 'Well Head Pressure [PSI]', 'Casing Pressure [Psi]', 'Choque Fijo', 'Choque Adjustable', 'After Opening to 14/64" Current Flowrate',
                        'Current Uplift (14/64") [MCFD]', 'Temp Line [°F]', 'Pressure Line [PSI]', 'Heater Temperature [°F]', 'Orifice Plate', 'Gas Production [Kcfd]', 'After Opening to 12/64" Current Flowrate', 'Current Uplift (12/64") [MCFD]', 'Gas Comsuption [Kcfd]', 'Volumen Oil [Bbls]', 'Volumen Condensate [bls/d]', 'Volumen Water [bls/d]', 'Ambient Temperature [°F]', 'Tubing Head Temperature [°F]',  'Well Name']

        data = data[data['Well Name'] == selected_well]
        data = data[['Date', 'Gas Production [Kcfd]']]
        data.reset_index(drop=True, inplace=True)

        return data

    forecast_params, forecast_plot, output_forecast = st.beta_columns(
        (1, 2, 1))

    with forecast_params:
        st.markdown('## Parameters')
        wells = ("Caramelo-2", "Caramelo-3", "Toposi-1",
                 "Toposi-2H", "LaEstancia-1H")
        selected_well = st.selectbox("Select a well", wells)

        data = load_data()

        production_expander = st.beta_expander('Show Data Table')
        production_expander.write(data)

        total_days = len(data['Date'])

        st.write('Total days:', total_days)

        ##################################
