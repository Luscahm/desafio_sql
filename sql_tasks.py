import psycopg2
import pandas as pd



def create_tables(conn):
    """
    _summary_: Creates the tables in the PostgreSQL database.
    
    Args:
        conn (psycopg2 connection): The connection to the PostgreSQL database.
    """
    # SQL query to create the tables
    query = """
        CREATE TABLE IF NOT EXISTS CLIENTE(
            nome_cliente VARCHAR(255) PRIMARY KEY NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS Vendedor(
            Nome_vendedor VARCHAR(255) PRIMARY KEY NOT NULL,
            Time VARCHAR(255) NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS Venda( ID VARCHAR(255)  PRIMARY KEY,
            nome_cliente VARCHAR(255) NOT NULL,
            Nome_vendedor VARCHAR(255) NOT NULL,
            Data_da_venda DATE NOT NULL,
            Categoria VARCHAR(255) NOT NULL,
            Tipo VARCHAR(255) NOT NULL,
            Valor DECIMAL(10,2) NOT NULL,
            Duracao_do_contrato INT NOT NULL,
            Regional VARCHAR(255) NOT NULL,
            FOREIGN KEY (nome_cliente) REFERENCES CLIENTE(nome_cliente),
            FOREIGN KEY (Nome_vendedor) REFERENCES Vendedor(Nome_vendedor)
        );
        
    """
    try:
        # Creating  a cursor object to interact with the database
        cur = conn.cursor()
        # Executing the query
        cur.execute(query)
        conn.commit()
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)


def insert_data(conn, data):
    """_summary_: Inserts the data in the PostgreSQL database.

    Args:
        conn (psycopg2 connection): The connection to the PostgreSQL database.
        data (Pandas Dataframe): The input DataFrame with formatted columns.
    """
    
    # Getting unique "Cliente" from the data
    clients = data['Cliente'].unique()
    try:
        # Inserting the "Cliente" in the CLIENTE table
        with conn.cursor() as cur:
            for client in clients:

                query = """
                INSERT INTO CLIENTE (nome_cliente)
                VALUES (%s) ON CONFLICT  DO NOTHING;
                """
                cur.execute(query, client)
                conn.commit()
    except Exception as e:
        print("error:", e)

    # Getting unique "Vendedor"  and "Equipe" from the data
    sellers = data[['Vendedor', 'Equipe']].drop_duplicates(subset=['Vendedor']).reset_index(drop=True)

    # Inserting the "Vendedor"  and "Equipe"  in the Vendedor table
    for i in range(len(sellers)):
        try:
            with conn.cursor() as cur:
                query = """
                INSERT INTO Vendedor (Nome_vendedor, Time)
                VALUES (%s, %s) ON CONFLICT DO NOTHING;
                """
                cur.execute(query, (sellers['Vendedor'][i], sellers['Equipe'][i]))
                conn.commit()
        except Exception as e:
            print("error:", e)


    # Inserting all the data in Venda table
    for i in range(len(data)):
        try:
            with conn.cursor() as cur:
                query = """
                INSERT INTO Venda (ID, nome_cliente, Nome_vendedor, Data_da_venda, Categoria, Tipo, Valor, Duracao_do_contrato, Regional)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;
                """
                values = (data['ID'][i], data['Cliente'][i], data['Vendedor'][i], data['Data da Venda'][i], 
                        data['Categoria'][i], data['Tipo'][i], float(data['Valor'][i]), 
                        int(data['Duração do Contrato (Meses)'][i]), data['Regional'][i])
                cur.execute(query, values)
                conn.commit()
        except Exception as e:
            print("error: ", e)
    
    
def get_sales2020(conn):
    """
    _summary_: Returns the sales made in 2020.
    
    Args:
        conn (psycopg2 connection): The connection to the PostgreSQL database.
    
    Returns: Pandas Dataframe: A DataFrame with the sales made in 2020.
    """
    # SQL query to select sales(Venda) made in 2020
    query = """
    SELECT ID , nome_cliente
    FROM Venda
    WHERE EXTRACT(Year FROM Data_da_venda) = 2020;
    """    
    # Executing the SQL query and saving the results into a DataFrame
    sales2020 = pd.read_sql_query(query, conn)
    return sales2020
 

def get_team(conn):
    """
    _summary_: Returns the team of sellers.
    
    Args:
    
    conn (psycopg2 connection): The connection to the PostgreSQL database.
    
    Returns: Pandas Dataframe: A DataFrame with the team of sellers.
    
    """
    # SQL query to select the "Nome_vendedor" and "Time"
    query = """
    SELECT Nome_vendedor, Time 
    FROM Vendedor
    """
    # Executing the SQL query and saving the results into a DataFrame
    teams = pd.read_sql_query(query, conn).reset_index(drop=True)
    return teams

def get_quarter_sales(conn):
    """
    _summary_: Returns the total sales for each quarter.
    
    Args:
        conn (psycopg2 connection): The connection to the PostgreSQL database.
        
    Returns: Pandas Dataframe: A DataFrame with the total sales for each quarter.
    """
    # SQL query to calculate total sales for each quarter
    query = """
    SELECT
        EXTRACT(Year FROM Data_da_venda) AS ano,
        EXTRACT(QUARTER FROM Data_da_venda) AS trimestre, 
        SUM(Valor) AS vendas_totais
    FROM Venda
    GROUP BY ano, trimestre
    Order BY ano, trimestre;
    """
    # Executing the SQL query and saving the results into a DataFrame
    quarter_sales = pd.read_sql_query(query, conn).reset_index(drop=True)
    # Converting "ano" column to int, for remove transforming 2018.0 to 2018, then transforming in string
    quarter_sales['ano'] = quarter_sales['ano'].astype(int).astype(str)
    # Combining "ano" and "trimestre" columns to represent quarters (e.g., 2018Q2)
    quarter_sales['trimestre'] = quarter_sales['ano'] + 'Q' + quarter_sales['trimestre'].astype(int).astype(str)
    quarter_sales.drop('ano', axis=1, inplace=True)
    
    return quarter_sales

