import pandas as pd
def formating_columns(data):
    """
    _summary_: Formats specific columns in the given Pandas DataFrame.
    This function performs the following operations on the DataFrame:
    1. Converts the 'Valor' column from a string with currency formatting to a float.
    2. Converts the 'Duração do Contrato (Meses)' column to an integer.
    3. Converts the 'Data da Venda' column from a string in the format 'dd/mm/yyyy' to a date object.
    
    Args:
        data (Pandas Dataframe): The input DataFrame without format

    Returns:
        Pandas Dataframe: The formatted DataFrame with 'Valor' as float, 'Duração do Contrato (Meses)' as integer, 
                          and 'Data da Venda' as date.
    """
    # changing the Valor column: removing the R$ symbol and the dots, changing a comma to a period and converting from string to float
    data['Valor'] = data['Valor'].replace( {'R\$': '', 
                                            '\.': '',
                                            ',':'.',
                                           '\s+':''}, regex=True).astype(float)
    # converting the column "Duração do Contrato (Meses)" to int
    data['Duração do Contrato (Meses)'] = data['Duração do Contrato (Meses)'].astype(int)
    # Converting the column Data da Venda to date
    data['Data da Venda'] = pd.to_datetime(data['Data da Venda'], format='%d/%m/%Y')
    data['Data da Venda'] = data['Data da Venda'].dt.date
    
    return data

def sumarize_sellers(data):
    """
    _summary_: Returns the total sales for each seller in the given DataFrame.
    
    Args:
        data (Pandas Dataframe): The input DataFrame with formatted columns.

    Returns: Pandas Dataframe: A DataFrame with the total sales for each seller.
    
    """
    # Grouping the data by "Vendedor" and sum the "Valor" column of each group
    data_seller = data.groupby('Vendedor').agg({'Valor': 'sum'}).sort_values(by='Valor', ascending=False)
    # Take back de "Valor" column to format R$X.XXX,XX
    data_seller['Valor'] = data_seller['Valor'].apply(lambda x: "R$ {:,.2f}".format(x))
    data_seller['Valor'] = data_seller['Valor'].replace({'.': '', 
                                                         ',': '.'})
    
    return data_seller

def best_and_worst_client(data):
    """
    _summary_: Returns the best and worst clients in terms of total sales, and the total sales for each.
    
    Args:
        data (Pandas Dataframe): The input DataFrame with formatted columns.

    Returns: Pandas Dataframe: A DataFrame with the best and worst clients in terms of total sales.
    
    """
    # Finding the maximum and minimum "Valor"
    max_value = data['Valor'].max()
    min_value = data['Valor'].min()
    
    # Filtering the data only to maximum or minimum "Valor", to adquire a df with the best and worst sale
    data_client = data[(data['Valor'] == max_value) | (data['Valor'] == min_value)].sort_values(by='Valor', ascending=False)
    # Take back de "Valor" column to format R$X.XXX,XX
    data_client['Valor'] = data_client['Valor'].apply(lambda x: "R$ {:,.2f}".format(x))
    data_client['Valor'] = data_client['Valor'].replace({'.': '', 
                                                         ',': '.'})
    data_client = data_client.reset_index(drop=True)
    return data_client

def type_sales_mean(data):
    """_summary_: Returns the mean value of sales for each type of sale.

    Args:
        data (Pandas Dataframe): The input DataFrame with formatted columns.

    Returns:
        Pandas Dataframe: A DataFrame with the mean value of sales for each type of sale.
    """
    # Grouping the data by "Tipo" and calculate mean  of  the "Valor" column of each group
    data_mean  = data.groupby('Tipo').agg({'Valor': 'mean'}).sort_values(by='Valor', ascending=False)
    
    # Take back de "Valor" column to format R$X.XXX,XX
    data_mean['Valor'] = data_mean['Valor'].apply(lambda x: "R$ {:,.2f}".format(x))
    data_mean['Valor'] = data_mean['Valor'].replace({'.': '',
                                                        ',': '.'})
    
    return data_mean

def sales_per_client(data):
    """_summary_: Returns the total sales for each client.

    Args:
        data (Pandas Dataframe): The input DataFrame with formatted columns.

    Returns:
        Pandas Dataframe: A DataFrame with the total sales for each client.
    """
    # Grouping the data by "Cliente", count the number of occurrences for each group and creating a new column 'Número de Compras' for these counts
    data_client = (data.groupby('Cliente').size().reset_index(name='Número de Compras').
                   sort_values(by='Número de Compras', ascending=False).
                   reset_index(drop=True)
                    )
    data_client['Número de Compras'] = data_client['Número de Compras'].astype(int)

    return data_client