import streamlit as st
import pandas as pd
import json

# Configuração da página
st.set_page_config(page_title="Sistema de Biblioteca", layout="wide")

# --- INICIALIZAÇÃO DO ESTADO (PERSISTÊNCIA TEMPORÁRIA) ---
if 'autores' not in st.session_state:
    st.session_state.autores = []
if 'obras' not in st.session_state:
    st.session_state.obras = []

st.title("📚 Biblioteca Digital - Gestão RotaFlex")

# --- BARRA LATERAL: MENU E GESTÃO DE ARQUIVOS ---
st.sidebar.header("⚙️ Gestão de Dados")

# Botão para Baixar JSON
data_to_save = {"autores": st.session_state.autores, "obras": st.session_state.obras}
json_string = json.dumps(data_to_save, indent=4)
st.sidebar.download_button(
    label="📥 Baixar Backup (JSON)",
    data=json_string,
    file_name="biblioteca_backup.json",
    mime="application/json"
)

# Botão para Carregar JSON
uploaded_file = st.sidebar.file_uploader("📤 Carregar Backup (JSON)", type="json")
if uploaded_file is not None:
    content = json.load(uploaded_file)
    st.session_state.autores = content.get("autores", [])
    st.session_state.obras = content.get("obras", [])
    st.sidebar.success("Dados carregados!")

st.sidebar.divider()
opcao = st.sidebar.radio("Navegação:", 
    ["Início", "Cadastrar Autor", "Cadastrar Obra", "Alugar Obra", "Devolver Obra", "Relatórios"])

# --- FUNÇÕES DE AUXÍLIO (IDs AUTOMÁTICOS) ---
def get_next_id(lista, campo="id"):
    if not lista:
        return 1
    return max(item[campo] for item in lista) + 1

# --- TELAS ---

if opcao == "Início":
    st.info("Bem-vindo ao sistema. Use o menu lateral para gerenciar o acervo.")
    st.metric("Total de Obras", len(st.session_state.obras))
    st.metric("Total de Autores", len(st.session_state.autores))

elif opcao == "Cadastrar Autor":
    st.header("📝 Novo Autor")
    prox_id = get_next_id(st.session_state.autores)
    st.write(f"**ID Automático:** {prox_id}")
    
    with st.form("form_autor"):
        nome = st.text_input("Nome do Autor")
        pais = st.text_input("País de Origem")
        if st.form_submit_button("Salvar"):
            st.session_state.autores.append({"id": prox_id, "nome": nome, "pais": pais})
            st.success(f"Autor {nome} cadastrado com ID {prox_id}!")

elif opcao == "Cadastrar Obra":
    st.header("📖 Nova Obra")
    if not st.session_state.autores:
        st.warning("Cadastre um autor primeiro.")
    else:
        prox_id_obra = get_next_id(st.session_state.obras, "id_obra")
        st.write(f"**ID da Obra:** {prox_id_obra}")
        with st.form("form_obra"):
            titulo = st.text_input("Título")
            isbn = st.text_input("ISBN")
            lista_autores = {a['nome']: a['id'] for a in st.session_state.autores}
            autor_nome = st.selectbox("Autor", list(lista_autores.keys()))
            if st.form_submit_button("Salvar Obra"):
                st.session_state.obras.append({
                    "id_obra": prox_id_obra, "titulo": titulo, "isbn": isbn,
                    "autor_id": lista_autores[autor_nome], "status": "LIVRE"
                })
                st.success(f"Obra '{titulo}' registrada!")

elif opcao == "Alugar Obra":
    st.header("🔑 Alugar Obra")
    obras_livres = [o for o in st.session_state.obras if o['status'] == "LIVRE"]
    if not obras_livres:
        st.write("Não há obras disponíveis para aluguel.")
    else:
        obra_alugar = st.selectbox("Selecione a Obra", [o['titulo'] for o in obras_livres])
        if st.button("Confirmar Aluguel"):
            for o in st.session_state.obras:
                if o['titulo'] == obra_alugar:
                    o['status'] = "ALUGADA"
            st.success(f"Obra '{obra_alugar}' alugada com sucesso!")

elif opcao == "Devolver Obra":
    st.header("🔙 Devolução")
    obras_alugadas = [o for o in st.session_state.obras if o['status'] == "ALUGADA"]
    if not obras_alugadas:
        st.write("Nenhuma obra está alugada no momento.")
    else:
        obra_devolver = st.selectbox("Selecione a Obra para Devolver", [o['titulo'] for o in obras_alugadas])
        if st.button("Confirmar Devolução"):
            for o in st.session_state.obras:
                if o['titulo'] == obra_devolver:
                    o['status'] = "LIVRE"
            st.success(f"Obra '{obra_devolver}' devolvida ao acervo!")

elif opcao == "Relatórios":
    st.header("📊 Central de Relatórios")
    tab_geral, tab_pais = st.tabs(["Relatório Geral", "Relatório por País"])
    
    df_autores = pd.DataFrame(st.session_state.autores)
    df_obras = pd.DataFrame(st.session_state.obras)
    
    with tab_geral:
        st.subheader("Todas as Obras no Sistema")
        if not df_obras.empty:
            st.dataframe(df_obras, use_container_width=True)
        else:
            st.write("Nenhuma obra cadastrada.")

    with tab_pais:
        st.subheader("Obras Filtradas por País do Autor")
        if not df_autores.empty and not df_obras.empty:
            # Join entre Obras e Autores para pegar o país
            df_merge = pd.merge(df_obras, df_autores, left_on="autor_id", right_on="id")
            lista_paises = df_merge['pais'].unique()
            pais_sel = st.selectbox("Selecione o País", lista_paises)
            st.table(df_merge[df_merge['pais'] == pais_sel][['id_obra', 'titulo', 'status', 'pais']])
        else:
            st.write("Dados insuficientes para gerar relatório por país.")
