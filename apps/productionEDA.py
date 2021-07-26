import streamlit as st
import numpy as np
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import seasonal_decompose
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import pandas as pd
from plotly import graph_objs as go
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
                    production_plot.markdown('## Plot')
                    production_plot.markdown('### Scatter')

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

                        fig.update_layout(width=1100, height=700)
                        production_plot.plotly_chart(fig)

                        with summary_statistics:
                            summary_statistics.markdown('## Summary')
                            summary_statistics.write('Marico el que lo lea')

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

                        fig.update_layout(width=1100, height=700)
                        production_plot.plotly_chart(fig)

                        with summary_statistics:
                            summary_statistics.markdown('## Summary')
                            summary_statistics.write('Marico el que lo lea')

            elif (plot_Type == 'Boxplot'):

                production_plot.markdown('## Plot')
                production_plot.markdown('### Boxplot')

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

                fig.update_layout(width=1100, height=700)
                production_plot.plotly_chart(fig)

                with summary_statistics:
                    summary_statistics.markdown('## Summary')
                    summary_statistics.write('Marico el que lo lea')

            elif (plot_Type == 'Hist'):

                production_plot.markdown('## Plot')
                production_plot.markdown('### Histogram')

                histMode = ['overlay', 'stack', 'normal']

                hist_Mode = production_params.radio('Histogram Mode', histMode)

                histOpacity = production_params.slider('Opacity:',
                                                       min_value=0.0, value=0.5, max_value=1.0)

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

                    fig.update_layout(barmode=hist_Mode,
                                      width=1100, height=630)
                    fig.update_traces(opacity=histOpacity)
                    production_plot.plotly_chart(fig)

                elif (hist_Mode == 'stack'):
                    fig.update_layout(barmode=hist_Mode,
                                      width=1100, height=630)
                    production_plot.plotly_chart(fig)

                else:
                    fig.update_layout(width=1100, height=630)
                    production_plot.plotly_chart(fig)

                production_plot.write(
                    'Note: Zero values were replaced by NAN.')

                with summary_statistics:
                    summary_statistics.markdown('## Summary')
                    summary_statistics.write('Marico el que lo lea')

        else:
            wells = ("Caramelo-2", "Caramelo-3", "Toposi-1",
                     "Toposi-2H", "LaEstancia-1H")

            selected_well = production_params.selectbox("Select a well", wells)

            data = load_data()

            data['Date'] = pd.to_datetime(data['Date']).dt.date

            plot_selectionVariable = production_params.selectbox(
                'Feature:', columns)

            plotType = ['Full', 'Decomposition']

            plot_Type = production_params.radio('Plot Type', plotType)

            if (plot_Type == 'Full'):
                production_plot.markdown('## Plot')
                production_plot.markdown('### Scatter | Full')

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=data['Date'], y=data[plot_selectionVariable]))
                fig.layout.update(xaxis_rangeslider_visible=True)

                fig.update_layout(width=1100, height=700)
                production_plot.plotly_chart(fig)

                with summary_statistics:
                    summary_statistics.markdown('## Summary')
                    summary_statistics.write('Marico el que lo lea')

            else:
                production_plot.markdown('## Plot')
                production_plot.markdown('### Scatter | Decomposition')

                seasonalModelType = ['additive', 'multiplicative']

                seasonalModel_Type = production_params.radio(
                    'Seasonal Model Type', seasonalModelType)

                production_params_checkbox = production_params.radio(
                    'Seasonality Periods: ', ['Daily', 'Monthly', 'Yearly', 'Custom'])

                if (production_params_checkbox == 'Daily'):
                    seanalityPeriod = 1
                elif (production_params_checkbox == 'Monthly'):
                    seanalityPeriod = 30
                elif (production_params_checkbox == 'Yearly'):
                    seanalityPeriod = 365
                else:
                    seanalityPeriod = production_params.slider('Period:',
                                                               min_value=1, value=30, max_value=365)

                dataSeasonal = seasonal_decompose(
                    data[plot_selectionVariable], model=seasonalModel_Type, period=seanalityPeriod)

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

                fig.update_layout(width=1100, height=600)
                production_plot.plotly_chart(fig)

                with summary_statistics:
                    summary_statistics.markdown('## Summary')
                    summary_statistics.write('### Stationarity')

                    original = data[plot_selectionVariable]
                    trend = (dataSeasonal.trend).dropna()
                    seasonal = (dataSeasonal.seasonal).dropna()
                    residual = (dataSeasonal.resid).dropna()

                    adftest_original = adfuller(original)
                    adftest_trend = adfuller(trend)
                    adftest_seasonal = adfuller(seasonal)
                    adftest_resid = adfuller(residual)

                    summary_statistics.write('Dickey-Fuller Test (P-value): ')
                    summary_statistics.write(
                        'Original: ' + str(adftest_original[1]))
                    summary_statistics.write(
                        'Trend: ' + str(adftest_trend[1]))
                    summary_statistics.write(
                        'Seasonal: ' + str(adftest_seasonal[1]))
                    summary_statistics.write(
                        'Resid: ' + str(adftest_resid[1]))

                    if adftest_original[1] < 0.05:
                        summary_statistics.markdown(
                            f'<p style="color:#008000">The series is likely stationary.</p>', unsafe_allow_html=True)

                        summary_statistics.write(
                            'Low P-vale (lower than 0.05) implies series is stationary.')

                    else:
                        summary_statistics.markdown(
                            f'<p style="color:#ff0000">The series is likely non-stationary.</p>', unsafe_allow_html=True)
                        summary_statistics.write(
                            'High P-vale (higher than 0.05) implies series is not stationary.')
