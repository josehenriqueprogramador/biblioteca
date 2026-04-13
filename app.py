import streamlit as st
import pandas as pd
import json

# Configuração da página
st.set_page_config(page_title="Sistema de Biblioteca", layout="wide")

# --- INICIALIZAÇÃO DO ESTADO (Garante que as listas existam antes de qualquer coisa) ---
if 'autores' not in st.session_state:
    st.session_state.autores = []
if 'obras' not in st.session_state:
    st.session_state.obras = []

st.title("📚 Biblioteca Digital - Gestão RotaFlex")

# --- BARRA LATERAL: GESTÃO DE DADOS ---
st.sidebar.header("⚙️ Gestão de Dados")

# Download JSON (Sempre pega o que está na memória ATUAL)
data_to_save = {"autores": st.session_state.autores, "obras": st.session_state.obras}
json_string = json.dumps(data_to_save, indent=4)
st.sidebar.download_button(
    label="📥 Baixar Backup (JSON)",
    data=json_string,
    file_name="biblioteca_backup.json",
    mime="application/json"
)

# Upload JSON (Soma ao que já existe ou substitui)
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

# --- FUNÇÃO PARA ID AUTOMÁTICO ---
def get_next_id(lista, campo="id"):
    if not lista:
        return 1
    return max(item[campo] for item in lista) + 1

# --- TELAS ---

if opcao == "Início":
    st.info("Sistema aberto. Você pode cadastrar dados manualmente ou subir um JSON.")
    col1, col2 = st.columns(2)
    col1.metric("Autores", len(st.session_state.autores))
    col2.metric("Obras", len(st.session_state.obras))

elif opcao == "Cadastrar Autor":
    st.header("📝 Novo Autor")
    prox_id = get_next_id(st.session_state.autores)
    st.write(f"**ID Automático:** {prox_id}")
    
    with st.form("form_novo_autor", clear_on_submit=True):
        nome = st.text_input("Nome do Autor")
        pais = st.text_input("País")
        if st.form_submit_button("Salvar Autor"):
            if nome and pais:
                st.session_state.autores.append({"id": prox_id, "nome": nome, "pais": pais})
                st.success(f"Autor {nome} salvo com sucesso!")
                # Não damos rerun aqui para o usuário ver a mensagem de sucesso
            else:
                st.error("Preencha todos os campos!")

elif opcao == "Cadastrar Obra":
    st.header("📖 Nova Obra")
    if not st.session_state.autores:
        st.warning("Cadastre um autor primeiro para poder vincular a obra.")
    else:
        prox_id_obra = get_next_id(st.session_state.obras, "id_obra")
        with st.form("form_nova_obra", clear_on_submit=True):
            titulo = st.text_input("Título")
            isbn = st.text_input("ISBN")
            lista_nomes_autores = [a['nome'] for a in st.session_state.autores]
            autor_nome = st.selectbox("Selecione o Autor", lista_nomes_autores)
            
            if st.form_submit_button("Salvar Obra"):
                id_autor = next(a['id'] for a in st.session_state.autores if a['nome'] == autor_nome)
                st.session_state.obras.append({
                    "id_obra": prox_id_obra, "titulo": titulo, "isbn": isbn,
                    "autor_id": id_autor, "status": "LIVRE"
                })
                st.success(f"Obra '{titulo}' cadastrada!")

elif opcao == "Alugar Obra":
    st.header("🔑 Alugar Obra")
    obras_livres = [o['titulo'] for o in st.session_state.obras if o['status'] == "LIVRE"]
    
    if not obras_livres:
        st.write("Nenhuma obra disponível para aluguel.")
    else:
        with st.container():
            obra_aluguel = st.selectbox("Selecione a obra:", obras_livres, key="sel_alugar")
            if st.button("Confirmar Aluguel"):
                for i, o in enumerate(st.session_state.obras):
                    if o['titulo'] == obra_aluguel:
                        st.session_state.obras[i]['status'] = "ALUGADA"
                        st.success(f"Aluguel confirmado!")
                        st.rerun()

elif opcao == "Devolver Obra":
    st.header("🔙 Devolver Obra")
    obras_alugadas = [o['titulo'] for o in st.session_state.obras if o['status'] == "ALUGADA"]
    
    if not obras_alugadas:
        st.write("Não há obras alugadas.")
    else:
        obra_devolucao = st.selectbox("Selecione a obra:", obras_alugadas, key="sel_devolver")
        if st.button("Confirmar Devolução"):
            for i, o in enumerate(st.session_state.obras):
                if o['titulo'] == obra_devolucao:
                    st.session_state.obras[i]['status'] = "LIVRE"
                    st.success(f"Obra devolvida!")
                    st.rerun()

elif opcao == "Relatórios":
    st.header("📊 Relatórios")
    tab1, tab2 = st.tabs(["Geral", "Por País"])
    
    if not st.session_state.obras:
        st.write("Base de dados vazia.")
    else:
        df_obras = pd.DataFrame(st.session_state.obras)
        df_autores = pd.DataFrame(st.session_state.autores)
        
        with tab1:
            st.dataframe(df_obras, use_container_width=True)
            
        with tab2:
            if not df_autores.empty:
                df_merged = pd.merge(df_obras, df_autores, left_on="autor_id", right_on="id")
                lista_paises = df_merged['pais'].unique()
                pais_sel = st.selectbox("Escolha o País", lista_paises)
                st.table(df_merged[df_merged['pais'] == pais_sel][['id_obra', 'titulo', 'status', 'pais']])
