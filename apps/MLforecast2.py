import streamlit as st
# from statsmodels.tsa.seasonal import seasonal_decompose
# import datetime
import copy

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.stattools import pacf, acf
# from prophet import Prophet
# from prophet.diagnostics import cross_validation
# from prophet.diagnostics import performance_metrics
# from prophet.plot import plot_cross_validation_metric

# from prophet.plot import plot_plotly, plot_components_plotly
from plotly import graph_objs as go
from plotly.subplots import make_subplots
import warnings

# Kats Model Import
from kats.consts import TimeSeriesData
from kats.models.prophet import ProphetModel, ProphetParams
from kats.models.theta import ThetaModel, ThetaParams
from kats.models.sarima import SARIMAModel, SARIMAParams
from kats.models.arima import ARIMAModel, ARIMAParams
from kats.models.holtwinters import HoltWintersParams, HoltWintersModel
from kats.models.linear_model import LinearModel, LinearModelParams
from kats.models.quadratic_model import QuadraticModel, QuadraticModelParams

# Vector autoregression (VAR) used in Multivariable forecasting
from kats.models.var import VARModel, VARParams


from kats.models.ensemble.ensemble import EnsembleParams, BaseModelParams
from kats.models.ensemble.kats_ensemble import KatsEnsemble

# Hyperparameter tuning libraries
import kats.utils.time_series_parameter_tuning as tpt
from kats.consts import ModelEnum, SearchMethodEnum, TimeSeriesData

from ax.core.parameter import ChoiceParameter, FixedParameter, ParameterType
from ax.models.random.sobol import SobolGenerator
from ax.models.random.uniform import UniformGenerator


warnings.simplefilter('ignore')


