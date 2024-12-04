import streamlit as st
import pandas as pd
from datetime import datetime

# Configurar o layout da página para wide
st.set_page_config(layout="wide")

# Função para salvar o DataFrame no Excel
def save_to_excel(df, file_path, sheet_name='Contratos'):
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)

# Função para registrar histórico
def log_change(contract_num, action, df_historico):
    new_log = pd.DataFrame({
        'CONTRATO Nº': [contract_num],
        'AÇÃO': [action],
        'DATA': [datetime.now()]
    })
    df_historico = pd.concat([df_historico, new_log], ignore_index=True)
    save_to_excel(df_historico, "planilhas/2024.xlsx", sheet_name='Históricos')
    return df_historico

# Leia os dados do arquivo Excel
df = pd.read_excel("planilhas/2024.xlsx", sheet_name='Contratos')

# Leia o histórico de alterações
try:
    df_historico = pd.read_excel("planilhas/2024.xlsx", sheet_name='Históricos')
except FileNotFoundError:
    df_historico = pd.DataFrame(columns=['CONTRATO Nº', 'AÇÃO', 'DATA'])

# Exibir a tabela de contratos
st.title('Gerenciamento de Contratos')
st.dataframe(df)

# Barra lateral para ações
st.sidebar.header('Ações')

# Campo para inserir número de ticket
ticket_num = st.sidebar.text_input('Número do Ticket')

# Botão para adicionar uma nova linha
if st.sidebar.button('Adicionar Novo Contrato'):
    if df.empty or not df.iloc[-1].isnull().all():  # Verifica se a última linha não está vazia
        new_row = pd.DataFrame([{col: "" for col in df.columns}])  # Cria uma nova linha vazia
        df = pd.concat([df, new_row], ignore_index=True)
        st.experimental_rerun()  # Recarrega a página para atualizar a exibição

# Campos para editar o último contrato adicionado
if not df.empty and df.iloc[-1].isnull().all():
    st.subheader('Preencha os detalhes do novo contrato')
    for col in df.columns:
        df.at[df.index[-1], col] = st.text_input(f'{col}', value=df.at[df.index[-1], col])

# Botão para salvar as alterações
if st.sidebar.button('Salvar Alterações'):
    save_to_excel(df, "planilhas/2024.xlsx")
    st.success('Alterações salvas com sucesso!')

# Campo para excluir uma linha
contrato_excluir = st.sidebar.text_input('Número do Contrato para Excluir')
if st.sidebar.button('Excluir Contrato'):
    if contrato_excluir in df['CONTRATO Nº'].values:
        df = df[df['CONTRATO Nº'] != contrato_excluir]
        df_historico = log_change(contrato_excluir, 'Excluído', df_historico)
        save_to_excel(df, "planilhas/2024.xlsx")
        st.success('Contrato excluído com sucesso!')
    else:
        st.sidebar.error('Contrato não encontrado!')

# Opção para exibir histórico
if st.sidebar.checkbox('Mostrar Histórico de Alterações'):
    st.subheader('Histórico de Alterações')
    st.dataframe(df_historico)
