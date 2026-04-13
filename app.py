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
    st.sidebar.success("Dados carregados com sucesso!")

st.sidebar.divider()
opcao = st.sidebar.radio("Navegação:", 
    ["Início", "Cadastrar Autor", "Cadastrar Obra", "Alugar Obra", "Devolver Obra", "Relatórios"])

# --- FUNÇÕES DE APOIO ---
def get_next_id(lista, campo="id"):
    if not lista:
        return 1
    return max(item[campo] for item in lista) + 1

# --- TELAS ---

if opcao == "Início":
    st.info("Sistema operacional. Utilize o menu lateral para gerenciar o acervo e carregar seus dados.")
    col_m1, col_m2 = st.columns(2)
    col_m1.metric("Autores Cadastrados", len(st.session_state.autores))
    col_m2.metric("Obras no Acervo", len(st.session_state.obras))

elif opcao == "Cadastrar Autor":
    st.header("📝 Novo Autor")
    prox_id = get_next_id(st.session_state.autores)
    st.write(f"**ID Gerado:** {prox_id}")
    
    with st.form("form_autor"):
        nome = st.text_input("Nome completo do Autor")
        pais = st.text_input("País de Origem")
        if st.form_submit_button("Salvar Registro"):
            if nome and pais:
                st.session_state.autores.append({"id": prox_id, "nome": nome, "pais": pais})
                st.success(f"Autor {nome} registrado!")
            else:
                st.error("Preencha todos os campos.")

elif opcao == "Cadastrar Obra":
    st.header("📖 Nova Obra")
    if not st.session_state.autores:
        st.warning("É necessário cadastrar ao menos um autor antes de registrar obras.")
    else:
        prox_id_obra = get_next_id(st.session_state.obras, "id_obra")
        st.write(f"**ID da Obra:** {prox_id_obra}")
        with st.form("form_obra"):
            titulo = st.text_input("Título da Obra")
            isbn = st.text_input("ISBN")
            lista_autores = {a['nome']: a['id'] for a in st.session_state.autores}
            autor_nome = st.selectbox("Vincular Autor", list(lista_autores.keys()))
            
            if st.form_submit_button("Confirmar Cadastro"):
                st.session_state.obras.append({
                    "id_obra": prox_id_obra, 
                    "titulo": titulo, 
                    "isbn": isbn,
                    "autor_id": lista_autores[autor_nome], 
                    "status": "LIVRE"
                })
                st.success(f"Obra '{titulo}' adicionada ao catálogo!")

elif opcao == "Alugar Obra":
    st.header("🔑 Gestão de Aluguel")
    obras_livres = [o for o in st.session_state.obras if o['status'] == "LIVRE"]
    
    if not obras_livres:
        st.info("Não existem obras disponíveis para novos aluguéis.")
    else:
        with st.form("aluguel_confirm"):
            obra_sel = st.selectbox("Escolha a obra para alugar:", [o['titulo'] for o in obras_livres])
            if st.form_submit_button("Confirmar Saída"):
                for o in st.session_state.obras:
                    if o['titulo'] == obra_sel:
                        o['status'] = "ALUGADA"
                st.success(f"Status de '{obra_sel}' atualizado para ALUGADA.")
                st.rerun()

elif opcao == "Devolver Obra":
    st.header("🔙 Gestão de Devolução")
    obras_alugadas = [o for o in st.session_state.obras if o['status'] == "ALUGADA"]
    
    if not obras_alugadas:
        st.info("Nenhuma obra consta como alugada no sistema.")
    else:
        with st.form("devolucao_confirm"):
            obra_sel_dev = st.selectbox("Escolha a obra para devolução:", [o['titulo'] for o in obras_alugadas])
            if st.form_submit_button("Confirmar Entrada"):
                for o in st.session_state.obras:
                    if o['titulo'] == obra_sel_dev:
                        o['status'] = "LIVRE"
                st.success(f"Obra '{obra_sel_dev}' retornou ao status LIVRE.")
                st.rerun()

elif opcao == "Relatórios":
    st.header("📊 Painel de Relatórios")
    tab_geral, tab_pais = st.tabs(["📋 Relatório Geral", "🌍 Filtrar por País"])
    
    if not st.session_state.obras:
        st.write("A base de dados está vazia.")
    else:
        df_obras = pd.DataFrame(st.session_state.obras)
        df_autores = pd.DataFrame(st.session_state.autores)

        with tab_geral:
            st.subheader("Visão Completa do Acervo")
            st.dataframe(df_obras, use_container_width=True)

        with tab_pais:
            st.subheader("Filtro Geográfico")
            if not df_autores.empty:
                # Merge para trazer o nome do país para o dataframe de obras
                df_completo = pd.merge(df_obras, df_autores, left_on="autor_id", right_on="id")
                paises_disponiveis = df_completo['pais'].unique()
                pais_escolhido = st.selectbox("Selecione o País:", paises_disponiveis)
                
                filtro = df_completo[df_completo['pais'] == pais_escolhido]
                st.table(filtro[['id_obra', 'titulo', 'status', 'pais']])
            else:
                st.write("Cadastre autores com países para habilitar este filtro.")
