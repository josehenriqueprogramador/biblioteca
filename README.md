# 📚 Sistema de Gestão de Biblioteca - RotaFlex

Este é um projeto desenvolvido como parte dos meus estudos em **Ciência de Dados** na Unigranrio/Afya. O objetivo é gerenciar o acervo de uma biblioteca de forma eficiente, utilizando **Python** e **Streamlit** para criar uma interface dinâmica e funcional, com persistência de dados via **JSON**.

## 🚀 Funcionalidades

- **Cadastro de Autores:** Registro com ID autoincremento e país de origem.
- **Cadastro de Obras:** Registro de livros vinculados aos autores cadastrados.
- **Gestão de Aluguel:** Fluxo completo para alugar e devolver obras, com atualização de status em tempo real.
- **Relatórios Inteligentes:** - Visão geral do acervo.
  - Filtro geográfico (obras por país do autor).
  - Exportação de dados para CSV (com nomes de autores).
- **Persistência de Dados:** Importação e exportação de backups via arquivos JSON para garantir a portabilidade dos dados.

## 🛠️ Tecnologias Utilizadas

- **Python 3.x**: Linguagem principal.
- **Streamlit**: Framework para a interface web.
- **Pandas**: Manipulação e tratamento de dados (merging de tabelas).
- **JSON**: Estrutura de persistência de dados.
- **Render**: Plataforma de deploy.

## 📁 Estrutura do Projeto

```text
├── app.py              # Código principal da aplicação
├── requirements.txt    # Dependências do projeto (Streamlit, Pandas)
└── README.md           # Documentação do projeto
