import streamlit as st
import pandas as pd
import json

# Configuração da página
st.set_page_config(page_title="Sistema de Biblioteca", layout="wide")

# --- INICIALIZAÇÃO DO ESTADO (Persistência na Sessão) ---
if 'autores' not in st.session_state:
    st.session_state.autores = []
if 'obras' not in st.session_state:
    st.session_state.obras = []

st.title("📚 Biblioteca Digital - Gestão RotaFlex")

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Gestão de Dados")

# Download JSON
data_to_save = {"autores": st.session_state.autores, "obras": st.session_state.obras}
json_string = json.dumps(data_to_save, indent=4)
st.sidebar.download_button(label="📥 Baixar Backup (JSON)", data=json_string, file_name="biblioteca.json", mime="application/json")

# Upload JSON
uploaded_file = st.sidebar.file_uploader("📤 Carregar Backup (JSON)", type="json")
if uploaded_file:
    content = json.load(uploaded_file)
    st.session_state.autores = content.get("autores", [])
    st.session_state.obras = content.get("obras", [])
    st.sidebar.success("Dados carregados!")

st.sidebar.divider()
opcao = st.sidebar.radio("Navegação:", ["Início", "Cadastrar Autor", "Cadastrar Obra", "Alugar Obra", "Devolver Obra", "Relatórios"])

# --- FUNÇÕES ---
def get_next_id(lista, campo="id"):
    if not lista: return 1
    return max(item[campo] for item in lista) + 1

# --- TELAS ---

if opcao == "Início":
    st.info("Sistema Pronto. Carregue seu JSON para começar.")
    st.metric("Obras no Acervo", len(st.session_state.obras))

elif opcao == "Cadastrar Autor":
    st.header("📝 Novo Autor")
    prox_id = get_next_id(st.session_state.autores)
    with st.form("f_autor"):
        nome = st.text_input("Nome")
        pais = st.text_input("País")
        if st.form_submit_button("Salvar"):
            st.session_state.autores.append({"id": prox_id, "nome": nome, "pais": pais})
            st.success("Cadastrado!")
            st.rerun()

elif opcao == "Cadastrar Obra":
    st.header("📖 Nova Obra")
    if not st.session_state.autores:
        st.warning("Cadastre um autor primeiro.")
    else:
        prox_id_o = get_next_id(st.session_state.obras, "id_obra")
        with st.form("f_obra"):
            titulo = st.text_input("Título")
            isbn = st.text_input("ISBN")
            lista_a = {a['nome']: a['id'] for a in st.session_state.autores}
            aut_sel = st.selectbox("Autor", list(lista_a.keys()))
            if st.form_submit_button("Cadastrar"):
                st.session_state.obras.append({"id_obra": prox_id_o, "titulo": titulo, "isbn": isbn, "autor_id": lista_a[aut_sel], "status": "LIVRE"})
                st.success("Obra salva!")
                st.rerun()

elif opcao == "Alugar Obra":
    st.header("🔑 Alugar Obra")
    # Pegamos apenas os títulos das obras que estão LIVRES
    livres = [o['titulo'] for o in st.session_state.obras if o['status'] == "LIVRE"]
    
    if not livres:
        st.warning("Não há obras disponíveis.")
    else:
        obra_escolhida = st.selectbox("Selecione para alugar:", livres)
        if st.button("Confirmar Aluguel"):
            # Atualização direta no session_state
            for i, obra in enumerate(st.session_state.obras):
                if obra['titulo'] == obra_escolhida:
                    st.session_state.obras[i]['status'] = "ALUGADA"
                    st.success(f"Aluguel de '{obra_escolhida}' confirmado!")
                    st.rerun() # Isso força a atualização do relatório na hora

elif opcao == "Devolver Obra":
    st.header("🔙 Devolver Obra")
    alugadas = [o['titulo'] for o in st.session_state.obras if o['status'] == "ALUGADA"]
    
    if not alugadas:
        st.info("Nenhuma obra alugada.")
    else:
        obra_devolucao = st.selectbox("Selecione para devolver:", alugadas)
        if st.button("Confirmar Devolução"):
            for i, obra in enumerate(st.session_state.obras):
                if obra['titulo'] == obra_devolucao:
                    st.session_state.obras[i]['status'] = "LIVRE"
                    st.success(f"'{obra_devolucao}' devolvida!")
                    st.rerun()

elif opcao == "Relatórios":
    st.header("📊 Relatórios")
    t1, t2 = st.tabs(["Geral", "Por País"])
    
    if not st.session_state.obras:
        st.write("Sem dados.")
    else:
        df_obras = pd.DataFrame(st.session_state.obras)
        df_autores = pd.DataFrame(st.session_state.autores)
        
        with t1:
            st.dataframe(df_obras, use_container_width=True)
            
        with t2:
            if not df_autores.empty:
                df_m = pd.merge(df_obras, df_autores, left_on="autor_id", right_on="id")
                p_lista = df_m['pais'].unique()
                p_sel = st.selectbox("Filtrar por País:", p_lista)
                st.table(df_m[df_m['pais'] == p_sel][['titulo', 'status', 'pais']])
