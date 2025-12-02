import streamlit as st
import psycopg2
import psycopg2.extras
from confing import get_MinhaConexaoBD


class CRUDapp:
    def __init__(self):
        self.repo = get_MinhaConexaoBD()
        self.conn = self.repo.get_connection()
        if self.conn is None:
            st.stop()
        

    def get_all_categories(self):
        categorias = []
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM categorias ORDER BY nome")
                records = cursor.fetchall()
                categorias = [dict(record) for record in records]
        except psycopg2.Error as e:
            st.error(f"Erro ao buscar categorias: {e}")
        return categorias

    def run(self):
        st.sidebar.title("Informações Sobre")
        categories = self.get_all_categories()
        category_names = [cat['nome'] for cat in categories]
        nav_options = ["➕ Adicionar Item"] + category_names
        selected_page_name = st.sidebar.selectbox("Editar Seção", nav_options)

        if selected_page_name == "➕ Adicionar Item":
            self.create_page()
        else:
            selected_cat_data = next(
                (cat for cat in categories if cat['nome'] == selected_page_name), 
                None
            )
            if selected_cat_data:
                self.edit_page(selected_cat_data)

    def create_page(self):
        st.title("Adicionar Novo Item")
        with st.form("create_form", clear_on_submit=True):
            nome = st.text_input("Nome do Item (Ex: 'Sanduíches')")
            descricao = st.text_area("Descrição", height=300)
            submitted = st.form_submit_button("Criar Item")

            if submitted:
                if not nome:
                    st.warning("O campo 'Nome' é obrigatório.")
                else:
                    try:
                        with self.conn.cursor() as cursor:
                            sql = "INSERT INTO categorias (nome, descricao) VALUES (%s, %s)"
                            cursor.execute(sql, (nome, descricao))
                            self.conn.commit()
                        st.success(f"Item '{nome}' criado com sucesso!")
                        st.rerun()
                    except psycopg2.Error as e:
                        self.conn.rollback()
                        st.error(f"Erro ao criar: {e}")

    def edit_page(self, category_data):
        st.title(category_data['nome'])
        with st.form("edit_form"):
            nome = st.text_input("Nome", value=category_data['nome'])
            descricao = st.text_area(
                "Descrição", 
                value=category_data['descricao'], 
                height=300
            )
            submitted = st.form_submit_button("Salvar")

            if submitted:
                try:
                    with self.conn.cursor() as cursor:
                        sql = "UPDATE categorias SET nome = %s, descricao = %s WHERE id = %s"
                        cursor.execute(sql, (nome, descricao, category_data['id']))
                        self.conn.commit()
                    st.success("Salvo com sucesso!")
                    st.rerun()
                except psycopg2.Error as e:
                    self.conn.rollback()
                    st.error(f"Erro ao salvar: {e}")

        with st.expander("⚠️ Excluir Item"):
            st.write(f"Isso irá apagar '{category_data['nome']}' permanentemente.")
            if st.button("Excluir Permanentemente"):
                try:
                    with self.conn.cursor() as cursor:
                        sql = "DELETE FROM categorias WHERE id = %s"
                        cursor.execute(sql, (category_data['id'],))
                        self.conn.commit()
                    st.success("Item excluído.")
                    st.rerun()
                except psycopg2.Error as e:
                    self.conn.rollback()
                    st.error(f"Erro ao excluir: {e}")



def logout():
    """Função para 'deslogar' o usuário."""
    st.session_state.logged_in = False
    

def main():
    """Função principal que controla o login e a exibição do app."""
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    
    if not st.session_state.logged_in:
        st.title("Login do Administrador") 
        
        with st.form("login_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar")

            if submitted:
                try:
                    correct_username = st.secrets["admin"]["username"]
                    correct_password = st.secrets["admin"]["password"]
                except KeyError:
                    st.error("Erro: Configuração de [admin] não encontrada no secrets.toml.")
                    return

                if username == correct_username and password == correct_password:
                    st.session_state.logged_in = True
                   
                    st.rerun() 
                else:
                    st.error("Usuário ou senha incorretos.")

    
    else:
        st.sidebar.button("Sair", on_click=logout) 
        
       
        app = CRUDapp()
        app.run()


if __name__ == "__main__":
    main() 