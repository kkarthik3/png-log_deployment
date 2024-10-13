import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from request_log import get_logs
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

if "data" not in st.session_state:
    st.session_state.data = None


st.set_page_config(
    page_title="Development PNG Logs",layout="wide")

st.title("Development PNG Logs & Analysis")

is_production = st.toggle("Click here to Analyse Production")

if is_production:
    try:
        st.button("Click To refresh logs", on_click=get_logs,args=("prod",))
    except Exception as e:
        st.error("Client not accessible")
else:
    try:
        st.button("Click To refresh logs", on_click=get_logs,args=("dev",))
    except Exception as e:
        st.error("Client not accessible")  

options_tab = option_menu(None, ["Logs","Token Analysis", "Cost Analysis"], 
    icons=['database-fill', 'clipboard-data-fill','coin'], 
    menu_icon="cast", default_index=0, orientation="horizontal")

if options_tab == "Logs":
    try:
        if is_production:
            csv_data = "prod.csv"
        else:
            csv_data = "dev.csv"
        data = pd.read_csv(csv_data,header=None)
        data.columns = ['Date', 'Time(24hr IST)','Query', 'Input_Tokens', 'Output_Tokens', 'Time_Taken' ,'LLM_output' ,'Overall_Output'] 


        # data['Datetime'] = pd.to_datetime(data['Date'] + ' ' + data['Time(24hr IST)'], format='%Y-%m-%d %H:%M')

        st.session_state.data = data

        st.dataframe(data.tail(10))

    except Exception as e:
        st.error("Please refresh the logs")

elif options_tab == "Token Analysis":
    if st.session_state.data is not None:

        ##############################HIstogram For Time Taken############################
        st.subheader("Time Taken For Exceution")
        
        fig = px.histogram(st.session_state.data, x='Time_Taken', 
                        title="time taken",
                        width=700, height=500)
        
        fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), 
                        title_x=0.5, )
        
        st.plotly_chart(fig)

        st.info("Average Time taken is {}".format(st.session_state.data['Time_Taken'].mean()))
        st.divider()

        ############################## BAR chart for Date wise Token ############################
        st.subheader("Date-wise Input and Output Tokens")
        tota_datewise_data = st.session_state.data.groupby('Date', as_index=False)[['Input_Tokens', 'Output_Tokens']].sum()
        mean_datewise_data = st.session_state.data.groupby('Date', as_index=False)[['Input_Tokens', 'Output_Tokens']].mean()
        mean_datewise_data.columns = ['Date', 'Avg_Input_Tokens', 'Avg_Output_Tokens']

        datewise_data = pd.merge(tota_datewise_data, mean_datewise_data, on='Date')

        st.dataframe(datewise_data.tail(10),use_container_width=True)

        # Make sure your data includes 'Date', 'Input_Tokens', and 'Output_Tokens' columns
        fig = px.bar(datewise_data, 
                    x='Date', 
                    y=['Input_Tokens', 'Output_Tokens'], 
                    title="Date-wise Input and Output Tokens",
                    labels={'Date': 'Date', 'value': 'Tokens'},
                    width=800, height=500)

        # Update layout for better visualization
        fig.update_layout(
            margin=dict(l=0, r=0, t=30, b=0),
            title_x=0.5,
            xaxis_title="Date",
            yaxis_title="Tokens",
            legend_title="Token Type"
        )

        # Display the chart in Streamlit
        st.plotly_chart(fig)

        st.info("Average Input Tokens used is {}".format(st.session_state.data['Input_Tokens'].mean()))
        st.info("Average Output Tokens used is {}".format(st.session_state.data['Output_Tokens'].mean()))


        st.divider()
        st.subheader("Day and month wise requests calclation")
        daily_group = st.session_state.data.groupby('Date').size().reset_index(name='Daily_Count')

        # Plot the bar chart using Plotly
        fig = px.bar(daily_group, 
                    x='Date', 
                    y='Daily_Count', 
                    title='Daily Log Count',
                    labels={'Date': 'Date', 'Daily_Count': 'Number of Entries'},
                    width=800, height=500)

        # Update layout for better visualization
        fig.update_layout(
            margin=dict(l=0, r=0, t=30, b=0),
            title_x=0.5,
            xaxis_title="Date",
            yaxis_title="Number of Entries",
            legend_title="Daily Count"
        )

        # Display the chart in Streamlit
        st.plotly_chart(fig)

