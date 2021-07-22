import streamlit as st
from statsmodels.tsa.seasonal import seasonal_decompose
import datetime
import copy

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
        forecast_params.markdown('## Parameters')
        wells = ("Caramelo-2", "Caramelo-3", "Toposi-1",
                 "Toposi-2H", "LaEstancia-1H")
        selected_well = st.selectbox("Select a well", wells)

        data = load_data()

        production_expander = st.beta_expander('Show Data Table')
        production_expander.write(data)

        total_days = len(data['Date'])

        st.write('Total days:', total_days)

        ##################################

        forecast_params.markdown('#### Economic')

        economicParameters = forecast_params.beta_expander('Parameters')

        workingInterest = economicParameters.slider('Working Interest (%):',
                                                    min_value=0.0, value=100.0, max_value=100.0)

        royalty = economicParameters.slider('Effective Royalty | ANH (%):',
                                            min_value=0.0, value=11.4, max_value=100.0)

        stateTax = economicParameters.slider('State Tax (%):',
                                             min_value=0.0, value=0.0, max_value=100.0)

        totalOperatingCost = economicParameters.slider('TOTAL Operating Cost ($/month):',
                                                       min_value=0.0, value=135000.0, max_value=1000000.0)

        percentageFixedOperatingCost = economicParameters.slider('Fixed Operating Cost (%):',
                                                                 min_value=0.0, value=75.0, max_value=100.0)

        percentageVariableOperatingCost = economicParameters.slider('Variable Operating Cost (%):',
                                                                    min_value=0.0, value=100.0-percentageFixedOperatingCost, max_value=100.0)

        numberWells = economicParameters.slider('Number of Wells:',
                                                min_value=0, value=5, max_value=10)

        economicParameters.write('Fixed Operating Cost per Well (US$/day): ')
        FixedOperatingCost = round((
            (totalOperatingCost/30)*(percentageFixedOperatingCost/100))/numberWells, 2)
        economicParameters.write(FixedOperatingCost)

        economicParameters.write(
            'Variable Operating Cost per Well (US$/day): ')
        VariableOperatingCost = round((
            (totalOperatingCost/30)*(percentageVariableOperatingCost/100))/numberWells, 2)
        economicParameters.write(VariableOperatingCost)

        gasPrice = economicParameters.slider('Gas Price ($/MCF):',
                                             min_value=0.0, value=6.60, max_value=10.0)

        gasWellConsumption = economicParameters.slider('Gas Consumption (%):',
                                                       min_value=0.0, value=2.0, max_value=10.0)

        NRI = (workingInterest/100)*(1-(royalty/100))

        st.write('Net Renevue Interest (NRI) %: ', round(NRI, 2))

        netPrice = NRI*gasPrice*(1.0-(stateTax/100))

        st.write('Net Price ($/MCF): ', round(netPrice, 2))

        economicLimit = (VariableOperatingCost+FixedOperatingCost)/netPrice

        st.write('Economic Limit (MCF/d): ', round(economicLimit, 2))

        ##################################

    with forecast_plot:
        # remove header of the data

        data_df = copy.copy(data)

        data_df.rename(columns={'Date': 'time'}, index={
                       'Gas Production [Kcfd]': 'production'})

        st.write(data_df)

        # convert to TimeSeriesData object

        data_ts = TimeSeriesData(data_df)

        # create a model param instance
        # additive mode gives worse results
        params = ProphetParams(seasonality_mode='multiplicative')

        # create a prophet model instance
        m = ProphetModel(data_ts, params)

        # fit model simply by calling m.fit()
        m.fit()

        # make prediction for next 30 month
        fcst = m.predict(steps=30, freq="D")

    with output_forecast:
        pass
