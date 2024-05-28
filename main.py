import psycopg2
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
from csv_tasks import *
from sql_tasks import *


def connect():
    """_summary_: Connects to the PostgreSQL database.

    Returns:
        psycopg2 connection: The connection to the PostgreSQL database.
    """
    try:
        # Edit the below lines  with your credentials 
        conn = psycopg2.connect(host = 'localhost',
                                database = 'testeSQL',
                                user = 'admin',
                                password = 'admin',
                                port = '5432')
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    
    return conn


# Realizing the connection with database and reading the csv
conn = connect() 
data = pd.read_csv('DB_Teste.csv', sep=';')

#creating the streamlit page
st.set_page_config(page_title='SQL Test for triggo.ai', layout="wide",page_icon = ':chart_with_upwards_trend:',
                   menu_items={
        'About': """
                    # This app was made for the triggo.ai sql challenge. 
                    Made by: Lucas Henrique Marchiori"""
    })

#creating the option menu for navigate between the pages
selected = option_menu(None, ['Home', 'CSV Tasks', 'SQL Tasks', 'About'], 
    icons=['house-fill', 'file-earmark-bar-graph-fill', "database-fill", 'info-circle-fill'], 
    menu_icon="cast", default_index=0, orientation="horizontal")

if selected == 'Home':
    st.title('Home')
    st.write('The original data whitout any pre-process can be found on this homepage for consultation purposes.')
    st.write('To view the tasks carried out using Pandas and CSV or those using SQL, use the main menu above')
    st.dataframe(data)

elif selected == 'CSV Tasks':
    formated_data = formating_columns(data)
    st.title('CSV Tasks')
    
    # CSV TASK1
    st.subheader('Sales by vendor')
    st.write('Here is a summary of the amount sold by each seller, where the table is sorted from highest to lowest, there is also a graph to better visualize the difference in values between the sellers')
    c1, c2 = st.columns(2)
    with c1:
        # Calling the function sumarize_sellers  from csv_tasks and plotting the output dataframe.
        data_seller = sumarize_sellers(formated_data)
        st.dataframe(data_seller)
    with c2:
        # getting the sum of "Valor" column for each vendor and plot a barchart
        data_seller = formated_data.groupby('Vendedor').agg({'Valor': 'sum'})
        st.bar_chart(data_seller)
    
    # CSV TASK2
    st.subheader('Customer with the highest and lowest sales')
    st.write("This shows which customer made the largest purchase and which made the smallest. We've divided it into two dataframes for better visualization: the first contains only the customer's ID and the value of the purchase, and the second contains all the information in case of need a more detailed query.")
    # Calling the function best_and_worst_client from csv_tasks and save the output on the data_cliente variable
    data_client = best_and_worst_client(formated_data)
    c3,c4 = st.columns(2)
    with c3:
        # ploting only de columns "Cliente" and "Valor" from the data_cliente dataframe
        st.dataframe(data_client[['Cliente', 'Valor']])
    with c4:
        # ploting all the data_cliente dataframe
        st.dataframe(data_client)
    
    #CSV TASK3
    st.subheader('Average value by sales type')
    st.write('Here is the average sales value of each different type, where the table is sorted from highest to lowest, there is also a graph to better visualize the difference in values between the types')
    c5,c6 = st.columns(2)
    with c5:
        # Calling the function sumarize_sellers  from csv_tasks and plotting the output dataframe.
        data_mean = type_sales_mean(formated_data)
        st.dataframe(data_mean)
    with c6:
        # getting the mean of "Valor" column for each type(Tipo) and plot a barchart
        data_mean  = formated_data.groupby('Tipo').agg({'Valor': 'mean'})
        st.bar_chart(data_mean)
        
    # CSV TASK 4  
    st.subheader('Purchases per customer')
    st.write('Here is the  total number of purchases made by each customer, where the table is sorted from highest to lowest, there is also a graph to better visualize the difference in values between the costumers')
    c7,c8 = st.columns(2)
    with c7:
        # Calling the function sales_per_client  from csv_tasks and plotting the output dataframe.
        data_client = sales_per_client(formated_data)
        st.dataframe(data_client)
    with c8:
        # plotting the barchart from data_client variable
        st.bar_chart(data_client, x= 'Cliente', y='Número de Compras')
        
elif selected == 'SQL Tasks':
    # formating the data
    formated_data = formating_columns(data)
    # crating tables and insert the data
    create_tables(conn)
    insert_data(conn, formated_data)
    st.title('SQL Tasks')
    
    #SQL TASK 1
    st.subheader('Entity Relationship Diagram')
    st.write('Here we have an entity-relationship diagram of our database, to better visualize which data and its types will be worked on here, and how they relate to each other')
    st.image('db_diagram.png')
    
    #SQL TASK 2
    st.subheader('Sales made in 2020')
    st.write('Here are the sales made in 2020, where the table have the saleID(id) and the customer name(nome_cliente)')
    # Calling the function get_sales2020  from sql_tasks and plotting the output dataframe.
    sales2020 = get_sales2020(conn)
    st.dataframe(sales2020)
    
    #SQL TASK 3
    st.subheader('list of teams for each seller')
    st.write('Here are the teams of each seler, where the table have the Vendor name and his team, there is also a graph to  visualize which team has most vendor')
    # Calling the function get_team  from sql_tasks and saving the output in teams variable.
    teams = get_team(conn)
    c1,c2 = st.columns(2)
    with c1: 
        # ploting the dataframe from teams dataframe variable
        st.dataframe(teams)
    with c2:
        # Getting the counts of diferent teams from teams dataframe
        team_counts = teams['time'].value_counts()
        # Convert the Series 'team_counts' to a DataFrame and reset the index to get a column for the counts
        team_counts_df = team_counts.reset_index()
        # Rename the columns of the DataFrame to 'Time' and 'Count'
        team_counts_df.columns = ['Time', 'Count']
        team_counts_df.set_index('Time', inplace=True)
        # Create a barchart with the count of vendors for each team
        st.bar_chart(team_counts_df)

    # SQL TASK 4
    st.subheader('Quarterly sales')
    st.write('Here are the quarterly sales figures, where the table shows the quarter and the total sold, and the line graph shows the progression of these sales')
    # Calling the function get_quarter_sales from sql_tasks and saving the output in quarter_sales variable.
    quarter_sales = get_quarter_sales(conn)
    c3,c4 = st.columns(2)
    with c3:
        # plot the quarter_sales dataframe
        st.dataframe(quarter_sales)
    with c4:
        # plot  a line chart using the 'trimestre' column from quarter_sales for x-axis and 'vendas_totais' column for y-axis
        st.line_chart(quarter_sales, x='trimestre', y='vendas_totais')
        
elif selected == 'About':
    st.title('About')
    st.write("This is a webpage created for data visualization (tables and graphs), whose selections for creating tables, both using csv and pandas, and sql and pandas are part of triggo.ai internship selection process.")
    st.write('More information about the code, both the "back-end" and the interface, is available at [github](https://github.com/Luscahm/desafio_sql)')
    st.write('Made by Lucas Henrique Marchiori.')
    st.write('Contact information:')
    st.write('[lucasmarchiori20@gmail.com](mailto:lucasmarchiori20@gmail.com)')
    st.write('[LinkedIn](https://www.linkedin.com/in/lucashm/)')