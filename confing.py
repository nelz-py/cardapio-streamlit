import streamlit as st
import psycopg2
from psycopg2 import OperationalError

class repositorio:
    def __init__(self):
        self.conn = None
        try:
            
            self.conn = psycopg2.connect(
                host=st.secrets["postgres"]["host"],
                port=st.secrets["postgres"]["port"],
                dbname=st.secrets["postgres"]["dbname"],
                user=st.secrets["postgres"]["user"],
                password=st.secrets["postgres"]["password"],
                sslmode="require"
            )
        except OperationalError as e:
            st.error(f"Erro ao conectar ao PostgreSQL: {e}")

    def get_connection(self):
        return self.conn


@st.cache_resource
def get_repositorio():
    return repositorio()