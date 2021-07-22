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

warnings.simplefilter('ignore')


def app():
    st.markdown('# Production')
    st.markdown('## Machine Learning')

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
        st.markdown('### Train-Test Split Range')

        test_days = st.slider('Test Days:',
                              min_value=0, value=365, max_value=total_days)

        training_days = st.slider('Training Days:',
                                  min_value=0, value=[0, total_days-test_days], max_value=total_days)

        train_first = datetime.datetime.strptime(
            data['Date'].iloc[training_days[0]], '%m/%d/%Y').date()
        train_end = datetime.datetime.strptime(
            data['Date'].iloc[training_days[1]], '%m/%d/%Y').date()

        #train_end = train_end - pd.to_timedelta(test_days, unit='d')

        test_first = datetime.datetime.strptime(
            data['Date'].iloc[training_days[1]+1], '%m/%d/%Y').date()
        test_end = datetime.datetime.strptime(
            data['Date'].iloc[-1], '%m/%d/%Y').date()

        # st.write('train_first: ', train_first)
        # st.write('train_end: ', train_end)

        # st.write('test_first: ', test_first)
        # st.write('test_end: ', test_end)

        # st.write('Train_index First: ', training_days[0])
        # st.write('Train_index End: ', training_days[1])

        # st.write('Test_index First: ', training_days[1]+1)
        # st.write('Test_index End: ', len(data))

        dates_expander = st.beta_expander('Show Dates')

        dates_expander.markdown('### Train')
        train_start_date = dates_expander.date_input('Start date', train_first)
        train_end_date = dates_expander.date_input('End date', train_end)

        if train_start_date > train_end_date:
            dates_expander.error('Error: End date must fall after start date.')

        dates_expander.markdown('### Test')

        test_start_date = dates_expander.date_input('Start date ', test_first)
        test_end_date = dates_expander.date_input('End date ', test_end)

        if test_start_date > test_end_date:
            dates_expander.error('Error: End date must fall after start date.')

        st.markdown('### Forecast')
        forecast_days = st.slider('Days:',
                                  min_value=1, value=1825, max_value=3650)

        forecast_end_date = train_end + \
            pd.to_timedelta(forecast_days, unit='d')

        st.markdown('### Parameters')
        interval_width = st.slider(
            'Interval width:', min_value=0.0, value=0.95, max_value=1.0)

        # st.write(data)

    # Forecasting
    data = data.rename(
        columns={'Date': 'ds', 'Gas Production [Kcfd]': 'y'})

    df_train = data[['ds', 'y']
                    ].iloc[training_days[0]:training_days[1]]

    df_test = data[['ds', 'y']
                   ].iloc[training_days[1]+1:len(data)]

    st.write('df_train', len(df_train))
    st.write('df_test', len(df_test))

    m = Prophet(interval_width=interval_width,
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=True)
    # m = add_seasonality(m, name='monthly', period=30*1.8, fourier.order=14)

    model = m.fit(df_train)

    future = m.make_future_dataframe(periods=forecast_days, freq='d')
    forecast = m.predict(future)

    st.write(len(forecast))

    with forecast_plot:
        # data = load_data()
        st.markdown('## Plot')

        fig = plot_plotly(m, forecast)
        # fig.update_layout(width=1130)
        fig.add_vrect(x0=train_start_date, x1=train_end_date,
                      line_width=0, fillcolor="red", opacity=0.05)
        fig.add_vrect(x0=test_start_date, x1=test_end_date,
                      line_width=0, fillcolor="green", opacity=0.05)

        fig.add_vline(x=train_start_date,  line_width=1,
                      line_dash="solid", line_color="black")
        fig.add_vline(x=train_end_date,  line_width=1,
                      line_dash="solid", line_color="red")
        fig.add_vline(x=train_end_date,  line_width=1,
                      line_dash="solid", line_color="green")
        fig.add_vline(x=forecast_end_date,  line_width=1,
                      line_dash="solid", line_color="purple")
        fig.add_hline(y=economicLimit,  line_width=1,
                      line_dash="dash", line_color="purple")

        st.plotly_chart(fig)

        forecast_errorPlot = st.beta_expander('Show Forecast Error Plot')

        fig1 = m.plot(forecast)

        forecast.plot(x='ds', y='yhat')
        df_test.plot(x='ds', y='y')
        forecast_errorPlot.plotly_chart(fig1)

    with output_forecast:
        st.markdown('## Output')

        st.markdown('### Forecast')
        st.markdown(
            f"##### {forecast_days} days")

        st.markdown(
            f"#### Gas Cum Production [Kcfd]")

        gasCumForecast = round(forecast['yhat'].sum(), 2)
        gasCumForecast = f"{gasCumForecast:,}"

        st.markdown(
            f"<h1 style = 'text-align: center; color: black;'>{gasCumForecast}</h1>", unsafe_allow_html=True)

        st.markdown("<hr/>", unsafe_allow_html=True)

        st.markdown("#### Max Gas Cum Production [Kcfd]")
        gasCumForecastMax = round(forecast['yhat_upper'].sum(), 2)
        gasCumForecastMax = f"{gasCumForecastMax:,}"

        st.markdown(
            f"<h2 style = 'text-align: center; color: black;'>{gasCumForecastMax}</h2>", unsafe_allow_html=True)

        st.markdown("#### Min Gas Cum Production [Kcfd]")
        gasCumForecastMin = round(forecast['yhat_lower'].sum(), 2)
        gasCumForecastMin = f"{gasCumForecastMin:,}"

        st.markdown(
            f"<h2 style = 'text-align: center; color: black;'>{gasCumForecastMin}</h2>", unsafe_allow_html=True)

        st.markdown("<hr/>", unsafe_allow_html=True)

        st.markdown("#### Average Gas Production [Kcfd/dayly]")
        gasAverageForecast = round(forecast['yhat'].mean(), 2)
        gasAverageForecast = f"{gasAverageForecast:,}"

        st.markdown(
            f"<h3 style = 'text-align: center; color: black;'>{gasAverageForecast}</h3>", unsafe_allow_html=True)

        st.markdown("#### Max Gas Production [Kcfd/day]")
        gasCumForecastMax = round(forecast['yhat'].max(), 2)
        gasCumForecastMax = f"{gasCumForecastMax:,}"

        st.markdown(
            f"<h3 style = 'text-align: center; color: black;'>{gasCumForecastMax}</h3>", unsafe_allow_html=True)

        st.markdown("#### Min Gas Production [Kcfd/day]")
        gasCumForecastMin = round(forecast['yhat'].min(), 2)

        gasCumForecastMin = f"{gasCumForecastMin:,}"
        st.markdown(
            f"<h3 style = 'text-align: center; color: black;'>{gasCumForecastMin}</h3>", unsafe_allow_html=True)

        st.markdown("<hr/>", unsafe_allow_html=True)

        st.markdown('### Error (Test)')

        # Initial training period
        initial = 2*365
        initial = str(initial) + ' days'

        error = 6183.29

        error = f"{error:,}"

        st.markdown(
            f"<h4 style = 'text-align: center; color: purple;'>{error}</h4>", unsafe_allow_html=True)

        forecast_expander = st.beta_expander('Show Forecast Data Table')
        forecast_expander.write(forecast.tail())
