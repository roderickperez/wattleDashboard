from re import I
import streamlit as st
import numpy as np
import pandas as pd
from plotly import graph_objs as go
from plotly.subplots import make_subplots

wells = ("Crisol-1", "Crisol-2", "Crisol-3",
         "Norean-1", "Aguachica-2", "Bandera-1", "Caramelo-1", "Caramelo-2", "Caramelo-3", "Pital-1", "Toposi-2HST1", "LaEstancia-1")

columns = ['SP', 'RD', 'RM', 'RS',
           'GR', 'NPHI', 'DT', 'RHOB']

##############


def app():
    st.markdown('# Well Logs')
    st.markdown('## Exploratory Data Analysis')

    def load_ALLdata():
        data = pd.read_csv(
            r'data/VMM_1_WellLogs.csv', header=None)
        data.columns = ['Depth', 'SP', 'RD', 'RM', 'RS',
                        'GR', 'NPHI', 'DT', 'RHOB', 'Well Name']
        # data = data[data['Well Name'] == selected_well]
        return data

    def load_data():
        data = pd.read_csv(
            r'data/VMM_1_WellLogs.csv', header=None)
        data.columns = ['Depth', 'SP', 'RD', 'RM', 'RS',
                        'GR', 'NPHI', 'DT', 'RHOB', 'Well Name']
        data = data[data['Well Name'] == selected_well]
        return data

    ##########

    logs_params, logs_plot = st.columns((1, 4))

    with logs_params:
        st.markdown('## Parameters')

        mode = ['Single Well', 'Multi Well', 'All Wells']

        modeType = logs_params.radio('Mode', mode)

        if (modeType == 'All Wells'):
            data = load_ALLdata()

            data_crisol_1 = data[data['Well Name'] == "Crisol-1"]
            data_crisol_2 = data[data['Well Name'] == "Crisol-2"]
            data_crisol_3 = data[data['Well Name'] == "Crisol-3"]
            data_norean_1 = data[data['Well Name'] == "Norean-1"]
            data_aguachica_2 = data[data['Well Name'] == "Aguachica-2"]
            data_bandera_1 = data[data['Well Name'] == "Bandera-1"]
            data_caramelo_1 = data[data['Well Name'] == "Caramelo-1"]
            data_caramelo_2 = data[data['Well Name'] == "Caramelo-2"]
            data_caramelo_3 = data[data['Well Name'] == "Caramelo-3"]
            data_pital_1 = data[data['Well Name'] == "Pital-1"]
            data_toposi_2HST1 = data[data['Well Name'] == "Toposi-2HST1"]
            data_laEstancia_1 = data[data['Well Name'] == "LaEstancia-1"]

            plotType = ['Pairplot', 'Scatter', 'Boxplot', 'Hist']

            plot_Type = logs_params.radio('Plot Type', plotType)

            # st.write(data['Well Name'].unique()) # Verify unique wells in list

            # Verify unique wells in list
            # st.write(len(data['Well Name'].unique()))

            if (plot_Type == 'Pairplot'):

                index_vals = data['Well Name'].astype('category').cat.codes
                fig = go.Figure()

                fig.add_trace(go.Splom(
                    dimensions=[dict(label='SP',
                                     values=data['SP']),
                                dict(label='RD',
                                     values=data['RD']),
                                dict(label='RM',
                                     values=data['RM']),
                                dict(label='RS',
                                     values=data['RS']),
                                dict(label='GR',
                                     values=data['GR']),
                                dict(label='NPHI',
                                     values=data['NPHI']),
                                dict(label='DT',
                                     values=data['DT']),
                                dict(label='RHOB',
                                     values=data['RHOB'])
                                ],
                    marker=dict(color=index_vals,
                                showscale=False)
                ))
                fig.update_layout(width=650, height=650)
                logs_plot.plotly_chart(fig)

                # x=data_crisol_1[plot_selectionVariable], y=data_crisol_1['Depth'], name="Crisol-1"))

            elif (plot_Type == 'Scatter'):

                plot_selectionVariable = logs_params.selectbox(
                    'Feature:', columns)

                with logs_plot:
                    logs_plot.markdown('## Plot')
                    logs_plot.markdown('### Scatter')

                    scatterType = ['All', 'Individual']

                    scatter_Type = logs_params.radio(
                        'Scatter Type', scatterType)

                    wellTops_mode = logs_params.radio(
                        'Well Tops:', ['Off', 'On'])

                    if (scatter_Type == 'All'):
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=data_crisol_1[plot_selectionVariable], y=data_crisol_1['Depth'], name="Crisol-1"))
                        fig.add_trace(go.Scatter(
                            x=data_crisol_2[plot_selectionVariable], y=data_crisol_2['Depth'], name="Crisol-2"))
                        fig.add_trace(go.Scatter(
                            x=data_crisol_3[plot_selectionVariable], y=data_crisol_3['Depth'], name="Crisol-3"))
                        fig.add_trace(go.Scatter(
                            x=data_norean_1[plot_selectionVariable], y=data_norean_1['Depth'], name="Norean-1"))
                        fig.add_trace(go.Scatter(
                            x=data_aguachica_2[plot_selectionVariable], y=data_aguachica_2['Depth'], name="Aguachica-2"))
                        fig.add_trace(go.Scatter(
                            x=data_bandera_1[plot_selectionVariable], y=data_bandera_1['Depth'], name="Bandera-1"))
                        fig.add_trace(go.Scatter(
                            x=data_caramelo_1[plot_selectionVariable], y=data_caramelo_1['Depth'], name="Caramelo-1"))
                        fig.add_trace(go.Scatter(
                            x=data_caramelo_2[plot_selectionVariable], y=data_pital_1['Depth'], name="Caramelo-2"))
                        fig.add_trace(go.Scatter(
                            x=data_caramelo_3[plot_selectionVariable], y=data_pital_1['Depth'], name="Caramelo-3"))
                        fig.add_trace(go.Scatter(
                            x=data_pital_1[plot_selectionVariable], y=data_pital_1['Depth'], name="Pital-1"))
                        fig.add_trace(go.Scatter(
                            x=data_toposi_2HST1[plot_selectionVariable], y=data_pital_1['Depth'], name="Toposi-2HST1"))
                        fig.add_trace(go.Scatter(
                            x=data_laEstancia_1[plot_selectionVariable], y=data_pital_1['Depth'], name="LaEstancia-1"))

                        fig.update_yaxes(autorange="reversed")
                        fig.update_layout(width=500, height=700)
                        fig.update_layout(
                            title=plot_selectionVariable,
                            yaxis_title="Depth [ft]")

                        logs_plot.plotly_chart(fig)

                    else:

                        ylabelType = [True, False]

                        ylabel_Type = logs_params.radio(
                            'Shared Y-label', ylabelType)

                        fig = make_subplots(
                            rows=1, cols=len(data['Well Name'].unique()), shared_yaxes=ylabel_Type, horizontal_spacing=0.05)

                        fig.add_trace(go.Scatter(
                            x=data_crisol_1[plot_selectionVariable], y=data_crisol_1['Depth'], name="Crisol-1"), row=1, col=1)

                        fig.add_trace(go.Scatter(
                            x=data_crisol_2[plot_selectionVariable], y=data_crisol_2['Depth'], name="Crisol-2"), row=1, col=2)

                        fig.add_trace(go.Scatter(
                            x=data_crisol_3[plot_selectionVariable], y=data_norean_1['Depth'], name="Crisol-3"), row=1, col=4)

                        fig.add_trace(go.Scatter(
                            x=data_norean_1[plot_selectionVariable], y=data_crisol_3['Depth'], name="Norean-1"), row=1, col=3)

                        fig.add_trace(go.Scatter(
                            x=data_aguachica_2[plot_selectionVariable], y=data_aguachica_2['Depth'], name="Aguachica-2"), row=1, col=5)

                        fig.add_trace(go.Scatter(
                            x=data_bandera_1[plot_selectionVariable], y=data_bandera_1['Depth'], name="Banderal-1"), row=1, col=6)

                        fig.add_trace(go.Scatter(
                            x=data_caramelo_1[plot_selectionVariable], y=data_caramelo_1['Depth'], name="Caramelo-1"), row=1, col=7)

                        fig.add_trace(go.Scatter(
                            x=data_caramelo_2[plot_selectionVariable], y=data_caramelo_1['Depth'], name="Caramelo-2"), row=1, col=8)

                        fig.add_trace(go.Scatter(
                            x=data_caramelo_3[plot_selectionVariable], y=data_caramelo_1['Depth'], name="Caramelo-3"), row=1, col=9)

                        fig.add_trace(go.Scatter(
                            x=data_pital_1[plot_selectionVariable], y=data_pital_1['Depth'], name="Pital-1"), row=1, col=10)

                        fig.add_trace(go.Scatter(
                            x=data_toposi_2HST1[plot_selectionVariable], y=data_pital_1['Depth'], name="Toposi-2HST1"), row=1, col=11)

                        fig.add_trace(go.Scatter(
                            x=data_laEstancia_1[plot_selectionVariable], y=data_pital_1['Depth'], name="LaEstancia-1"), row=1, col=12)

                        fig.update_yaxes(autorange="reversed")
                        fig.update_layout(width=1400, height=700)
                        fig.update_layout(
                            title=plot_selectionVariable,
                            yaxis_title="Depth [ft]")
                        logs_plot.plotly_chart(fig)

            elif (plot_Type == 'Boxplot'):

                plot_selectionVariable = logs_params.selectbox(
                    'Feature:', columns)

                logs_plot.markdown('## Plot')
                logs_plot.markdown('### Boxplot')

                fig = go.Figure()
                fig.add_trace(go.Box(
                    y=data_crisol_1[plot_selectionVariable], name="Crisol-1"))

                fig.add_trace(go.Box(
                    y=data_crisol_2[plot_selectionVariable], name="Crisol-2"))

                fig.add_trace(go.Box(
                    y=data_crisol_3[plot_selectionVariable], name="Crisol-3"))

                fig.add_trace(go.Box(
                    y=data_norean_1[plot_selectionVariable], name="Norean-1"))

                fig.add_trace(go.Box(
                    y=data_aguachica_2[plot_selectionVariable], name="Aguachica-2"))

                fig.add_trace(go.Box(
                    y=data_bandera_1[plot_selectionVariable], name="Bandera-1"))

                fig.add_trace(go.Box(
                    y=data_caramelo_1[plot_selectionVariable], name="Caramelo-1"))

                fig.add_trace(go.Box(
                    y=data_caramelo_2[plot_selectionVariable], name="Caramelo-2"))
                fig.add_trace(go.Box(
                    y=data_caramelo_3[plot_selectionVariable], name="Caramelo-3"))
                fig.add_trace(go.Box(
                    y=data_pital_1[plot_selectionVariable], name="Pital-1"))
                fig.add_trace(go.Box(
                    y=data_toposi_2HST1[plot_selectionVariable], name="Toposi-2HST1"))

                fig.add_trace(go.Box(
                    y=data_laEstancia_1[plot_selectionVariable], name="LaEstancia-1"))

                fig.update_layout(width=1300, height=700)
                logs_plot.plotly_chart(fig)

            elif (plot_Type == 'Hist'):

                plot_selectionVariable = logs_params.selectbox(
                    'Feature:', columns)

                logs_plot.markdown('## Plot')
                logs_plot.markdown('### Histogram')

                histMode = ['overlay', 'stack', 'normal']

                hist_Mode = logs_params.radio('Histogram Mode', histMode)

                histOpacity = logs_params.slider('Opacity:',
                                                 min_value=0.0, value=0.5, max_value=1.0)

                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=data_crisol_1[plot_selectionVariable].replace(0, np.nan), name="Crisol-1"))
                fig.add_trace(go.Histogram(
                    x=data_crisol_2[plot_selectionVariable].replace(0, np.nan), name="Crisol-2"))
                fig.add_trace(go.Histogram(
                    x=data_crisol_3[plot_selectionVariable].replace(0, np.nan), name="Crisol-3"))
                fig.add_trace(go.Histogram(
                    x=data_norean_1[plot_selectionVariable].replace(0, np.nan), name="Norean-1"))
                fig.add_trace(go.Histogram(
                    x=data_aguachica_2[plot_selectionVariable].replace(0, np.nan), name="Aguachica-2"))
                fig.add_trace(go.Histogram(
                    x=data_bandera_1[plot_selectionVariable].replace(0, np.nan), name="Bandera-1"))
                fig.add_trace(go.Histogram(
                    x=data_caramelo_1[plot_selectionVariable].replace(0, np.nan), name="Caramelo-1"))
                fig.add_trace(go.Histogram(
                    x=data_caramelo_2[plot_selectionVariable].replace(0, np.nan), name="Caramelo-2"))
                fig.add_trace(go.Histogram(
                    x=data_caramelo_3[plot_selectionVariable].replace(0, np.nan), name="Caramelo-3"))
                fig.add_trace(go.Histogram(
                    x=data_pital_1[plot_selectionVariable].replace(0, np.nan), name="Pital-1"))
                fig.add_trace(go.Histogram(
                    x=data_toposi_2HST1[plot_selectionVariable].replace(0, np.nan), name="Toposi-2HST1"))
                fig.add_trace(go.Histogram(
                    x=data_laEstancia_1[plot_selectionVariable].replace(0, np.nan), name="LaEstancia-1"))

                if (hist_Mode == 'overlay'):

                    fig.update_layout(barmode=hist_Mode,
                                      width=1300, height=630)
                    fig.update_traces(opacity=histOpacity)
                    logs_plot.plotly_chart(fig)

                elif (hist_Mode == 'stack'):
                    fig.update_layout(barmode=hist_Mode,
                                      width=1300, height=630)
                    logs_plot.plotly_chart(fig)

                else:
                    fig.update_layout(width=1300, height=630)
                    logs_plot.plotly_chart(fig)

                logs_plot.write(
                    'Note: Zero values were replaced by NAN.')

        elif (modeType == 'Single Well'):

            selected_well = logs_params.selectbox("Select a well", wells)

            plot_selectionVariable = logs_params.multiselect(
                'Feature:', columns, default='SP')

            wellTops_mode = logs_params.radio(
                'Well Tops', ['Off', 'On'])

            data = load_data()

            fig = go.Figure()

            # logs_plot.write(data)
            # logs_plot.write(data[plot_selectionVariable])

            # logs_plot.write(len(plot_selectionVariable))
            # logs_plot.write(data[plot_selectionVariable[0]])

            for i in range(len(plot_selectionVariable)):
                fig = make_subplots(
                    rows=1, cols=len(plot_selectionVariable), horizontal_spacing=0.05)

                fig.add_trace(go.Scatter(
                    x=data[plot_selectionVariable[i]], y=data['Depth'], name=plot_selectionVariable[i]), row=1, col=i+1)

            fig.update_yaxes(autorange="reversed")
            fig.update_layout(width=400, height=700)
            fig.update_layout(
                yaxis_title="Depth [ft]")
            logs_plot.plotly_chart(fig)

        elif (modeType == 'Multi Well'):
            pass
