import streamlit as st
import copy

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose

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
from kats.models.lstm import LSTMModel, LSTMParams

# Vector autoregression (VAR) used in Multivariable forecasting
from kats.models.var import VARModel, VARParams

from kats.models.ensemble.ensemble import EnsembleParams, BaseModelParams
from kats.models.ensemble.kats_ensemble import KatsEnsemble

# Hyperparameter tuning libraries
import kats.utils.time_series_parameter_tuning as tpt
from kats.consts import SearchMethodEnum, TimeSeriesData

# Backtesting
from kats.utils.backtesters import BackTesterSimple

warnings.simplefilter('ignore')


def app():
    st.markdown('# Production Forecast')

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

        forecast_params.markdown('### Parameters')

        economicParameters = forecast_params.beta_expander(
            'Economic Limit Parameters')

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
        forecast_Type = ['Single Well', 'All Wells']

        forecastType = forecast_params.radio(
            'Forecast Type', forecast_Type)

        if forecastType == 'Single Well':

            wells = ("Caramelo-2", "Caramelo-3", "Toposi-1",
                     "Toposi-2H", "LaEstancia-1H")
            selected_well = st.selectbox("Select a well", wells)

            #################################
            forecast_params.markdown('#### Data')

            seriesParameters = forecast_params.beta_expander(
                'Seasonality')

            seasonalityMode = ['Daily', 'Monthly', 'Yearly', 'Custom']

            seasonalityType = seriesParameters.radio(
                'Mode', seasonalityMode, index=1)

            #############################################

            forecast_params.markdown('#### Forecast')

            forecastParameters = forecast_params.beta_expander(
                'Dates')

            #################################
            moduleSelection = forecast_params.radio(
                'Forecast Model Type', ['Forecast', 'Hyperparameter tuning', 'Backtesting'])

            if moduleSelection == 'Forecast':

                forecastModelType = [
                    'Naive', 'ARIMA (Manual)', 'Prophet', 'ARIMA', 'SARIMA', 'LSTM', 'Linear', 'Quadratic', 'Holt-Winter', 'Theta', 'Bi-variate', 'Ensamble']

                forecastModel_Type = forecast_params.selectbox(
                    'Forecast Model Type', forecastModelType)

                modelParametersExpander = forecast_params.beta_expander(
                    'Model Parameters')

                #################################
                # Data Loading

                data = load_data()

                data_df = copy.deepcopy(data)

                data_df.rename(
                    {'Date': 'time', 'Gas Production [Kcfd]': 'production'}, axis=1, inplace=True)

                data_df['time'] = pd.to_datetime(
                    data_df.time, format='%m/%d/%Y')

                #################################
                # Check if there is any null value in the data

                nullTest = data_df['production'].isnull(
                ).values.any()

                if (nullTest == True):
                    data_df['production'] = data_df['production'].fillna(
                        0)

                #################################

                if (seasonalityType == 'Daily'):
                    seasonalityPeriod = 1
                elif (seasonalityType == 'Monthly'):
                    seasonalityPeriod = 30
                elif (seasonalityType == 'Yearly'):
                    seasonalityPeriod = 365
                else:
                    seasonalityPeriod = seriesParameters.slider('Period:',
                                                                min_value=1, value=30, max_value=365)
                #############################################

                dataSeasonal = seasonal_decompose(
                    data_df['production'], model=seasonalityType, period=seasonalityPeriod)

                #################################

                # Forecast Parameters
                total_days = len(data_df['time'])

                test_days = forecastParameters.slider('Test (days):',
                                                      min_value=0, value=730, max_value=total_days)

                train_days = forecastParameters.slider('Train (days):',
                                                       min_value=0, value=total_days-test_days, max_value=total_days)

                predictionPeriod = forecastParameters.slider(
                    'Predict (days):', min_value=1, value=1825, max_value=3650)

                train_first = data_df['time'].iloc[0].date()
                train_end = data_df['time'].iloc[train_days].date()

                test_first = data_df['time'].iloc[train_days+1].date()
                test_end = data_df['time'].iloc[-1].date()

                forecastParameters.markdown('### Train')
                train_start_date = forecastParameters.date_input(
                    'Start date', train_first)
                train_end_date = forecastParameters.date_input(
                    'End date', train_end)

                if train_start_date > train_end_date:
                    forecastParameters.error(
                        'Error: End date must fall after start date.')

                forecastParameters.markdown('### Test')

                test_start_date = forecastParameters.date_input(
                    'Start date ', test_first)
                test_end_date = forecastParameters.date_input(
                    'End date ', test_end)

                if test_start_date > test_end_date:
                    forecastParameters.error(
                        'Error: End date must fall after start date.')

                #################################

                if forecastModel_Type == 'Naive':

                    shift = modelParametersExpander.slider(
                        'Shift:', min_value=0, value=1, max_value=365)

                    data_ts = pd.concat(
                        [dataSeasonal.trend, dataSeasonal.trend.shift(shift)], axis=1)

                    data_ts.columns = ['original', 'forecast']

                    data_ts.dropna(inplace=True)

                    fcst = pd.concat(
                        [data_df['time'], data_ts['forecast']], axis=1)

                    fcst.columns = ['time', 'fcst']

                    fcst['date'] = pd.to_datetime(
                        fcst['time']).dt.date

                    fcst.dropna(inplace=True)

                    forecast_error = mean_squared_error(
                        data_ts.original, fcst.fcst)

                elif forecastModel_Type == 'ARIMA (Manual)':

                    data_df_ = pd.concat(
                        [data_df['time'], dataSeasonal.trend], axis=1)

                    data_df_.columns = ['time', 'production']

                    #################################
                    # Check if there is any null value in the data

                    nullTest = data_df_['production'].isnull(
                    ).values.any()

                    # Delete rows with NA values
                    if (nullTest == True):
                        data_df_ = data_df_.dropna()

                    #################################

                    # Train - Test Split

                    train_ts = data_df_[0:train_days]
                    test_ts = data_df_[train_days+1:]

                    #################################
                    # Parameters

                    arima_p = modelParametersExpander.slider(
                        'p:', min_value=0, value=0, max_value=10, help='Order of Auto-Regressive Model (AR), or periods (See ACF plot).')

                    arima_d = modelParametersExpander.slider(
                        'd: ', min_value=0, value=0, max_value=2, help='Order of Differentiation in order to make the series stationary (See Differentiating plot).')

                    arima_q = modelParametersExpander.slider(
                        'q:', min_value=0, value=0, max_value=10, help='Dependency on error of the previous lagged values (Moving Average, MA) (See PACF plot)')

                    #################################
                    #  Model
                    m = ARIMA(train_ts['production'], order=(
                        arima_p, arima_d, arima_q))

                    # Fit the model

                    model_fit = m.fit(disp=0)

                    #################################
                    # Test Results with Test Data

                    start = len(train_ts)
                    end = len(train_ts) + len(test_ts)-1

                    pred = model_fit.predict(start=start, end=end)

                    pred_ = pd.concat(
                        [test_ts['time'], pred.shift(1)], axis=1)

                    pred_.columns = ['time', 'prediction']

                    error = mean_squared_error(
                        pred, test_ts.production)

                    #################################
                    # Forecast (Use the full time series)

                    m_ = ARIMA(data_df_['production'], order=(
                        arima_p, arima_d, arima_q))

                    model_fit_ = m_.fit(disp=0)

                    fcst_ = model_fit_.forecast(steps=predictionPeriod)[0]

                    fcst_ = pd.DataFrame(fcst_, columns=['fcst'])

                    fcst_date = pd.DataFrame(pd.date_range(
                        start=test_end, periods=predictionPeriod), columns=['time'])

                    fcst_date['date'] = fcst_date['time'].dt.date

                    fcst_date['date'] = pd.to_datetime(
                        fcst_date.date, format='%Y-%m-%d')
                    # fcst_date.date.dt.strftime('%Y-%m-%d').astype(int)

                    fcst_date['date'] = fcst_date['date'].dt.strftime(
                        '%Y-%m-%d')

                    fcst_date = pd.DataFrame(fcst_date.drop(['time'], axis=1))

                    frame = [fcst_date, fcst_]

                    fcst = pd.concat(frame, axis=1)

                elif forecastModel_Type == 'Prophet':

                    data_df_ = pd.concat(
                        [data_df['time'], dataSeasonal.trend], axis=1)

                    data_df_.columns = ['time', 'production']

                    #################################
                    # Check if there is any null value in the data

                    nullTest = data_df_['production'].isnull(
                    ).values.any()

                    # Delete rows with NA values
                    if (nullTest == True):
                        data_df_ = data_df_.dropna()

                    #################################

                    # Train - Test Split

                    train_ts = data_df_[0:train_days]
                    test_ts = data_df_[train_days+1:]

                    #################################

                    # Convert to Prophet Time Series format

                    train_ts_ = TimeSeriesData(train_ts)

                    #################################
                    # Parameters

                    # Check extra parameters: https://facebookresearch.github.io/Kats/api/kats.models.prophet.html
                    # https://github.com/facebook/prophet/blob/master/python/prophet/forecaster.py
                    prophet_Growth = modelParametersExpander.radio(
                        'Seasonal Model Type', ['linear', 'logistic'], help='String ‘linear’ or ‘logistic’ to specify a linear or logistic trend.')

                    n_changepoints = modelParametersExpander.slider(
                        'Number of change points:', min_value=1, value=60, max_value=100, help='Number of potential changepoints to include. Not used if input changepoints is supplied. If changepoints is not supplied, then n_changepoints potential changepoints are selected uniformly from the first changepoint_range proportion of the history.')

                    changepoint_range = modelParametersExpander.slider(
                        'Changepoint Range', min_value=0.0, value=0.8, max_value=1.0, help='Proportion of history in which trend changepoints will be estimated. Defaults to 0.8 for the first 80%. Not used if changepoints is specified.')

                    yearly_seasonality = modelParametersExpander.radio(
                        'Yearly Seasonality', ['auto', True, False], help='Fit yearly seasonality. Can be ‘auto’, True, False, or a number of Fourier terms to generate.')

                    weekly_seasonality = modelParametersExpander.radio(
                        'Weekly Seasonality', ['auto', True, False], help='Fit weekly seasonality. Can be ‘auto’, True, False, or a number of Fourier terms to generate.')

                    daily_seasonality = modelParametersExpander.radio(
                        'Daily  Seasonality', ['auto', True, False], help='Fit daily seasonality. Can be ‘auto’, True, False, or a number of Fourier terms to generate.')

                    prophet_seasonality = modelParametersExpander.radio(
                        'Seasonalily Model', ['multiplicative', 'additive'], help='Seasonalily model, "additive" (default) or "multiplicative".')

                    seasonality_prior_scale = modelParametersExpander.slider(
                        'Seasonality Prior Scale', min_value=0.0, value=10.0, max_value=100.0, help='Parameter modulating the strength of the seasonality model. Larger values allow the model to fit larger seasonal fluctuations, smaller values dampen the seasonality. Can be specified for individual seasonalities using add_seasonality.')

                    holidays_prior_scale = modelParametersExpander.slider(
                        'Holidays Prior Scale', min_value=0.0, value=10.0, max_value=100.0, help='Parameter modulating the strength of the holiday components model, unless overridden in the holidays input.')
                    changepoint_prior_scale = modelParametersExpander.slider(
                        'Changepoint Prior Scale', min_value=0.00, value=0.05, max_value=1.00, help='Parameter modulating the flexibility of the automatic changepoint selection. Large values will allow many changepoints, small values will allow few changepoints.')
                    interval_width = modelParametersExpander.slider(
                        'Interval Width', min_value=0.00, value=0.05, max_value=1.00, help='Width of the uncertainty intervals provided for the forecast.')
                    uncertainty_samples = modelParametersExpander.slider(
                        'Uncertainty Samples', min_value=0, value=1000, max_value=len(data_df_), help='Number of simulated draws used to estimate uncertainty intervals. Settings this value to 0 will disable uncertainty estimation and speed up the calculation.')
                    cap = modelParametersExpander.slider(
                        'Cap', min_value=0.0, value=150.0, max_value=5000.0, help='Capacity, provided for logistic growth.')
                    floor = modelParametersExpander.slider(
                        'Floor', min_value=0.0, value=150.0, max_value=5000.0, help='The forecast value must be greater than the specified floor.')

                    params = ProphetParams(
                        growth=prophet_Growth,
                        n_changepoints=n_changepoints,
                        changepoint_range=changepoint_range,
                        yearly_seasonality=yearly_seasonality,
                        weekly_seasonality=weekly_seasonality,
                        daily_seasonality=daily_seasonality,
                        seasonality_mode=prophet_seasonality,
                        seasonality_prior_scale=seasonality_prior_scale,
                        holidays_prior_scale=holidays_prior_scale,
                        changepoint_prior_scale=changepoint_prior_scale,
                        interval_width=interval_width,
                        uncertainty_samples=uncertainty_samples,
                        cap=cap,
                        floor=floor)

                    ##################################
                    # TEST model

                    m = ProphetModel(train_ts_, params)
                    model_fit = m.fit()

                    #################################
                    # Test Results with Test Data

                    pred = m.predict(steps=len(test_ts))

                    # forecast_plot.write(pred)

                    # forecast_plot.write(test_ts)

                    #####################################
                    # Calculate Test Error
                    error = np.mean(
                        np.abs(pred['fcst'].values - test_ts['production'].values))

                    ##################################
                    # FORECAST model (using the entire time series)

                    # forecast_plot.write(data_df_)

                    # Convert to Prophet Time Series format

                    data_df_ = TimeSeriesData(data_df_)

                    # forecast_plot.write(data_df_)

                    m_ = ProphetModel(data_df_, params)
                    model_fit_ = m_.fit()

                    fcst = m_.predict(steps=predictionPeriod)

                elif forecastModel_Type == 'ARIMA':

                    data_df_ = pd.concat(
                        [data_df['time'], dataSeasonal.trend], axis=1)

                    data_df_.columns = ['time', 'production']

                    #################################
                    # Check if there is any null value in the data

                    nullTest = data_df_['production'].isnull(
                    ).values.any()

                    # Delete rows with NA values
                    if (nullTest == True):
                        data_df_ = data_df_.dropna()

                    #################################

                    # Train - Test Split

                    train_ts = data_df_[0:train_days]
                    test_ts = data_df_[train_days+1:]

                    #################################

                    # Convert to Prophet Time Series format

                    train_ts_ = TimeSeriesData(train_ts)

                    #################################
                    # Parameters

                    # Check extra parameters: https://facebookresearch.github.io/Kats/api/kats.models.arima.html
                    arima_p = modelParametersExpander.slider(
                        'p:', min_value=0, value=0, max_value=10, help='Order of Auto-Regressive Model (AR), or periods (See ACF plot).')

                    arima_d = modelParametersExpander.slider(
                        'd: ', min_value=0, value=0, max_value=2, help='Order of Differentiation in order to make the series stationary (See Differentiating plot).')

                    arima_q = modelParametersExpander.slider(
                        'q:', min_value=0, value=0, max_value=10, help='Dependency on error of the previous lagged values (Moving Average, MA) (See PACF plot)')

                    method = modelParametersExpander.radio(
                        'Method', ['css-mle', 'mle', 'css'], help='Loglikelihood to maximize.')
                    trend = modelParametersExpander.radio(
                        'Trend', ['c', 'nc'], help='Specifies the whether to include a constant in the trend or not.')
                    solver = modelParametersExpander.radio(
                        'Solver', ['bfgs', 'newton', 'cg', 'ncg', 'powell'], help='A string that specifies specifies the solver to be used.')
                    maxiter = modelParametersExpander.slider(
                        'Maximum Iterations', min_value=1, value=500, max_value=3000, help='Maximum number of function iterations.')
                    tol = modelParametersExpander.slider(
                        'Convergence Tolerance ', min_value=1, value=500, max_value=3000, help='Convergence tolerance for the fitting.')

                    params = ARIMAParams(
                        p=arima_p,
                        d=arima_d,
                        q=arima_q,
                        method=method,
                        trend=trend,
                        solver=solver,
                        maxiter=maxiter,
                        tol=tol)

                    ##################################
                    # TEST model

                    m = ARIMAModel(train_ts_, params)
                    model_fit = m.fit()

                    #################################
                    # Test Results with Test Data

                    pred = m.predict(steps=len(test_ts))

                    #####################################
                    # Calculate Test Error
                    error = np.mean(
                        np.abs(pred['fcst'].values - test_ts['production'].values))

                    ##################################
                    # Convert to Prophet Time Series format

                    data_df_ = TimeSeriesData(data_df_)

                    # forecast_plot.write(data_df_)

                    m_ = ARIMAModel(data_df_, params)
                    model_fit_ = m_.fit()

                    fcst = m_.predict(steps=predictionPeriod)

                elif forecastModel_Type == 'SARIMA':
                    data_df_ = pd.concat(
                        [data_df['time'], dataSeasonal.trend], axis=1)

                    data_df_.columns = ['time', 'production']

                    #################################
                    # Check if there is any null value in the data

                    nullTest = data_df_['production'].isnull(
                    ).values.any()

                    # Delete rows with NA values
                    if (nullTest == True):
                        data_df_ = data_df_.dropna()

                    #################################

                    # Train - Test Split

                    train_ts = data_df_[0:train_days]
                    test_ts = data_df_[train_days+1:]

                    #################################

                    # Convert to Prophet Time Series format

                    train_ts_ = TimeSeriesData(train_ts)

                    #################################
                    # Parameters

                    # Check extra parameters: https://facebookresearch.github.io/Kats/api/kats.models.sarima.html
                    sarima_p = modelParametersExpander.slider(
                        'p:', min_value=0, value=0, max_value=10, help='Order of Auto-Regressive Model (AR), or periods (See ACF plot).')

                    sarima_d = modelParametersExpander.slider(
                        'd: ', min_value=0, value=0, max_value=2, help='Order of Differentiation in order to make the series stationary (See Differentiating plot).')

                    sarima_q = modelParametersExpander.slider(
                        'q:', min_value=0, value=0, max_value=10, help='Dependency on error of the previous lagged values (Moving Average, MA) (See PACF plot)')

                    cov_type = modelParametersExpander.radio(
                        'Covariance Matrix', ['opg', 'oim', 'approx', 'robust', 'robust_approx'], help='Method for calculating the covariance matrix of parameter estimates. Can be "opg" (outer product of gradient estimator), "oim" (observed information matrix estimato), "approx" (observed information matrix estimator), "robust" (approximate (quasi-maximum likelihood) covariance matrix), or "robust_approx". Default is "opg" when memory conservation is not used, otherwise default is "approx".')

                    method = modelParametersExpander.radio(
                        'Method', ['lbfgs', 'newton', 'nm', 'bfgs', 'powell', 'cg', 'ncg', 'basinhopping'], help='Solver method.')
                    trend = modelParametersExpander.radio(
                        'Trend', ['ct', 'nc'], help='Specifies the whether to include a constant in the trend or not.')
                    maxiter = modelParametersExpander.slider(
                        'Maximum Iterations', min_value=1, value=500, max_value=3000, help='Maximum number of function iterations.')
                    alpha = modelParametersExpander.slider(
                        'Confidence Level', min_value=0.00, value=0.05, max_value=1.00, help='Prediction confidence level.')

                    params = SARIMAParams(
                        p=sarima_p,
                        d=sarima_d,
                        q=sarima_q,
                        cov_type=cov_type,
                        method=method,
                        trend=trend,
                        maxiter=maxiter,
                        alpha=alpha
                    )

                    ##################################
                    # TEST model

                    m = SARIMAModel(train_ts_, params)
                    model_fit = m.fit()

                    #################################
                    # Test Results with Test Data

                    pred = m.predict(steps=len(test_ts))

                    #####################################
                    # Calculate Test Error
                    error = np.mean(
                        np.abs(pred['fcst'].values - test_ts['production'].values))

                    ##################################
                    # Convert to Prophet Time Series format

                    data_df_ = TimeSeriesData(data_df_)

                    # forecast_plot.write(data_df_)

                    m_ = SARIMAModel(data_df_, params)
                    model_fit_ = m_.fit()

                    fcst = m_.predict(steps=predictionPeriod)

                elif forecastModel_Type == 'LSTM':
                    data_df_ = pd.concat(
                        [data_df['time'], dataSeasonal.trend], axis=1)

                    data_df_.columns = ['time', 'production']

                    #################################
                    # Check if there is any null value in the data

                    nullTest = data_df_['production'].isnull(
                    ).values.any()

                    # Delete rows with NA values
                    if (nullTest == True):
                        data_df_ = data_df_.dropna()

                    #################################

                    # Train - Test Split

                    train_ts = data_df_[0:train_days]
                    test_ts = data_df_[train_days+1:]

                    #################################

                    # Convert to Prophet Time Series format

                    train_ts_ = TimeSeriesData(train_ts)

                    #################################
                    # Parameters
                    epochs = modelParametersExpander.slider(
                        'Epochs', min_value=1, value=1, max_value=100, help='Training epochs.')
                    hidden_size = modelParametersExpander.slider(
                        'Hidden Size', min_value=1, value=1, max_value=100, help='Training epochs.')
                    time_window = modelParametersExpander.slider(
                        'Time Window', min_value=1, value=1, max_value=100, help='Training epochs.')

                    # Check extra parameters: https://facebookresearch.github.io/Kats/api/kats.models.lstm.html

                    params = LSTMParams(
                        num_epochs=epochs,
                        hidden_size=hidden_size,
                        time_window=time_window
                    )

                    ##################################
                    # TEST model

                    m = LSTMModel(train_ts_, params)
                    model_fit = m.fit()

                    #################################
                    # Test Results with Test Data

                    pred = m.predict(steps=len(test_ts))

                    #####################################
                    # Calculate Test Error
                    error = np.mean(
                        np.abs(pred['fcst'].values - test_ts['production'].values))

                    ##################################
                    # Convert to Prophet Time Series format

                    data_df_ = TimeSeriesData(data_df_)

                    # forecast_plot.write(data_df_)

                    m_ = LSTMModel(data_df_, params)
                    model_fit_ = m_.fit()

                    fcst = m_.predict(steps=predictionPeriod)

                elif forecastModel_Type == 'Linear':
                    data_df_ = pd.concat(
                        [data_df['time'], dataSeasonal.trend], axis=1)

                    data_df_.columns = ['time', 'production']

                    #################################
                    # Check if there is any null value in the data

                    nullTest = data_df_['production'].isnull(
                    ).values.any()

                    # Delete rows with NA values
                    if (nullTest == True):
                        data_df_ = data_df_.dropna()

                    #################################

                    # Train - Test Split

                    train_ts = data_df_[0:train_days]
                    test_ts = data_df_[train_days+1:]

                    #################################

                    # Convert to Prophet Time Series format

                    train_ts_ = TimeSeriesData(train_ts)

                    #################################
                    # Parameters
                    # Check extra parameters: https://facebookresearch.github.io/Kats/api/kats.models.linear_model.html
                    alpha = modelParametersExpander.slider(
                        'Confidence Level', min_value=0.00, value=0.05, max_value=1.00, help='Prediction confidence level.')

                    params = LinearModelParams(
                        alpha=alpha
                    )

                    ##################################
                    # TEST model

                    m = LinearModel(train_ts_, params)
                    model_fit = m.fit()

                    #################################
                    # Test Results with Test Data

                    pred = m.predict(steps=len(test_ts))

                    #####################################
                    # Calculate Test Error
                    error = np.mean(
                        np.abs(pred['fcst'].values - test_ts['production'].values))

                    ##################################
                    # Convert to Prophet Time Series format

                    data_df_ = TimeSeriesData(data_df_)

                    # forecast_plot.write(data_df_)

                    m_ = LinearModel(data_df_, params)
                    model_fit_ = m_.fit()

                    fcst = m_.predict(steps=predictionPeriod)

                elif forecastModel_Type == 'Quadratic':
                    data_df_ = pd.concat(
                        [data_df['time'], dataSeasonal.trend], axis=1)

                    data_df_.columns = ['time', 'production']

                    #################################
                    # Check if there is any null value in the data

                    nullTest = data_df_['production'].isnull(
                    ).values.any()

                    # Delete rows with NA values
                    if (nullTest == True):
                        data_df_ = data_df_.dropna()

                    #################################

                    # Train - Test Split

                    train_ts = data_df_[0:train_days]
                    test_ts = data_df_[train_days+1:]

                    #################################

                    # Convert to Prophet Time Series format

                    train_ts_ = TimeSeriesData(train_ts)

                    #################################
                    # Parameters
                    # Check extra parameters: https://facebookresearch.github.io/Kats/api/kats.models.quadratic_model.html
                    alpha = modelParametersExpander.slider(
                        'Confidence Level', min_value=0.00, value=0.05, max_value=1.00, help='Prediction confidence level.')

                    params = QuadraticModelParams(
                        alpha=alpha
                    )

                    ##################################
                    # TEST model

                    m = QuadraticModel(train_ts_, params)
                    model_fit = m.fit()

                    #################################
                    # Test Results with Test Data

                    pred = m.predict(steps=len(test_ts))

                    #####################################
                    # Calculate Test Error
                    error = np.mean(
                        np.abs(pred['fcst'].values - test_ts['production'].values))

                    ##################################
                    # Convert to Prophet Time Series format

                    data_df_ = TimeSeriesData(data_df_)

                    # forecast_plot.write(data_df_)

                    m_ = QuadraticModel(data_df_, params)
                    model_fit_ = m_.fit()

                    fcst = m_.predict(steps=predictionPeriod)
                elif forecastModel_Type == 'Holt-Winter':
                    data_df_ = pd.concat(
                        [data_df['time'], dataSeasonal.trend], axis=1)

                    data_df_.columns = ['time', 'production']

                    #################################
                    # Check if there is any null value in the data

                    nullTest = data_df_['production'].isnull(
                    ).values.any()

                    # Delete rows with NA values
                    if (nullTest == True):
                        data_df_ = data_df_.dropna()

                    #################################

                    # Train - Test Split

                    train_ts = data_df_[0:train_days]
                    test_ts = data_df_[train_days+1:]

                    #################################

                    # Convert to Prophet Time Series format

                    train_ts_ = TimeSeriesData(train_ts)

                    #################################
                    # Parameters
                    # Check extra parameters: https://facebookresearch.github.io/Kats/api/kats.models.holtwinters.html
                    # trend = modelParametersExpander.radio(
                    #     'Trend', ['additive', 'multiplicative'], help='Type of trend component.')

                    damped = modelParametersExpander.radio(
                        'Trend', [True, False], help='indicates whether the trend should be damped or not (Default is False).')

                    # seasonal = modelParametersExpander.radio(
                    #     'Seasonal', [None, 'additive', 'multiplicative'], help='Type of trend component.')
                    alpha = modelParametersExpander.slider(
                        'Confidence Level', min_value=0.00, value=0.1, max_value=1.00, help='Prediction confidence level.')

                    params = HoltWintersParams(
                        # trend=trend,
                        damped=damped,
                        # seasonal=seasonal

                    )

                    ##################################
                    # TEST model

                    m = HoltWintersModel(train_ts_, params)
                    model_fit = m.fit()

                    #################################
                    # Test Results with Test Data

                    pred = m.predict(steps=len(test_ts), alpha=alpha)

                    #####################################
                    # Calculate Test Error
                    error = np.mean(
                        np.abs(pred['fcst'].values - test_ts['production'].values))

                    ##################################
                    # Convert to Prophet Time Series format

                    data_df_ = TimeSeriesData(data_df_)

                    # forecast_plot.write(data_df_)

                    m_ = HoltWintersModel(data_df_, params)
                    model_fit_ = m_.fit()

                    fcst = m_.predict(steps=predictionPeriod, alpha=alpha)

                elif forecastModel_Type == 'Theta':
                    data_df_ = pd.concat(
                        [data_df['time'], dataSeasonal.trend], axis=1)

                    data_df_.columns = ['time', 'production']

                    #################################
                    # Check if there is any null value in the data

                    nullTest = data_df_['production'].isnull(
                    ).values.any()

                    # Delete rows with NA values
                    if (nullTest == True):
                        data_df_ = data_df_.dropna()

                    #################################

                    # Train - Test Split

                    train_ts = data_df_[0:train_days]
                    test_ts = data_df_[train_days+1:]

                    #################################

                    # Convert to Prophet Time Series format

                    train_ts_ = TimeSeriesData(train_ts)

                    #################################
                    # Parameters
                    # Check extra parameters: https://facebookresearch.github.io/Kats/api/kats.models.theta.html

                    m_ = modelParametersExpander.slider(
                        'Observations Before Trend', min_value=1, value=1, max_value=365, help='Number of observations before the seasonal pattern repeats. For example, if m = 12 (montly data) model assumes a yearly seasonality.')

                    alpha = modelParametersExpander.slider(
                        'Confidence Level', min_value=0.00, value=0.2, max_value=1.00, help='Prediction confidence level.')

                    params = ThetaParams(
                        m=m_
                    )

                    ##################################
                    # TEST model

                    m = ThetaModel(train_ts_, params)
                    model_fit = m.fit()

                    #################################
                    # Test Results with Test Data

                    pred = m.predict(steps=len(test_ts), alpha=alpha)

                    #####################################
                    # Calculate Test Error
                    error = np.mean(
                        np.abs(pred['fcst'].values - test_ts['production'].values))

                    ##################################
                    # Convert to Prophet Time Series format

                    data_df_ = TimeSeriesData(data_df_)

                    # forecast_plot.write(data_df_)

                    m_ = ThetaModel(data_df_, params)
                    model_fit_ = m_.fit()

                    fcst = m_.predict(steps=predictionPeriod, alpha=alpha)

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
                    checkARIMA = st.checkbox('ARIMA', value=False)

                    if checkProphet:
                        pass
                    if checkARIMA:
                        pass

                    # we need define params for each individual forecasting model in `EnsembleParams` class
                    # here we include 6 different models
                    model_params = EnsembleParams(
                        [
                            BaseModelParams(
                                "arima",
                                ARIMAParams(
                                    p=1,
                                    d=1,
                                    q=1)),
                            BaseModelParams("prophet", ProphetParams()),
                        ]
                    )

                    prophetSeasonality = ['Multiplicative', 'Additive']

                    prophet_seasonality = modelParametersExpander.radio(
                        'Seasonal Model Type', prophetSeasonality)

                    # create `KatsEnsembleParam` with detailed configurations
                    KatsEnsembleParam = {
                        "models": model_params,
                        "aggregation": "median",
                        "seasonality_length": 2,
                        "decomposition_method": prophet_seasonality,
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

                with forecast_plot:

                    fig = go.Figure()

                    if forecastModel_Type == 'Naive':

                        # forecast_plot.write(dataSeasonal.trend)

                        fig.add_trace(go.Scatter(
                            x=data_df['time'], y=data_df['production'], name='Production', line=dict(color='gray', width=0.5)))

                        fig.add_trace(go.Scatter(
                            x=data_df['time'], y=dataSeasonal.trend, name='Trend', line=dict(color='red')))

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

                        #########################
                        # Show results

                        resultsExpander = forecast_plot.beta_expander(
                            'Forecast Result Table')

                        resultsExpander.write(fcst)

                    elif forecastModel_Type == 'ARIMA (Manual)':

                        fig.add_trace(go.Scatter(
                            x=data_df['time'], y=data_df['production'], name='Production (Original)', line=dict(color='gray', width=0.5)))

                        fig.add_trace(go.Scatter(
                            x=train_ts['time'], y=train_ts['production'], name='Train | Production (Original)', line=dict(color='red')))

                        fig.add_trace(go.Scatter(
                            x=test_ts['time'], y=test_ts['production'], name='Test | Production (Original)', line=dict(color='green')))

                        fig.add_trace(go.Scatter(
                            x=pred_['time'], y=pred_[
                                'prediction'], name='Test',
                            mode='markers', line=dict(color='black')))

                        fig.add_trace(go.Scatter(
                            x=fcst['date'], y=fcst['fcst'], name='Forecast', line=dict(color='purple')))

                        fig.add_hline(y=economicLimit,  line_width=1,
                                      line_dash="dash", line_color="black")

                        fig.add_vrect(x0=train_start_date, x1=train_end_date,
                                      line_width=0, fillcolor="red", opacity=0.05)
                        fig.add_vrect(x0=test_start_date, x1=test_end_date,
                                      line_width=0, fillcolor="green", opacity=0.05)

                        fig.add_vline(x=train_start_date,  line_width=1,
                                      line_dash="dash", line_color="black")
                        fig.add_vline(x=train_end_date,  line_width=1,
                                      line_dash="dash", line_color="red")

                        fig.add_vline(x=test_start_date,  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.add_vline(x=test_end_date,  line_width=1,
                                      line_dash="dash", line_color="green")
                        # fig.add_vline(x=forecast_end_date,  line_width=1,
                        #               line_dash="solid", line_color="purple")

                        # fig.layout.update(xaxis_rangeslider_visible=True)

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
                            height=600,
                            margin=dict(
                            l=50,
                            r=0,
                            b=0,
                            t=0,
                            pad=0
                        ))
                        fig.update_yaxes(automargin=False)

                        forecast_plot.plotly_chart(fig)

                        #########################
                        # Show results

                        resultsExpander = forecast_plot.beta_expander(
                            'Forecast Result Table')

                        resultsExpander.write(fcst)

                    elif forecastModel_Type == 'Prophet':

                        fig.add_trace(go.Scatter(
                            x=data_df['time'], y=data_df['production'], name='Production (Original)', line=dict(color='gray', width=0.5)))

                        fig.add_trace(go.Scatter(
                            x=train_ts['time'], y=train_ts['production'], name='Train | Production (Original)', line=dict(color='red')))

                        fig.add_trace(go.Scatter(
                            x=test_ts['time'], y=test_ts['production'], name='Test | Production (Original)', line=dict(color='green')))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst'], name='Test',
                            mode='markers', line=dict(color='black', width=0.5)))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst_upper'], name='Test (upper)',
                            line=dict(color='royalblue', width=1, dash='dash')))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst_lower'], name='Test (lower)',
                            line=dict(color='royalblue', width=1, dash='dash')))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst'], name='Forecast'))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst_upper'], name='Forecast (upper)'))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst_lower'], name='Forecast (lower)', fill='tonexty', mode='none'))

                        fig.add_hline(y=economicLimit,  line_width=1,
                                      line_dash="dash", line_color="black")

                        fig.add_vrect(x0=train_start_date, x1=train_end_date,
                                      line_width=0, fillcolor="red", opacity=0.05)
                        fig.add_vrect(x0=test_start_date, x1=test_end_date,
                                      line_width=0, fillcolor="green", opacity=0.05)

                        fig.add_vline(x=train_start_date,  line_width=1,
                                      line_dash="dash", line_color="black")
                        fig.add_vline(x=train_end_date,  line_width=1,
                                      line_dash="dash", line_color="red")

                        fig.add_vline(x=test_start_date,  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.add_vline(x=test_end_date,  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.update_layout(legend=dict(
                            orientation="h",
                        ),
                            # showlegend=False,
                            autosize=True,
                            width=1000,
                            height=550,
                            margin=dict(
                            l=50,
                            r=0,
                            b=0,
                            t=0,
                            pad=0
                        ))
                        fig.update_yaxes(automargin=False)

                        forecast_plot.plotly_chart(fig)

                        #########################
                        # Show results

                        # Test Results

                        testResultsExpander = forecast_plot.beta_expander(
                            'Test Result')

                        testResultsExpander.write(pred)

                        # Forecast Results

                        forecastResultsExpander = forecast_plot.beta_expander(
                            'Forecast Result')

                        forecastResultsExpander.write(fcst)

                    elif forecastModel_Type == 'ARIMA':
                        fig.add_trace(go.Scatter(
                            x=data_df['time'], y=data_df['production'], name='Production (Original)', line=dict(color='gray', width=0.5)))

                        fig.add_trace(go.Scatter(
                            x=train_ts['time'], y=train_ts['production'], name='Train | Production (Original)', line=dict(color='red')))

                        fig.add_trace(go.Scatter(
                            x=test_ts['time'], y=test_ts['production'], name='Test | Production (Original)', line=dict(color='green')))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst'], name='Test',
                            mode='markers', line=dict(color='black', width=0.5)))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst_upper'], name='Test (upper)',
                            line=dict(color='royalblue', width=1, dash='dash')))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst_lower'], name='Test (lower)',
                            line=dict(color='royalblue', width=1, dash='dash')))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst'], name='Forecast'))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst_upper'], name='Forecast (upper)'))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst_lower'], name='Forecast (lower)', fill='tonexty', mode='none'))

                        fig.add_hline(y=economicLimit,  line_width=1,
                                      line_dash="dash", line_color="black")

                        fig.add_vrect(x0=train_start_date, x1=train_end_date,
                                      line_width=0, fillcolor="red", opacity=0.05)
                        fig.add_vrect(x0=test_start_date, x1=test_end_date,
                                      line_width=0, fillcolor="green", opacity=0.05)

                        fig.add_vline(x=train_start_date,  line_width=1,
                                      line_dash="dash", line_color="black")
                        fig.add_vline(x=train_end_date,  line_width=1,
                                      line_dash="dash", line_color="red")

                        fig.add_vline(x=test_start_date,  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.add_vline(x=test_end_date,  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.update_layout(legend=dict(
                            orientation="h",
                        ),
                            # showlegend=False,
                            autosize=True,
                            width=1000,
                            height=550,
                            margin=dict(
                            l=50,
                            r=0,
                            b=0,
                            t=0,
                            pad=0
                        ))
                        fig.update_yaxes(automargin=False)

                        forecast_plot.plotly_chart(fig)

                        #########################
                        # Show results

                        # Test Results

                        testResultsExpander = forecast_plot.beta_expander(
                            'Test Result')

                        testResultsExpander.write(pred)

                        # Forecast Results

                        forecastResultsExpander = forecast_plot.beta_expander(
                            'Forecast Result')

                        forecastResultsExpander.write(fcst)
                    elif forecastModel_Type == 'SARIMA':
                        fig.add_trace(go.Scatter(
                            x=data_df['time'], y=data_df['production'], name='Production (Original)', line=dict(color='gray', width=0.5)))

                        fig.add_trace(go.Scatter(
                            x=train_ts['time'], y=train_ts['production'], name='Train | Production (Original)', line=dict(color='red')))

                        fig.add_trace(go.Scatter(
                            x=test_ts['time'], y=test_ts['production'], name='Test | Production (Original)', line=dict(color='green')))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst'], name='Test',
                            mode='markers', line=dict(color='black', width=0.5)))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst_upper'], name='Test (upper)',
                            line=dict(color='royalblue', width=1, dash='dash')))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst_lower'], name='Test (lower)',
                            line=dict(color='royalblue', width=1, dash='dash')))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst'], name='Forecast'))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst_upper'], name='Forecast (upper)'))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst_lower'], name='Forecast (lower)', fill='tonexty', mode='none'))

                        fig.add_hline(y=economicLimit,  line_width=1,
                                      line_dash="dash", line_color="black")

                        fig.add_vrect(x0=train_start_date, x1=train_end_date,
                                      line_width=0, fillcolor="red", opacity=0.05)
                        fig.add_vrect(x0=test_start_date, x1=test_end_date,
                                      line_width=0, fillcolor="green", opacity=0.05)

                        fig.add_vline(x=train_start_date,  line_width=1,
                                      line_dash="dash", line_color="black")
                        fig.add_vline(x=train_end_date,  line_width=1,
                                      line_dash="dash", line_color="red")

                        fig.add_vline(x=test_start_date,  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.add_vline(x=test_end_date,  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.update_layout(legend=dict(
                            orientation="h",
                        ),
                            # showlegend=False,
                            autosize=True,
                            width=1000,
                            height=550,
                            margin=dict(
                            l=50,
                            r=0,
                            b=0,
                            t=0,
                            pad=0
                        ))
                        fig.update_yaxes(automargin=False)

                        forecast_plot.plotly_chart(fig)

                        #########################
                        # Show results

                        # Test Results

                        testResultsExpander = forecast_plot.beta_expander(
                            'Test Result')

                        testResultsExpander.write(pred)

                        # Forecast Results

                        forecastResultsExpander = forecast_plot.beta_expander(
                            'Forecast Result')

                        forecastResultsExpander.write(fcst)
                    elif forecastModel_Type == 'LSTM':
                        fig.add_trace(go.Scatter(
                            x=data_df['time'], y=data_df['production'], name='Production (Original)', line=dict(color='gray', width=0.5)))

                        fig.add_trace(go.Scatter(
                            x=train_ts['time'], y=train_ts['production'], name='Train | Production (Original)', line=dict(color='red')))

                        fig.add_trace(go.Scatter(
                            x=test_ts['time'], y=test_ts['production'], name='Test | Production (Original)', line=dict(color='green')))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst'], name='Test',
                            mode='markers', line=dict(color='black', width=0.5)))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst_upper'], name='Test (upper)',
                            line=dict(color='royalblue', width=1, dash='dash')))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst_lower'], name='Test (lower)',
                            line=dict(color='royalblue', width=1, dash='dash')))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst'], name='Forecast'))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst_upper'], name='Forecast (upper)'))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst_lower'], name='Forecast (lower)', fill='tonexty', mode='none'))

                        fig.add_hline(y=economicLimit,  line_width=1,
                                      line_dash="dash", line_color="black")

                        fig.add_vrect(x0=train_start_date, x1=train_end_date,
                                      line_width=0, fillcolor="red", opacity=0.05)
                        fig.add_vrect(x0=test_start_date, x1=test_end_date,
                                      line_width=0, fillcolor="green", opacity=0.05)

                        fig.add_vline(x=train_start_date,  line_width=1,
                                      line_dash="dash", line_color="black")
                        fig.add_vline(x=train_end_date,  line_width=1,
                                      line_dash="dash", line_color="red")

                        fig.add_vline(x=test_start_date,  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.add_vline(x=test_end_date,  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.update_layout(legend=dict(
                            orientation="h",
                        ),
                            # showlegend=False,
                            autosize=True,
                            width=1000,
                            height=550,
                            margin=dict(
                            l=50,
                            r=0,
                            b=0,
                            t=0,
                            pad=0
                        ))
                        fig.update_yaxes(automargin=False)

                        forecast_plot.plotly_chart(fig)

                        #########################
                        # Show results

                        # Test Results

                        testResultsExpander = forecast_plot.beta_expander(
                            'Test Result')

                        testResultsExpander.write(pred)

                        # Forecast Results

                        forecastResultsExpander = forecast_plot.beta_expander(
                            'Forecast Result')

                        forecastResultsExpander.write(fcst)
                    elif forecastModel_Type == 'Linear':
                        fig.add_trace(go.Scatter(
                            x=data_df['time'], y=data_df['production'], name='Production (Original)', line=dict(color='gray', width=0.5)))

                        fig.add_trace(go.Scatter(
                            x=train_ts['time'], y=train_ts['production'], name='Train | Production (Original)', line=dict(color='red')))

                        fig.add_trace(go.Scatter(
                            x=test_ts['time'], y=test_ts['production'], name='Test | Production (Original)', line=dict(color='green')))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst'], name='Test',
                            mode='markers', line=dict(color='black', width=0.5)))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst_upper'], name='Test (upper)',
                            line=dict(color='royalblue', width=1, dash='dash')))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst_lower'], name='Test (lower)',
                            line=dict(color='royalblue', width=1, dash='dash')))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst'], name='Forecast'))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst_upper'], name='Forecast (upper)'))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst_lower'], name='Forecast (lower)', fill='tonexty', mode='none'))

                        fig.add_hline(y=economicLimit,  line_width=1,
                                      line_dash="dash", line_color="black")

                        fig.add_vrect(x0=train_start_date, x1=train_end_date,
                                      line_width=0, fillcolor="red", opacity=0.05)
                        fig.add_vrect(x0=test_start_date, x1=test_end_date,
                                      line_width=0, fillcolor="green", opacity=0.05)

                        fig.add_vline(x=train_start_date,  line_width=1,
                                      line_dash="dash", line_color="black")
                        fig.add_vline(x=train_end_date,  line_width=1,
                                      line_dash="dash", line_color="red")

                        fig.add_vline(x=test_start_date,  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.add_vline(x=test_end_date,  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.update_layout(legend=dict(
                            orientation="h",
                        ),
                            # showlegend=False,
                            autosize=True,
                            width=1000,
                            height=550,
                            margin=dict(
                            l=50,
                            r=0,
                            b=0,
                            t=0,
                            pad=0
                        ))
                        fig.update_yaxes(automargin=False)

                        forecast_plot.plotly_chart(fig)

                        #########################
                        # Show results

                        # Test Results

                        testResultsExpander = forecast_plot.beta_expander(
                            'Test Result')

                        testResultsExpander.write(pred)

                        # Forecast Results

                        forecastResultsExpander = forecast_plot.beta_expander(
                            'Forecast Result')

                        forecastResultsExpander.write(fcst)
                    elif forecastModel_Type == 'Quadratic':
                        fig.add_trace(go.Scatter(
                            x=data_df['time'], y=data_df['production'], name='Production (Original)', line=dict(color='gray', width=0.5)))

                        fig.add_trace(go.Scatter(
                            x=train_ts['time'], y=train_ts['production'], name='Train | Production (Original)', line=dict(color='red')))

                        fig.add_trace(go.Scatter(
                            x=test_ts['time'], y=test_ts['production'], name='Test | Production (Original)', line=dict(color='green')))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst'], name='Test',
                            mode='markers', line=dict(color='black', width=0.5)))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst_upper'], name='Test (upper)',
                            line=dict(color='royalblue', width=1, dash='dash')))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst_lower'], name='Test (lower)',
                            line=dict(color='royalblue', width=1, dash='dash')))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst'], name='Forecast'))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst_upper'], name='Forecast (upper)'))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst_lower'], name='Forecast (lower)', fill='tonexty', mode='none'))

                        fig.add_hline(y=economicLimit,  line_width=1,
                                      line_dash="dash", line_color="black")

                        fig.add_vrect(x0=train_start_date, x1=train_end_date,
                                      line_width=0, fillcolor="red", opacity=0.05)
                        fig.add_vrect(x0=test_start_date, x1=test_end_date,
                                      line_width=0, fillcolor="green", opacity=0.05)

                        fig.add_vline(x=train_start_date,  line_width=1,
                                      line_dash="dash", line_color="black")
                        fig.add_vline(x=train_end_date,  line_width=1,
                                      line_dash="dash", line_color="red")

                        fig.add_vline(x=test_start_date,  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.add_vline(x=test_end_date,  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.update_layout(legend=dict(
                            orientation="h",
                        ),
                            # showlegend=False,
                            autosize=True,
                            width=1000,
                            height=550,
                            margin=dict(
                            l=50,
                            r=0,
                            b=0,
                            t=0,
                            pad=0
                        ))
                        fig.update_yaxes(automargin=False)

                        forecast_plot.plotly_chart(fig)

                        #########################
                        # Show results

                        # Test Results

                        testResultsExpander = forecast_plot.beta_expander(
                            'Test Result')

                        testResultsExpander.write(pred)

                        # Forecast Results

                        forecastResultsExpander = forecast_plot.beta_expander(
                            'Forecast Result')

                        forecastResultsExpander.write(fcst)
                    elif forecastModel_Type == 'Holt-Winter':
                        fig.add_trace(go.Scatter(
                            x=data_df['time'], y=data_df['production'], name='Production (Original)', line=dict(color='gray', width=0.5)))

                        fig.add_trace(go.Scatter(
                            x=train_ts['time'], y=train_ts['production'], name='Train | Production (Original)', line=dict(color='red')))

                        fig.add_trace(go.Scatter(
                            x=test_ts['time'], y=test_ts['production'], name='Test | Production (Original)', line=dict(color='green')))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst'], name='Test',
                            mode='markers', line=dict(color='black', width=0.5)))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst_upper'], name='Test (upper)',
                            line=dict(color='royalblue', width=1, dash='dash')))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst_lower'], name='Test (lower)',
                            line=dict(color='royalblue', width=1, dash='dash')))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst'], name='Forecast'))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst_upper'], name='Forecast (upper)'))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst_lower'], name='Forecast (lower)', fill='tonexty', mode='none'))

                        fig.add_hline(y=economicLimit,  line_width=1,
                                      line_dash="dash", line_color="black")

                        fig.add_vrect(x0=train_start_date, x1=train_end_date,
                                      line_width=0, fillcolor="red", opacity=0.05)
                        fig.add_vrect(x0=test_start_date, x1=test_end_date,
                                      line_width=0, fillcolor="green", opacity=0.05)

                        fig.add_vline(x=train_start_date,  line_width=1,
                                      line_dash="dash", line_color="black")
                        fig.add_vline(x=train_end_date,  line_width=1,
                                      line_dash="dash", line_color="red")

                        fig.add_vline(x=test_start_date,  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.add_vline(x=test_end_date,  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.update_layout(legend=dict(
                            orientation="h",
                        ),
                            # showlegend=False,
                            autosize=True,
                            width=1000,
                            height=550,
                            margin=dict(
                            l=50,
                            r=0,
                            b=0,
                            t=0,
                            pad=0
                        ))
                        fig.update_yaxes(automargin=False)

                        forecast_plot.plotly_chart(fig)

                        #########################
                        # Show results

                        # Test Results

                        testResultsExpander = forecast_plot.beta_expander(
                            'Test Result')

                        testResultsExpander.write(pred)

                        # Forecast Results

                        forecastResultsExpander = forecast_plot.beta_expander(
                            'Forecast Result')

                        forecastResultsExpander.write(fcst)

                    elif forecastModel_Type == 'Theta':
                        fig.add_trace(go.Scatter(
                            x=data_df['time'], y=data_df['production'], name='Production (Original)', line=dict(color='gray', width=0.5)))

                        fig.add_trace(go.Scatter(
                            x=train_ts['time'], y=train_ts['production'], name='Train | Production (Original)', line=dict(color='red')))

                        fig.add_trace(go.Scatter(
                            x=test_ts['time'], y=test_ts['production'], name='Test | Production (Original)', line=dict(color='green')))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst'], name='Test',
                            mode='markers', line=dict(color='black', width=0.5)))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst_upper'], name='Test (upper)',
                            line=dict(color='royalblue', width=1, dash='dash')))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst_lower'], name='Test (lower)',
                            line=dict(color='royalblue', width=1, dash='dash')))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst'], name='Forecast'))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst_upper'], name='Forecast (upper)'))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst_lower'], name='Forecast (lower)', fill='tonexty', mode='none'))

                        fig.add_hline(y=economicLimit,  line_width=1,
                                      line_dash="dash", line_color="black")

                        fig.add_vrect(x0=train_start_date, x1=train_end_date,
                                      line_width=0, fillcolor="red", opacity=0.05)
                        fig.add_vrect(x0=test_start_date, x1=test_end_date,
                                      line_width=0, fillcolor="green", opacity=0.05)

                        fig.add_vline(x=train_start_date,  line_width=1,
                                      line_dash="dash", line_color="black")
                        fig.add_vline(x=train_end_date,  line_width=1,
                                      line_dash="dash", line_color="red")

                        fig.add_vline(x=test_start_date,  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.add_vline(x=test_end_date,  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.update_layout(legend=dict(
                            orientation="h",
                        ),
                            # showlegend=False,
                            autosize=True,
                            width=1000,
                            height=550,
                            margin=dict(
                            l=50,
                            r=0,
                            b=0,
                            t=0,
                            pad=0
                        ))
                        fig.update_yaxes(automargin=False)

                        forecast_plot.plotly_chart(fig)

                        #########################
                        # Show results

                        # Test Results

                        testResultsExpander = forecast_plot.beta_expander(
                            'Test Result')

                        testResultsExpander.write(pred)

                        # Forecast Results

                        forecastResultsExpander = forecast_plot.beta_expander(
                            'Forecast Result')

                        forecastResultsExpander.write(fcst)

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

                    elif forecastModel_Type == 'Ensamble':
                        pass

                with output_forecast:
                    output_forecast.markdown('## Forecast Output')

                    if forecastModel_Type == 'Naive':

                        output_forecast.markdown(
                            f"#### Error")

                        error = round(np.sqrt(forecast_error), 2)

                        error_ = f"{error:,}"

                        output_forecast.markdown(
                            f"<h2 style = 'text-align: center; color: black;'>{error_} [Kcfd]</h2>", unsafe_allow_html=True)

                    elif forecastModel_Type == 'ARIMA (Manual)':

                        output_forecast.markdown(
                            f"#### Test")

                        output_forecast.markdown(
                            f"##### Error")

                        error = round(np.sqrt(error), 2)

                        error_ = f"{error:,}"

                        output_forecast.markdown(
                            f"<h2 style = 'text-align: center; color: black;'>{error_} [Kcfd]</h2>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            "<hr/>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"##### Akaike Information Criterion (AIC): " + str(round(model_fit.aic, 2)))

                        testModelSummary = output_forecast.beta_expander(
                            'Test Model Summary')
                        testModelSummary.write(
                            model_fit.summary())

                        output_forecast.markdown(
                            "<hr/>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"#### Forecast")

                        output_forecast.markdown(
                            f"##### Akaike Information Criterion (AIC): " + str(round(model_fit_.aic, 2)))

                        forecastModelSummary = output_forecast.beta_expander(
                            'Forecast Model Summary')
                        forecastModelSummary.write(
                            model_fit_.summary())

                    elif forecastModel_Type == 'Prophet':
                        output_forecast.markdown(
                            f"### Test")

                        output_forecast.markdown(
                            f"#### Error")

                        error = round(error, 2)

                        error_ = f"{error:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{error_} [Kcfd]</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Production")

                        output_forecast.markdown(
                            f"#### Gas Cum Production [Mcf]")

                        gasProduced_ = round(data_df['production'].sum(), 2)
                        gasProduced = f"{gasProduced_:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{gasProduced}</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Forecast")

                        gasForecast_ = round(fcst['fcst'].sum(), 2)
                        gasForecast = f"{gasForecast_:,}"

                        output_forecast.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecast}</h4>", unsafe_allow_html=True)

                        forecastBoundariesExpander = st.beta_expander(
                            'Forecast Boundaries')

                        forecastBoundariesExpander.markdown(
                            f"#### Forecast (Upper Boundary)")

                        gasForecastUpper_ = round(fcst['fcst_upper'].sum(), 2)
                        gasForecastUpper = f"{gasForecastUpper_:,}"

                        forecastBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecastUpper}</h4>", unsafe_allow_html=True)

                        forecastBoundariesExpander.markdown(
                            f"#### Forecast (Lower Boundary)")

                        gasForecastLower_ = round(fcst['fcst_lower'].sum(), 2)
                        gasForecastLower = f"{gasForecastLower_:,}"

                        forecastBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecastLower}</h4>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### EUR")

                        EUR = round(gasProduced_ + gasForecast_, 2)
                        EUR_ = f"{EUR:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{EUR_}</h3>", unsafe_allow_html=True)

                        EURBoundariesExpander = st.beta_expander(
                            'EUR Boundaries')

                        EURBoundariesExpander.markdown(
                            f"#### EUR (Upper Boundary)")

                        EURUpper_ = round(gasProduced_ + gasForecastUpper_, 2)
                        EURUpper = f"{EURUpper_:,}"

                        EURBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{EURUpper}</h4>", unsafe_allow_html=True)

                        EURBoundariesExpander.markdown(
                            f"##### EUR (Lower Boundary)")

                        EURLower_ = round(gasProduced_ + gasForecastLower_, 2)
                        EURLower = f"{EURLower_:,}"

                        EURBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{EURLower}</h4>", unsafe_allow_html=True)

                    elif forecastModel_Type == 'ARIMA':
                        output_forecast.markdown(
                            f"### Test")

                        output_forecast.markdown(
                            f"#### Error")

                        error = round(error, 2)

                        error_ = f"{error:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{error_} [Kcfd]</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Production")

                        output_forecast.markdown(
                            f"#### Gas Cum Production [Mcf]")

                        gasProduced_ = round(data_df['production'].sum(), 2)
                        gasProduced = f"{gasProduced_:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{gasProduced}</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Forecast")

                        gasForecast_ = round(fcst['fcst'].sum(), 2)
                        gasForecast = f"{gasForecast_:,}"

                        output_forecast.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecast}</h4>", unsafe_allow_html=True)

                        forecastBoundariesExpander = st.beta_expander(
                            'Forecast Boundaries')

                        forecastBoundariesExpander.markdown(
                            f"#### Forecast (Upper Boundary)")

                        gasForecastUpper_ = round(fcst['fcst_upper'].sum(), 2)
                        gasForecastUpper = f"{gasForecastUpper_:,}"

                        forecastBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecastUpper}</h4>", unsafe_allow_html=True)

                        forecastBoundariesExpander.markdown(
                            f"#### Forecast (Lower Boundary)")

                        gasForecastLower_ = round(fcst['fcst_lower'].sum(), 2)
                        gasForecastLower = f"{gasForecastLower_:,}"

                        forecastBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecastLower}</h4>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### EUR")

                        EUR = round(gasProduced_ + gasForecast_, 2)
                        EUR_ = f"{EUR:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{EUR_}</h3>", unsafe_allow_html=True)

                        EURBoundariesExpander = st.beta_expander(
                            'EUR Boundaries')

                        EURBoundariesExpander.markdown(
                            f"#### EUR (Upper Boundary)")

                        EURUpper_ = round(gasProduced_ + gasForecastUpper_, 2)
                        EURUpper = f"{EURUpper_:,}"

                        EURBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{EURUpper}</h4>", unsafe_allow_html=True)

                        EURBoundariesExpander.markdown(
                            f"##### EUR (Lower Boundary)")

                        EURLower_ = round(gasProduced_ + gasForecastLower_, 2)
                        EURLower = f"{EURLower_:,}"

                        EURBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{EURLower}</h4>", unsafe_allow_html=True)

                    elif forecastModel_Type == 'SARIMA':
                        output_forecast.markdown(
                            f"### Test")

                        output_forecast.markdown(
                            f"#### Error")

                        error = round(error, 2)

                        error_ = f"{error:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{error_} [Kcfd]</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Production")

                        output_forecast.markdown(
                            f"#### Gas Cum Production [Mcf]")

                        gasProduced_ = round(data_df['production'].sum(), 2)
                        gasProduced = f"{gasProduced_:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{gasProduced}</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Forecast")

                        gasForecast_ = round(fcst['fcst'].sum(), 2)
                        gasForecast = f"{gasForecast_:,}"

                        output_forecast.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecast}</h4>", unsafe_allow_html=True)

                        forecastBoundariesExpander = st.beta_expander(
                            'Forecast Boundaries')

                        forecastBoundariesExpander.markdown(
                            f"#### Forecast (Upper Boundary)")

                        gasForecastUpper_ = round(fcst['fcst_upper'].sum(), 2)
                        gasForecastUpper = f"{gasForecastUpper_:,}"

                        forecastBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecastUpper}</h4>", unsafe_allow_html=True)

                        forecastBoundariesExpander.markdown(
                            f"#### Forecast (Lower Boundary)")

                        gasForecastLower_ = round(fcst['fcst_lower'].sum(), 2)
                        gasForecastLower = f"{gasForecastLower_:,}"

                        forecastBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecastLower}</h4>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### EUR")

                        EUR = round(gasProduced_ + gasForecast_, 2)
                        EUR_ = f"{EUR:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{EUR_}</h3>", unsafe_allow_html=True)

                        EURBoundariesExpander = st.beta_expander(
                            'EUR Boundaries')

                        EURBoundariesExpander.markdown(
                            f"#### EUR (Upper Boundary)")

                        EURUpper_ = round(gasProduced_ + gasForecastUpper_, 2)
                        EURUpper = f"{EURUpper_:,}"

                        EURBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{EURUpper}</h4>", unsafe_allow_html=True)

                        EURBoundariesExpander.markdown(
                            f"##### EUR (Lower Boundary)")

                        EURLower_ = round(gasProduced_ + gasForecastLower_, 2)
                        EURLower = f"{EURLower_:,}"

                        EURBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{EURLower}</h4>", unsafe_allow_html=True)

                    elif forecastModel_Type == 'LSTM':
                        output_forecast.markdown(
                            f"### Test")

                        output_forecast.markdown(
                            f"#### Error")

                        error = round(error, 2)

                        error_ = f"{error:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{error_} [Kcfd]</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Production")

                        output_forecast.markdown(
                            f"#### Gas Cum Production [Mcf]")

                        gasProduced_ = round(data_df['production'].sum(), 2)
                        gasProduced = f"{gasProduced_:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{gasProduced}</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Forecast")

                        gasForecast_ = round(fcst['fcst'].sum(), 2)
                        gasForecast = f"{gasForecast_:,}"

                        output_forecast.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecast}</h4>", unsafe_allow_html=True)

                        forecastBoundariesExpander = st.beta_expander(
                            'Forecast Boundaries')

                        forecastBoundariesExpander.markdown(
                            f"#### Forecast (Upper Boundary)")

                        gasForecastUpper_ = round(fcst['fcst_upper'].sum(), 2)
                        gasForecastUpper = f"{gasForecastUpper_:,}"

                        forecastBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecastUpper}</h4>", unsafe_allow_html=True)

                        forecastBoundariesExpander.markdown(
                            f"#### Forecast (Lower Boundary)")

                        gasForecastLower_ = round(fcst['fcst_lower'].sum(), 2)
                        gasForecastLower = f"{gasForecastLower_:,}"

                        forecastBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecastLower}</h4>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### EUR")

                        EUR = round(gasProduced_ + gasForecast_, 2)
                        EUR_ = f"{EUR:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{EUR_}</h3>", unsafe_allow_html=True)

                        EURBoundariesExpander = st.beta_expander(
                            'EUR Boundaries')

                        EURBoundariesExpander.markdown(
                            f"#### EUR (Upper Boundary)")

                        EURUpper_ = round(gasProduced_ + gasForecastUpper_, 2)
                        EURUpper = f"{EURUpper_:,}"

                        EURBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{EURUpper}</h4>", unsafe_allow_html=True)

                        EURBoundariesExpander.markdown(
                            f"##### EUR (Lower Boundary)")

                        EURLower_ = round(gasProduced_ + gasForecastLower_, 2)
                        EURLower = f"{EURLower_:,}"

                        EURBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{EURLower}</h4>", unsafe_allow_html=True)

                    elif forecastModel_Type == 'Linear':
                        output_forecast.markdown(
                            f"### Test")

                        output_forecast.markdown(
                            f"#### Error")

                        error = round(error, 2)

                        error_ = f"{error:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{error_} [Kcfd]</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Production")

                        output_forecast.markdown(
                            f"#### Gas Cum Production [Mcf]")

                        gasProduced_ = round(data_df['production'].sum(), 2)
                        gasProduced = f"{gasProduced_:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{gasProduced}</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Forecast")

                        gasForecast_ = round(fcst['fcst'].sum(), 2)
                        gasForecast = f"{gasForecast_:,}"

                        output_forecast.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecast}</h4>", unsafe_allow_html=True)

                        forecastBoundariesExpander = st.beta_expander(
                            'Forecast Boundaries')

                        forecastBoundariesExpander.markdown(
                            f"#### Forecast (Upper Boundary)")

                        gasForecastUpper_ = round(fcst['fcst_upper'].sum(), 2)
                        gasForecastUpper = f"{gasForecastUpper_:,}"

                        forecastBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecastUpper}</h4>", unsafe_allow_html=True)

                        forecastBoundariesExpander.markdown(
                            f"#### Forecast (Lower Boundary)")

                        gasForecastLower_ = round(fcst['fcst_lower'].sum(), 2)
                        gasForecastLower = f"{gasForecastLower_:,}"

                        forecastBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecastLower}</h4>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### EUR")

                        EUR = round(gasProduced_ + gasForecast_, 2)
                        EUR_ = f"{EUR:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{EUR_}</h3>", unsafe_allow_html=True)

                        EURBoundariesExpander = st.beta_expander(
                            'EUR Boundaries')

                        EURBoundariesExpander.markdown(
                            f"#### EUR (Upper Boundary)")

                        EURUpper_ = round(gasProduced_ + gasForecastUpper_, 2)
                        EURUpper = f"{EURUpper_:,}"

                        EURBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{EURUpper}</h4>", unsafe_allow_html=True)

                        EURBoundariesExpander.markdown(
                            f"##### EUR (Lower Boundary)")

                        EURLower_ = round(gasProduced_ + gasForecastLower_, 2)
                        EURLower = f"{EURLower_:,}"

                        EURBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{EURLower}</h4>", unsafe_allow_html=True)

                    elif forecastModel_Type == 'Quadratic':
                        output_forecast.markdown(
                            f"### Test")

                        output_forecast.markdown(
                            f"#### Error")

                        error = round(error, 2)

                        error_ = f"{error:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{error_} [Kcfd]</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Production")

                        output_forecast.markdown(
                            f"#### Gas Cum Production [Mcf]")

                        gasProduced_ = round(data_df['production'].sum(), 2)
                        gasProduced = f"{gasProduced_:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{gasProduced}</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Forecast")

                        gasForecast_ = round(fcst['fcst'].sum(), 2)
                        gasForecast = f"{gasForecast_:,}"

                        output_forecast.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecast}</h4>", unsafe_allow_html=True)

                        forecastBoundariesExpander = st.beta_expander(
                            'Forecast Boundaries')

                        forecastBoundariesExpander.markdown(
                            f"#### Forecast (Upper Boundary)")

                        gasForecastUpper_ = round(fcst['fcst_upper'].sum(), 2)
                        gasForecastUpper = f"{gasForecastUpper_:,}"

                        forecastBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecastUpper}</h4>", unsafe_allow_html=True)

                        forecastBoundariesExpander.markdown(
                            f"#### Forecast (Lower Boundary)")

                        gasForecastLower_ = round(fcst['fcst_lower'].sum(), 2)
                        gasForecastLower = f"{gasForecastLower_:,}"

                        forecastBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecastLower}</h4>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### EUR")

                        EUR = round(gasProduced_ + gasForecast_, 2)
                        EUR_ = f"{EUR:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{EUR_}</h3>", unsafe_allow_html=True)

                        EURBoundariesExpander = st.beta_expander(
                            'EUR Boundaries')

                        EURBoundariesExpander.markdown(
                            f"#### EUR (Upper Boundary)")

                        EURUpper_ = round(gasProduced_ + gasForecastUpper_, 2)
                        EURUpper = f"{EURUpper_:,}"

                        EURBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{EURUpper}</h4>", unsafe_allow_html=True)

                        EURBoundariesExpander.markdown(
                            f"##### EUR (Lower Boundary)")

                        EURLower_ = round(gasProduced_ + gasForecastLower_, 2)
                        EURLower = f"{EURLower_:,}"

                        EURBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{EURLower}</h4>", unsafe_allow_html=True)

                    elif forecastModel_Type == 'Holt-Winter':
                        output_forecast.markdown(
                            f"### Test")

                        output_forecast.markdown(
                            f"#### Error")

                        error = round(error, 2)

                        error_ = f"{error:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{error_} [Kcfd]</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Production")

                        output_forecast.markdown(
                            f"#### Gas Cum Production [Mcf]")

                        gasProduced_ = round(data_df['production'].sum(), 2)
                        gasProduced = f"{gasProduced_:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{gasProduced}</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Forecast")

                        gasForecast_ = round(fcst['fcst'].sum(), 2)
                        gasForecast = f"{gasForecast_:,}"

                        output_forecast.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecast}</h4>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### EUR")

                        EUR = round(gasProduced_ + gasForecast_, 2)
                        EUR_ = f"{EUR:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{EUR_}</h3>", unsafe_allow_html=True)

                    elif forecastModel_Type == 'Theta':
                        output_forecast.markdown(
                            f"### Test")

                        output_forecast.markdown(
                            f"#### Error")

                        error = round(error, 2)

                        error_ = f"{error:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{error_} [Kcfd]</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Production")

                        output_forecast.markdown(
                            f"#### Gas Cum Production [Mcf]")

                        gasProduced_ = round(data_df['production'].sum(), 2)
                        gasProduced = f"{gasProduced_:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{gasProduced}</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Forecast")

                        gasForecast_ = round(fcst['fcst'].sum(), 2)
                        gasForecast = f"{gasForecast_:,}"

                        output_forecast.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecast}</h4>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### EUR")

                        EUR = round(gasProduced_ + gasForecast_, 2)
                        EUR_ = f"{EUR:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{EUR_}</h3>", unsafe_allow_html=True)

                    elif forecastModel_Type == 'Bi-variate':
                        output_forecast.markdown(
                            f"### Test")

                        output_forecast.markdown(
                            f"#### Error")

                        error = round(error, 2)

                        error_ = f"{error:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{error_} [Kcfd]</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Production")

                        output_forecast.markdown(
                            f"#### Gas Cum Production [Mcf]")

                        gasProduced_ = round(data_df['production'].sum(), 2)
                        gasProduced = f"{gasProduced_:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{gasProduced}</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Forecast")

                        gasForecast_ = round(fcst['fcst'].sum(), 2)
                        gasForecast = f"{gasForecast_:,}"

                        output_forecast.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecast}</h4>", unsafe_allow_html=True)

                        forecastBoundariesExpander = st.beta_expander(
                            'Forecast Boundaries')

                        forecastBoundariesExpander.markdown(
                            f"#### Forecast (Upper Boundary)")

                        gasForecastUpper_ = round(fcst['fcst_upper'].sum(), 2)
                        gasForecastUpper = f"{gasForecastUpper_:,}"

                        forecastBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecastUpper}</h4>", unsafe_allow_html=True)

                        forecastBoundariesExpander.markdown(
                            f"#### Forecast (Lower Boundary)")

                        gasForecastLower_ = round(fcst['fcst_lower'].sum(), 2)
                        gasForecastLower = f"{gasForecastLower_:,}"

                        forecastBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecastLower}</h4>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### EUR")

                        EUR = round(gasProduced_ + gasForecast_, 2)
                        EUR_ = f"{EUR:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{EUR_}</h3>", unsafe_allow_html=True)

                        EURBoundariesExpander = st.beta_expander(
                            'EUR Boundaries')

                        EURBoundariesExpander.markdown(
                            f"#### EUR (Upper Boundary)")

                        EURUpper_ = round(gasProduced_ + gasForecastUpper_, 2)
                        EURUpper = f"{EURUpper_:,}"

                        EURBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{EURUpper}</h4>", unsafe_allow_html=True)

                        EURBoundariesExpander.markdown(
                            f"##### EUR (Lower Boundary)")

                        EURLower_ = round(gasProduced_ + gasForecastLower_, 2)
                        EURLower = f"{EURLower_:,}"

                        EURBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{EURLower}</h4>", unsafe_allow_html=True)

            elif moduleSelection == 'Hyperparameter tuning':

                forecastModelType = [
                    'ARIMA', 'SARIMA', 'Prophet', 'LSTM']

                forecastModel_Type = forecast_params.selectbox(
                    'Forecast Model Type', forecastModelType)

                modelParametersExpander = forecast_params.beta_expander(
                    'Model Parameters')

                #################################
                # Data Loading

                data = load_data()

                data_df = copy.deepcopy(data)

                data_df.rename(
                    {'Date': 'time', 'Gas Production [Kcfd]': 'production'}, axis=1, inplace=True)

                data_df['time'] = pd.to_datetime(
                    data_df.time, format='%m/%d/%Y')

                #################################
                # Check if there is any null value in the data

                nullTest = data_df['production'].isnull(
                ).values.any()

                if (nullTest == True):
                    data_df['production'] = data_df['production'].fillna(
                        0)

                #################################

                if (seasonalityType == 'Daily'):
                    seasonalityPeriod = 1
                elif (seasonalityType == 'Monthly'):
                    seasonalityPeriod = 30
                elif (seasonalityType == 'Yearly'):
                    seasonalityPeriod = 365
                else:
                    seasonalityPeriod = seriesParameters.slider('Period:',
                                                                min_value=1, value=30, max_value=365)
                #############################################

                dataSeasonal = seasonal_decompose(
                    data_df['production'], model=seasonalityType, period=seasonalityPeriod)

                #################################

                # Forecast Parameters
                total_days = len(data_df['time'])

                test_days = forecastParameters.slider('Test (days):',
                                                      min_value=0, value=2030, max_value=total_days)

                train_days = forecastParameters.slider('Train (days):',
                                                       min_value=0, value=total_days-test_days, max_value=total_days)

                predictionPeriod = forecastParameters.slider(
                    'Predict (days):', min_value=1, value=1825, max_value=3650)

                train_first = data_df['time'].iloc[0].date()
                train_end = data_df['time'].iloc[train_days].date()

                test_first = data_df['time'].iloc[train_days+1].date()
                test_end = data_df['time'].iloc[-1].date()

                forecastParameters.markdown('### Train')
                train_start_date = forecastParameters.date_input(
                    'Start date', train_first)
                train_end_date = forecastParameters.date_input(
                    'End date', train_end)

                if train_start_date > train_end_date:
                    forecastParameters.error(
                        'Error: End date must fall after start date.')

                forecastParameters.markdown('### Test')

                test_start_date = forecastParameters.date_input(
                    'Start date ', test_first)
                test_end_date = forecastParameters.date_input(
                    'End date ', test_end)

                if test_start_date > test_end_date:
                    forecastParameters.error(
                        'Error: End date must fall after start date.')

                #############################################

                data_df_ = pd.concat(
                    [data_df['time'], dataSeasonal.trend], axis=1)

                data_df_.columns = ['time', 'production']

                #################################
                # Check if there is any null value in the data

                nullTest = data_df_['production'].isnull(
                ).values.any()

                # Delete rows with NA values
                if (nullTest == True):
                    data_df_ = data_df_.dropna()

                #################################

                # Train - Test Split

                train_ts = data_df_[0:train_days]
                test_ts = data_df_[train_days+1:]

                #################################

                # Convert to Prophet Time Series format

                train_ts_ = TimeSeriesData(train_ts)

                #############################################

                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=data_df['time'], y=data_df['production'], name='Production (Original)', line=dict(color='gray', width=0.5)))

                fig.add_trace(go.Scatter(
                    x=train_ts['time'], y=train_ts['production'], name='Train | Production (Original)', line=dict(color='red')))

                fig.add_trace(go.Scatter(
                    x=test_ts['time'], y=test_ts['production'], name='Test | Production (Original)', line=dict(color='green')))

                fig.add_hline(y=economicLimit,  line_width=1,
                              line_dash="dash", line_color="black")

                fig.add_vrect(x0=train_start_date, x1=train_end_date,
                              line_width=0, fillcolor="red", opacity=0.05)
                fig.add_vrect(x0=test_start_date, x1=test_end_date,
                              line_width=0, fillcolor="green", opacity=0.05)

                fig.add_vline(x=train_start_date,  line_width=1,
                              line_dash="dash", line_color="black")
                fig.add_vline(x=train_end_date,  line_width=1,
                              line_dash="dash", line_color="red")

                fig.add_vline(x=test_start_date,  line_width=1,
                              line_dash="dash", line_color="green")

                fig.add_vline(x=test_end_date,  line_width=1,
                              line_dash="dash", line_color="green")

                fig.update_layout(legend=dict(
                    orientation="h",
                ),
                    # showlegend=False,
                    autosize=True,
                    width=1000,
                    height=550,
                    margin=dict(
                    l=50,
                    r=0,
                    b=0,
                    t=0,
                    pad=0
                ))
                fig.update_yaxes(automargin=False)

                forecast_plot.plotly_chart(fig)

                ########################################################

                if forecastModel_Type == 'ARIMA':
                    # Model Parameters Range Selection
                    p = modelParametersExpander.slider(
                        'p:', min_value=0, value=[1, 3], max_value=10, help='Order of Auto-Regressive Model (AR), or periods (See ACF plot).')

                    d = modelParametersExpander.slider(
                        'd: ', min_value=0, value=[1, 3], max_value=2, help='Order of Differentiation in order to make the series stationary (See Differentiating plot).')

                    q = modelParametersExpander.slider(
                        'q:', min_value=0, value=[1, 3], max_value=10, help='Dependency on error of the previous lagged values (Moving Average, MA) (See PACF plot)')

                    ###############################################
                    # Parameters for the ARIMA model Grid Search
                    parameters_grid_search = [
                        {
                            "name": "p",
                            "type": "choice",
                            "values": list(range(p[0], p[1])),
                            "value_type": "int",
                            "is_ordered": True,
                        },
                        {
                            "name": "d",
                            "type": "choice",
                            "values": list(range(d[0], d[1])),
                            "value_type": "int",
                            "is_ordered": True,
                        },
                        {
                            "name": "q",
                            "type": "choice",
                            "values": list(range(q[0], q[1])),
                            "value_type": "int",
                            "is_ordered": True,
                        },
                    ]

                    ###############################################

                    parameter_tuner_grid = tpt.SearchMethodFactory.create_search_method(
                        objective_name="evaluation_metric",
                        parameters=parameters_grid_search,
                        selected_search_method=SearchMethodEnum.GRID_SEARCH,
                    )
                    ###############################################

                    # Fit an ARIMA model and calculate the MAE for the test data
                    def evaluation_function(params):
                        arima_params = ARIMAParams(
                            p=params['p'],
                            d=params['d'],
                            q=params['q']
                        )
                        model = ARIMAModel(train_ts_, arima_params)
                        model.fit()
                        model_pred = model.predict(steps=len(test_ts))
                        error = np.mean(
                            np.abs(model_pred['fcst'].values - test_ts['production'].values))

                        return error

                    ###############################################

                    parameter_tuner_grid.generate_evaluate_new_parameter_values(
                        evaluation_function=evaluation_function
                    )

                    # Retrieve parameter tuning results

                    parameter_tuning_results_grid = (
                        parameter_tuner_grid.list_parameter_value_scores()
                    )

                    forecast_plot.markdown('### Grid Search Results')

                    forecast_plot.write(parameter_tuning_results_grid)

                    ###############################################

                elif forecastModel_Type == 'SARIMA':
                    # Model Parameters Range Selection
                    p = modelParametersExpander.slider(
                        'p:', min_value=0, value=[1, 3], max_value=10, help='Order of Auto-Regressive Model (AR), or periods (See ACF plot).')

                    d = modelParametersExpander.slider(
                        'd: ', min_value=0, value=[1, 3], max_value=2, help='Order of Differentiation in order to make the series stationary (See Differentiating plot).')

                    q = modelParametersExpander.slider(
                        'q:', min_value=0, value=[1, 3], max_value=10, help='Dependency on error of the previous lagged values (Moving Average, MA) (See PACF plot)')

                    ###############################################
                    # Parameters for the ARIMA model Grid Search
                    parameters_grid_search = [
                        {
                            "name": "p",
                            "type": "choice",
                            "values": list(range(p[0], p[1])),
                            "value_type": "int",
                            "is_ordered": True,
                        },
                        {
                            "name": "d",
                            "type": "choice",
                            "values": list(range(d[0], d[1])),
                            "value_type": "int",
                            "is_ordered": True,
                        },
                        {
                            "name": "q",
                            "type": "choice",
                            "values": list(range(q[0], q[1])),
                            "value_type": "int",
                            "is_ordered": True,
                        },
                    ]

                    ###############################################

                    parameter_tuner_grid = tpt.SearchMethodFactory.create_search_method(
                        objective_name="evaluation_metric",
                        parameters=parameters_grid_search,
                        selected_search_method=SearchMethodEnum.GRID_SEARCH,
                    )
                    ###############################################

                    # Fit an ARIMA model and calculate the MAE for the test data
                    def evaluation_function(params):
                        arima_params = SARIMAParams(
                            p=params['p'],
                            d=params['d'],
                            q=params['q']
                        )
                        model = SARIMAModel(train_ts_, arima_params)
                        model.fit()
                        model_pred = model.predict(steps=len(test_ts))
                        error = np.mean(
                            np.abs(model_pred['fcst'].values - test_ts['production'].values))

                        return error

                    ###############################################

                    parameter_tuner_grid.generate_evaluate_new_parameter_values(
                        evaluation_function=evaluation_function
                    )

                    # Retrieve parameter tuning results

                    parameter_tuning_results_grid = (
                        parameter_tuner_grid.list_parameter_value_scores()
                    )

                    forecast_plot.markdown('### Grid Search Results')

                    forecast_plot.write(parameter_tuning_results_grid)

                    ###############################################

                elif forecastModel_Type == 'Prophet':
                    # Model Parameters Range Selection
                    n_changepoints = modelParametersExpander.slider(
                        'Number of change points:', min_value=0, value=[55, 60], max_value=100, help='Number of potential changepoints to include. Not used if input changepoints is supplied. If changepoints is not supplied, then n_changepoints potential changepoints are selected uniformly from the first changepoint_range proportion of the history.')

                    uncertainty_samples = modelParametersExpander.slider(
                        'Uncertainty Samples', min_value=0, value=[1000, 1002], max_value=len(data_df_), help='Number of simulated draws used to estimate uncertainty intervals. Settings this value to 0 will disable uncertainty estimation and speed up the calculation.')
                    ###############################################
                    # Parameters for the ARIMA model Grid Search
                    parameters_grid_search = [
                        {
                            "name": "n_changepoints",
                            "type": "choice",
                            "values": list(range((int(n_changepoints[0])), (int(n_changepoints[1])))),
                            "value_type": "int",
                            "is_ordered": True,
                        },
                        {
                            "name": "uncertainty_samples",
                            "type": "choice",
                            "values": list(range((int(uncertainty_samples[0])), (int(uncertainty_samples[1])))),
                            "value_type": "int",
                            "is_ordered": True,
                        }
                    ]

                    ###############################################

                    parameter_tuner_grid = tpt.SearchMethodFactory.create_search_method(
                        objective_name="evaluation_metric",
                        parameters=parameters_grid_search,
                        selected_search_method=SearchMethodEnum.GRID_SEARCH,
                    )
                    ###############################################

                    # Fit an ARIMA model and calculate the MAE for the test data
                    def evaluation_function(params):
                        prophet_params = ProphetParams(
                            n_changepoints=params['n_changepoints'],
                            uncertainty_samples=params['uncertainty_samples']
                        )
                        model = ProphetModel(train_ts_, prophet_params)
                        model.fit()
                        model_pred = model.predict(steps=len(test_ts))
                        error = np.mean(
                            np.abs(model_pred['fcst'].values - test_ts['production'].values))

                        return error

                    ###############################################

                    parameter_tuner_grid.generate_evaluate_new_parameter_values(
                        evaluation_function=evaluation_function
                    )

                    # Retrieve parameter tuning results

                    parameter_tuning_results_grid = (
                        parameter_tuner_grid.list_parameter_value_scores()
                    )

                    forecast_plot.markdown('### Grid Search Results')

                    forecast_plot.write(parameter_tuning_results_grid)

                    ###############################################

                elif forecastModel_Type == 'LSTM':
                    # Model Parameters Range Selection
                    epochs = modelParametersExpander.slider(
                        'Epochs', min_value=1, value=[2, 5], max_value=100, help='Training epochs.')
                    hidden_size = modelParametersExpander.slider(
                        'Hidden Size', min_value=1, value=[2, 5], max_value=100, help='Training epochs.')
                    time_window = modelParametersExpander.slider(
                        'Time Window', min_value=1, value=[2, 5], max_value=100, help='Training epochs.')

                    ###############################################
                    # Parameters for the ARIMA model Grid Search
                    parameters_grid_search = [
                        {
                            "name": "epochs",
                            "type": "choice",
                            "values": list(range((int(epochs[0])), (int(epochs[1])))),
                            "value_type": "int",
                            "is_ordered": True,
                        },
                        {
                            "name": "hidden_size",
                            "type": "choice",
                            "values": list(range((int(hidden_size[0])), (int(hidden_size[1])))),
                            "value_type": "int",
                            "is_ordered": True,
                        },
                        {
                            "name": "time_window",
                            "type": "choice",
                            "values": list(range((int(time_window[0])), (int(time_window[1])))),
                            "value_type": "int",
                            "is_ordered": True,
                        }
                    ]

                    ###############################################

                    parameter_tuner_grid = tpt.SearchMethodFactory.create_search_method(
                        objective_name="evaluation_metric",
                        parameters=parameters_grid_search,
                        selected_search_method=SearchMethodEnum.GRID_SEARCH,
                    )
                    ###############################################

                    # Fit an ARIMA model and calculate the MAE for the test data
                    def evaluation_function(params):
                        prophet_params = LSTMParams(
                            num_epochs=params['epochs'],
                            hidden_size=params['hidden_size'],
                            time_window=params['time_window']
                        )
                        model = LSTMModel(train_ts_, prophet_params)
                        model.fit()
                        model_pred = model.predict(steps=len(test_ts))
                        error = np.mean(
                            np.abs(model_pred['fcst'].values - test_ts['production'].values))

                        return error

                    ###############################################

                    parameter_tuner_grid.generate_evaluate_new_parameter_values(
                        evaluation_function=evaluation_function
                    )

                    # Retrieve parameter tuning results

                    parameter_tuning_results_grid = (
                        parameter_tuner_grid.list_parameter_value_scores()
                    )

                    forecast_plot.markdown('### Grid Search Results')

                    forecast_plot.write(parameter_tuning_results_grid)

                    ###############################################

            elif moduleSelection == 'Backtesting':

                backtester_errors = {}

                modelParametersExpander = forecast_params.beta_expander(
                    'Model Parameters')

                forecastModel_Type = 'ARIMA'

                #################################
                # Data Loading

                data = load_data()

                data_df = copy.deepcopy(data)

                data_df.rename(
                    {'Date': 'time', 'Gas Production [Kcfd]': 'production'}, axis=1, inplace=True)

                data_df['time'] = pd.to_datetime(
                    data_df.time, format='%m/%d/%Y')

                #################################
                # Check if there is any null value in the data

                nullTest = data_df['production'].isnull(
                ).values.any()

                if (nullTest == True):
                    data_df['production'] = data_df['production'].fillna(
                        0)

                #################################

                if (seasonalityType == 'Daily'):
                    seasonalityPeriod = 1
                elif (seasonalityType == 'Monthly'):
                    seasonalityPeriod = 30
                elif (seasonalityType == 'Yearly'):
                    seasonalityPeriod = 365
                else:
                    seasonalityPeriod = seriesParameters.slider('Period:',
                                                                min_value=1, value=30, max_value=365)
                #############################################

                dataSeasonal = seasonal_decompose(
                    data_df['production'], model=seasonalityType, period=seasonalityPeriod)

                #################################

                # Forecast Parameters
                total_days = len(data_df['time'])

                test_days = forecastParameters.slider('Test (days):',
                                                      min_value=0, value=2030, max_value=total_days)

                train_days = forecastParameters.slider('Train (days):',
                                                       min_value=0, value=total_days-test_days, max_value=total_days)

                predictionPeriod = forecastParameters.slider(
                    'Predict (days):', min_value=1, value=1825, max_value=3650)

                train_first = data_df['time'].iloc[0].date()
                train_end = data_df['time'].iloc[train_days].date()

                test_first = data_df['time'].iloc[train_days+1].date()
                test_end = data_df['time'].iloc[-1].date()

                forecastParameters.markdown('### Train')
                train_start_date = forecastParameters.date_input(
                    'Start date', train_first)
                train_end_date = forecastParameters.date_input(
                    'End date', train_end)

                if train_start_date > train_end_date:
                    forecastParameters.error(
                        'Error: End date must fall after start date.')

                forecastParameters.markdown('### Test')

                test_start_date = forecastParameters.date_input(
                    'Start date ', test_first)
                test_end_date = forecastParameters.date_input(
                    'End date ', test_end)

                if test_start_date > test_end_date:
                    forecastParameters.error(
                        'Error: End date must fall after start date.')

                #############################################

                data_df_ = pd.concat(
                    [data_df['time'], dataSeasonal.trend], axis=1)

                data_df_.columns = ['time', 'production']

                #################################
                # Check if there is any null value in the data

                nullTest = data_df_['production'].isnull(
                ).values.any()

                # Delete rows with NA values
                if (nullTest == True):
                    data_df_ = data_df_.dropna()

                #################################

                # Train - Test Split

                train_ts = data_df_[0:train_days]
                test_ts = data_df_[train_days+1:]

                #################################

                # Convert to Prophet Time Series format

                train_ts_ = TimeSeriesData(train_ts)

                #############################################

                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=data_df['time'], y=data_df['production'], name='Production (Original)', line=dict(color='gray', width=0.5)))

                fig.add_trace(go.Scatter(
                    x=train_ts['time'], y=train_ts['production'], name='Train | Production (Original)', line=dict(color='red')))

                fig.add_trace(go.Scatter(
                    x=test_ts['time'], y=test_ts['production'], name='Test | Production (Original)', line=dict(color='green')))

                fig.add_hline(y=economicLimit,  line_width=1,
                              line_dash="dash", line_color="black")

                fig.add_vrect(x0=train_start_date, x1=train_end_date,
                              line_width=0, fillcolor="red", opacity=0.05)
                fig.add_vrect(x0=test_start_date, x1=test_end_date,
                              line_width=0, fillcolor="green", opacity=0.05)

                fig.add_vline(x=train_start_date,  line_width=1,
                              line_dash="dash", line_color="black")
                fig.add_vline(x=train_end_date,  line_width=1,
                              line_dash="dash", line_color="red")

                fig.add_vline(x=test_start_date,  line_width=1,
                              line_dash="dash", line_color="green")

                fig.add_vline(x=test_end_date,  line_width=1,
                              line_dash="dash", line_color="green")

                fig.update_layout(legend=dict(
                    orientation="h",
                ),
                    # showlegend=False,
                    autosize=True,
                    width=1000,
                    height=550,
                    margin=dict(
                    l=50,
                    r=0,
                    b=0,
                    t=0,
                    pad=0
                ))
                fig.update_yaxes(automargin=False)

                forecast_plot.plotly_chart(fig)

                ########################################################
                # Parameters
                p = modelParametersExpander.slider(
                    'p:', min_value=0, value=1, max_value=10, help='Order of Auto-Regressive Model (AR), or periods (See ACF plot).')

                d = modelParametersExpander.slider(
                    'd: ', min_value=0, value=1, max_value=2, help='Order of Differentiation in order to make the series stationary (See Differentiating plot).')

                q = modelParametersExpander.slider(
                    'q:', min_value=0, value=1, max_value=10, help='Dependency on error of the previous lagged values (Moving Average, MA) (See PACF plot).')

                ########################################################
                # ARIMA
                params = ARIMAParams(p=p, d=d, q=q)
                ALL_ERRORS = ['mape', 'smape', 'mae', 'mase', 'mse', 'rmse']

                backtester_arima = BackTesterSimple(
                    error_methods=ALL_ERRORS,
                    data=train_ts_,
                    params=params,
                    train_percentage=75,
                    test_percentage=25,
                    model_class=ARIMAModel)

                backtester_arima.run_backtest()

                #########

                backtester_errors['arima'] = {}
                for error, value in backtester_arima.errors.items():
                    backtester_errors['arima'][error] = value

                ########################################################
                # SARIMA
                params = SARIMAParams(p=p, d=d, q=q)
                ALL_ERRORS = ['mape', 'smape', 'mae', 'mase', 'mse', 'rmse']

                backtester_sarima = BackTesterSimple(
                    error_methods=ALL_ERRORS,
                    data=train_ts_,
                    params=params,
                    train_percentage=75,
                    test_percentage=25,
                    model_class=SARIMAModel)

                backtester_sarima.run_backtest()

                #########

                backtester_errors['sarima'] = {}
                for error, value in backtester_sarima.errors.items():
                    backtester_errors['sarima'][error] = value

                # ########################################################
                # # Prophet

                # # additive mode gives worse results
                # params_prophet = ProphetParams(
                #     seasonality_mode='multiplicative')

                # backtester_prophet = BackTesterSimple(
                #     error_methods=ALL_ERRORS,
                #     data=train_ts_,
                #     params=params_prophet,
                #     train_percentage=75,
                #     test_percentage=25,
                #     model_class=ProphetModel)

                # backtester_prophet.run_backtest()

                # backtester_errors['prophet'] = {}
                # for error, value in backtester_prophet.errors.items():
                #     backtester_errors['prophet'][error] = value

                ########################################################

                output_forecast.markdown('## Backtesting Output')
                output_forecast.write(
                    pd.DataFrame.from_dict(backtester_errors))
