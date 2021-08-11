import streamlit as st
from datetime import date
#import pandas as pd
import yfinance as yf
from plotly import graph_objs as go


def app():
    st.markdown('# Market Financial Data')

    # Initial Parameters
    START = "2012-11-17"
    TODAY = date.today().strftime("%Y-%m-%d")

    @st.cache
    def load_stock_data(stock):
        data = yf.download(stock, START, TODAY)  # Data is already in pandas
        data.reset_index(inplace=True)  # Put the date in first column
        return data

    ##################################

    st.write('Source: Yahoo-Finance')

    crude_plot, naturGas_plot = st.columns(2)

    with crude_plot:
        st.markdown("### Crude")
        stock_crude = ("CLU21.NYM",
                       "CLV21.NYM", "CLX21.NYM", "CLZ21.NYM")
        selected_stock_crude = st.selectbox("Select stock", stock_crude)
        data_crude = load_stock_data(selected_stock_crude)

        fig_crude = go.Figure()
        fig_crude.add_trace(go.Scatter(
            x=data_crude['Date'], y=data_crude['Close'], fill='tozeroy',
            line=dict(color='green')))
        fig_crude.layout.update(xaxis_rangeslider_visible=True)
        st.plotly_chart(fig_crude)

        expander_crudePriceTable = st.expander(
            f'Show Crude Table: {selected_stock_crude}')
        expander_crudePriceTable.write(data_crude.head())

    with naturGas_plot:
        st.markdown("### Natural Gas")

        stock_naturGas = ("NGU21.NYM",
                          "NGV22.NYM?P=NGV22.NYM", "NGX21.NYM", "NGZ21.NYM")
        selected_stock_naturGas = st.selectbox("Select stock", stock_naturGas)
        data_naturGas = load_stock_data(selected_stock_naturGas)

        fig_gas = go.Figure()
        fig_gas.add_trace(go.Scatter(
            x=data_naturGas['Date'], y=data_naturGas['Close'], fill='tozeroy',
            line=dict(color='red')))
        fig_gas.layout.update(xaxis_rangeslider_visible=True)
        st.plotly_chart(fig_gas)

        expander_naturGasPriceTable = st.expander(
            f'Show Crude Table: {selected_stock_naturGas}')
        expander_naturGasPriceTable.write(data_naturGas.head())
