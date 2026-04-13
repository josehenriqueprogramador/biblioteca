import streamlit as st
import pandas as pd
import os

# Configuração da página
st.set_page_config(page_title="Sistema de Biblioteca", layout="wide")

st.title("📚 Sistema de Biblioteca - RotaFlex")
st.sidebar.header("Menu de Navegação")
opcao = st.sidebar.radio("Ir para:", ["Cadastrar Autor", "Cadastrar Obra", "Relatórios"])

# --- LÓGICA DE ARMAZENAMENTO SIMPLES (Simulando o que você fazia em C++) ---
if 'autores' not in st.session_state:
    st.session_state.autores = []
if 'obras' not in st.session_state:
    st.session_state.obras = []

# --- TELA: CADASTRAR AUTOR ---
if opcao == "Cadastrar Autor":
    st.header("📝 Cadastro de Autores")
    with st.form("form_autor"):
        id_autor = st.number_input("ID do Autor", min_value=1, step=1)
        nome = st.text_input("Nome do Autor")
        nacionalidade = st.text_input("Nacionalidade")
        enviar = st.form_submit_button("Salvar Autor")
        
        if enviar:
            st.session_state.autores.append({"id": id_autor, "nome": nome, "nacionalidade": nacionalidade})
            st.success(f"Autor {nome} cadastrado!")

# --- TELA: CADASTRAR OBRA ---
elif opcao == "Cadastrar Obra":
    st.header("📖 Cadastro de Obras")
    if not st.session_state.autores:
        st.warning("Cadastre um autor primeiro!")
    else:
        with st.form("form_obra"):
            isbn = st.text_input("ISBN")
            titulo = st.text_input("Título da Obra")
            # Seleção de autor baseada nos cadastrados
            lista_autores = {a['nome']: a['id'] for a in st.session_state.autores}
            autor_selecionado = st.selectbox("Autor", list(lista_autores.keys()))
            status = st.selectbox("Status", ["LIVRE", "EMPRESTADO", "RESERVADO"])
            
            enviar_obra = st.form_submit_button("Salvar Obra")
            if enviar_obra:
                st.session_state.obras.append({
                    "isbn": isbn, 
                    "titulo": titulo, 
                    "autor_id": lista_autores[autor_selecionado], 
                    "status": status
                })
                st.success(f"Obra '{titulo}' cadastrada com sucesso!")

# --- TELA: RELATÓRIOS ---
elif opcao == "Relatórios":
    st.header("📊 Relatório Geral")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Autores")
        if st.session_state.autores:
            st.table(pd.DataFrame(st.session_state.autores))
        else:
            st.write("Nenhum autor cadastrado.")
            
    with col2:
        st.subheader("Obras")
        if st.session_state.obras:
            st.dataframe(pd.DataFrame(st.session_state.obras))
        else:
            st.write("Nenhuma obra cadastrada.")
