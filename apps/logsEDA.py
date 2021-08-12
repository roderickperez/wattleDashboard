from re import I
import streamlit as st
import numpy as np
import pandas as pd
from plotly import graph_objs as go
from plotly.subplots import make_subplots
import lasio

wells = ("Crisol-1", "Crisol-2", "Crisol-3",
         "Norean-1", "Aguachica-2", "Bandera-1", "Caramelo-1", "Caramelo-2", "Caramelo-3", "Pital-1", "Toposi-2HST1", "La Estancia-1")

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
    # @st.cache
    def load_wellTops():
        wellTop = pd.read_csv(r'data/wellTops/wellTops.csv')

        wellTop = wellTop[wellTop['Well identifier'] == selected_well]

        return wellTop

    ##############

    logs_params, logs_plot, logs_summary = st.columns((1, 3, 1))

    with logs_params:
        st.markdown('## Parameters')

        mode = ['Single Well', 'Multi Well', 'All Wells']

        modeType = logs_params.radio('Mode', mode)

        if modeType == 'Single Well':

            wells = ("Aguachica-2", "Bandera-1", "Caramelo-1", "Caramelo-2", "Caramelo-3", "Caramelo-5",  "Crisol-1", "Crisol-2", "Crisol-3",
                     "Eucalipto-1", "La Estancia-1", "La Estancia- HST1", "Norean-1", "Pital-1", "Preludio-1", "Reposo-1", "Sabal-1",
                     "Toposi-1", "Toposi-2", "Toposi-2HST1")

            selected_well = logs_params.selectbox("Select a well", wells)

            if selected_well == "Aguachica-2":
                well = lasio.read(r"data/wellLogs/AGUACHICA-2.las")

            elif selected_well == "Bandera-1":
                well = lasio.read(r"data/wellLogs/BANDERA-1.las")

            elif selected_well == "Caramelo-1":
                well = lasio.read(r"data/wellLogs/CARAMELO-1.las")

            elif selected_well == "Caramelo-2":
                well = lasio.read(r"data/wellLogs/CARAMELO-2.las")

            elif selected_well == "Caramelo-3":
                well = lasio.read(r"data/wellLogs/CARAMELO-3.las")

            elif selected_well == "Caramelo-5":
                well = lasio.read(r"data/wellLogs/CARAMELO-5.las")

            elif selected_well == "Crisol-1":
                well = lasio.read(r"data/wellLogs/CRISOL-1.las")

            elif selected_well == "Crisol-2":
                well = lasio.read(r"data/wellLogs/CRISOL-2.las")

            elif selected_well == "Crisol-3":
                well = lasio.read(r"data/wellLogs/CRISOL-3.las")

            elif selected_well == "Eucalipto-1":
                well = lasio.read(r"data/wellLogs/EUCALIPTO-1.las")

            elif selected_well == "La Estancia-1":
                well = lasio.read(r"data/wellLogs/LA ESTANCIA-1.las")

            elif selected_well == "La Estancia- HST1":
                well = lasio.read(r"data/wellLogs/LA ESTANCIA1HST1.las")

            elif selected_well == "Norean-1":
                well = lasio.read(r"data/wellLogs/NOREAN-1.las")

            elif selected_well == "Pital-1":
                well = lasio.read(r"data/wellLogs/PITAL-1.las")

            elif selected_well == "Preludio-1":
                well = lasio.read(r"data/wellLogs/PRELUDIO-1.las")

            elif selected_well == "Reposo-1":
                well = lasio.read(r"data/wellLogs/REPOSO-1.las")

            elif selected_well == "Sabal-1":
                well = lasio.read(r"data/wellLogs/SABAL-1.las")

            elif selected_well == "Toposi-1":
                well = lasio.read(r"data/wellLogs/TOPOSI-1.las")

            elif selected_well == "Toposi-2":
                well = lasio.read(r"data/wellLogs/TOPOSI-2.las")

            elif selected_well == "Toposi-2HST1":
                well = lasio.read(r"data/wellLogs/TOPOSI 2-HST1.las")

            mnemonic = []

            for i in range(len(well.curves)):
                mnemonic.append(well.curves[i].mnemonic)

            well_df = pd.DataFrame(well.data, columns=mnemonic)

            mnemonic.remove('DEPTH')

            well_df = well_df.dropna()

            st.write(
                '<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

            visualizationType = logs_params.radio(
                'Visualization Type', ['1D', '2D'])

            if visualizationType == '1D':

                selected_logs = logs_params.multiselect("Logs", mnemonic,
                                                        default=mnemonic)

                fig = go.Figure()

                fig = make_subplots(
                    rows=1, cols=len(selected_logs), shared_yaxes=True)

                for i in range(len(selected_logs)):
                    fig.add_trace(go.Scatter(
                        x=well_df[selected_logs[i]], y=well_df['DEPTH'], name=selected_logs[i]), row=1, col=i+1)

                fig.update_yaxes(autorange="reversed")
                fig.update_layout(
                    yaxis_title="Depth [ft]",
                    legend=dict(
                        orientation="h",
                    ),
                    # showlegend=False,
                    autosize=True,
                    width=1000,
                    height=700,
                    margin=dict(
                        l=50,
                        r=0,
                        b=0,
                        t=0,
                        pad=0
                    ))

                with logs_summary:
                    logs_summary.markdown('## Summary')
                    logSummary_expander = logs_summary.expander('Details')
                    logSummary_expander.write(well_df.describe())

                    ###############################
                    logs_summary.markdown('### Well Tops')

                    wellTops_mode = logs_summary.radio(
                        'Well Tops', ['Off', 'On'])

                    if wellTops_mode == 'On':

                        wellTop = load_wellTops()

                        wellTop.drop('Well identifier', axis=1, inplace=True)

                        wellLogTable_expander = logs_summary.expander(
                            'Well Logs Table (MD)')

                        wellLogTable_expander.table(wellTop)

                        wellTops = wellTop['Surface'].unique()

                        logs_summary.markdown('#### Interpreter')

                        WattleInterpreter = logs_summary.checkbox(
                            'Wattle')

                        LewisInterpreter = logs_summary.checkbox(
                            'Lewis Energy')

                        selected_wellTops = logs_summary.multiselect(
                            "Well Tops", wellTops)

                        for i in range(len(selected_wellTops)):
                            wellSelection = wellTop[wellTop['Surface']
                                                    == selected_wellTops[i]]

                            fig.add_hline(y=int(wellSelection.MD),  line_width=1,
                                          line_dash="dash", line_color="black")

                logs_plot.plotly_chart(fig)

            elif visualizationType == '2D':
                selected_X = logs_params.selectbox("X", mnemonic)

                selected_Y = logs_params.selectbox("Y", mnemonic)

                depthRangeExpander = logs_params.expander(
                    'Depth Range')

                top_depth = depthRangeExpander.slider('Depth Top [ft]:',
                                                      min_value=float(well_df['DEPTH'].min()), value=float(well_df['DEPTH'].min()), max_value=float(well_df['DEPTH'].max()), step=0.5)

                bottom_depth = depthRangeExpander.slider('Depth Bottom [ft]:',
                                                         min_value=float(well_df['DEPTH'].min()), value=float(
                                                             well_df['DEPTH'].max()), max_value=float(well_df['DEPTH'].max()), step=0.5)

                if top_depth > bottom_depth:
                    depthRangeExpander.error(
                        "Error: Bottom depth can't be greater than top depth.")

                top_index = well_df[well_df['DEPTH'] == top_depth].index.tolist()[
                    0]
                bottom_index = well_df[well_df['DEPTH'] == bottom_depth].index.tolist()[
                    0]

                visualizationTypeExpander = logs_params.expander(
                    'Visualization Settings')

                radius = visualizationTypeExpander.slider('Radius:',
                                                          min_value=0, value=10, max_value=20)

                color = visualizationTypeExpander.color_picker(
                    'Color:', '#F900C9')

                fig = go.Figure()

                fig = make_subplots(
                    rows=1, cols=3, shared_yaxes=False, column_widths=[0.3, 0.3, 0.6])

                fig.add_trace(go.Scatter(
                    x=well_df[selected_X], y=well_df['DEPTH'], name=selected_X), row=1, col=1)

                fig.add_hline(y=top_depth,  line_width=1,
                              line_dash="dashdot", line_color="red", row=1, col=1)

                fig.add_hline(y=bottom_depth,  line_width=1,
                              line_dash="dashdot", line_color="red", row=1, col=1)

                fig.add_hrect(y0=top_depth, y1=bottom_depth,
                              line_width=0, fillcolor="green", opacity=0.05, row=1, col=1)

                fig.add_trace(go.Scatter(
                    x=well_df[selected_Y], y=well_df['DEPTH'], name=selected_Y), row=1, col=2)

                fig.add_hline(y=top_depth,  line_width=1,
                              line_dash="dashdot", line_color="red", row=1, col=2)

                fig.add_hline(y=bottom_depth,  line_width=1,
                              line_dash="dashdot", line_color="red", row=1, col=2)

                fig.add_hrect(y0=top_depth, y1=bottom_depth,
                              line_width=0, fillcolor="green", opacity=0.05, row=1, col=2)

                fig.add_trace(go.Scatter(
                    x=well_df.loc[top_index:bottom_index,
                                  selected_X], y=well_df.loc[top_index:bottom_index, selected_Y],
                    mode='markers', marker=dict(color=color, size=radius)), row=1, col=3)

                # Update xaxis properties
                fig.update_xaxes(title_text=selected_X, row=1, col=1)
                fig.update_xaxes(title_text=selected_Y, row=1, col=2)
                fig.update_xaxes(title_text=selected_X, row=1, col=3)

                fig.update_yaxes(
                    title_text="Depth [ft]", autorange="reversed", row=1, col=1)
                fig.update_yaxes(
                    title_text="Depth [ft]", autorange="reversed", row=1, col=2)
                fig.update_yaxes(title_text=selected_Y, row=1, col=3)

                # fig.update_yaxes(autorange="reversed")
                fig.update_layout(
                    showlegend=False,
                    autosize=True,
                    width=1400,
                    height=700,
                    margin=dict(
                        l=50,
                        r=0,
                        b=0,
                        t=0,
                        pad=0
                    ))

                wellTops_mode = logs_params.radio(
                    'Well Tops', ['Off', 'On'])

                if wellTops_mode == 'On':

                    wellTop = load_wellTops()

                    wellTop.drop('Well identifier', axis=1, inplace=True)

                    wellLogSettings_expander = logs_params.expander(
                        'Well Logs Settings')

                    wellTops = wellTop['Surface'].unique()

                    wellLogSettings_expander.markdown('#### Interpreter')

                    WattleInterpreter = wellLogSettings_expander.checkbox(
                        'Wattle')

                    LewisInterpreter = wellLogSettings_expander.checkbox(
                        'Lewis Energy')

                    selected_wellTops = wellLogSettings_expander.multiselect(
                        "Well Tops", wellTops)

                    for i in range(len(selected_wellTops)):
                        wellSelection = wellTop[wellTop['Surface']
                                                == selected_wellTops[i]]

                        fig.add_hline(y=int(wellSelection.MD),  line_width=1,
                                      line_dash="dash", line_color="black", row=1, col=1)

                        fig.add_hline(y=int(wellSelection.MD),  line_width=1,
                                      line_dash="dash", line_color="black", row=1, col=2)

                logs_plot.plotly_chart(fig)

        elif (modeType == 'All Wells'):
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

        elif (modeType == 'Multi Well'):
            pass
