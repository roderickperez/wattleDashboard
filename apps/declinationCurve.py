import streamlit as st
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
from plotly import graph_objs as go
from PIL import *
import datetime
import warnings

warnings.simplefilter('ignore')


def app():
    st.markdown('# Production')
    st.markdown('## Declination Curve Analysis')

    # Load data

    wells = ("Caramelo-2", "Caramelo-3", "Toposi-1",
             "Toposi-2H", "LaEstancia-1H")

    columns = ['Date', 'DP in H2O', 'Well Head Pressure [PSI]', 'Casing Pressure [Psi]', 'Choque Fijo', 'Choque Adjustable', 'After Opening to 14/64" Current Flowrate',
               'Current Uplift (14/64") [MCFD]', 'Temp Line [°F]', 'Pressure Line [PSI]', 'Heater Temperature [°F]', 'Orifice Plate', 'Gas Production [Kcfd]', 'After Opening to 12/64" Current Flowrate', 'Current Uplift (12/64") [MCFD]', 'Gas Comsuption [Kcfd]', 'Volumen Oil [Bbls]', 'Volumen Condensate [bls/d]', 'Volumen Water [bls/d]', 'Ambient Temperature [°F]', 'Tubing Head Temperature [°F]',  'Well Name']

    # @st.cache
    def load_data():
        data = pd.read_csv(
            'data/VMM1_AllWells_DetailedProduction_Updated.csv', header=None, infer_datetime_format=True)
        data.columns = ['Date', 'DP in H2O', 'Well Head Pressure [PSI]', 'Casing Pressure [Psi]', 'Choque Fijo', 'Choque Adjustable', 'After Opening to 14/64" Current Flowrate',
                        'Current Uplift (14/64") [MCFD]', 'Temp Line [°F]', 'Pressure Line [PSI]', 'Heater Temperature [°F]', 'Orifice Plate', 'Gas Production [Kcfd]', 'After Opening to 12/64" Current Flowrate', 'Current Uplift (12/64") [MCFD]', 'Gas Comsuption [Kcfd]', 'Volumen Oil [Bbls]', 'Volumen Condensate [bls/d]', 'Volumen Water [bls/d]', 'Ambient Temperature [°F]', 'Tubing Head Temperature [°F]',  'Well Name']

        data = data[data['Well Name'] == selected_well]

        return data

    def ArpsRate(qi, Di, b, t):
        """
        Args:
            qi (constant): initial rate
            Di (constant): initial decline rate
            b (constant): b value
            t : time
        """
        Di = Di/100
        # b = b/100
        arps = qi / (1+b*Di*t)**(1/b)
        return arps

    def cumProduction(qi, Di, b, q):
        """[summary]

        Args:
            qi (constant): initial rate
            Di (constant): initial decline rate
            b (constant): b value
            q : flow rate
        """
        cumProd = qi**(b)/(Di * (1-b))*(qi**(1-b)-q**(1-b))
        return cumProd

    def nominalDecline(Di, b, t):
        """[summary]

        Args:
            Di (constant): initial decline rate
            b (constant): b value
            t : time
        """
        nomDecline = Di/(1+b*Di*t)
        return nomDecline

    ############################
    DCA_params, prod_plot, DCA_output = st.beta_columns((1, 3, 1))

    with DCA_params:
        DCA_params.markdown('### Declination Curve Parameters')
        selected_well = DCA_params.selectbox("Select a well", wells)

        # Load data

        data = load_data()

        DCA_params.markdown('#### Declination Curve (Arps)')

        arpsParameters = st.beta_expander('Parameters')

        qi = arpsParameters.slider('qi:',
                                   min_value=0.001, value=3500.0, max_value=10000.0)
        Di = arpsParameters.slider('Di:',
                                   min_value=0.0, value=0.15, max_value=1.0)
        b = arpsParameters.slider('b:',
                                  min_value=0.0, value=1.4, max_value=3.0)

        DCA_params.markdown('#### Economic')

        economicParameters = st.beta_expander('Parameters')

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

        economicParameters.write('Fixed Operating Cost per Well:')
        FixedOperatingCost = round((
            totalOperatingCost*(percentageFixedOperatingCost/100))/numberWells, 2)
        economicParameters.write(FixedOperatingCost)

        economicParameters.write('Variable Operating Cost per Well:')
        VariableOperatingCost = round((
            totalOperatingCost*(percentageVariableOperatingCost/100))/numberWells, 2)
        economicParameters.write(VariableOperatingCost)

        gasPrice = economicParameters.slider('Gas Price ($/MCF):',
                                             min_value=0.0, value=6.60, max_value=10.0)

        NRI = (workingInterest/100)*(1-(royalty/100))
        st.write('Net Renevue Interest (NRI): ', round(NRI, 2)

        netPrice=NRI*gasPrice*(1-(stateTax/100))

        st.write('Net Price ($/MCF): ', round(netPrice, 2))

        economicLimit=(percentageVariableOperatingCost/100)/netPrice

        st.write('Economic Limit (MCF/d): ', round(economicLimit, 2))

        DCA_params.markdown('#### Forecast')

        foreecastParameters=st.beta_expander('Parameters')
        forecast_days=foreecastParameters.slider('Days:',
                                                   min_value=0, value=1825, max_value=3650)

        DCA_params.markdown('#### Equations')

        arpsEquation_expander=st.beta_expander('Arps Equation')

        arpsEquation_expander.write('Arps Equation')
        arpsEquation_expander.markdown(
            '$q\\left ( t \\right ) = \\frac{q_{i}}{\\left ( 1+b D_{i}t \\right )^{\\frac{1}{b}}}$')

        arpsEquation_expander.write('Arps Cummulative Production')
        arpsEquation_expander.markdown(
            '$G_{p} = \\frac{q_{i}^{b}}{D_{i}\\left ( 1-b \\right )}\\left [ q_{i}^{1-b} - q^{1-b}\\right ]$')

        arpsEquation_expander.write('Nominal Decline')
        arpsEquation_expander.markdown(
            '$D = \\frac{D_{i}}{1+bD_{i}t}$')

        DCAimage_expander=st.beta_expander('DCA Sketch')

        image=Image.open('images/DeclinationCurve.png')
        DCAimage_expander.image(image, width=300)

        economicEquations_expander=DCA_params.beta_expander(
            'Economics')

        economicEquations_expander.write('Net Cash Flow Eq')
        economicEquations_expander.markdown(
            '$NCF = R - I  - E-FIT-OS$')

        economicEquations_expander.write('where:')
        economicEquations_expander.markdown('$R$=Revenue')
        economicEquations_expander.markdown('$I$=Investments')
        economicEquations_expander.markdown('$E$=Expenses')
        economicEquations_expander.markdown('$R$=Federal Income Taxes')
        economicEquations_expander.markdown('$OS$=Outside Shares')

        economicEquations_expander.markdown("<hr/>", unsafe_allow_html=True)

        economicEquations_expander.write('NRI Eq')
        economicEquations_expander.markdown(
            '$NCF = R - I  - E-FIT-OS$')

        economicEquations_expander.markdown("<hr/>", unsafe_allow_html=True)

        economicEquations_expander.write('Economic Limit Eq')
        economicEquations_expander.markdown(
            '$q_{ecl} = \\frac{Operating Cost}{Net Price}$')
        #############################################

        arpsFlowRate=[]

        for i in range(len(data)):
            flow=ArpsRate(qi, Di, b, i)
            arpsFlowRate.append(flow)

        data['arpsFlowRate']=arpsFlowRate

        data_edit=data['Gas Production [Kcfd]'].replace(0, np.nan)

        data['error']=abs((data_edit -
                            data['arpsFlowRate'])/data['Gas Production [Kcfd]'])  # Absolute Relative Error

        firstDay_Forecast=datetime.datetime.strptime(
            data['Date'].iloc[0], '%m/%d/%Y').date()

        endDay_Forecast_=datetime.datetime.strptime(
            data['Date'].iloc[-1], '%m/%d/%Y').date()

        endDay_Forecast=endDay_Forecast_ + \
            pd.to_timedelta(forecast_days, unit='d')

        DCA_forecast=[]

        forecast_dateList=pd.date_range(
            firstDay_Forecast, endDay_Forecast, freq='d')

        DCA_forecast=pd.DataFrame(np.array(
            forecast_dateList.to_pydatetime(), dtype=np.datetime64), columns=['Date'])

        # data['newDate'] = pd.DataFrame(np.array(
        # forecast_dateList.to_pydatetime(), dtype=np.datetime64), columns=['Date'])

        DCA_forecast['Date']=pd.to_datetime(DCA_forecast['Date']).dt.date

        data['Date']=pd.to_datetime(data['Date']).dt.date

        arpsFlowRate_Forecast=[]

        for i in range(len(DCA_forecast)):
            flow_Forecast=ArpsRate(qi, Di, b, i)
            arpsFlowRate_Forecast.append(flow_Forecast)

        DCA_forecast['arpsFlowRate_Forecast']=arpsFlowRate_Forecast

    with prod_plot:
        st.markdown('## Plot')

        fig=make_subplots(rows=2, cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.02)

        fig.add_trace(go.Scatter(
            x=data['Date'], y=data['Gas Production [Kcfd]'], name='Gas Production [Kcfd]'),
            row=1, col=1)

        fig.add_trace(go.Scatter(
            x=DCA_forecast['Date'], y=DCA_forecast['arpsFlowRate_Forecast'], name='Forecast'),
            row=1, col=1)

        fig.add_trace(go.Scatter(
            x=data['Date'], y=data['arpsFlowRate'], name='Arps'),
            row=1, col=1)

        fig.update_layout(legend=dict(
            yanchor="top", y=0.95, xanchor="left", x=0.75))

        fig.update_layout(height=600, width=1100,
                          title_text=f'Gas Production Data: {selected_well}', yaxis_title="Gas Production [Kcfd]")
        # fig.layout.update()
        fig.add_vline(x=endDay_Forecast_,  line_width=1,
                      line_dash="dash", line_color="purple")
        fig.add_hrect(y0=0, y1=economicLimit,
                      line_width=0, fillcolor="red", opacity=0.1)

        fig.add_hline(y=economicLimit,  line_width=1,
                      line_dash="dash", line_color="purple")

        fig.add_trace(go.Scatter(
            x=data['Date'], y=data['error'], name='Absolute Relative Error [Kcfd]'),
            row=2, col=1)

        st.plotly_chart(fig)

    with DCA_output:
        DCA_output.markdown('## Forecast Output')

        DCA_output.markdown(
            f"#### Gas Cum Production [Mcf]")

        gasProduced_=round(data['Gas Production [Kcfd]'].sum(), 2)
        gasProduced=f"{gasProduced_:,}"

        DCA_output.markdown(
            f"<h1 style = 'text-align: center; color: black;'>{gasProduced}</h1>", unsafe_allow_html=True)

        DCA_output.markdown(
            f"#### Gas Reserves [Mcf]")

        nomDecline_=nominalDecline(
            Di, b, DCA_forecast.arpsFlowRate_Forecast[len(DCA_forecast)-1])

        gasReservesDCA_=round(cumProduction(DCA_forecast.arpsFlowRate_Forecast[len(
            DCA_forecast)-1], nomDecline_, b, economicLimit), 2)
        gasReservesDCA=f"{gasReservesDCA_:,}"
        DCA_output.markdown(
            f"<h1 style = 'text-align: center; color: black;'>{gasReservesDCA}</h1>", unsafe_allow_html=True)

        DCA_output.markdown(
            f"#### EUR [Mcf]")

        EUR_=round(gasProduced_ + gasReservesDCA_, 2)

        EUR=f"{EUR_:,}"
        DCA_output.markdown(
            f"<h1 style = 'text-align: center; color: black;'>{EUR}</h1>", unsafe_allow_html=True)

        st.markdown("<hr/>", unsafe_allow_html=True)

        st.markdown(
            f"###### DCA Error")

        DCA_error=round(data['error'].sum(), 2)
        DCA_error=f"{DCA_error:,}"
        DCA_output.markdown(
            f"<h3 style = 'text-align: center; color: black;'>{DCA_error}%</h3>", unsafe_allow_html=True)

        DCA_output.markdown(
            f"###### Nominal Decline")

        nomDecline=round(nomDecline_*100, 4)
        DCA_output.markdown(
            f"<h3 style = 'text-align: center; color: black;'>{nomDecline}%</h3>", unsafe_allow_html=True)
