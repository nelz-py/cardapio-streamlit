import streamlit as st
import psycopg2
from psycopg2 import OperationalError

class MinhaConexaoBD:

    def __init__(self):
        
        try:
            self.conn = psycopg2.connect(
                host=st.secrets["postgres"]["host"],
                port=st.secrets["postgres"]["port"],
                dbname=st.secrets["postgres"]["database"],
                user=st.secrets["postgres"]["user"],
                password=st.secrets["postgres"]["password"]
            )
        except OperationalError as e:
            st.error(f"Erro ao conectar ao PostgresSQL: {e}")
            self.conn = None
    def get_connection(self):
        return self.conn
    
    def tabela_db(self):
        if self.conn:
            try:
                with self.conn.cursor() as cursor:
                    cursor.execute("""CREATE TABLE IF NOT EXISTS categorias (
                                id SERIAL PRIMARY KEY,
                                nome VARCHAR(100) NOT NULL UNIQUE,
                                descricao TEXT         
                                   )
                                """)
                    
                    self.conn.commit()
            except psycopg2.Error as e:
                st.error(f"Erro ao inicializar a tabela 'categoria' : {e}")
                self.conn.rollback()
@st.cache_resource
def get_MinhaConexaoBD():

    print("--- INICIANDO NOVO REPOSITORIO ---")
    repo = MinhaConexaoBD()
    if repo.get_connection():
        repo.tabela_db()
    return repo