else:
    if st.session_state.data is not None:
        ####################################### AWS COST ########################################
        st.markdown(
                "[View AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)"
            )
        
        col1, col2, col3 = st.columns(3)

        with col1:
            cost_input = st.number_input("Enter your AWS Cost for input tokens per 1000 tokens in USD",value=0.00054, min_value=0.000001)

        with col2:
            cost_output = st.number_input("Enter your AWS Cost for output tokens per 1000 tokens in USD",value=0.00084, min_value=0.000001)

        with col3:
            USD_To_INR = st.number_input("Enter your USD to INR conversion rate", value=83)

        def calculate_cost(cost_input, cost_output):
            if cost_input and cost_output:
                if USD_To_INR:
                    st.session_state.data['Cost(INR)'] = st.session_state.data['Input_Tokens'] * (float(cost_input) / 1000) * USD_To_INR + st.session_state.data['Output_Tokens'] * (float(cost_output) / 1000)* USD_To_INR
                else:
                    st.session_state.data['Cost(INR)'] = st.session_state.data['Input_Tokens'] * (float(cost_input) / 1000) * 83 + st.session_state.data['Output_Tokens'] * (float(cost_output) / 1000)* 83
                if cost_input and cost_output:
                    st.session_state.data['Cost(USD)'] = st.session_state.data['Input_Tokens'] * (float(cost_input) / 1000) + st.session_state.data['Output_Tokens'] * (float(cost_output) / 1000)
        price_click = st.button("Click to calculate cost", on_click=calculate_cost, args=(cost_input, cost_output))
        # st.session_state.data =
        st.divider()
        


        ############################## BAR LINE CHART FOR DATE WISE COST ############################
        if price_click:
            st.subheader("Date-wise Cost Default Cost of MIstral 8x7b In AWS Bedrock Mumbai region")

            if "Cost(INR)" in st.session_state.data.columns and "Cost(USD)" in st.session_state.data.columns:
                total_cost_datewise_data = st.session_state.data.groupby('Date', as_index=False)[['Cost(INR)', 'Cost(USD)']].sum()
                mean_cost_datewise_data = st.session_state.data.groupby('Date', as_index=False)[['Cost(INR)', 'Cost(USD)']].mean()

                mean_cost_datewise_data.columns = ['Date', 'Avg_cost_INR', 'Avg_cost_USD']

                cost_datewise_data = pd.merge(total_cost_datewise_data, mean_cost_datewise_data, on='Date')

                
                # Make sure your data includes 'Date', 'Input_Tokens', and 'Output_Tokens' columns
                fig = px.bar(cost_datewise_data, 
                            x='Date', 
                            y=['Cost(INR)'], 
                            title="Date-wise COST Analysis",
                            labels={'Date': 'Date', 'value': 'COST INR'},
                            width=800, height=500)

                # Update layout for better visualization
                fig.update_layout(
                    margin=dict(l=0, r=0, t=30, b=0),
                    title_x=0.5,
                    xaxis_title="Date",
                    yaxis_title="Tokens",
                    legend_title="Token Type"
                )

                # Display the chart in Streamlit
                st.plotly_chart(fig)

                st.info("Average Cost INR used is {}".format(st.session_state.data['Cost(INR)'].mean()))
                st.info("Average Cost USD used is {}".format(st.session_state.data['Cost(USD)'].mean()))


        
