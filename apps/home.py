import streamlit as st
import pandas as pd
from plotly import graph_objs as go


def app():
    st.markdown('# Production Summary | VMM-1')
    st.write("Updated: 6/28/2021")

    @st.cache
    def load_data():
        data = pd.read_csv('data/VMM1_AllWells_DetailedProduction_Updated.csv',
                           header=None, infer_datetime_format=True)
        data.columns = ['Date', 'DP in H2O', 'Well Head Pressure [PSI]', 'Casing Pressure [Psi]', 'Choque Fijo', 'Choque Adjustable', 'After Opening to 14/64" Current Flowrate',
                        'Current Uplift (14/64") [MCFD]', 'Temp Line [°F]', 'Pressure Line [PSI]', 'Heater Temperature [°F]', 'Orifice Plate', 'Gas Production [Kcfd]', 'After Opening to 12/64" Current Flowrate', 'Current Uplift (12/64") [MCFD]', 'Gas Comsuption [Kcfd]', 'Volumen Oil [Bbls]', 'Volumen Condensate [bls/d]', 'Volumen Water [bls/d]', 'Ambient Temperature [°F]', 'Tubing Head Temperature [°F]',  'Well Name']

        return data

    data_total = load_data()

    data_Caramelo_2 = data_total[data_total['Well Name'] == "Caramelo-2"]
    data_Caramelo_3 = data_total[data_total['Well Name'] == "Caramelo-3"]
    data_Toposi_1 = data_total[data_total['Well Name'] == "Toposi-1"]
    data_Toposi_2H = data_total[data_total['Well Name'] == "Toposi-2H"]
    data_LaEstancia_1H = data_total[data_total['Well Name'] == "LaEstancia-1H"]

    ######################
    # Cummulative
    ######################

    gas_cum_total = round(data_total['Gas Production [Kcfd]'].sum(), 2)
    oil_cum_total = round(data_total['Volumen Oil [Bbls]'].sum(), 2)
    condens_cum_total = round(
        data_total['Volumen Condensate [bls/d]'].sum(), 2)
    water_cum_total = round(
        data_total['Volumen Water [bls/d]'].sum(), 2)

    #############
    # Gas
    gas_cum_caramelo_2 = round(
        data_Caramelo_2['Gas Production [Kcfd]'].sum(), 2)
    gas_cum_caramelo_3 = round(
        data_Caramelo_3['Gas Production [Kcfd]'].sum(), 2)
    gas_cum_toposi_1 = round(
        data_Toposi_1['Gas Production [Kcfd]'].sum(), 2)
    gas_cum_toposi_2H = round(
        data_Toposi_1['Gas Production [Kcfd]'].sum(), 2)
    gas_cum_laEstancia_1H = round(
        data_LaEstancia_1H['Gas Production [Kcfd]'].sum(), 2)

    #############
    # Oil
    oil_cum_caramelo_2 = round(
        data_Caramelo_2['Volumen Oil [Bbls]'].sum(), 2)
    oil_cum_caramelo_3 = round(
        data_Caramelo_3['Volumen Oil [Bbls]'].sum(), 2)
    oil_cum_toposi_1 = round(
        data_Toposi_1['Volumen Oil [Bbls]'].sum(), 2)
    oil_cum_toposi_2H = round(
        data_Toposi_2H['Volumen Oil [Bbls]'].sum(), 2)
    oil_cum_laEstancia_1H = round(
        data_LaEstancia_1H['Volumen Oil [Bbls]'].sum(), 2)

    #############
    # Condensate
    condens_cum_caramelo_2 = round(
        data_Caramelo_2['Volumen Condensate [bls/d]'].sum(), 2)
    condens_cum_caramelo_3 = round(
        data_Caramelo_3['Volumen Condensate [bls/d]'].sum(), 2)
    condens_cum_toposi_1 = round(
        data_Toposi_1['Volumen Condensate [bls/d]'].sum(), 2)
    condens_cum_toposi_2H = round(
        data_Toposi_2H['Volumen Condensate [bls/d]'].sum(), 2)
    condens_cum_laEstancia_1H = round(
        data_LaEstancia_1H['Volumen Condensate [bls/d]'].sum(), 2)

    #############
    # Water
    water_cum_caramelo_2 = round(
        data_Caramelo_2['Volumen Water [bls/d]'].sum(), 2)
    water_cum_caramelo_3 = round(
        data_Caramelo_3['Volumen Water [bls/d]'].sum(), 2)
    water_cum_toposi_1 = round(
        data_Toposi_1['Volumen Water [bls/d]'].sum(), 2)
    water_cum_toposi_2H = round(
        data_Toposi_2H['Volumen Water [bls/d]'].sum(), 2)
    water_cum_laEstancia_1H = round(
        data_LaEstancia_1H['Volumen Water [bls/d]'].sum(), 2)

    ######################
    # Current
    ######################

    # Wells

    # Gas
    gas_current_caramelo_2 = round(
        data_Caramelo_2['Gas Production [Kcfd]'].iloc[-1], 2)
    gas_current_caramelo_3 = round(
        data_Caramelo_3['Gas Production [Kcfd]'].iloc[-1], 2)
    gas_current_toposi_1 = round(
        data_Toposi_1['Gas Production [Kcfd]'].iloc[-1], 2)
    gas_current_toposi_2H = round(
        data_Toposi_1['Gas Production [Kcfd]'].iloc[-1], 2)
    gas_current_laEstancia_1H = round(
        data_LaEstancia_1H['Gas Production [Kcfd]'].iloc[-1], 2)
    ##############################################

    # Oil
    oil_current_caramelo_2 = round(
        data_Caramelo_2['Volumen Oil [Bbls]'].iloc[-1], 2)
    oil_current_caramelo_3 = round(
        data_Caramelo_3['Volumen Oil [Bbls]'].iloc[-1], 2)
    oil_current_toposi_1 = round(
        data_Toposi_1['Volumen Oil [Bbls]'].iloc[-1], 2)
    oil_current_toposi_2H = round(
        data_Toposi_1['Volumen Oil [Bbls]'].iloc[-1], 2)
    oil_current_laEstancia_1H = round(
        data_LaEstancia_1H['Volumen Oil [Bbls]'].iloc[-1], 2)
    ##############################################

    # Water
    water_current_caramelo_2 = round(
        data_Caramelo_2['Volumen Water [bls/d]'].iloc[-1], 2)
    water_current_caramelo_3 = round(
        data_Caramelo_3['Volumen Water [bls/d]'].iloc[-1], 2)
    water_current_toposi_1 = round(
        data_Toposi_1['Volumen Water [bls/d]'].iloc[-1], 2)
    water_current_toposi_2H = round(
        data_Toposi_1['Volumen Water [bls/d]'].iloc[-1], 2)
    water_current_laEstancia_1H = round(
        data_LaEstancia_1H['Volumen Water [bls/d]'].iloc[-1], 2)
    ##############################################

    # First Row
    gas_current, gauge_gas = st.columns(2)

    with gas_current:

        fig_current_gas = go.Figure()
        fig_current_gas.add_trace(
            go.Pie(values=[gas_current_caramelo_2, gas_current_caramelo_3, gas_current_toposi_1, gas_current_toposi_2H, gas_current_laEstancia_1H],
                   labels=['Caramelo-2', 'Caramelo-3',
                           'Toposi-1', 'Toposi-2H', 'La Estancia-1H'],
                   domain=dict(x=[0.0, 0.0]), hole=.5))

        fig_current_gas.update_traces(textposition='inside')
        fig_current_gas.update_layout(legend=dict(
            yanchor="bottom", y=0.1, xanchor="left", x=0.01))

        fig_current_gas.update_layout(

            uniformtext_minsize=20,
            uniformtext_mode='hide',
            legend=dict(
                orientation="h",
            ),
            # showlegend=False,
            autosize=True,
            width=550,
            height=700,
            margin=dict(
                l=50,
                r=50,
                b=0,
                t=0,
                pad=100
            ))
        gas_current.plotly_chart(fig_current_gas)

    with gauge_gas:

        gas_current_total = gas_current_caramelo_2+gas_current_caramelo_3 + \
            gas_current_toposi_1+gas_current_toposi_2H+gas_current_laEstancia_1H

        # gas_current_total = f"{gas_current_total:,}"
        # gas_current.markdown(
        #     f"<h1 style = 'text-align: center; color: red;'>{gas_current_total}</h1>", unsafe_allow_html=True)

        fig_gaugeGas = go.Figure(go.Indicator(
            domain={'x': [0, 1], 'y': [0, 1]},
            value=gas_current_total,
            mode="gauge+number+delta",
            title={'text': "Gas Production [Kcfd]"},
            delta={'reference': 6000},
            gauge={'axis': {'range': [None, 7000]},
                   'steps': [
                {'range': [0, 4500], 'color': "lightgray"},
                {'range': [4500, 5500], 'color': "lightgreen"}],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 6000}}))

        fig_gaugeGas.update_layout(
            autosize=True,
            width=750,
            height=700,
            margin=dict(
                l=50,
                r=50,
                b=0,
                t=0,
                pad=100
            ))
        gauge_gas.plotly_chart(fig_gaugeGas)

    st.markdown("<hr/>", unsafe_allow_html=True)

    ##############################################
    # Second Row

    st.markdown("### Wells")

    caramelo_2_current, caramelo_3_current, toposi_1_current, toposi_2H_current, laEstancia_1H_current = st.columns(
        5)

    with caramelo_2_current:
        caramelo_2_current.markdown("#### Caramelo-2 [MCF]")

        gas_current_caramelo_2 = f"{gas_current_caramelo_2:,}"
        caramelo_2_current.markdown(
            f"<h2 style = 'text-align: center; color: black;'>{gas_current_caramelo_2}</h2>", unsafe_allow_html=True)

    with caramelo_3_current:
        caramelo_3_current.markdown("#### Caramelo-3 [MCF]")

        gas_current_caramelo_3 = f"{gas_current_caramelo_3:,}"
        caramelo_3_current.markdown(
            f"<h2 style = 'text-align: center; color: black;'>{gas_current_caramelo_3}</h2>", unsafe_allow_html=True)

    with toposi_1_current:
        toposi_1_current.markdown("#### Toposi-1 [MCF]")

        gas_current_toposi_1 = f"{gas_current_toposi_1:,}"

        toposi_1_current.markdown(
            f"<h2 style = 'text-align: center; color: black;'>{gas_current_toposi_1}</h2>", unsafe_allow_html=True)

    with toposi_2H_current:
        toposi_2H_current.markdown("#### Toposi-2H [MCF]")

        gas_current_toposi_2H = f"{gas_current_toposi_2H:,}"
        toposi_2H_current.markdown(
            f"<h2 style = 'text-align: center; color: black;'>{gas_current_toposi_2H}</h2>", unsafe_allow_html=True)

    with laEstancia_1H_current:
        laEstancia_1H_current.markdown("#### La Estancia-1H [MCF]")

        gas_current_laEstancia_1H = f"{gas_current_laEstancia_1H:,}"

        laEstancia_1H_current.markdown(
            f"<h2 style = 'text-align: center; color: black;'>{gas_current_laEstancia_1H}</h2>", unsafe_allow_html=True)

    ##############################################

    # Third Row

    st.markdown("<hr/>", unsafe_allow_html=True)

    st.markdown("## Cummulative")

    st.markdown("### Field")

    gas_kpi, oil_kpi, water_kpi = st.columns(3)  # condens_kpi

    with gas_kpi:
        gas_kpi.markdown("### Gas [MCF]")

        gas_cum_total = f"{gas_cum_total:,}"
        gas_kpi.markdown(
            f"<h1 style = 'text-align: center; color: red;'>{gas_cum_total}</h1>", unsafe_allow_html=True)

        fig_gas = go.Figure()
        fig_gas.add_trace(
            go.Pie(values=[gas_cum_caramelo_2, gas_cum_caramelo_3, gas_cum_toposi_1, gas_cum_toposi_2H, gas_cum_laEstancia_1H],
                   labels=['Caramelo-2', 'Caramelo-3',
                           'Toposi-1', 'Toposi-2H', 'La Estancia-1H'],
                   domain=dict(x=[0.0, 0.0]), hole=.5))

        fig_gas.update_traces(textposition='inside')
        fig_gas.update_layout(uniformtext_minsize=20, uniformtext_mode='hide')
        fig_gas.update_layout(legend=dict(
            yanchor="top", y=0.99, xanchor="left", x=0.01))
        gas_kpi.plotly_chart(fig_gas)

    with oil_kpi:
        oil_kpi.markdown("### Oil [Bbls]")
        oil_cum_total = f"{oil_cum_total:,}"
        oil_kpi.markdown(
            f"<h1 style = 'text-align: center; color: green;'>{oil_cum_total}</h1>", unsafe_allow_html=True)

        fig_oil = go.Figure()
        fig_oil.add_trace(
            go.Pie(values=[oil_cum_caramelo_2, oil_cum_caramelo_3, oil_cum_toposi_1, oil_cum_toposi_2H, oil_cum_laEstancia_1H],
                   labels=['Caramelo-2', 'Caramelo-3',
                           'Toposi-1', 'Toposi-2H', 'La Estancia-1H'],
                   domain=dict(x=[0.0, 0.0]), hole=.5))

        fig_oil.update_traces(textposition='inside')
        fig_oil.update_layout(uniformtext_minsize=20, uniformtext_mode='hide')
        fig_oil.update_layout(legend=dict(
            yanchor="top", y=0.99, xanchor="left", x=0.01))
        oil_kpi.plotly_chart(fig_oil)

    # with condens_kpi:
    #     condens_kpi.markdown("### Condensate [Bbls]")
    #     condens_kpi.markdown(
    #         f"<h1 style = 'text-align: center; color: green;'>{condens_cum_total}</h1>", unsafe_allow_html=True)

    #     fig_condens = go.Figure()
    #     fig_condens.add_trace(
    #         go.Pie(values=[condens_cum_caramelo_2, condens_cum_caramelo_3, condens_cum_toposi_1, condens_cum_toposi_2H, condens_cum_laEstancia_1H],
    #                labels=['Caramelo-2', 'Caramelo-3',
    #                        'Toposi-1', 'Toposi-2H', 'La Estancia-1H'],
    #                domain=dict(x=[0.0, 0.0]), hole=.5))

    #     fig_condens.update_traces(textposition='inside')
    #     fig_condens.update_layout(
    #         uniformtext_minsize=20, uniformtext_mode='hide')
    #     fig_condens.update_layout(legend=dict(
    #         yanchor="top", y=0.99, xanchor="left", x=0.01))
    #     condens_kpi.plotly_chart(fig_condens)

    with water_kpi:
        water_kpi.markdown("### Water [Bbls]")
        water_cum_total = f"{water_cum_total:,}"
        water_kpi.markdown(
            f"<h1 style = 'text-align: center; color: blue;'>{water_cum_total}</h1>", unsafe_allow_html=True)

        fig_water = go.Figure()
        fig_water.add_trace(
            go.Pie(values=[water_cum_caramelo_2, water_cum_caramelo_3, water_cum_toposi_1, water_cum_toposi_2H, water_cum_laEstancia_1H],
                   labels=['Caramelo-2', 'Caramelo-3',
                           'Toposi-1', 'Toposi-2H', 'La Estancia-1H'],
                   domain=dict(x=[0.0, 0.0]), hole=.5))

        fig_water.update_traces(textposition='inside')
        fig_water.update_layout(uniformtext_minsize=20,
                                uniformtext_mode='hide')
        fig_water.update_layout(legend=dict(
            yanchor="top", y=0.99, xanchor="left", x=0.01))
        water_kpi.plotly_chart(fig_oil)

    st.markdown("<hr/>", unsafe_allow_html=True)

    ##############################################

    # Forth Row
    st.markdown("### Well")

    caramelo_2_kpi, caramelo_3_kpi, toposi_1_kpi, toposi_2H_kpi, laEstancia_1H_kpi = st.columns(
        5)

    with caramelo_2_kpi:
        st.markdown("#### Caramelo-2 [MCF]")

        gas_cum_caramelo_2 = f"{gas_cum_caramelo_2:,}"
        st.markdown(
            f"<h2 style = 'text-align: center; color: black;'>{gas_cum_caramelo_2}</h2>", unsafe_allow_html=True)

    with caramelo_3_kpi:
        st.markdown("#### Caramelo-3 [MCF]")

        gas_cum_caramelo_3 = f"{gas_cum_caramelo_3:,}"
        st.markdown(
            f"<h2 style = 'text-align: center; color: black;'>{gas_cum_caramelo_3}</h2>", unsafe_allow_html=True)

    with toposi_1_kpi:
        st.markdown("#### Toposi-1 [MCF]")

        gas_cum_toposi_1 = f"{gas_cum_toposi_1:,}"

        st.markdown(
            f"<h2 style = 'text-align: center; color: black;'>{gas_cum_toposi_1}</h2>", unsafe_allow_html=True)

    with toposi_2H_kpi:
        st.markdown("#### Toposi-2H [MCF]")

        gas_cum_toposi_2H = f"{gas_cum_toposi_2H:,}"
        st.markdown(
            f"<h2 style = 'text-align: center; color: black;'>{gas_cum_toposi_2H}</h2>", unsafe_allow_html=True)

    with laEstancia_1H_kpi:
        st.markdown("#### La Estancia-1H [MCF]")

        gas_cum_laEstancia_1H = f"{gas_cum_laEstancia_1H:,}"

        st.markdown(
            f"<h2 style = 'text-align: center; color: black;'>{gas_cum_laEstancia_1H}</h2>", unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)
