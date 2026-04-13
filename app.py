import streamlit as st
import pandas as pd
import json

# Configuração da página
st.set_page_config(page_title="Sistema de Biblioteca", layout="wide")

# --- INICIALIZAÇÃO DO ESTADO ---
if 'autores' not in st.session_state:
    st.session_state.autores = []
if 'obras' not in st.session_state:
    st.session_state.obras = []

st.title("📚 Biblioteca Digital - Gestão RotaFlex")

# --- BARRA LATERAL: GESTÃO DE ARQUIVOS ---
st.sidebar.header("⚙️ Gestão de Dados")

# Preparação dos dados para Backup (JSON)
data_to_save = {"autores": st.session_state.autores, "obras": st.session_state.obras}
json_string = json.dumps(data_to_save, indent=4)
st.sidebar.download_button(
    label="📥 Baixar Backup (JSON)",
    data=json_string,
    file_name="biblioteca_backup.json",
    mime="application/json"
)

# Upload JSON
uploaded_file = st.sidebar.file_uploader("📤 Carregar Backup (JSON)", type="json")
if uploaded_file is not None:
    if st.sidebar.button("Confirmar Importação"):
        content = json.load(uploaded_file)
        st.session_state.autores = content.get("autores", [])
        st.session_state.obras = content.get("obras", [])
        st.sidebar.success("Dados carregados!")
        st.rerun()

st.sidebar.divider()
opcao = st.sidebar.radio("Navegação:", 
    ["Início", "Cadastrar Autor", "Cadastrar Obra", "Alugar Obra", "Devolver Obra", "Relatórios"])

# --- FUNÇÕES DE APOIO ---
def get_next_id(lista, campo="id"):
    if not lista: return 1
    return max(item[campo] for item in lista) + 1

def get_df_completo():
    """Une as obras com os nomes dos autores para exibição e exportação."""
    if not st.session_state.obras:
        return pd.DataFrame()
    df_obras = pd.DataFrame(st.session_state.obras)
    df_autores = pd.DataFrame(st.session_state.autores)
    
    if df_autores.empty:
        df_obras['nome_autor'] = "Autor não encontrado"
        return df_obras
        
    # Merge para trazer o nome do autor baseado no ID
    df_merge = pd.merge(df_obras, df_autores, left_on="autor_id", right_on="id", how="left")
    # Limpando colunas e renomeando para o usuário
    df_final = df_merge[['id_obra', 'titulo', 'isbn', 'nome', 'pais', 'status']].rename(columns={'nome': 'autor'})
    return df_final

# --- TELAS ---

if opcao == "Início":
    st.info("Sistema operacional. Utilize o menu lateral para gerenciar dados.")
    col1, col2 = st.columns(2)
    col1.metric("Autores", len(st.session_state.autores))
    col2.metric("Obras", len(st.session_state.obras))

elif opcao == "Cadastrar Autor":
    st.header("📝 Novo Autor")
    prox_id = get_next_id(st.session_state.autores)
    with st.form("form_autor", clear_on_submit=True):
        nome = st.text_input("Nome do Autor")
        pais = st.text_input("País")
        if st.form_submit_button("Salvar Autor"):
            if nome and pais:
                st.session_state.autores.append({"id": prox_id, "nome": nome, "pais": pais})
                st.success(f"Autor {nome} salvo!")
            else: st.error("Preencha tudo!")

elif opcao == "Cadastrar Obra":
    st.header("📖 Nova Obra")
    if not st.session_state.autores:
        st.warning("Cadastre um autor primeiro.")
    else:
        prox_id_o = get_next_id(st.session_state.obras, "id_obra")
        with st.form("form_obra", clear_on_submit=True):
            titulo = st.text_input("Título")
            isbn = st.text_input("ISBN")
            lista_autores = {a['nome']: a['id'] for a in st.session_state.autores}
            aut_nome = st.selectbox("Autor", list(lista_autores.keys()))
            if st.form_submit_button("Salvar Obra"):
                st.session_state.obras.append({
                    "id_obra": prox_id_o, "titulo": titulo, "isbn": isbn,
                    "autor_id": lista_autores[aut_nome], "status": "LIVRE"
                })
                st.success("Obra cadastrada!")

elif opcao == "Alugar Obra":
    st.header("🔑 Alugar Obra")
    livres = [o['titulo'] for o in st.session_state.obras if o['status'] == "LIVRE"]
    if not livres: st.write("Nenhuma obra disponível.")
    else:
        obra_sel = st.selectbox("Obra:", livres)
        if st.button("Confirmar Aluguel"):
            for i, o in enumerate(st.session_state.obras):
                if o['titulo'] == obra_sel:
                    st.session_state.obras[i]['status'] = "ALUGADA"
                    st.rerun()

elif opcao == "Devolver Obra":
    st.header("🔙 Devolver Obra")
    alugadas = [o['titulo'] for o in st.session_state.obras if o['status'] == "ALUGADA"]
    if not alugadas: st.write("Nenhuma obra alugada.")
    else:
        obra_dev = st.selectbox("Obra:", alugadas)
        if st.button("Confirmar Devolução"):
            for i, o in enumerate(st.session_state.obras):
                if o['titulo'] == obra_dev:
                    st.session_state.obras[i]['status'] = "LIVRE"
                    st.rerun()

elif opcao == "Relatórios":
    st.header("📊 Relatórios")
    df_final = get_df_completo()
    
    if df_final.empty:
        st.write("Sem dados para exibir.")
    else:
        tab1, tab2 = st.tabs(["Geral", "Por País"])
        
        with tab1:
            st.dataframe(df_final, use_container_width=True)
            # Botão para baixar CSV com NOME do autor
            csv = df_final.to_csv(index=False).encode('utf-8')
            st.download_button("📄 Baixar Relatório (CSV)", data=csv, file_name="relatorio_biblioteca.csv", mime="text/csv")
            
        with tab2:
            lista_paises = df_final['pais'].unique()
            p_sel = st.selectbox("Filtrar País:", lista_paises)
            st.table(df_final[df_final['pais'] == p_sel])
