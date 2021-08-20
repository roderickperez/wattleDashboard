import streamlit as st
import copy
import time
import io
import base64
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
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


# PyCaret
from pycaret.regression import *

warnings.simplefilter('ignore')


def app():
    st.markdown('# Production Forecast')

    def load_data():

        data = pd.read_csv(
            'data/VMM1_AllWells_DetailedProduction_Updated.csv', header=None, infer_datetime_format=True)

        # data = pd.DataFrame(data).dropna()
        data.columns = ['Date', 'DP in H2O', 'Well Head Pressure [PSI]', 'Casing Pressure [Psi]',
                        'Choque Fijo', 'Choque Adjustable', 'After Opening to 14/64" Current Flowrate',
                        'Current Uplift (14/64") [MCFD]', 'Temp Line [°F]', 'Pressure Line [PSI]', 'Heater Temperature [°F]',
                        'Orifice Plate', 'Gas Production [Kcfd]', 'After Opening to 12/64" Current Flowrate',
                        'Current Uplift (12/64") [MCFD]', 'Gas Comsuption [Kcfd]', 'Volumen Oil [Bbls]',
                        'Volumen Condensate [bls/d]', 'Volumen Water [bls/d]', 'Ambient Temperature [°F]',
                        'Tubing Head Temperature [°F]',  'Well Name']

        if moduleSelection == 'Forecast Bi-variate (Prophet)':
            data = data[data['Well Name'] == selected_well]
            data = data[['Date', variable_1, variable_2]]
            data.reset_index(drop=True, inplace=True)

            return data

        elif moduleSelection == 'PyCaret' and numberVariables == 1:

            data = data[data['Well Name'] == selected_well]
            #data = data[['Date', variable_1]]
            #data.reset_index(drop=True, inplace=True)

            return data

        elif moduleSelection == 'PyCaret' and numberVariables == 2:

            data = data[data['Well Name'] == selected_well]
            # data = data[['Date', variable_1, variable_2]]
            # data.reset_index(drop=True, inplace=True)

            return data

        else:

            data = data[data['Well Name'] == selected_well]
            data = data[['Date', 'Gas Production [Kcfd]']]
            data.reset_index(drop=True, inplace=True)

            return data

    ##################################

    forecast_params, forecast_plot, output_forecast = st.columns(
        (1, 3, 1))

    with forecast_params:

        forecast_params.markdown('### Parameters')

        economicParameters = forecast_params.expander(
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

            seriesParameters = forecast_params.expander(
                'Seasonality')

            seasonalityMode = ['Daily', 'Monthly', 'Yearly', 'Custom']

            seasonalityType = seriesParameters.radio(
                'Mode', seasonalityMode, index=0)

            #############################################

            forecast_params.markdown('#### Forecast')

            forecastParameters = forecast_params.expander(
                'Dates')

            #################################
            moduleSelection = forecast_params.radio(
                'Forecast Model Type', ['Prophet', 'PyCaret', 'Forecast Bi-variate (Prophet)', 'Hyperparameter tuning', 'Backtesting'])

            if moduleSelection == 'Prophet':

                forecastModelType = [
                    'Prophet', 'ARIMA', 'SARIMA', 'LSTM', 'Linear', 'Quadratic', 'Holt-Winter', 'Theta', 'Ensamble']

                forecastModel_Type = forecast_params.selectbox(
                    'Forecast Model Type', forecastModelType)

                modelParametersExpander = forecast_params.expander(
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

                train_perct = forecastParameters.slider('Train (days):',
                                                        min_value=0.05, value=0.7, max_value=1.0, step=0.05)
                test_perct = forecastParameters.slider('Test (days):',
                                                       min_value=0.0, value=1.0-train_perct, max_value=0.90, step=0.05)

                date_first = data_df['time'].iloc[0].date()

                date_end = data_df['time'].iloc[-1].date()

                predictionPeriod = forecastParameters.slider(
                    'Predict (days):', min_value=1, value=1825, max_value=3650)

                start_date = forecastParameters.date_input(
                    'Start date', date_first)

                end_date = forecastParameters.date_input(
                    'End date ', date_end)

                if start_date > end_date:
                    forecastParameters.error(
                        'Error: End date must fall after start date.')

                start_date_ = pd.to_datetime(start_date)
                end_date_ = pd.to_datetime(end_date)

                start_date_index = data_df[data_df['time']
                                           == start_date_].index[0]

                end_date_index = data_df[data_df['time']
                                         == end_date_].index[0]

                ############ Data Loading ############

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
                total_days = int(len(data_df_))

                # Train - Test Split

                train_ts = data_df_[start_date_index:(
                    int(total_days*train_perct))]
                test_ts = data_df_[(
                    int(total_days*train_perct)):]

                #################################

                # Convert to Prophet Time Series format

                train_ts_ = TimeSeriesData(train_ts)

                #################################

                if forecast_params.button('Forecast'):

                    if forecastModel_Type == 'Prophet':

                        #################################
                        # Parameters

                        # Check extra parameters: https://facebookresearch.github.io/Kats/api/kats.models.prophet.html
                        # https://github.com/facebook/prophet/blob/master/python/prophet/forecaster.py
                        prophet_Growth = modelParametersExpander.radio(
                            'Seasonal Model Type', ['linear', 'logistic'], help='String ‘linear’ or ‘logistic’ to specify a linear or logistic trend.')

                        n_changepoints = modelParametersExpander.slider(
                            'Number of change points:', min_value=1, value=10, max_value=100, help='Number of potential changepoints to include. Not used if input changepoints is supplied. If changepoints is not supplied, then n_changepoints potential changepoints are selected uniformly from the first changepoint_range proportion of the history.')

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
                            'Interval Width', min_value=0.00, value=0.95, max_value=1.00, help='Width of the uncertainty intervals provided for the forecast.')
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
                        m.fit()

                        #################################
                        # Test Results with Test Data

                        pred = m.predict(steps=len(test_ts))

                        # forecast_plot.write(pred)

                        # forecast_plot.write(len(pred))

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
                        m_.fit()

                        fcst = m_.predict(steps=predictionPeriod)

                    elif forecastModel_Type == 'ARIMA':

                        #################################
                        # Parameters

                        # Check extra parameters: https://facebookresearch.github.io/Kats/api/kats.models.arima.html
                        arima_p = modelParametersExpander.slider(
                            'p:', min_value=0, value=0, max_value=5, help='Order of Auto-Regressive Model (AR), or periods (See ACF plot).')

                        arima_d = modelParametersExpander.slider(
                            'd: ', min_value=0, value=0, max_value=3, help='Order of Differentiation in order to make the series stationary (See Differentiating plot).')

                        arima_q = modelParametersExpander.slider(
                            'q:', min_value=0, value=0, max_value=5, help='Dependency on error of the previous lagged values (Moving Average, MA) (See PACF plot)')

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
                        m.fit()

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
                        m_.fit()

                        fcst = m_.predict(steps=predictionPeriod)

                    elif forecastModel_Type == 'SARIMA':

                        #################################
                        # Parameters

                        # Check extra parameters: https://facebookresearch.github.io/Kats/api/kats.models.sarima.html
                        sarima_p = modelParametersExpander.slider(
                            'p:', min_value=0, value=0, max_value=5, help='Order of Auto-Regressive Model (AR), or periods (See ACF plot).')

                        sarima_d = modelParametersExpander.slider(
                            'd: ', min_value=0, value=0, max_value=3, help='Order of Differentiation in order to make the series stationary (See Differentiating plot).')

                        sarima_q = modelParametersExpander.slider(
                            'q:', min_value=0, value=0, max_value=5, help='Dependency on error of the previous lagged values (Moving Average, MA) (See PACF plot)')

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
                        m.fit()

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
                        m_.fit()

                        fcst = m_.predict(steps=predictionPeriod)

                    elif forecastModel_Type == 'LSTM':

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
                        m.fit()

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
                        m_.fit()

                        fcst = m_.predict(steps=predictionPeriod)

                    elif forecastModel_Type == 'Linear':

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
                        m.fit()

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
                        m_.fit()

                        fcst = m_.predict(steps=predictionPeriod)

                    elif forecastModel_Type == 'Quadratic':

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
                        m.fit()

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
                        m_.fit()

                        fcst = m_.predict(steps=predictionPeriod)

                    elif forecastModel_Type == 'Holt-Winter':

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
                        m.fit()

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
                        m_.fit()

                        fcst = m_.predict(steps=predictionPeriod, alpha=alpha)

                    elif forecastModel_Type == 'Theta':

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
                        m.fit()

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
                        m_.fit()

                        fcst = m_.predict(steps=predictionPeriod, alpha=alpha)

                    # elif forecastModel_Type == 'Ensamble':

                        # ##################################

                        # # Data Preparation

                        # data = load_data()

                        # data_df = copy.deepcopy(data)

                        # data_df.rename(
                        #     {'Date': 'time', 'Gas Production [Kcfd]': 'production'}, axis=1, inplace=True)

                        # # convert to TimeSeriesData object

                        # data_ts = TimeSeriesData(data_df)

                        # ##################################

                        # st.write("Select models to add into ensamble")
                        # checkProphet = st.checkbox('Prophet', value=True)
                        # checkARIMA = st.checkbox('ARIMA', value=False)

                        # if checkProphet:
                        #     pass
                        # if checkARIMA:
                        #     pass

                        # # we need define params for each individual forecasting model in `EnsembleParams` class
                        # # here we include 6 different models
                        # model_params = EnsembleParams(
                        #     [
                        #         BaseModelParams(
                        #             "arima",
                        #             ARIMAParams(
                        #                 p=1,
                        #                 d=1,
                        #                 q=1)),
                        #         BaseModelParams("prophet", ProphetParams()),
                        #     ]
                        # )

                        # prophetSeasonality = ['Multiplicative', 'Additive']

                        # prophet_seasonality = modelParametersExpander.radio(
                        #     'Seasonal Model Type', prophetSeasonality)

                        # # create `KatsEnsembleParam` with detailed configurations
                        # KatsEnsembleParam = {
                        #     "models": model_params,
                        #     "aggregation": "median",
                        #     "seasonality_length": 2,
                        #     "decomposition_method": prophet_seasonality,
                        # }

                        # # create 'KatsEnsemble' model
                        # m = KatsEnsemble(
                        #     data=data_ts,
                        #     params=KatsEnsembleParam
                        # )

                        # ##################################
                        # # Fit the model
                        # m.fit()

                        # #####################################
                        # # Generate forecast values

                        # fcst = m.predict(steps=predictionPeriod)

                        # # aggregate individual model results
                        # m.aggregate()

                    ##################################

                    with forecast_plot:

                        fig = go.Figure()

                        fig.add_trace(go.Scatter(
                            x=data_df['time'], y=data_df['production'], name='Production (Original)', line=dict(color='gray', width=0.5)))

                        fig.add_trace(go.Scatter(
                            x=train_ts['time'], y=train_ts['production'], name='Train | Production (Original)', line=dict(color='red')))

                        fig.add_trace(go.Scatter(
                            x=test_ts['time'], y=test_ts['production'], name='Test | Production (Original)', line=dict(color='green')))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred['fcst'], name='Test',
                            mode='markers', marker=dict(color='blue', size=2)))

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

                        fig.add_vrect(x0=train_ts['time'].iloc[0].date(), x1=train_ts['time'].iloc[-1].date(),
                                      line_width=0, fillcolor="red", opacity=0.05)
                        fig.add_vrect(x0=test_ts['time'].iloc[0].date(), x1=test_ts['time'].iloc[-1].date(),
                                      line_width=0, fillcolor="green", opacity=0.05)

                        fig.add_vline(x=train_ts['time'].iloc[0].date(),  line_width=1,
                                      line_dash="dash", line_color="black")
                        fig.add_vline(x=train_ts['time'].iloc[-1].date(),  line_width=1,
                                      line_dash="dash", line_color="red")

                        fig.add_vline(x=test_ts['time'].iloc[0].date(),  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.add_vline(x=test_ts['time'].iloc[-1].date(),  line_width=1,
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

                        testResultsExpander = forecast_plot.expander(
                            'Test Result')

                        testResultsExpander.write(pred)

                        # Forecast Results

                        forecastResultsExpander = forecast_plot.expander(
                            'Forecast Result')

                        forecastResultsExpander.write(fcst)

                    with output_forecast:
                        output_forecast.markdown('## Forecast Output')

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

                        forecastBoundariesExpander = st.expander(
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

                        EURBoundariesExpander = st.expander(
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

            elif moduleSelection == 'PyCaret':

                modelParametersExpander = forecast_params.expander(
                    'Model Parameters')

                numberVariables = modelParametersExpander.radio(
                    'Number of Variables', [1, 2], index=0)

                ##############################
                data = load_data()

                data['time'] = pd.to_datetime(
                    data.Date, format='%m/%d/%Y')

                data.reset_index(drop=True, inplace=True)

                ##############################

                # Forecast Parameters

                train_perct = forecastParameters.slider('Train (days):',
                                                        min_value=0.05, value=0.8, max_value=1.0, step=0.05)
                test_perct = forecastParameters.slider('Test (days):',
                                                       min_value=0.0, value=1.0-train_perct, max_value=0.90, step=0.05)

                date_first = data['time'].iloc[0].date()

                date_end = data['time'].iloc[-1].date()

                predictionPeriod = forecastParameters.slider(
                    'Predict (days):', min_value=1, value=1825, max_value=3650, step=1)

                start_date = forecastParameters.date_input(
                    'Start date', date_first)

                end_date = forecastParameters.date_input(
                    'End date ', date_end)

                ##############################

                if start_date > end_date:
                    forecastParameters.error(
                        'Error: End date must fall after start date.')

                start_date_ = pd.to_datetime(start_date)
                end_date_ = pd.to_datetime(end_date)

                start_date_index = data[data['time']
                                        == start_date_].index[0]

                end_date_index = data[data['time']
                                      == end_date_].index[0]

                # Original data for plotting
                data_ = copy.deepcopy(data)

                data = data.iloc[start_date_index:end_date_index+1]

                #########################################

                if numberVariables == 1:

                    data_df = copy.deepcopy(data)

                    columns1 = ['Gas Production [Kcfd]', 'Well Head Pressure [PSI]', 'Pressure Line [PSI]', 'DP in H2O', 'Casing Pressure [Psi]', 'Choque Fijo', 'Choque Adjustable', 'After Opening to 14/64" Current Flowrate',
                                'Current Uplift (14/64") [MCFD]', 'Temp Line [°F]', 'Heater Temperature [°F]', 'Orifice Plate', 'After Opening to 12/64" Current Flowrate', 'Current Uplift (12/64") [MCFD]', 'Gas Comsuption [Kcfd]', 'Volumen Oil [Bbls]', 'Volumen Condensate [bls/d]', 'Volumen Water [bls/d]', 'Ambient Temperature [°F]', 'Tubing Head Temperature [°F]']
                    variable_1 = modelParametersExpander.selectbox(
                        "1st Variable (Target):", columns1)

                    data_df = data_df[['time', variable_1]]

                    data_df.rename(
                        {variable_1: 'V1'}, axis=1, inplace=True)

                    # #################################
                    # # Check if there is any null value in the data

                    # nullTest = data_df['V1'].isnull(
                    # ).values.any()

                    # if (nullTest == True):
                    #     data_df['V1'] = data_df['V1'].fillna(
                    #         0)

                    # #################################

                    # if (seasonalityType == 'Daily'):
                    #     seasonalityPeriod = 1
                    # elif (seasonalityType == 'Monthly'):
                    #     seasonalityPeriod = 30
                    # elif (seasonalityType == 'Yearly'):
                    #     seasonalityPeriod = 365
                    # else:
                    #     seasonalityPeriod = seriesParameters.slider('Period:',
                    #                                                 min_value=1, value=30, max_value=365)
                    # #############################################

                    # dataSeasonal = seasonal_decompose(
                    #     data_df['V1'], model=seasonalityType, period=seasonalityPeriod)

                    # #################################

                    # data_df = pd.concat(
                    #     [data_df['time'], dataSeasonal.trend], axis=1)

                    data_df.columns = ['time', 'V1']

                elif numberVariables == 2:

                    data_df = copy.deepcopy(data)

                    columns1 = ['Gas Production [Kcfd]', 'Well Head Pressure [PSI]', 'Pressure Line [PSI]', 'DP in H2O', 'Casing Pressure [Psi]', 'Choque Fijo', 'Choque Adjustable', 'After Opening to 14/64" Current Flowrate',
                                'Current Uplift (14/64") [MCFD]', 'Temp Line [°F]', 'Heater Temperature [°F]', 'Orifice Plate', 'After Opening to 12/64" Current Flowrate', 'Current Uplift (12/64") [MCFD]', 'Gas Comsuption [Kcfd]', 'Volumen Oil [Bbls]', 'Volumen Condensate [bls/d]', 'Volumen Water [bls/d]', 'Ambient Temperature [°F]', 'Tubing Head Temperature [°F]']
                    variable_1 = modelParametersExpander.selectbox(
                        "1st Variable:", columns1)

                    columns2 = ['Well Head Pressure [PSI]', 'Pressure Line [PSI]', 'DP in H2O', 'Casing Pressure [Psi]', 'Choque Fijo', 'Choque Adjustable', 'After Opening to 14/64" Current Flowrate',
                                'Current Uplift (14/64") [MCFD]', 'Temp Line [°F]', 'Heater Temperature [°F]', 'Orifice Plate', 'Gas Production [Kcfd]', 'After Opening to 12/64" Current Flowrate', 'Current Uplift (12/64") [MCFD]', 'Gas Comsuption [Kcfd]', 'Volumen Oil [Bbls]', 'Volumen Condensate [bls/d]', 'Volumen Water [bls/d]', 'Ambient Temperature [°F]', 'Tubing Head Temperature [°F]']

                    variable_2 = modelParametersExpander.selectbox(
                        "2nd Variable:", columns2)

                    data_df = data_df[['time', variable_1, variable_1]]

                    data_df.rename(
                        {variable_1: 'V1', variable_2: 'V2'}, axis=1, inplace=True)

                    # #################################

                    # if (seasonalityType == 'Daily'):
                    #     seasonalityPeriod = 1
                    # elif (seasonalityType == 'Monthly'):
                    #     seasonalityPeriod = 30
                    # elif (seasonalityType == 'Yearly'):
                    #     seasonalityPeriod = 365
                    # else:
                    #     seasonalityPeriod = seriesParameters.slider('Period:',
                    #                                                 min_value=1, value=30, max_value=365)
                    # #############################################

                    # dataSeasonal_V1 = seasonal_decompose(
                    #     data_df['V1'], model=seasonalityType, period=seasonalityPeriod)

                    # V1 = pd.DataFrame(dataSeasonal_V1.trend)

                    # V1.rename(columns={'trend': 'V1'}, inplace=True)

                    # dataSeasonal_V2 = seasonal_decompose(
                    #     data_df['V2'], model=seasonalityType, period=seasonalityPeriod)

                    # V2 = pd.DataFrame(dataSeasonal_V2.trend)

                    # V2.rename(columns={'trend': 'V2'}, inplace=True)

                    # dataSeasonal = pd.concat(
                    #     [V1, V2], axis=1)

                    # data_df_ = pd.concat(
                    #     [data_df['time'], dataSeasonal], axis=1)

                    data_df.columns = ['time', 'V1', 'V2']

                # #################################
                # # Check if there is any null value in the data

                # nullTest = data_df.isnull(
                # ).values.any()

                # # Delete rows with NA values
                # if (nullTest == True):
                #     data_df = data_df.dropna()

                #################################
                # Train - Test Split for Plotting

                total_days = int(len(data_df))

                train_ts = data_df[:(
                    int(total_days*train_perct))]
                test_ts = data_df[(
                    int(total_days*train_perct)):]

                # Original Data

                data_df_ = copy.deepcopy(data_df)

                data_df_['Day'] = [i.day for i in data_df_['time']]
                data_df_['Month'] = [i.month for i in data_df_['time']]
                data_df_['Year'] = [i.year for i in data_df_[
                    'time']]
                # drop unnecessary columns and re-arrange
                data_df_['Series'] = np.arange(1, len(data_df_)+1)
                #data_df_.drop(['Date', 'MA12'], axis=1, inplace=True)

                # Train

                train_ts_ = copy.deepcopy(train_ts)

                train_ts_['Day'] = [i.day for i in train_ts['time']]
                train_ts_['Month'] = [i.month for i in train_ts['time']]
                train_ts_['Year'] = [i.year for i in train_ts[
                    'time']]
                # drop unnecessary columns and re-arrange
                train_ts_['Series'] = np.arange(1, len(train_ts)+1)
                #data_df_.drop(['Date', 'MA12'], axis=1, inplace=True)

                # Test

                test_ts_ = copy.deepcopy(test_ts)

                test_ts_['Day'] = [i.day for i in test_ts['time']]
                test_ts_['Month'] = [i.month for i in test_ts['time']]
                test_ts_['Year'] = [i.year for i in test_ts[
                    'time']]
                # drop unnecessary columns and re-arrange
                test_ts_['Series'] = np.arange(1, len(test_ts)+1)
                #data_df_.drop(['Date', 'MA12'], axis=1, inplace=True)

                #################################
                # Reorganize the columns in dataframe
                if numberVariables == 1:
                    train_ts_ = train_ts_[
                        ['Series', 'Day', 'Month', 'Year', 'V1']]

                    test_ts_ = test_ts_[
                        ['Series', 'Day', 'Month', 'Year', 'V1']]

                elif numberVariables == 2:
                    train_ts_ = train_ts_[
                        ['Series', 'Day', 'Month', 'Year', 'V1', 'V2']]

                    test_ts_ = test_ts_[
                        ['Series', 'Day', 'Month', 'Year', 'V1', 'V2']]

                #################################

                # Parameters
                fold = modelParametersExpander.slider('Fold', min_value=0, value=10, max_value=20, step=1,
                                                      help='Number of folds for cross-validation. Increasing the value will increase the accuracy but will take more time.')

                polynomial_features = modelParametersExpander.radio(
                    'Polynomial Features', [True, False], index=1, help='When set to True, new features are derived using existing numeric features.')

                trigonometry_features = modelParametersExpander.radio(
                    'Trigonometry Features', [True, False], index=1, help='When set to True, new features are created based on all trigonometric combinations that exist within the numeric features in a dataset to the degree defined in the polynomial_degree param.')

                feature_interaction = modelParametersExpander.radio(
                    'Feature Interaction', [True, False], index=1, help='When set to True, new features are created by interacting (a * b) all the numeric variables in the dataset. This feature is not scalable and may not work as expected on datasets with large feature space.')

                if forecast_params.button('Forecast'):

                    #################################
                    # initialize setup

                    if numberVariables == 1:
                        s = setup(data=train_ts_, test_data=test_ts_,
                                  target='V1', fold_strategy='timeseries', fold=fold,
                                  numeric_features=['Series', 'Day', 'Month', 'Year'], session_id=123, silent=True,
                                  verbose=False, polynomial_features=polynomial_features, trigonometry_features=trigonometry_features,
                                  feature_interaction=feature_interaction)

                    elif numberVariables == 2:
                        s = setup(data=train_ts_, test_data=test_ts_,
                                  target='V1', fold_strategy='timeseries', fold=fold,
                                  session_id=123, silent=True,
                                  verbose=False, polynomial_features=polynomial_features, trigonometry_features=trigonometry_features,
                                  feature_interaction=feature_interaction)

                    best = compare_models(sort='MAE')

                    best_tuned = tune_model(best)

                    final_best = finalize_model(best_tuned)

                    prediction_holdout = predict_model(best_tuned)

                    data_df_selection = pd.concat(
                        [train_ts, test_ts], axis=0)

                    data_df_selection_ = pd.concat(
                        [train_ts_, test_ts_], axis=0)

                    pred_ = predict_model(best, data=data_df_selection_)

                    pred = copy.deepcopy(data_df_selection)
                    pred['fcst'] = pred_['Label']

                    #####################################
                    # Calculate Test Error
                    error = np.mean(
                        np.abs(pred_['Label'].values - pred_['V1'].values))

                    #################################
                    # Future dates
                    future_dates = pd.date_range(
                        start=end_date_, periods=predictionPeriod, freq='D')

                    future_dates_ = pd.DataFrame({'time': future_dates})

                    future_df = pd.DataFrame()

                    future_df['Day'] = [i.day for i in future_dates]
                    future_df['Month'] = [i.month for i in future_dates]
                    future_df['Year'] = [i.year for i in future_dates]
                    future_df['Series'] = np.arange(
                        len(data_df), (len(data_df)+len(future_dates)))

                    #################################
                    # Now, let’s use the future_df to score and generate predictions.

                    predictions_future = predict_model(
                        final_best, data=future_df)

                    # #################################
                    fcst = pd.concat(
                        [future_dates_, predictions_future['Label']], axis=1)

                    fcst.columns = ['time', 'fcst']

                    #################################

                    with forecast_plot:

                        fig = go.Figure()

                        fig.add_trace(go.Scatter(
                            x=data_['time'], y=data_[variable_1], name='Production (Original)', line=dict(color='gray', width=0.5)))

                        fig.add_trace(go.Scatter(
                            x=train_ts['time'], y=train_ts['V1'], name='Train | Production (Original)', line=dict(color='red')))

                        fig.add_trace(go.Scatter(
                            x=test_ts['time'], y=test_ts['V1'], name='Test | Production (Original)', line=dict(color='green')))

                        fig.add_trace(go.Scatter(
                            x=pred['time'], y=pred[
                                'fcst'], name='Test', line=dict(color='magenta', width=2.0)))

                        # fig.add_trace(go.Scatter(
                        #     x=pred['time'], y=pred[
                        #         'fcst_tuned'], name='Test (Tuned)',
                        #     mode='markers', marker=dict(color='blue', size=2)))

                        fig.add_trace(go.Scatter(
                            x=fcst['time'], y=fcst['fcst'], name='Forecast'))

                        fig.add_hline(y=economicLimit,  line_width=1,
                                      line_dash="dash", line_color="black")

                        fig.add_vrect(x0=train_ts['time'].iloc[0].date(), x1=train_ts['time'].iloc[-1].date(),
                                      line_width=0, fillcolor="red", opacity=0.05)
                        fig.add_vrect(x0=test_ts['time'].iloc[0].date(), x1=test_ts['time'].iloc[-1].date(),
                                      line_width=0, fillcolor="green", opacity=0.05)

                        fig.add_vline(x=train_ts['time'].iloc[0].date(),  line_width=1,
                                      line_dash="dash", line_color="black")
                        fig.add_vline(x=train_ts['time'].iloc[-1].date(),  line_width=1,
                                      line_dash="dash", line_color="red")

                        fig.add_vline(x=test_ts['time'].iloc[0].date(),  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.add_vline(x=test_ts['time'].iloc[-1].date(),  line_width=1,
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

                        testResultsExpander = forecast_plot.expander(
                            'Test Result')

                        testResultsExpander.write(pred)

                        # Forecast Results

                        forecastResultsExpander = forecast_plot.expander(
                            'Forecast Result')

                        forecastResultsExpander.write(fcst)

                        def st_pandas_to_csv_download_link(_df: pd.DataFrame, file_name: str = "dataframe.csv"):
                            csv_exp = _df.to_csv(index=False)
                            # some strings <-> bytes conversions necessary here
                            b64 = base64.b64encode(csv_exp.encode()).decode()
                            href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}" > Download Dataframe (CSV) </a>'
                            forecastResultsExpander.markdown(
                                href, unsafe_allow_html=True)

                        st_pandas_to_csv_download_link(
                            fcst, file_name="pred.csv")

                    with output_forecast:
                        output_forecast.markdown('## Forecast Output')

                        output_forecast.markdown(
                            f"### Model")

                        output_forecast.markdown(
                            f"<h4 style = 'text-align: center; color: blue;'>{best.__class__.__name__}</h4>", unsafe_allow_html=True)

                        st.markdown("<hr/>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Test")

                        output_forecast.markdown(
                            f"#### Error")

                        error = round(error, 2)

                        error_ = f"{error:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{error_} [Kcfd]</h3>", unsafe_allow_html=True)

                        # output_forecast.markdown(
                        #     f"#### Error (Tuned)")

                        # error_tuned = round(error_tuned, 2)

                        # error_tuned_ = f"{error_tuned:,}"

                        # output_forecast.markdown(
                        #     f"<h3 style = 'text-align: center; color: black;'>{error_tuned_} [Kcfd]</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Production")

                        output_forecast.markdown(
                            f"#### Gas Cum Production [Mcf]")

                        gasProduced_ = round(data_df['V1'].sum(), 2)
                        gasProduced = f"{gasProduced_:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{gasProduced}</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Forecast")

                        gasForecast_ = round(fcst['fcst'].sum(), 2)
                        gasForecast = f"{gasForecast_:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{gasForecast}</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### EUR")

                        EUR = round(gasProduced_ + gasForecast_, 2)
                        EUR_ = f"{EUR:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{EUR_}</h3>", unsafe_allow_html=True)

            elif moduleSelection == 'Hyperparameter tuning':

                if forecast_params.button('Run'):

                    forecastModelType = [
                        'ARIMA', 'SARIMA', 'Prophet', 'LSTM']

                    forecastModel_Type = forecast_params.selectbox(
                        'Forecast Model Type', forecastModelType)

                    modelParametersExpander = forecast_params.expander(
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

                    train_perct = forecastParameters.slider('Train (days):',
                                                            min_value=0.0, value=0.7, max_value=1.0)
                    test_perct = forecastParameters.slider('Test (days):',
                                                           min_value=0.0, value=1.0-train_perct, max_value=1.0)

                    date_first = data_df['time'].iloc[0].date()

                    date_end = data_df['time'].iloc[-1].date()

                    predictionPeriod = forecastParameters.slider(
                        'Predict (days):', min_value=1, value=1825, max_value=3650)

                    start_date = forecastParameters.date_input(
                        'Start date', date_first)

                    end_date = forecastParameters.date_input(
                        'End date ', date_end)

                    if start_date > end_date:
                        forecastParameters.error(
                            'Error: End date must fall after start date.')

                    start_date_ = pd.to_datetime(start_date)
                    end_date_ = pd.to_datetime(end_date)

                    start_date_index = data_df[data_df['time']
                                               == start_date_].index[0]

                    end_date_index = data_df[data_df['time']
                                             == end_date_].index[0]

                    ############ Data Loading ############

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
                    total_days = int(len(data_df_))

                    # Train - Test Split

                    train_ts = data_df_[start_date_index:(
                        int(total_days*train_perct))]
                    test_ts = data_df_[(
                        int(total_days*train_perct)):]

                    #################################

                    # Convert to Prophet Time Series format

                    train_ts_ = TimeSeriesData(train_ts)

                    #################################

                    with forecast_plot:

                        fig = go.Figure()

                        fig.add_trace(go.Scatter(
                            x=data_df['time'], y=data_df['production'], name='Production (Original)', line=dict(color='gray', width=0.5)))

                        fig.add_trace(go.Scatter(
                            x=train_ts['time'], y=train_ts['production'], name='Train | Production (Original)', line=dict(color='red')))

                        fig.add_trace(go.Scatter(
                            x=test_ts['time'], y=test_ts['production'], name='Test | Production (Original)', line=dict(color='green')))

                        fig.add_hline(y=economicLimit,  line_width=1,
                                      line_dash="dash", line_color="black")

                        fig.add_vrect(x0=train_ts['time'].iloc[0].date(), x1=train_ts['time'].iloc[-1].date(),
                                      line_width=0, fillcolor="red", opacity=0.05)
                        fig.add_vrect(x0=test_ts['time'].iloc[0].date(), x1=test_ts['time'].iloc[-1].date(),
                                      line_width=0, fillcolor="green", opacity=0.05)

                        fig.add_vline(x=train_ts['time'].iloc[0].date(),  line_width=1,
                                      line_dash="dash", line_color="black")
                        fig.add_vline(x=train_ts['time'].iloc[-1].date(),  line_width=1,
                                      line_dash="dash", line_color="red")

                        fig.add_vline(x=test_ts['time'].iloc[0].date(),  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.add_vline(x=test_ts['time'].iloc[-1].date(),  line_width=1,
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
                            'p:', min_value=0, value=[0, 3], max_value=5, help='Order of Auto-Regressive Model (AR), or periods (See ACF plot).')

                        d = modelParametersExpander.slider(
                            'd: ', min_value=0, value=[0, 2], max_value=2, help='Order of Differentiation in order to make the series stationary (See Differentiating plot).')

                        q = modelParametersExpander.slider(
                            'q:', min_value=0, value=[0, 3], max_value=5, help='Dependency on error of the previous lagged values (Moving Average, MA) (See PACF plot)')

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
                            'p:', min_value=0, value=[0, 3], max_value=5, help='Order of Auto-Regressive Model (AR), or periods (See ACF plot).')

                        d = modelParametersExpander.slider(
                            'd: ', min_value=0, value=[0, 2], max_value=2, help='Order of Differentiation in order to make the series stationary (See Differentiating plot).')

                        q = modelParametersExpander.slider(
                            'q:', min_value=0, value=[0, 3], max_value=5, help='Dependency on error of the previous lagged values (Moving Average, MA) (See PACF plot)')

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

            elif moduleSelection == 'Forecast Bi-variate (Prophet)':

                columns1 = ['Gas Production [Kcfd]', 'Well Head Pressure [PSI]', 'Pressure Line [PSI]', 'DP in H2O', 'Casing Pressure [Psi]', 'Choque Fijo', 'Choque Adjustable', 'After Opening to 14/64" Current Flowrate',
                            'Current Uplift (14/64") [MCFD]', 'Temp Line [°F]', 'Heater Temperature [°F]', 'Orifice Plate', 'After Opening to 12/64" Current Flowrate', 'Current Uplift (12/64") [MCFD]', 'Gas Comsuption [Kcfd]', 'Volumen Oil [Bbls]', 'Volumen Condensate [bls/d]', 'Volumen Water [bls/d]', 'Ambient Temperature [°F]', 'Tubing Head Temperature [°F]']

                columns2 = ['Well Head Pressure [PSI]', 'Pressure Line [PSI]', 'DP in H2O', 'Casing Pressure [Psi]', 'Choque Fijo', 'Choque Adjustable', 'After Opening to 14/64" Current Flowrate',
                            'Current Uplift (14/64") [MCFD]', 'Temp Line [°F]', 'Heater Temperature [°F]', 'Orifice Plate', 'Gas Production [Kcfd]', 'After Opening to 12/64" Current Flowrate', 'Current Uplift (12/64") [MCFD]', 'Gas Comsuption [Kcfd]', 'Volumen Oil [Bbls]', 'Volumen Condensate [bls/d]', 'Volumen Water [bls/d]', 'Ambient Temperature [°F]', 'Tubing Head Temperature [°F]']

                variable_1 = st.selectbox("1st Variable:", columns1)

                variable_2 = st.selectbox("2nd Variable:", columns2)

                ##################################

                # Data Preparation

                data = load_data()

                data_df = copy.deepcopy(data)

                data_df.rename(
                    {'Date': 'time', variable_1: 'V1', variable_2: 'V2'}, axis=1, inplace=True)

                data_df['time'] = pd.to_datetime(
                    data_df.time, format='%m/%d/%Y')

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

                dataSeasonal_V1 = seasonal_decompose(
                    data_df['V1'], model=seasonalityType, period=seasonalityPeriod)

                V1 = pd.DataFrame(dataSeasonal_V1.trend)

                V1.rename(columns={'trend': 'V1'}, inplace=True)

                dataSeasonal_V2 = seasonal_decompose(
                    data_df['V2'], model=seasonalityType, period=seasonalityPeriod)

                V2 = pd.DataFrame(dataSeasonal_V2.trend)

                V2.rename(columns={'trend': 'V2'}, inplace=True)

                dataSeasonal = pd.concat(
                    [V1, V2], axis=1)

                #################################

                # Forecast Parameters

                train_perct = forecastParameters.slider('Train (days):',
                                                        min_value=0.0, value=0.7, max_value=1.0)
                test_perct = forecastParameters.slider('Test (days):',
                                                       min_value=0.0, value=1.0-train_perct, max_value=1.0)

                date_first = data_df['time'].iloc[0].date()

                date_end = data_df['time'].iloc[-1].date()

                predictionPeriod = forecastParameters.slider(
                    'Predict (days):', min_value=1, value=1825, max_value=3650)

                start_date = forecastParameters.date_input(
                    'Start date', date_first)

                end_date = forecastParameters.date_input(
                    'End date ', date_end)

                if start_date > end_date:
                    forecastParameters.error(
                        'Error: End date must fall after start date.')

                start_date_ = pd.to_datetime(start_date)
                end_date_ = pd.to_datetime(end_date)

                start_date_index = data_df[data_df['time']
                                           == start_date_].index[0]

                end_date_index = data_df[data_df['time']
                                         == end_date_].index[0]

                ############ Data Loading ############

                data_df_ = pd.concat(
                    [data_df['time'], dataSeasonal], axis=1)

                data_df_.columns = ['time', 'V1', 'V2']

                # forecast_plot.write(data_df_)

                #################################
                # Check if there is any null value in the data

                nullTest = data_df_.isnull(
                ).values.any()

                if (nullTest == True):
                    data_df_ = data_df_.dropna()

                #################################
                total_days = int(len(data_df_))

                # Train - Test Split

                train_ts = data_df_[start_date_index:(
                    int(total_days*train_perct))]
                test_ts = data_df_[(
                    int(total_days*train_perct)):]

                #################################
                # Parameters
                # Check extra parameters: https://facebookresearch.github.io/Kats/api/_modules/kats/models/var.html
                # https://facebookresearch.github.io/Kats/api/kats.models.var.html

                modelParametersExpander = forecast_params.expander(
                    'Model Parameters')

                trend = modelParametersExpander.radio(
                    'Trend', ['c', 'ct', 'ctt', 'nc'], index=2, help='“c” - add constant (Default), “ct” - constant and trend, “ctt” - constant, linear and quadratic trend, “n”/“nc” - no constant, no trend.')

                alpha = modelParametersExpander.slider(
                    'Alpha', min_value=0.0, value=0.05, max_value=1.0, help='Significance level of confidence interval.')

                params = VARParams(
                    trend=trend,
                )

                if forecast_params.button('Forecast'):

                    # convert to TimeSeriesData object

                    train_ts_ = TimeSeriesData(train_ts)

                    # data_df = TimeSeriesData(data_df_)

                    ##################################
                    # TEST model

                    m = VARModel(train_ts_, params)
                    m.fit()

                    #################################
                    # Test Results with Test Data

                    pred = m.predict(steps=len(test_ts), alpha=alpha)

                    # forecast_plot.write(test_ts)

                    # forecast_plot.write(pred)

                    # predV1 = pd.DataFrame(pred['V1'])

                    # forecast_plot.write(pred['V1'])

                    pred_V1 = pred['V1']
                    predV1 = pred_V1.to_dataframe()

                    pred_V2 = pred['V2']
                    predV2 = pred_V2.to_dataframe()

                    # forecast_plot.write(test_ts)

                    # forecast_plot.write(predV1)

                    #####################################
                    # Calculate Test Error
                    errorV1 = np.mean(
                        np.abs(predV1['fcst'].values - test_ts['V1'].values))

                    errorV2 = np.mean(
                        np.abs(predV1['fcst'].values - test_ts['V2'].values))

                    # forecast_plot.write(errorV1)

                    # forecast_plot.write(errorV2)

                    ##################################
                    # FORECAST model (using the entire time series)

                    # forecast_plot.write(data_df_)

                    # Convert to Prophet Time Series format

                    data_df_ = TimeSeriesData(data_df_)

                    # # forecast_plot.write(data_df_)

                    m_ = VARModel(data_df_, params)
                    m_.fit()

                    fcst = m_.predict(steps=predictionPeriod, alpha=alpha)

                    fcst_V1 = fcst['V1']
                    fcstV1 = fcst_V1.to_dataframe()

                    fcst_V2 = fcst['V2']
                    fcstV2 = fcst_V2.to_dataframe()

                    #############################################

                    with forecast_plot:

                        # Plot

                        fig = go.Figure()

                        fig = make_subplots(
                            rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02)

                        fig.add_trace(go.Scatter(
                            x=data_df['time'], y=data_df['V1'], name='Variable 1 (Original)', line=dict(color='gray', width=0.5)), row=1, col=1)

                        fig.add_trace(go.Scatter(
                            x=train_ts['time'], y=train_ts['V1'], name='Variable 1 | Train (Trend)', line=dict(color='red')), row=1, col=1)

                        fig.add_trace(go.Scatter(
                            x=test_ts['time'], y=test_ts['V1'], name='Variable 1 | Test (Trend)', line=dict(color='green')), row=1, col=1)

                        fig.add_trace(go.Scatter(
                            x=predV1['time'], y=predV1['fcst'], name='Test',
                            mode='markers', marker=dict(color='blue', size=2)), row=1, col=1)

                        fig.add_trace(go.Scatter(
                            x=predV1['time'], y=predV1['fcst_upper'], name='Test (Upper)',
                            line=dict(color='royalblue', width=1, dash='dash')), row=1, col=1)

                        fig.add_trace(go.Scatter(
                            x=predV1['time'], y=predV1['fcst_lower'], name='Test (Lower)',
                            line=dict(color='royalblue', width=1, dash='dash')), row=1, col=1)

                        fig.add_trace(go.Scatter(
                            x=fcstV1['time'], y=fcstV1['fcst'], name='Forecast'), row=1, col=1)

                        fig.add_trace(go.Scatter(
                            x=fcstV1['time'], y=fcstV1['fcst_upper'], name='Forecast (upper)'), row=1, col=1)

                        fig.add_trace(go.Scatter(
                            x=fcstV1['time'], y=fcstV1['fcst_lower'], name='Forecast (lower)', fill='tonexty', mode='none'), row=1, col=1)

                        ####################
                        fig.add_trace(go.Scatter(
                            x=data_df['time'], y=data_df['V2'], name='Variable 2 (Original)', line=dict(color='gray', width=0.5)), row=2, col=1)

                        fig.add_trace(go.Scatter(
                            x=train_ts['time'], y=train_ts['V2'], name='Variable 2 | Train (Trend)', line=dict(color='red')), row=2, col=1)

                        fig.add_trace(go.Scatter(
                            x=test_ts['time'], y=test_ts['V2'], name='Variable 2 | Test (Trend)', line=dict(color='green')), row=2, col=1)

                        fig.add_trace(go.Scatter(
                            x=predV2['time'], y=predV2['fcst'], name='Test',
                            mode='markers', marker=dict(color='blue', size=2)), row=2, col=1)

                        fig.add_trace(go.Scatter(
                            x=predV2['time'], y=predV2['fcst_upper'], name='Test (Upper)',
                            line=dict(color='royalblue', width=1, dash='dash')), row=2, col=1)

                        fig.add_trace(go.Scatter(
                            x=predV2['time'], y=predV2['fcst_lower'], name='Test (Lower)',
                            line=dict(color='royalblue', width=1, dash='dash')), row=2, col=1)

                        fig.add_trace(go.Scatter(
                            x=fcstV2['time'], y=fcstV2['fcst'], name='Forecast'), row=2, col=1)

                        fig.add_trace(go.Scatter(
                            x=fcstV2['time'], y=fcstV2['fcst_upper'], name='Forecast (upper)'), row=2, col=1)

                        fig.add_trace(go.Scatter(
                            x=fcstV2['time'], y=fcstV2['fcst_lower'], name='Forecast (lower)', fill='tonexty', mode='none'), row=2, col=1)

                        fig.add_vrect(x0=train_ts['time'].iloc[0].date(), x1=train_ts['time'].iloc[-1].date(),
                                      line_width=0, fillcolor="red", opacity=0.05)
                        fig.add_vrect(x0=test_ts['time'].iloc[0].date(), x1=test_ts['time'].iloc[-1].date(),
                                      line_width=0, fillcolor="green", opacity=0.05)

                        fig.add_vline(x=train_ts['time'].iloc[0].date(),  line_width=1,
                                      line_dash="dash", line_color="black")
                        fig.add_vline(x=train_ts['time'].iloc[-1].date(),  line_width=1,
                                      line_dash="dash", line_color="red")

                        fig.add_vline(x=test_ts['time'].iloc[0].date(),  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.add_vline(x=test_ts['time'].iloc[-1].date(),  line_width=1,
                                      line_dash="dash", line_color="green")

                        fig.update_layout(legend=dict(
                            orientation="h"
                        ),
                            # showlegend=False,
                            autosize=True,
                            width=1000,
                            height=630,
                            margin=dict(
                            l=50,
                            r=0,
                            b=0,
                            t=0,
                            pad=0
                        ))
                        fig.update_yaxes(automargin=False)

                        forecast_plot.plotly_chart(fig)

                        resultsExpanderV1 = forecast_plot.expander(
                            'Forecast Variable 1')
                        resultsExpanderV1.write(
                            predV1.iloc[-predictionPeriod:])

                        def st_pandas_to_csv_download_link(_df: pd.DataFrame, file_name: str = "dataframe.csv"):
                            csv_exp = _df.to_csv(index=False)
                            # some strings <-> bytes conversions necessary here
                            b64 = base64.b64encode(csv_exp.encode()).decode()
                            href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}" > Download Dataframe (CSV) </a>'
                            resultsExpanderV1.markdown(
                                href, unsafe_allow_html=True)

                        st_pandas_to_csv_download_link(
                            predV1, file_name="predV1.csv")

                        resultsExpanderV2 = forecast_plot.expander(
                            'Forecast Variable 2')
                        resultsExpanderV2.write(
                            predV2.iloc[-predictionPeriod:])

                        def st_pandas_to_csv_download_link(_df: pd.DataFrame, file_name: str = "dataframe.csv"):
                            csv_exp = _df.to_csv(index=False)
                            # some strings <-> bytes conversions necessary here
                            b64 = base64.b64encode(csv_exp.encode()).decode()
                            href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}" > Download Dataframe (CSV) </a>'
                            resultsExpanderV2.markdown(
                                href, unsafe_allow_html=True)

                        st_pandas_to_csv_download_link(
                            predV2, file_name="predV2.csv")

                    with output_forecast:
                        output_forecast.markdown(
                            f"### Test")

                        output_forecast.markdown(
                            f"#### Error V1")

                        errorV1 = round(errorV1, 2)

                        errorV1_ = f"{errorV1:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{errorV1_} [Kcfd]</h3>", unsafe_allow_html=True)

                        #############################

                        output_forecast.markdown(
                            f"#### Error V2")

                        errorV2 = round(errorV2, 2)

                        errorV2_ = f"{errorV2:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{errorV2_} [Kcfd]</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Production")

                        output_forecast.markdown(
                            f"#### Gas Cum Production [Mcf]")

                        gasProduced_ = round(data_df['V1'].sum(), 2)
                        gasProduced = f"{gasProduced_:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{gasProduced}</h3>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### Forecast")

                        gasForecast_ = round(fcstV1['fcst'].sum(), 2)
                        gasForecast = f"{gasForecast_:,}"

                        output_forecast.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecast}</h4>", unsafe_allow_html=True)

                        forecastBoundariesExpander = st.expander(
                            'Forecast Boundaries')

                        forecastBoundariesExpander.markdown(
                            f"#### Forecast (Upper Boundary)")

                        gasForecastUpper_ = round(
                            fcstV1['fcst_upper'].sum(), 2)
                        gasForecastUpper = f"{gasForecastUpper_:,}"

                        forecastBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecastUpper}</h4>", unsafe_allow_html=True)

                        forecastBoundariesExpander.markdown(
                            f"#### Forecast (Lower Boundary)")

                        gasForecastLower_ = round(
                            fcstV1['fcst_lower'].sum(), 2)
                        gasForecastLower = f"{gasForecastLower_:,}"

                        forecastBoundariesExpander.markdown(
                            f"<h4 style = 'text-align: center; color: black;'>{gasForecastLower}</h4>", unsafe_allow_html=True)

                        output_forecast.markdown(
                            f"### EUR")

                        EUR = round(gasProduced_ + gasForecast_, 2)
                        EUR_ = f"{EUR:,}"

                        output_forecast.markdown(
                            f"<h3 style = 'text-align: center; color: black;'>{EUR_}</h3>", unsafe_allow_html=True)

                        EURBoundariesExpander = st.expander(
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

            elif moduleSelection == 'Backtesting':

                backtester_errors = {}

                modelParametersExpander = forecast_params.expander(
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

                train_perct = forecastParameters.slider('Train (days):',
                                                        min_value=0.0, value=0.7, max_value=1.0)
                test_perct = forecastParameters.slider('Test (days):',
                                                       min_value=0.0, value=1.0-train_perct, max_value=1.0)

                date_first = data_df['time'].iloc[0].date()

                date_end = data_df['time'].iloc[-1].date()

                predictionPeriod = forecastParameters.slider(
                    'Predict (days):', min_value=1, value=1825, max_value=3650)

                start_date = forecastParameters.date_input(
                    'Start date', date_first)

                end_date = forecastParameters.date_input(
                    'End date ', date_end)

                if start_date > end_date:
                    forecastParameters.error(
                        'Error: End date must fall after start date.')

                start_date_ = pd.to_datetime(start_date)
                end_date_ = pd.to_datetime(end_date)

                start_date_index = data_df[data_df['time']
                                           == start_date_].index[0]

                end_date_index = data_df[data_df['time']
                                         == end_date_].index[0]

                ############ Data Loading ############

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
                total_days = int(len(data_df_))

                # Train - Test Split

                train_ts = data_df_[start_date_index:(
                    int(total_days*train_perct))]
                test_ts = data_df_[(
                    int(total_days*train_perct)):]

                #################################
                if forecast_params.button('Run'):

                    #################################

                    # Convert to Prophet Time Series format

                    train_ts_ = TimeSeriesData(train_ts)

                    #################################

                    fig = go.Figure()

                    fig.add_trace(go.Scatter(
                        x=data_df['time'], y=data_df['production'], name='Production (Original)', line=dict(color='gray', width=0.5)))

                    fig.add_trace(go.Scatter(
                        x=train_ts['time'], y=train_ts['production'], name='Train | Production (Original)', line=dict(color='red')))

                    fig.add_trace(go.Scatter(
                        x=test_ts['time'], y=test_ts['production'], name='Test | Production (Original)', line=dict(color='green')))

                    fig.add_hline(y=economicLimit,  line_width=1,
                                  line_dash="dash", line_color="black")

                    fig.add_vrect(x0=train_ts['time'].iloc[0].date(), x1=train_ts['time'].iloc[-1].date(),
                                  line_width=0, fillcolor="red", opacity=0.05)
                    fig.add_vrect(x0=test_ts['time'].iloc[0].date(), x1=test_ts['time'].iloc[-1].date(),
                                  line_width=0, fillcolor="green", opacity=0.05)

                    fig.add_vline(x=train_ts['time'].iloc[0].date(),  line_width=1,
                                  line_dash="dash", line_color="black")
                    fig.add_vline(x=train_ts['time'].iloc[-1].date(),  line_width=1,
                                  line_dash="dash", line_color="red")

                    fig.add_vline(x=test_ts['time'].iloc[0].date(),  line_width=1,
                                  line_dash="dash", line_color="green")

                    fig.add_vline(x=test_ts['time'].iloc[-1].date(),  line_width=1,
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
                    ALL_ERRORS = ['mape', 'smape',
                                  'mae', 'mase', 'mse', 'rmse']

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
                    ALL_ERRORS = ['mape', 'smape',
                                  'mae', 'mase', 'mse', 'rmse']

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

                    output_forecast.markdown('## Backtesting Output')
                    output_forecast.write(
                        pd.DataFrame.from_dict(backtester_errors))

        elif forecastType == 'All Wells':
            pass
