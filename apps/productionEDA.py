import streamlit as st
import copy
import numpy as np
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.stattools import pacf, acf
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import pandas as pd
from plotly import graph_objs as go
import matplotlib.pyplot as plt
import itertools
from pandas.plotting import autocorrelation_plot
import warnings

warnings.simplefilter('ignore')


def app():
    st.markdown('# Production')
    st.markdown('## Exploration Data Analysis')

    columns = ['Gas Production [Kcfd]', 'DP in H2O', 'Well Head Pressure [PSI]', 'Casing Pressure [Psi]', 'Choque Fijo', 'Choque Adjustable', 'After Opening to 14/64" Current Flowrate',
               'Current Uplift (14/64") [MCFD]', 'Temp Line [°F]', 'Pressure Line [PSI]', 'Heater Temperature [°F]', 'Orifice Plate', 'After Opening to 12/64" Current Flowrate', 'Current Uplift (12/64") [MCFD]', 'Gas Comsuption [Kcfd]', 'Volumen Oil [Bbls]', 'Volumen Condensate [bls/d]', 'Volumen Water [bls/d]', 'Ambient Temperature [°F]', 'Tubing Head Temperature [°F]']

    # @st.cache
    def load_ALLdata():
        data = pd.read_csv(
            'data/VMM1_AllWells_DetailedProduction_Updated.csv', header=None, infer_datetime_format=True)
        data.columns = ['Date', 'DP in H2O', 'Well Head Pressure [PSI]', 'Casing Pressure [Psi]', 'Choque Fijo', 'Choque Adjustable', 'After Opening to 14/64" Current Flowrate',
                        'Current Uplift (14/64") [MCFD]', 'Temp Line [°F]', 'Pressure Line [PSI]', 'Heater Temperature [°F]', 'Orifice Plate', 'Gas Production [Kcfd]', 'After Opening to 12/64" Current Flowrate', 'Current Uplift (12/64") [MCFD]', 'Gas Comsuption [Kcfd]', 'Volumen Oil [Bbls]', 'Volumen Condensate [bls/d]', 'Volumen Water [bls/d]', 'Ambient Temperature [°F]', 'Tubing Head Temperature [°F]',  'Well Name']
        # data = data[data['Well Name'] == selected_well]

        return data

    def load_data():
        data = pd.read_csv(
            'data/VMM1_AllWells_DetailedProduction_Updated.csv', header=None, infer_datetime_format=True)
        data.columns = ['Date', 'DP in H2O', 'Well Head Pressure [PSI]', 'Casing Pressure [Psi]', 'Choque Fijo', 'Choque Adjustable', 'After Opening to 14/64" Current Flowrate',
                        'Current Uplift (14/64") [MCFD]', 'Temp Line [°F]', 'Pressure Line [PSI]', 'Heater Temperature [°F]', 'Orifice Plate', 'Gas Production [Kcfd]', 'After Opening to 12/64" Current Flowrate', 'Current Uplift (12/64") [MCFD]', 'Gas Comsuption [Kcfd]', 'Volumen Oil [Bbls]', 'Volumen Condensate [bls/d]', 'Volumen Water [bls/d]', 'Ambient Temperature [°F]', 'Tubing Head Temperature [°F]',  'Well Name']
        data = data[data['Well Name'] == selected_well]

        return data

    ##########

    production_params, production_plot, summary_statistics = st.beta_columns(
        (1, 4, 1))

    with production_params:
        st.markdown('## Parameters')

        mode = ['All Wells', 'Single Well']

        modeType = production_params.radio('Mode', mode)

        if (modeType == 'All Wells'):

            data = load_ALLdata()

            data['Date'] = pd.to_datetime(data['Date']).dt.date

            data_caramelo_2 = data[data['Well Name'] == "Caramelo-2"]
            data_caramelo_3 = data[data['Well Name'] == "Caramelo-3"]
            data_toposi_1 = data[data['Well Name'] == "Toposi-1"]
            data_toposi_2H = data[data['Well Name'] == "Toposi-2H"]
            data_laEstancia_1H = data[data['Well Name'] == "LaEstancia-1H"]

            plot_selectionVariable = production_params.selectbox(
                'Feature:', columns)

            plotType = ['Scatter', 'Boxplot', 'Hist']

            plot_Type = production_params.radio('Plot Type', plotType)

            if (plot_Type == 'Scatter'):

                with production_plot:

                    scatterType = ['All', 'Individual']

                    scatter_Type = production_params.radio(
                        'Scatter Type', scatterType)

                    if (scatter_Type == 'All'):

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=data_caramelo_2['Date'], y=data_caramelo_2[plot_selectionVariable], name="Caramelo-2"))
                        fig.layout.update(xaxis_rangeslider_visible=True)

                        fig.add_trace(go.Scatter(
                            x=data_caramelo_3['Date'], y=data_caramelo_3[plot_selectionVariable], name="Caramelo-3"))
                        fig.layout.update(xaxis_rangeslider_visible=True)

                        fig.add_trace(go.Scatter(
                            x=data_toposi_1['Date'], y=data_toposi_1[plot_selectionVariable], name="Toposi-1"))
                        fig.layout.update(xaxis_rangeslider_visible=True)

                        fig.add_trace(go.Scatter(
                            x=data_toposi_2H['Date'], y=data_toposi_2H[plot_selectionVariable], name="Toposi-2H"))
                        fig.layout.update(xaxis_rangeslider_visible=True)

                        fig.add_trace(go.Scatter(
                            x=data_laEstancia_1H['Date'], y=data_laEstancia_1H[plot_selectionVariable], name="La Estancia-1H"))
                        fig.layout.update(xaxis_rangeslider_visible=True)

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
                            width=1150,
                            height=650,
                            margin=dict(
                            l=0,
                            r=0,
                            b=0,
                            t=0,
                            pad=0
                        ))
                        fig.update_yaxes(automargin=False)
                        production_plot.plotly_chart(fig)

                    else:
                        fig = make_subplots(
                            rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.02)

                        fig.add_trace(go.Scatter(
                            x=data_caramelo_2['Date'], y=data_caramelo_2[plot_selectionVariable], name="Caramelo-2"), row=1, col=1)

                        fig.add_trace(go.Scatter(
                            x=data_caramelo_3['Date'], y=data_caramelo_3[plot_selectionVariable], name="Caramelo-3"), row=2, col=1)

                        fig.add_trace(go.Scatter(
                            x=data_toposi_1['Date'], y=data_toposi_1[plot_selectionVariable], name="Toposi-1"), row=3, col=1)

                        fig.add_trace(go.Scatter(
                            x=data_toposi_2H['Date'], y=data_toposi_2H[plot_selectionVariable], name="Toposi-2H"), row=4, col=1)

                        fig.add_trace(go.Scatter(
                            x=data_laEstancia_1H['Date'], y=data_laEstancia_1H[plot_selectionVariable], name="La Estancia-1H"), row=5, col=1)

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
                            width=1150,
                            height=650,
                            margin=dict(
                            l=0,
                            r=0,
                            b=0,
                            t=0,
                            pad=0
                        ))
                        fig.update_yaxes(automargin=False)
                        production_plot.plotly_chart(fig)

            elif (plot_Type == 'Boxplot'):

                fig = go.Figure()
                fig.add_trace(go.Box(
                    y=data_caramelo_2[plot_selectionVariable], name="Caramelo-2"))

                fig.add_trace(go.Box(
                    y=data_caramelo_3[plot_selectionVariable], name="Caramelo-3"))

                fig.add_trace(go.Box(
                    y=data_toposi_1[plot_selectionVariable], name="Toposi-1"))

                fig.add_trace(go.Box(
                    y=data_toposi_2H[plot_selectionVariable], name="Toposi-2H"))

                fig.add_trace(go.Box(
                    y=data_laEstancia_1H[plot_selectionVariable], name="La Estancia-1H"))

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
                    width=1150,
                    height=650,
                    margin=dict(
                    l=0,
                    r=0,
                    b=0,
                    t=0,
                    pad=0
                ))
                fig.update_yaxes(automargin=False)
                production_plot.plotly_chart(fig)

            elif (plot_Type == 'Hist'):

                histMode = ['overlay', 'stack', 'normal']

                hist_Mode = production_params.radio('Histogram Mode', histMode)

                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=data_caramelo_2[plot_selectionVariable].replace(0, np.nan), name="Caramelo-2"))

                fig.add_trace(go.Histogram(
                    x=data_caramelo_3[plot_selectionVariable].replace(0, np.nan), name="Caramelo-3"))

                fig.add_trace(go.Histogram(
                    x=data_toposi_1[plot_selectionVariable].replace(0, np.nan), name="Toposi-1"))

                fig.add_trace(go.Histogram(
                    x=data_toposi_2H[plot_selectionVariable].replace(0, np.nan), name="Toposi-2H"))

                fig.add_trace(go.Histogram(
                    x=data_laEstancia_1H[plot_selectionVariable].replace(0, np.nan), name="La Estancia-1H"))

                if (hist_Mode == 'overlay'):

                    histOpacity = production_params.slider('Opacity:',
                                                           min_value=0.0, value=0.5, max_value=1.0)

                    fig.update_traces(opacity=histOpacity)
                    fig.update_layout(barmode=hist_Mode,
                                      legend=dict(
                                          orientation="h",
                                          #     yanchor="bottom",
                                          #     yanchor="top",
                                          #     y=0.99,
                                          #     xanchor="right",
                                          #     x=0.01
                                      ),
                                      # showlegend=False,
                                      autosize=True,
                                      width=1150,
                                      height=650,
                                      margin=dict(
                                          l=50,
                                          r=0,
                                          b=0,
                                          t=0,
                                          pad=0
                                      ))
                    fig.update_yaxes(automargin=False)
                    production_plot.plotly_chart(fig)

                elif (hist_Mode == 'stack'):
                    fig.update_layout(barmode=hist_Mode,
                                      legend=dict(
                                          orientation="h",
                                          #     yanchor="bottom",
                                          #     yanchor="top",
                                          #     y=0.99,
                                          #     xanchor="right",
                                          #     x=0.01
                                      ),
                                      # showlegend=False,
                                      autosize=True,
                                      width=1150,
                                      height=650,
                                      margin=dict(
                                          l=50,
                                          r=0,
                                          b=0,
                                          t=0,
                                          pad=0
                                      ))
                    fig.update_yaxes(automargin=False)
                    production_plot.plotly_chart(fig)

                else:
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
                        width=1150,
                        height=650,
                        margin=dict(
                        l=50,
                        r=0,
                        b=0,
                            t=0,
                            pad=0
                    ))
                    fig.update_yaxes(automargin=False)
                    production_plot.plotly_chart(fig)

                production_plot.write(
                    'Note: Zero values were replaced by NAN.')

            with summary_statistics:

                summary_statistics.markdown('## Summary')
                summaryExpander = summary_statistics.beta_expander(
                    'Statistics')
                summaryExpander.write(
                    data[plot_selectionVariable].describe())

        elif (modeType == 'Single Well'):
            wells = ("Caramelo-2", "Caramelo-3", "Toposi-1",
                     "Toposi-2H", "LaEstancia-1H")

            selected_well = production_params.selectbox("Select a well", wells)

            data = load_data()

            data['Date'] = pd.to_datetime(data['Date']).dt.date

            plot_selectionVariable = production_params.selectbox(
                'Feature:', columns)

            visualizationType = ['Visualization', 'Analysis']

            visualization_Type = production_params.radio(
                'Visualization Type', visualizationType)

            if (visualization_Type == 'Visualization'):
                plotType = ['Full', 'Decomposition']

                plot_Type = production_params.radio('Plot Type', plotType)

                if (plot_Type == 'Full'):

                    with production_plot:

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=data['Date'], y=data[plot_selectionVariable]))
                        fig.layout.update(xaxis_rangeslider_visible=True)

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
                            width=1150,
                            height=650,
                            margin=dict(
                            l=50,
                            r=0,
                            b=0,
                            t=0,
                            pad=0
                        ))
                        fig.update_yaxes(automargin=False)
                        production_plot.plotly_chart(fig)

                    with summary_statistics:
                        summary_statistics.markdown('## Summary')
                        summaryExpander = summary_statistics.beta_expander(
                            'Statistics')
                        summaryExpander.write(
                            data[plot_selectionVariable].describe())

                elif (plot_Type == 'Decomposition'):

                    decompositionExpander = production_params.beta_expander(
                        'Parameters')

                    seasonalModelType = ['Additive', 'Multiplicative']

                    if (seasonalModelType == 'Additive'):
                        seasonalModelType = 'additive'
                    elif (seasonalModelType == 'Multiplicative'):
                        seasonalModelType = 'multiplicative'

                    seasonalModel_Type = decompositionExpander.radio(
                        'Decomposition Model Type', seasonalModelType)

                    production_params_checkbox = decompositionExpander.radio(
                        'Seasonality Periods: ', ['Daily', 'Monthly', 'Yearly', 'Custom'], index=1)

                    if (production_params_checkbox == 'Daily'):
                        seasonalityPeriod = 1
                    elif (production_params_checkbox == 'Monthly'):
                        seasonalityPeriod = 30
                    elif (production_params_checkbox == 'Yearly'):
                        seasonalityPeriod = 365
                    else:
                        seasonalityPeriod = production_params.slider('Period:',
                                                                     min_value=1, value=30, max_value=365)

                    # Check if there is any null value in the data

                    nullTest = data[plot_selectionVariable].isnull(
                    ).values.any()

                    if (nullTest == True):
                        data[plot_selectionVariable] = data[plot_selectionVariable].fillna(
                            0)

                    dataSeasonal = seasonal_decompose(
                        data[plot_selectionVariable], model=seasonalModel_Type, period=seasonalityPeriod)

                    with production_plot:

                        fig = make_subplots(
                            rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.02)

                        fig.add_trace(go.Scatter(
                            x=data['Date'], y=data[plot_selectionVariable], name="Observed"), row=1, col=1)
                        fig.add_trace(go.Scatter(
                            x=data['Date'], y=dataSeasonal.trend, name="Trend"), row=2, col=1)
                        fig.add_trace(go.Scatter(
                            x=data['Date'], y=dataSeasonal.seasonal, name="Seasonal"), row=3, col=1)
                        fig.add_trace(go.Scatter(
                            x=data['Date'], y=dataSeasonal.resid, name="Residuals"), row=4, col=1)

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
                            width=1150,
                            height=650,
                            margin=dict(
                            l=50,
                            r=0,
                            b=0,
                            t=0,
                            pad=0
                        ))
                        fig.update_yaxes(automargin=False)
                        production_plot.plotly_chart(fig)

                    #################################

                    with summary_statistics:
                        summary_statistics.markdown('## Summary')
                        summary_statistics.write('### Stationarity')

                        summaryExpander = summary_statistics.beta_expander(
                            'Statistics')
                        summaryExpander.write(
                            data[plot_selectionVariable].describe())

                        stationarityExpander = summary_statistics.beta_expander(
                            'Stationarity')

                        original = data[plot_selectionVariable]
                        trend = (dataSeasonal.trend).dropna()
                        seasonal = (dataSeasonal.seasonal).dropna()
                        residual = (dataSeasonal.resid).dropna()

                        adftest_original = adfuller(original)
                        adftest_trend = adfuller(trend)
                        adftest_seasonal = adfuller(seasonal)
                        adftest_resid = adfuller(residual)

                        stationarityExpander.write(
                            'Dickey-Fuller Test (P-value): ')
                        stationarityExpander.write(
                            'Original: ' + str(round(adftest_original[1], 5)))
                        stationarityExpander.write(
                            'Trend: ' + str(round(adftest_trend[1], 5)))
                        stationarityExpander.write(
                            'Seasonal: ' + str(round(adftest_seasonal[1], 5)))
                        stationarityExpander.write(
                            'Resid: ' + str(round(adftest_resid[1], 5)))

                        if adftest_original[1] < 0.05:
                            stationarityExpander.markdown(
                                f'<p style="color:#008000">The series is likely stationary.</p>', unsafe_allow_html=True)

                            stationarityExpander.write(
                                'Low P-vale (lower than 0.05) implies series is stationary.')

                        else:
                            stationarityExpander.markdown(
                                f'<p style="color:#ff0000">The series is likely non-stationary.</p>', unsafe_allow_html=True)
                            stationarityExpander.write(
                                'High P-vale (higher than 0.05) implies series is not stationary.')

            elif (visualization_Type == 'Analysis'):

                analysisModelType = ['ARIMA', 'Moving Average']

                customModel_Type = production_params.radio(
                    'Model', analysisModelType)

                if customModel_Type == 'ARIMA':

                    ARIMAanalysisExpander = production_params.beta_expander(
                        'Data')

                    ARIMAanalysisModelType = ['Full', 'Seasonal']

                    ARIMAanalysisModel_Type = ARIMAanalysisExpander.radio(
                        'Select:', ARIMAanalysisModelType, index=1)

                    # Mode
                    ARIMAmodelExpander = production_params.beta_expander(
                        'Mode')

                    # ARIMA Parameters

                    ARIMAModelParameters = st.beta_expander(
                        'Parameters')

                    train_perc = ARIMAModelParameters.slider(
                        'Training %:', min_value=0.0, value=0.8, max_value=1.0, help='Percentage of data to be used for training')

                    lags = ARIMAModelParameters.slider(
                        'Lags:', min_value=0, value=100, max_value=1000, help='Lags to be considered in the model')

                    alpha = ARIMAModelParameters.slider(
                        'Alpha (%):', min_value=0.00, value=0.05, max_value=1.00, help='The confidence level of the forecast')

                    arima_p = ARIMAModelParameters.slider(
                        'p:', min_value=0, value=0, max_value=lags, help='Order of Auto-Regressive Model (AR), or periods')

                    arima_d = ARIMAModelParameters.slider(
                        'd:', min_value=0, value=0, max_value=2, help='Order of Differentiation in order to make the series stationary.')

                    arima_q = ARIMAModelParameters.slider(
                        'q:', min_value=0, value=0, max_value=lags, help='Dependency on error of the previous lagged values (Moving Average, MA)')
                    # Data Loading

                    data_df = copy.deepcopy(data)

                    data_ts = pd.concat(
                        [data_df['Date'], data_df[plot_selectionVariable]], axis=1)

                    # TODO: Review this since in time-series I need to select the % of training by dates.
                    data_df_train = data_ts[0:int(
                        len(data_df) * train_perc)]
                    data_df_test = data_ts[int(
                        len(data_df) * train_perc):]

                    if (ARIMAanalysisModel_Type == 'Full'):
                        production_params.warning(
                            'Due to the complexity of the timeseries, the full ARIMA model might lead to high computational time.')

                    elif (ARIMAanalysisModel_Type == 'Seasonal'):

                        seasonalityARIMAExpander = production_params.beta_expander(
                            'Seasonality Mode')

                        ###########

                        seasonalModel_Type = ['Additive', 'Multiplicative']

                        if (seasonalModel_Type == 'Additive'):
                            seasonalModel_Type = 'additive'
                        elif (seasonalModel_Type == 'Multiplicative'):
                            seasonalModel_Type = 'multiplicative'

                        seasonalityType = seasonalityARIMAExpander.radio(
                            'Seasonal Model Type', seasonalModel_Type)

                        ###########
                        seasonalityMode = [
                            'Daily', 'Monthly', 'Yearly', 'Custom']

                        seasonalityType = seasonalityARIMAExpander.radio(
                            'Mode', seasonalityMode, index=1)

                        nullTestARIMA = data_ts[plot_selectionVariable].isnull(
                        ).values.any()

                        if (nullTestARIMA == True):
                            data_ts[plot_selectionVariable] = data_ts[plot_selectionVariable].fillna(
                                0)

                        if (seasonalityType == 'Daily'):
                            seasonalityPeriod = 1
                            data_ts_ = seasonal_decompose(
                                data_ts[plot_selectionVariable], model=seasonalityType, period=seasonalityPeriod)
                            data_ts_ = pd.DataFrame(data_ts_.trend)
                        elif (seasonalityType == 'Monthly'):
                            seasonalityPeriod = 30
                            data_ts_ = seasonal_decompose(
                                data_ts[plot_selectionVariable], model=seasonalityType, period=seasonalityPeriod)
                            data_ts_ = pd.DataFrame(data_ts_.trend)
                        elif (seasonalityType == 'Yearly'):
                            seasonalityPeriod = 365
                            data_ts_ = seasonal_decompose(
                                data_ts[plot_selectionVariable], model=seasonalityType, period=seasonalityPeriod)
                            data_ts_ = pd.DataFrame(data_ts_.trend)
                        else:
                            seasonalityPeriod = seasonalityARIMAExpander.slider('Period:',
                                                                                min_value=1, value=30, max_value=365)
                            data_ts_ = seasonal_decompose(
                                data_ts[plot_selectionVariable], model=seasonalityType, period=seasonalityPeriod)
                            data_ts_ = pd.DataFrame(data_ts_.trend)

                        data_ts_.rename(
                            columns={'trend': plot_selectionVariable}, inplace=True)

                        data_ts = pd.concat(
                            [data_ts['Date'], data_ts_[plot_selectionVariable]], axis=1)

                        data_ts.dropna(inplace=True)

                        #############################################

                    ARIMAModelType = ARIMAmodelExpander.radio(
                        'Select:', ['Analysis', 'Search Parameters', 'Search Parameters (Loop)', 'Auto ARIMA'])

                    if ARIMAModelType == 'Analysis':

                        ARIMA_model = ARIMA(data_ts[plot_selectionVariable], order=(
                            arima_p, arima_d, arima_q))

                        ARIMA_model_fit = ARIMA_model.fit()

                        fcst = ARIMA_model_fit.forecast(
                            steps=len(data_df_test))[0]

                        ARIMAplotExpander = production_params.beta_expander(
                            'Plot Type')

                        ARIMAPlot = ARIMAplotExpander.radio(
                            'ARIMA Plot', ['Differentiation Plot', 'Autocorrelation Plot', 'PACF & ACF'])

                        if (ARIMAPlot == 'Differentiation Plot'):
                            # plt.plot(data_ts[plot_selectionVariable])production_plot.write(arima_d)
                            data_ts_ = copy.deepcopy(data_ts)
                            data_ts_[plot_selectionVariable] = data_ts_[plot_selectionVariable].diff(
                                periods=arima_d)

                            with production_plot:

                                fig = make_subplots(
                                    rows=2, cols=1, subplot_titles=("Original", "Differentiation"))

                                fig.add_trace(go.Scatter(
                                    x=data_ts['Date'], y=data_ts[plot_selectionVariable]), row=1, col=1)

                                fig.add_trace(go.Scatter(
                                    x=data_ts_['Date'], y=data_ts_[plot_selectionVariable]), row=2, col=1)

                                fig.update_layout(legend=dict(
                                    orientation="h",
                                    #     yanchor="bottom",
                                    #     yanchor="top",
                                    #     y=0.99,
                                    #     xanchor="right",
                                    #     x=0.01
                                ),
                                    showlegend=False,
                                    autosize=True,
                                    width=1150,
                                    height=650
                                )

                                fig.update_yaxes(automargin=False)

                                production_plot.plotly_chart(fig)

                        elif ARIMAPlot == 'Autocorrelation Plot':

                            data_ts_ = data_ts.set_index('Date')

                            fig = plt.figure()
                            pd.plotting.autocorrelation_plot(data_ts_)

                            production_plot.pyplot(fig)

                            plotDescriptionExpander = st.beta_expander(
                                'Plot description')

                            plotDescriptionExpander.markdown(
                                'Autocorrelation plots are a commonly used tool for checking randomness in a data set. This randomness is ascertained by computing autocorrelation for data values at varying time lags. Plot starts at 1.00 since Autocorrelation with lag zero always equal 1, because this represents the autocorrelation between each term and itself. The dash lines correspond to critical boundaries.')
                        elif ARIMAPlot == 'PACF & ACF':

                            with production_plot:
                                fig = make_subplots(
                                    rows=1, cols=2, subplot_titles=("Partial Autocorrelation (PACF)", "Autocorrelation (ACF)"))

                                df_pacf = pacf(
                                    data_ts[plot_selectionVariable], nlags=lags, alpha=alpha)
                                df_acf = acf(
                                    data_ts[plot_selectionVariable], nlags=lags, alpha=alpha)

                                df_pacf_lower_y = df_pacf[1][:,
                                                             0] - df_pacf[0]
                                df_pacf_upper_y = df_pacf[1][:,
                                                             1] - df_pacf[0]

                                df_acf_lower_y = df_acf[1][:,
                                                           0] - df_acf[0]
                                df_acf_upper_y = df_acf[1][:,
                                                           1] - df_acf[0]

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

                                production_plot.plotly_chart(fig)

                        with summary_statistics:
                            summary_statistics.markdown('## Parameters')
                            ARIMAModelSummary = summary_statistics.beta_expander(
                                'ARIMA Model Summary')
                            ARIMAModelSummary.write(
                                ARIMA_model_fit.summary())

                            ARIMA_error = np.sqrt(mean_squared_error(
                                data_df_test[plot_selectionVariable], fcst))

                            st.markdown("<hr/>", unsafe_allow_html=True)

                            summary_statistics.markdown(
                                f"#### Akaike Information Critera (AIC)")

                            AIC = round(ARIMA_model_fit.aic, 2)

                            AIC_ = f"{AIC:,}"

                            summary_statistics.markdown(
                                f"<h1 style = 'text-align: center; color: black;'>{AIC_}</h1>", unsafe_allow_html=True)

                            st.markdown("<hr/>", unsafe_allow_html=True)

                            summary_statistics.markdown(
                                f"#### ARIMA Model Error")

                            ARIMA_error_ = round(ARIMA_error, 2)

                            ARIMA_error_ = f"{ARIMA_error_:,}"

                            summary_statistics.markdown(
                                f"<h1 style = 'text-align: center; color: black;'>{ARIMA_error_}</h1>", unsafe_allow_html=True)

                            st.markdown("<hr/>", unsafe_allow_html=True)

                            summary_statistics.write(
                                'Total samples: ' + (str(len(data_df))))
                            summary_statistics.write(
                                'Training samples ' + (str(len(data_df_train))))
                            summary_statistics.write(
                                'Testing samples: ' + (str(len(data_df_test))))

                    elif ARIMAModelType == 'Search Parameters':

                        # Calculate the Auto-Regressive Integrated Moving Average
                        data_df = copy.deepcopy(data)

                        data_ts = pd.concat(
                            [data_df['Date'], data_df[plot_selectionVariable]], axis=1)

                        ARIMAModelParameters = st.beta_expander(
                            'ARIMA Parameters')

                        lags = ARIMAModelParameters.slider(
                            'Lags:', min_value=0, value=100, max_value=1000, help='Lags to be considered in the model')

                        alpha = ARIMAModelParameters.slider(
                            'Alpha (%):', min_value=0.00, value=0.05, max_value=1.00, help='The confidence level of the forecast')

                        train_perc = ARIMAModelParameters.slider(
                            'Training %:', min_value=0.0, value=0.8, max_value=1.0, help='Percentage of data to be used for training')

                        # data_df_train = data_ts[0:int(
                        #     len(data_df) * train_perc)]
                        # data_df_test = data_ts[int(len(data_df) * train_perc):]

                        arima_p = ARIMAModelParameters.slider(
                            'p:', min_value=0, value=[0, 1], max_value=lags, help='Order of Auto-Regressive Model (AR), or periods')

                        arima_d = ARIMAModelParameters.slider(
                            'd:', min_value=0, value=[0, 1], max_value=2, help='Order of Differentiation in order to make the series stationary.')

                        arima_q = ARIMAModelParameters.slider(
                            'q:', min_value=0, value=[0, 1], max_value=lags, help='Dependency on error of the previous lagged values (Moving Average, MA)')

                        p_values = range(arima_p[0], arima_p[1])
                        d_values = range(arima_d[0], arima_d[1])
                        q_values = range(arima_q[0], arima_q[1])

                        # with production_plot:

                        with summary_statistics:

                            summary_statistics.markdown(
                                '## Parameters')
                            summary_statistics.markdown(
                                '#### ARIMA Error Table')

                            for p in p_values:
                                for d in d_values:
                                    for q in q_values:
                                        order = (p, d, q)
                                        data_df_train, data_df_test = data_ts[0:int(
                                            len(data_df) * train_perc)], data_ts[int(len(data_df) * train_perc):]
                                        predictions = list()
                                        for i in range(len(data_df_test)):
                                            try:
                                                model = ARIMA(
                                                    data_df_train[plot_selectionVariable], order=order)
                                                model_fit = model.fit(
                                                    disp=0)
                                                pred_y = model_fit.forecast()[
                                                    0]
                                                predictions.append(pred_y)

                                                # summary_statistics.write(
                                                #     predictions)
                                                error = mean_squared_error(
                                                    data_df_test, predictions)

                                                summary_statistics.write(
                                                    f'ARIMA%s MSE = %.2f' % (order, error))
                                            except:
                                                continue

                        # with summary_statistics:
                        #     summary_statistics.write(data_df_train)
                        #     summary_statistics.write(data_df_test)
                        #     summary_statistics.write(predictions)

                    elif ARIMAModelType == 'Search Parameters (Loop)':
                        pass
                        # # Calculate the Auto-Regressive Integrated Moving Average
                        # data_df = copy.deepcopy(data)

                        # data_ts = pd.concat(
                        #     [data_df['Date'], data_df[plot_selectionVariable]], axis=1)

                        # ARIMAModelParameters = st.beta_expander(
                        #     'ARIMA Parameters')

                        # lags = ARIMAModelParameters.slider(
                        #     'Lags:', min_value=0, value=100, max_value=1000, help='Lags to be considered in the model')

                        # alpha = ARIMAModelParameters.slider(
                        #     'Alpha (%):', min_value=0.00, value=0.05, max_value=1.00, help='The confidence level of the forecast')

                        # train_perc = ARIMAModelParameters.slider(
                        #     'Training %:', min_value=0.0, value=0.8, max_value=1.0, help='Percentage of data to be used for training')

                        # # data_df_train = data_ts[0:int(
                        # #     len(data_df) * train_perc)]
                        # # data_df_test = data_ts[int(len(data_df) * train_perc):]

                        # arima_p = ARIMAModelParameters.slider(
                        #     'p:', min_value=0, value=[0, 2], max_value=lags, help='Order of Auto-Regressive Model (AR), or periods')

                        # arima_d = ARIMAModelParameters.slider(
                        #     'd:', min_value=0, value=[0, 1], max_value=2, help='Order of Differentiation in order to make the series stationary.')

                        # arima_q = ARIMAModelParameters.slider(
                        #     'q:', min_value=0, value=[0, 2], max_value=lags, help='Dependency on error of the previous lagged values (Moving Average, MA)')

                        # p_values = range(arima_p[0], arima_p[1])
                        # d_values = range(arima_d[0], arima_d[1])
                        # q_values = range(arima_q[0], arima_q[1])

                        # pdq_combination = list(itertools.product(
                        #     p_values, d_values, q_values))

                        # rmse = []
                        # order_ = []

                        # data_df_train = data_ts[0:int(
                        #     len(data_df) * train_perc)]
                        # data_df_test = data_ts[int(len(data_df) * train_perc):]

                        # for pdq in pdq_combination:
                        #     try:
                        #         ARIMA_model = ARIMA(
                        #             data_df_train[plot_selectionVariable], order=pdq)

                        #         ARIMA_model_fit = ARIMA_model.fit()
                        #         fcst = ARIMA_model_fit.predict(
                        #             steps=len(data_df_test))[0]

                        #         error = np.sqrt(
                        #             mean_squared_error(data_df_test, fcst))
                        #         order_.append(pdq)
                        #         rmse.append(error)
                        #     except:
                        #         continue

                        # # with production_plot:

                        # results = pd.DataFrame(
                        #     index=order_, data=rmse, columns=['RMSE'])

                        # with summary_statistics:

                        #     summary_statistics.markdown(
                        #         '## Parameters')
                        #     summary_statistics.markdown(
                        #         '#### ARIMA Error Table')

                        #     summary_statistics.write(results)
                    elif ARIMAModelType == 'Auto ARIMA':
                        pass
                        # data_df = copy.deepcopy(data)

                        # data_ts = pd.concat(
                        #     [data_df['Date'], data_df[plot_selectionVariable]], axis=1)

                        # ARIMAModelParameters = st.beta_expander(
                        #     'ARIMA Parameters')

                        # train_perc = ARIMAModelParameters.slider(
                        #     'Training %:', min_value=0.0, value=0.8, max_value=1.0, help='Percentage of data to be used for training')

                        # # data_df_train = data_ts[0:int(
                        # #     len(data_df) * train_perc)]
                        # # data_df_test = data_ts[int(len(data_df) * train_perc):]

                        # m = ARIMAModelParameters.slider(
                        #     'm:', min_value=0, value=1, max_value=365, help='Order of Auto-Regressive Model (AR), or periods')

                        # data_df_train = data_ts[0:int(
                        #     len(data_df) * train_perc)]
                        # data_df_test = data_ts[int(len(data_df) * train_perc):]

                        # auto_arima(data_df_train, m = m, start = 0, seasonal = True, trace = True, error_action = 'ignore', suppress_warnings = True, stepwise = True)
                elif customModel_Type == 'Moving Average':

                    MovingAverageExpander = st.beta_expander(
                        'Moving Average Parameters')

                    customModel_period = MovingAverageExpander.slider('Period:',
                                                                      min_value=1, value=30, max_value=365)

                    data['MovAverage'] = data[plot_selectionVariable].rolling(
                        window=customModel_period).mean()

                    with production_plot:

                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=data['Date'], y=data[plot_selectionVariable], name="Observed"))

                        fig.add_trace(go.Scatter(
                            x=data['Date'], y=data['MovAverage'], name="Moving Average"))
                        fig.layout.update(xaxis_rangeslider_visible=True)

                        # fig.add_vline(x=economicLimit,  line_width=1,
                        #   line_dash="dash", line_color="black")

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
                            width=1150,
                            height=650,
                            margin=dict(
                            l=50,
                            r=0,
                            b=0,
                            t=0,
                            pad=0
                        ))
                        fig.update_yaxes(automargin=False)
                        production_plot.plotly_chart(fig)