def app():
    st.markdown('# Production')
    st.markdown('## Machine Learning (Beta)')

    columns = ['Well Head Pressure [PSI]', 'Pressure Line [PSI]', 'DP in H2O', 'Casing Pressure [Psi]', 'Choque Fijo', 'Choque Adjustable', 'After Opening to 14/64" Current Flowrate',
               'Current Uplift (14/64") [MCFD]', 'Temp Line [°F]', 'Heater Temperature [°F]', 'Orifice Plate', 'Gas Production [Kcfd]', 'After Opening to 12/64" Current Flowrate', 'Current Uplift (12/64") [MCFD]', 'Gas Comsuption [Kcfd]', 'Volumen Oil [Bbls]', 'Volumen Condensate [bls/d]', 'Volumen Water [bls/d]', 'Ambient Temperature [°F]', 'Tubing Head Temperature [°F]']

    def load_data():

        data = pd.read_csv(
            'data/VMM1_AllWells_DetailedProduction_Updated.csv', header=None, infer_datetime_format=True)

        # data = pd.DataFrame(data).dropna()
        data.columns = ['Date', 'DP in H2O', 'Well Head Pressure [PSI]', 'Casing Pressure [Psi]', 'Choque Fijo', 'Choque Adjustable', 'After Opening to 14/64" Current Flowrate',
                        'Current Uplift (14/64") [MCFD]', 'Temp Line [°F]', 'Pressure Line [PSI]', 'Heater Temperature [°F]', 'Orifice Plate', 'Gas Production [Kcfd]', 'After Opening to 12/64" Current Flowrate', 'Current Uplift (12/64") [MCFD]', 'Gas Comsuption [Kcfd]', 'Volumen Oil [Bbls]', 'Volumen Condensate [bls/d]', 'Volumen Water [bls/d]', 'Ambient Temperature [°F]', 'Tubing Head Temperature [°F]',  'Well Name']

        if forecastModel_Type == 'Bi-variate':
            data = data[data['Well Name'] == selected_well]
            data = data[['Date', 'Gas Production [Kcfd]', variable_2]]
            data.reset_index(drop=True, inplace=True)

            return data
        else:

            data = data[data['Well Name'] == selected_well]
            data = data[['Date', 'Gas Production [Kcfd]']]
            data.reset_index(drop=True, inplace=True)

            return data

    ##################################

    forecast_params, forecast_plot, output_forecast = st.beta_columns(
        (1, 3, 1))

    with forecast_params:

        forecast_params.markdown('## Parameters')

        economicParameters = forecast_params.beta_expander('Economic')

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

        # TO DO: Add Gas Price to economic parameters
        # gasWellConsumption = economicParameters.slider('Gas Consumption (%):',
        #                                                min_value=0.0, value=2.0, max_value=10.0)

        NRI = (workingInterest/100)*(1-(royalty/100))

        economicParameters.write('Net Renevue Interest (NRI) %: ')
        economicParameters.write(round(NRI, 2))

        netPrice = NRI*gasPrice*(1.0-(stateTax/100))

        economicParameters.write('Net Price ($/MCF): ')
        economicParameters.write(round(netPrice, 2))

        economicLimit = (VariableOperatingCost+FixedOperatingCost)/netPrice

        economicParameters.write('Economic Limit (MCF/d): ')
        economicParameters.write(round(economicLimit, 2))

        #############################################

        forecast_params.markdown('#### Type')

        forecast_Type = ['Single Well', 'All Wells']

        forecastType = forecast_params.radio(
            'Forecast Type', forecast_Type)

        if forecastType == 'Single Well':

            wells = ("Caramelo-2", "Caramelo-3", "Toposi-1",
                     "Toposi-2H", "LaEstancia-1H")
            selected_well = st.selectbox("Select a well", wells)

            #############################################

            forecast_params.markdown('#### Forecast')

            forecastParameters = forecast_params.beta_expander(
                'General Parameters')

            predictionPeriod = forecastParameters.slider(
                'Period (days):', min_value=1, value=1825, max_value=3650)

            forecastModelType = [
                'Manual', 'Univariate', 'Ensamble', 'Bi-variate']

            forecastModel_Type = forecast_params.radio(
                'Forecast Model Type', forecastModelType)

            modelParametersExpander = forecast_params.beta_expander(
                'Parameters')

            if forecastModel_Type == 'Manual':

                # Data Preparation

                data = load_data()

                data_df = copy.deepcopy(data)

                data_df.rename(
                    {'Date': 'time', 'Gas Production [Kcfd]': 'production'}, axis=1, inplace=True)

                ##################################

                forecastModels = ("Naive", "ARIMA")
                selected_forecastModels = forecast_params.selectbox(
                    "Select Forecast Model", forecastModels)

                if selected_forecastModels == 'Naive':
                    # convert to TimeSeriesData object

                    shift = modelParametersExpander.slider(
                        'Shift:', min_value=0, value=1, max_value=365)

                    data_ts = pd.concat(
                        [data_df['production'], data_df['production'].shift(shift)], axis=1)

                    data_ts.columns = ['original', 'forecast']
                    data_ts.dropna(inplace=True)

                    # fcst = data_df['time']

                    fcst = pd.concat(
                        [data_df['time'], data_ts['forecast']], axis=1)

                    fcst.columns = ['time', 'fcst']

                    fcst['date'] = pd.to_datetime(fcst['time']).dt.date

                    fcst.dropna(inplace=True)

                    forecast_error = mean_squared_error(
                        data_ts.original, fcst.fcst)

                elif selected_forecastModels == 'ARIMA':
                    # Calculate the Auto-Regressive Integrated Moving Average

                    # plot_acf(data_df)
                    data_df['date'] = pd.to_datetime(data_df['time']).dt.date

                    ARIMAModelParameters = st.beta_expander(
                        'ARIMA Parameters')

                    lags = ARIMAModelParameters.slider(
                        'Lags:', min_value=0, value=100, max_value=300)

                    alpha = ARIMAModelParameters.slider(
                        'Alpha:', min_value=0.00, value=0.05, max_value=1.00)

                    train_perc = ARIMAModelParameters.slider(
                        'Training %:', min_value=0.0, value=0.8, max_value=1.0)

                    data_df_train = data_df[0:int(len(data_df) * train_perc)]
                    data_df_test = data_df[int(len(data_df) * train_perc):]

                    arima_p = ARIMAModelParameters.slider(
                        'p:', min_value=0, value=0, max_value=lags)

                    arima_d = ARIMAModelParameters.slider(
                        'd:', min_value=0, value=0, max_value=2)

                    arima_q = ARIMAModelParameters.slider(
                        'q:', min_value=0, value=0, max_value=lags)

                    ARIMA_model = ARIMA(data_df_train['production'], order=(
                        arima_p, arima_d, arima_q))

                    ARIMA_model_fit = ARIMA_model.fit()

                    fcst = ARIMA_model_fit.forecast(steps=len(data_df_test))[0]

            elif forecastModel_Type == 'Univariate':

                ##################################

                # Data Preparation

                data = load_data()

                data_df = copy.deepcopy(data)

                data_df.rename(
                    {'Date': 'time', 'Gas Production [Kcfd]': 'production'}, axis=1, inplace=True)

                # convert to TimeSeriesData object

                data_ts = TimeSeriesData(data_df)

                ##################################

                forecastModels = ("Prophet", "ARIMA",
                                  "SARIMA", "Holt-Winters", "Theta", "Linear", "Quadratic")
                selected_forecastModels = forecast_params.selectbox(
                    "Select Forecast Model", forecastModels)

                if selected_forecastModels == 'Prophet':
                    # Check extra parameters: https://facebookresearch.github.io/Kats/api/kats.models.prophet.html

                    prophetSeasonality = ['Multiplicative', 'Additive']

                    prophet_seasonality = modelParametersExpander.radio(
                        'Seasonal Model Type', prophetSeasonality)

                    prophet_seasonality = prophet_seasonality.lower()

                    params = ProphetParams(
                        seasonality_mode=prophet_seasonality)

                    # create a prophet model instance
                    m = ProphetModel(data_ts, params)

                elif selected_forecastModels == 'ARIMA':
                    # Check extra parameters: https://facebookresearch.github.io/Kats/api/kats.models.arima.html

                    forecastModel_Type = modelParametersExpander.radio(
                        'Forecast Model Type', ['Manual', 'Automatic'])

                    if forecastModel_Type == 'Manual':

                        arima_p = modelParametersExpander.slider(
                            'p:', min_value=0, value=1, max_value=5)

                        arima_d = modelParametersExpander.slider(
                            'd:', min_value=0, value=0, max_value=2)

                        arima_q = modelParametersExpander.slider(
                            'q:', min_value=0, value=1, max_value=5)

                    elif forecastModel_Type == 'Automatic':
                        arima_p = 1
                        arima_d = 0
                        arima_q = 1

                        arima_p_range = modelParametersExpander.slider(
                            'p:', min_value=0, value=[1, 3], max_value=5)

                        arima_d_range = modelParametersExpander.slider(
                            'd:', min_value=0, value=[1, 3], max_value=5)

                        arima_q_range = modelParametersExpander.slider(
                            'q:', min_value=0, value=[1, 3], max_value=5)

                        parameters_grid_search = [
                            {
                                "name": "p",
                                "type": "choice",
                                "values": list(range(arima_p_range[0], arima_p_range[1])),
                                "value_type": "int",
                                "is_ordered": True,
                            },
                            {
                                "name": "d",
                                "type": "choice",
                                "values": list(range(0, 1)),
                                # "values": list(range(arima_d_range[0], arima_d_range[1])),
                                "value_type": "int",
                                "is_ordered": True,
                            },
                            {
                                "name": "q",
                                "type": "choice",
                                "values": list(range(0, 1)),
                                # "values": list(range(arima_q_range[0], arima_q_range[1])),
                                "value_type": "int",
                                "is_ordered": True,
                            },
                        ]

                        parameter_tuner_grid = tpt.SearchMethodFactory.create_search_method(
                            objective_name="evaluation_metric",
                            parameters=parameters_grid_search,
                            selected_search_method=SearchMethodEnum.GRID_SEARCH,
                        )

                        splitPercentage = modelParametersExpander.slider(
                            'Split Percentage [%]:', min_value=0.0, value=80.0, max_value=100.0)

                        split = int((splitPercentage/100)*len(data_df))

                        train_ts = data_ts[0:split]
                        test_ts = data_ts[split:]

                        evaluationFunction = modelParametersExpander.radio(
                            'Forecast Model Type', [
                                'Mean Absolute Error (MAE)',
                                'Mean Absolute Percentage Error (MAPE)',
                                'Symmetric Mean Absolute Percentage Error (SMAPE)',
                                'Mean Squared Error (MSE)',
                                'Mean Absolute Scaled Error (MASE)',
                                'Root Mean Squared Error (RMSE)'
                            ])

                        if evaluationFunction == 'Mean Absolute Error (MAE)':
                            evaluationFunction = 'mae'
                            # Fit an ARIMA model and calculate the MAE for the test data

                            def evaluation_function(params):
                                arima_params = ARIMAParams(
                                    p=params['p'],
                                    d=params['d'],
                                    q=params['q']
                                )
                                model = ARIMAModel(train_ts, arima_params)
                                model.fit()
                                model_pred = model.predict(steps=len(test_ts))
                                error = np.mean(
                                    np.abs(model_pred['fcst'].values - test_ts.value.values))
                                return error

                        elif evaluationFunction == 'Mean Absolute Percentage Error (MAPE)':
                            pass
                        elif evaluationFunction == 'Symmetric Mean Absolute Percentage Error (SMAPE)':
                            pass
                        elif evaluationFunction == 'Mean Squared Error (MSE)':
                            pass
                        elif evaluationFunction == 'Mean Absolute Scaled Error (MASE)':
                            pass
                        elif evaluationFunction == 'Root Mean Squared Error (RMSE)':
                            pass

                        parameter_tuner_grid.generate_evaluate_new_parameter_values(
                            evaluation_function=evaluation_function
                        )

                        parameter_tuning_results_grid = (
                            parameter_tuner_grid.list_parameter_value_scores()
                        )

                        # Retrieve parameter tuning results

                        st.write(parameter_tuning_results_grid)

                    params = ARIMAParams(
                        p=arima_p,
                        d=arima_d,
                        q=arima_q
                    )

                    # initiate ARIMA model
                    m = ARIMAModel(data=data_ts, params=params)

                elif selected_forecastModels == 'SARIMA':
                    # Check extra parameters: https://facebookresearch.github.io/Kats/api/kats.models.sarima.html
                    sarima_p = st.slider(
                        'p:', min_value=0, value=2, max_value=5)

                    sarima_d = st.slider(
                        'd:', min_value=0, value=1, max_value=5)

                    sarima_q = st.slider(
                        'q:', min_value=0, value=1, max_value=5)

                    params = SARIMAParams(
                        p=sarima_p,
                        d=sarima_d,
                        q=sarima_q
                    )

                    # initiate SARIMA model
                    m = SARIMAModel(data=data_ts, params=params)

                elif selected_forecastModels == 'Holt-Winters':
                    HoltWintersTrend = ["add", "mul",
                                        "additive", "multiplicative"]

                    HoltWinters_trend = st.radio(
                        'Seasonal Model Type', HoltWintersTrend)

                    HoltWintersSamped = [False, True]

                    HoltWinters_damped = st.radio(
                        'Seasonal Model Type', HoltWintersSamped)

                    HoltWintersSeasonal = [None, 'add',
                                           'mul', 'additive', 'multiplicative']

                    HoltWinters_seasonal = st.radio(
                        'Seasonal Model Type', HoltWintersSeasonal)

                    HoltWinters_seasonal_periods = st.slider(
                        'Seasonal Periods:', min_value=1, value=10, max_value=20)

                    HoltWinters_alpha = st.slider(
                        'Alpha:', min_value=0.0, value=0.1, max_value=1.0)

                    params = HoltWintersParams(
                        trend=HoltWinters_trend,
                        damped=HoltWinters_damped,
                        seasonal=HoltWinters_seasonal,
                        seasonal_periods=HoltWinters_seasonal_periods,
                    )

                    # initiate Holt-Winters model
                    m = HoltWintersModel(data=data_ts, params=params)

                elif selected_forecastModels == 'Theta':
                    theta_m = st.slider(
                        'm:', min_value=0, value=100, max_value=200)

                    params = ThetaParams(
                        m=theta_m,
                    )

                    # initiate THETA model
                    m = ThetaModel(data=data_ts, params=params)

                elif selected_forecastModels == 'Linear':

                    params = LinearModelParams(
                    )

                    # initiate LINEAR model
                    m = LinearModel(data=data_ts, params=params)

                elif selected_forecastModels == 'Quadratic':
                    params = QuadraticModelParams(
                    )

                    # initiate LINEAR model
                    m = QuadraticModel(data=data_ts, params=params)

                    # ##################################

                # Fit the model
                m.fit()

                #####################################
                # Generate forecast values

                if selected_forecastModels == 'Holt-Winters':
                    fcst = m.predict(
                        steps=predictionPeriod,
                        alpha=HoltWinters_alpha)

                elif forecastModelType == 'Ensamble':
                    fcst = m.predict(steps=predictionPeriod)

                    # aggregate individual model results
                    m.aggregate()

                else:
                    fcst = m.predict(
                        steps=predictionPeriod,
                        freq="D"
                    )

            elif forecastModel_Type == 'Ensamble':

                ##################################

                # Data Preparation

                data = load_data()

                data_df = copy.deepcopy(data)

                data_df.rename(
                    {'Date': 'time', 'Gas Production [Kcfd]': 'production'}, axis=1, inplace=True)

                # convert to TimeSeriesData object

                data_ts = TimeSeriesData(data_df)

                ##################################

                st.write("Select models to add into ensamble")
                checkProphet = st.checkbox('Prophet', value=True)
                checkSARIMA = st.checkbox('SARIMA', value=True)
                checkARIMA = st.checkbox('ARIMA', value=False)
                checkHoltWinters = st.checkbox('Holt-Winters', value=False)
                checkTheta = st.checkbox('Theta', value=False)
                checkLinear = st.checkbox('Linear', value=False)
                checkQuadratic = st.checkbox('Quadratic', value=False)

                if checkProphet:
                    pass
                if checkSARIMA:
                    pass
                if checkARIMA:
                    pass
                if checkHoltWinters:
                    pass
                if checkTheta:
                    pass
                if checkLinear:
                    pass
                if checkQuadratic:
                    pass

                # we need define params for each individual forecasting model in `EnsembleParams` class
                # here we include 6 different models
                model_params = EnsembleParams(
                    [
                        # BaseModelParams(
                        #     "arima",
                        #     ARIMAParams(
                        #           p=1,
                        #           d=1,
                        #           q=1)),
                        # BaseModelParams(
                        #     "sarima",
                        #     SARIMAParams(
                        #         p=2,
                        #         d=1,
                        #         q=1,
                        #         trend="ct",
                        #         seasonal_order=(1, 0, 1, 12),
                        #         enforce_invertibility=False,
                        #         enforce_stationarity=False)),

                        BaseModelParams("prophet", ProphetParams()),
                        BaseModelParams(
                            "linear", LinearModelParams()),
                        # BaseModelParams(
                        #     "quadratic", QuadraticModelParams()),
                        # BaseModelParams("theta", ThetaParams(m=100)),
                    ]
                )

                # create `KatsEnsembleParam` with detailed configurations
                KatsEnsembleParam = {
                    "models": model_params,
                    "aggregation": "median",
                    "seasonality_length": 2,
                    "decomposition_method": "multiplicative",
                }

                # create 'KatsEnsemble' model
                m = KatsEnsemble(
                    data=data_ts,
                    params=KatsEnsembleParam
                )

                ##################################
                # Fit the model
                m.fit()

                #####################################
                # Generate forecast values

                fcst = m.predict(steps=predictionPeriod)

                # aggregate individual model results
                m.aggregate()

            elif forecastModel_Type == 'Bi-variate':

                variable_2 = st.selectbox("Select 2nd Variable", columns)

                st.write('Select Bi-variate Model')

                st.radio("Model", ['VAR'], help='VAR model is a multivariate extension of the univariate autoregressive (AR) model. It captures the linear interdependencies between multiple variables using a system of equations. Each variable depends not only on its own lagged values but also on the lagged values of other variables. ')

                ##################################

                # Data Preparation

                data = load_data()

                data_df = copy.deepcopy(data)

                data_df.rename(
                    {'Date': 'time', 'Gas Production [Kcfd]': 'V1', variable_2: 'V2'}, axis=1, inplace=True)

                data_df['time'] = pd.to_datetime(data_df['time']).dt.date

                # # convert to TimeSeriesData object

                data_ts = TimeSeriesData(data_df)
                ##################################

                params = VARParams()
                m = VARModel(data_ts, params)

                #####################################
                # Fit model
                m.fit()

                #####################################
                # Forecast
                fcst = m.predict(steps=predictionPeriod)

                fcst_V1 = fcst['V1']
                fcstV1 = fcst_V1.to_dataframe()
                fcst_V2 = fcst['V2']
                fcstV2 = fcst_V2.to_dataframe()

        elif forecastType == 'All Wells':
            pass

    ##################################
    ##################################

    with forecast_plot:

        ##################
        # Plot

        # Add column with Date (re-formated)

        data_df['date'] = pd.to_datetime(data_df['time']).dt.date

        fig = go.Figure()

        if forecastModel_Type == 'Manual':

            if selected_forecastModels == 'Naive':
                fig.add_trace(go.Scatter(
                    x=data_df['date'], y=data_df['production'], name='Production'))

                fig.add_trace(go.Scatter(
                    x=fcst['date'], y=fcst['fcst'], name='Forecast'))

                fig.layout.update(xaxis_rangeslider_visible=True)

                fig.add_hline(y=economicLimit,  line_width=1,
                              line_dash="dash", line_color="black")

                fig.update_layout(legend=dict(
                    orientation="h",
                    #     yanchor="bottom",
                    #     yanchor="top",
                    #     y=0.99,
                    #     xanchor="right",
                    #     x=0.01
                ),
                    # showlegend=False,
                    autosize=True,
                    width=1000,
                    #   height=500,
                    margin=dict(
                    l=50,
                    r=0,
                    b=0,
                    t=0,
                    pad=0
                ))
                fig.update_yaxes(automargin=False)

                forecast_plot.plotly_chart(fig)

                resultsExpander = forecast_plot.beta_expander(
                    'Forecast Result Table')

                resultsExpander.write(fcst)

            if selected_forecastModels == 'ARIMA':

                fig = make_subplots(
                    rows=1, cols=2, subplot_titles=("Partial Autocorrelation (PACF)", "Autocorrelation (ACF)"))

                df_pacf = pacf(data_df['production'], nlags=lags, alpha=alpha)
                df_acf = acf(data_df['production'], nlags=lags, alpha=alpha)

                df_pacf_lower_y = df_pacf[1][:, 0] - df_pacf[0]
                df_pacf_upper_y = df_pacf[1][:, 1] - df_pacf[0]

                df_acf_lower_y = df_acf[1][:, 0] - df_acf[0]
                df_acf_upper_y = df_acf[1][:, 1] - df_acf[0]

                #####################

                [fig.add_scatter(x=(x, x), y=(0, df_pacf[0][x]), row=1, col=1, mode='lines', line_color='#3f3f3f')
                 for x in range(len(df_pacf[0]))]

                fig.add_scatter(x=np.arange(len(df_pacf[0])), y=df_pacf[0], mode='markers', marker_color='#1f77b4',
                                marker_size=12, row=1, col=1)

                fig.add_scatter(x=np.arange(len(
                    df_pacf[0])), y=df_pacf_upper_y, mode='lines', line_color='rgba(255,255,255,0)', row=1, col=1)
                fig.add_scatter(x=np.arange(len(df_pacf[0])), y=df_pacf_lower_y, mode='lines', fillcolor='rgba(32, 146, 230,0.3)',
                                fill='tonexty', line_color='rgba(255,255,255,0)', row=1, col=1)

                fig.add_vline(x=arima_p,  line_width=1, row=1, col=1,
                              line_dash="dash", line_color="red")

                fig.update_layout(showlegend=False,
                                  autosize=True,
                                  width=1000,
                                  height=700,
                                  xaxis_title="Lag",
                                  yaxis_title="Partial Autocorrelation",
                                  )

                #####################

                [fig.add_scatter(x=(x, x), y=(0, df_acf[0][x]), row=1, col=2, mode='lines', line_color='#3f3f3f')
                 for x in range(len(df_pacf[0]))]

                fig.add_scatter(x=np.arange(len(df_acf[0])), y=df_acf[0], mode='markers', marker_color='#1f77b4',
                                marker_size=12, row=1, col=2)

                fig.add_scatter(x=np.arange(len(
                    df_acf[0])), y=df_acf_upper_y, mode='lines', line_color='rgba(255,255,255,0)', row=1, col=2)
                fig.add_scatter(x=np.arange(len(df_acf[0])), y=df_acf_lower_y, mode='lines', fillcolor='rgba(32, 146, 230,0.3)',
                                fill='tonexty', line_color='rgba(255,255,255,0)', row=1, col=2)

                fig.add_vline(x=arima_q,  line_width=1, row=1, col=2,
                              line_dash="dash", line_color="red")

                fig.update_layout(showlegend=False,
                                  autosize=True,
                                  width=1100,
                                  height=700,
                                  xaxis_title="Lag",
                                  yaxis_title="Autocorrelation",
                                  )

                fig['layout']['xaxis']['title'] = 'Lags'
                fig['layout']['xaxis2']['title'] = 'Lags'
                fig['layout']['yaxis']['title'] = 'Partial Autocorrelation'
                fig['layout']['yaxis2']['title'] = 'Autocorrelation'

                forecast_plot.plotly_chart(fig)

        elif forecastModel_Type == 'Bi-variate':

            fig = make_subplots(
                rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02)

            fig.add_trace(go.Scatter(
                x=data_df['date'], y=data_df['V1'], name='Gas Production [Kcfd]'), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=fcstV1['time'], y=fcstV1['fcst'], name='Gas Production [Kcfd] (Prediction)'), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=fcstV1['time'], y=fcstV1['fcst_upper'], name='Forecast (Upper)', fill=None,
                line=dict(color='red', width=0.2)), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=fcstV1['time'], y=fcstV1['fcst_lower'], name='Forecast (Lower)', fill='tonexty', fillcolor='rgba(255, 0, 0, 0.1)',
                line=dict(color='red', width=0.2)), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=data_df['date'], y=data_df['V2'], name=variable_2), row=2, col=1)

            fig.add_trace(go.Scatter(
                x=fcstV2['time'], y=fcstV2['fcst'], name=variable_2), row=2, col=1)

            fig.add_trace(go.Scatter(
                x=fcstV2['time'], y=fcstV2['fcst_upper'], name='Forecast (Upper)', fill=None,
                line=dict(color='red', width=0.2)), row=2, col=1)

            fig.add_trace(go.Scatter(
                x=fcstV2['time'], y=fcstV2['fcst_lower'], name='Forecast (Lower)', fill='tonexty', fillcolor='rgba(0, 255, 247, 0.1)',
                line=dict(color='red', width=0.2)), row=2, col=1)

            fig.add_hline(y=economicLimit,  line_width=1,
                          line_dash="dash", line_color="black", row=1, col=1)

            # fig.update_layout(width=1300, height=700)

            fig.update_layout(legend=dict(
                orientation="h",
                #     yanchor="bottom",
                #     yanchor="top",
                #     y=0.99,
                #     xanchor="right",
                #     x=0.01
            ),
                # showlegend=False,
                autosize=True,
                width=1000,
                #   height=500,
                margin=dict(
                l=50,
                r=0,
                b=0,
                t=0,
                pad=0
            ))
            fig.update_yaxes(automargin=False)

            forecast_plot.plotly_chart(fig)

            resultsExpander = forecast_plot.beta_expander(
                'Forecast Result Table')

            resultsExpander.write('Forecasted Production Data:')
            # TODO: edit date in table with forecasted data (V1)
            # fcstV1['date'] = pd.to_datetime(fcstV1['time']).dt.date
            # fcstV1 = ['date', 'fcst', 'fcst_lower', 'fcst_upper']
            resultsExpander.write(fcstV1)

            resultsExpander.write('Forecasted Variable 2:')
            # TODO: edit date in table with forecasted data (V2)
            # # fcstV2['date'] = pd.to_datetime(fcstV2['time']).dt.date
            # fcstV2 = ['date', 'fcst', 'fcst_lower', 'fcst_upper']
            resultsExpander.write(fcstV2)

        else:

            fig.add_trace(go.Scatter(
                x=data_df['date'], y=data_df['production'], name='Production'))
            fig.layout.update(xaxis_rangeslider_visible=True)

            fig.add_trace(go.Scatter(
                x=fcst['time'], y=fcst['fcst'], name='Forecast',
                line=dict(color='firebrick', width=2)))
            fig.layout.update(xaxis_rangeslider_visible=True)

            fig.add_trace(go.Scatter(
                x=fcst['time'], y=fcst['fcst_upper'], name='Forecast (Upper)', fill=None,
                line=dict(color='red', width=0.2)))

            fig.add_trace(go.Scatter(
                x=fcst['time'], y=fcst['fcst_lower'], name='Forecast (Lower)', fill='tonexty', fillcolor='rgba(255, 0, 0, 0.1)',
                line=dict(color='red', width=0.2)))

            fig.layout.update(xaxis_rangeslider_visible=True)

            fig.add_hline(y=economicLimit,  line_width=1,
                          line_dash="dash", line_color="black")

            # fig.update_layout(width=1300, height=700)

            fig.update_layout(legend=dict(
                orientation="h",
                #     yanchor="bottom",
                #     yanchor="top",
                #     y=0.99,
                #     xanchor="right",
                #     x=0.01
            ),
                # showlegend=False,
                autosize=True,
                width=1000,
                #   height=500,
                margin=dict(
                l=50,
                r=0,
                b=0,
                t=0,
                pad=0
            ))
            fig.update_yaxes(automargin=False)

            forecast_plot.plotly_chart(fig)

            resultsExpander = forecast_plot.beta_expander(
                'Forecast Result Table')

            resultsExpander.write(fcst)

    with output_forecast:
        output_forecast.markdown('## Forecast Output')

        if forecastModel_Type == 'Manual':

            if selected_forecastModels == 'Naive':

                output_forecast.markdown(
                    f"#### Naive Model Error")

                Naive_error = round(np.sqrt(forecast_error), 2)

                Naive_error_ = f"{Naive_error:,}"

                output_forecast.markdown(
                    f"<h1 style = 'text-align: center; color: black;'>{Naive_error_}</h1>", unsafe_allow_html=True)

            elif selected_forecastModels == 'ARIMA':

                ARIMAModelSummary = output_forecast.beta_expander(
                    'ARIMA Model Summary')

                ARIMAModelSummary.write(ARIMA_model_fit.summary())

                ARIMA_error = np.sqrt(mean_squared_error(
                    data_df_test['production'], fcst))

                st.markdown("<hr/>", unsafe_allow_html=True)

                output_forecast.markdown(
                    f"#### Akaike Information Critera (AIC)")

                AIC = round(ARIMA_model_fit.aic, 2)

                AIC_ = f"{AIC:,}"

                output_forecast.markdown(
                    f"<h1 style = 'text-align: center; color: black;'>{AIC_}</h1>", unsafe_allow_html=True)

                st.markdown("<hr/>", unsafe_allow_html=True)

                output_forecast.markdown(
                    f"#### ARIMA Model Error")

                ARIMA_error_ = round(ARIMA_error, 2)

                ARIMA_error_ = f"{ARIMA_error_:,}"

                output_forecast.markdown(
                    f"<h1 style = 'text-align: center; color: black;'>{ARIMA_error_}</h1>", unsafe_allow_html=True)

                st.markdown("<hr/>", unsafe_allow_html=True)

                output_forecast.write(
                    'Total samples: ' + (str(len(data_df))))
                output_forecast.write(
                    'Training samples ' + (str(len(data_df_train))))
                output_forecast.write(
                    'Testing samples: ' + (str(len(data_df_test))))

        else:

            output_forecast.markdown(
                f"#### Gas Cum Production [Mcf]")

            gasProduced_ = round(data['Gas Production [Kcfd]'].sum(), 2)
            gasProduced = f"{gasProduced_:,}"

            output_forecast.markdown(
                f"<h1 style = 'text-align: center; color: black;'>{gasProduced}</h1>", unsafe_allow_html=True)

            st.markdown("<hr/>", unsafe_allow_html=True)

            output_forecast.markdown(
                f"#### Gas Reserves [Mcf] | Average")

            gasReserves = round(fcst['fcst'].sum(), 2)

            gasReserves = f"{gasReserves:,}"
            output_forecast.markdown(
                f"<h1 style = 'text-align: center; color: black;'>{gasReserves}</h1>", unsafe_allow_html=True)

            output_forecast.markdown(
                f"#### Gas Reserves [Mcf] | Upper")

            gasReserves_upper = round(fcst['fcst_upper'].sum(), 2)

            gasReserves_upper = f"{gasReserves_upper:,}"
            output_forecast.markdown(
                f"<h3 style = 'text-align: center; color: black;'>{gasReserves_upper}</h1>", unsafe_allow_html=True)

            output_forecast.markdown(
                f"#### Gas Reserves [Mcf] | Lower")

            gasReserves_lower = round(fcst['fcst_lower'].sum(), 2)

            gasReserves_lower = f"{gasReserves_lower:,}"
            output_forecast.markdown(
                f"<h3 style = 'text-align: center; color: black;'>{gasReserves_lower}</h1>", unsafe_allow_html=True)

            st.markdown("<hr/>", unsafe_allow_html=True)
