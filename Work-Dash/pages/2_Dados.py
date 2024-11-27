import streamlit as st
import pandas as pd
from datetime import datetime

# Leia os dados do arquivo Excel
df = pd.read_excel("planilhas/2024.xlsx")

# Criar listas únicas para validação
unique_systems = df['SISTEMA'].unique()
unique_indices = df['ÍNDICE'].unique()
unique_companies = df['EMPRESA'].unique()

# Função para salvar o DataFrame no Excel
def save_to_excel(df, file_path):
    df.to_excel(file_path, index=False)

# Exiba o DataFrame no Streamlit
st.dataframe(df)

# Filtros e campos na barra lateral
st.sidebar.header('Filtros e Modificações')

# Adicione uma opção para filtrar pelo número de contrato
contrato_selecionado = st.sidebar.selectbox('Selecione o Número do Contrato', df['CONTRATO Nº'].unique())

# Filtre o DataFrame com base no contrato selecionado
df_filtrado = df[df['CONTRATO Nº'] == contrato_selecionado]
st.write(f"Exibindo dados para o contrato: {contrato_selecionado}")
st.dataframe(df_filtrado)

# Campos para adicionar ou modificar um contrato
st.sidebar.header('Adicionar/Modificar Contrato')
novo_cliente = st.sidebar.checkbox('Novo Cliente?')

# Campos comuns para modificação
contrato_num = st.sidebar.text_input('Número do Contrato', value=contrato_selecionado if not novo_cliente else "")
sistema = st.sidebar.selectbox('Sistema', unique_systems)

# Campos adicionais apenas para novos clientes
if novo_cliente:
    empresa = st.sidebar.selectbox('Empresa', unique_companies)
    inicio = st.sidebar.date_input('Início', value=datetime.today())
    termino = st.sidebar.date_input('Término', value=datetime.today())
    mes = st.sidebar.text_input('Mês')
    vigencia = st.sidebar.text_input('Vigência')
    indice = st.sidebar.selectbox('Índice', unique_indices, index=0)  # Definindo índice padrão
    periodo_faturamento = st.sidebar.text_input('Período de Faturamento')
    valor_pago = st.sidebar.number_input('Valor Pago', min_value=0.0, format='%f')
    valor_pago_12 = st.sidebar.number_input('Valor Pago (por 12 Meses)', min_value=0.0, format='%f')
    indice_publicado = st.sidebar.text_input('Índice Publicado', value='Padrão')  # Valor padrão
    indice_aplicado = st.sidebar.text_input('Índice Aplicado', value='Padrão')  # Valor padrão
    valor_reajustado = st.sidebar.number_input('Valor Reajustado', min_value=0.0, format='%f')
    valor_reajustado_12 = st.sidebar.number_input('Valor Reajustado (por 12 Meses)', min_value=0.0, format='%f')
    pedido_ordem_compras = st.sidebar.text_input('Pedido/Ordem de Compras')
    status_acao = st.sidebar.text_input('Status / Ação')
    data_acao = st.sidebar.date_input('Data da Ação', value=datetime.today())
    diferenca_valor_contrato = st.sidebar.number_input('Diferença de Valor de Contrato', min_value=0.0, format='%f')
else:
    # Preenchimento automático se não for novo cliente
    if contrato_selecionado:
        contrato_anterior = df[df['CONTRATO Nº'] == contrato_selecionado].iloc[0]
        empresa = contrato_anterior['EMPRESA']
        sistema = contrato_anterior['SISTEMA']
        # Preencha outros campos conforme necessário

# Função para validar os campos
def validate_fields():
    errors = []
    if not contrato_num:
        errors.append("Número do Contrato é obrigatório.")
    if novo_cliente and not empresa:
        errors.append("Empresa é obrigatória.")
    if not sistema:
        errors.append("Sistema é obrigatório.")
    if novo_cliente and not indice:
        errors.append("Índice é obrigatório.")
    if novo_cliente and inicio > termino:
        errors.append("A data de início não pode ser maior que a data de término.")
    return errors

# Botão para adicionar ou modificar o contrato
if st.sidebar.button('Adicionar/Modificar'):
    errors = validate_fields()
    if errors:
        for error in errors:
            st.sidebar.error(error)
    else:
        if novo_cliente:
            # Adicionar novo contrato
            new_data = pd.DataFrame({
                'CONTRATO Nº': [contrato_num],
                'EMPRESA': [empresa],
                'SISTEMA': [sistema],
                'INÍCIO': [inicio],
                'TÉRMINO': [termino],
                'MÊS': [mes],
                'VIGÊNCIA': [vigencia],
                'ÍNDICE': [indice],
                'PERÍODO DE FATURAMENTO': [periodo_faturamento],
                'VALOR PAGO': [valor_pago],
                'VALOR PAGO (POR 12 MESES)': [valor_pago_12],
                'ÍNDICE PUBLICADO': [indice_publicado],
                'ÍNDICE APLICADO': [indice_aplicado],
                'VALOR REAJUSTADO': [valor_reajustado],
                'VALOR REAJUSTADO (POR 12 MESES)': [valor_reajustado_12],
                'PEDIDO/ORDEM DE COMPRAS': [pedido_ordem_compras],
                'STATUS / AÇÃO': [status_acao],
                'DATA DA AÇÃO': [data_acao],
                'DIFERENÇA DE VALOR DE CONTRATO': [diferenca_valor_contrato]
            })
            df = pd.concat([df, new_data], ignore_index=True)
            st.success('Contrato adicionado com sucesso!')
        else:
            # Modificar o contrato existente
            df.loc[df['CONTRATO Nº'] == contrato_num, ['SISTEMA']] = [sistema]
            st.success('Contrato modificado com sucesso!')

        # Salve as alterações no arquivo Excel
        save_to_excel(df, "planilhas/dados_estruturados.xlsx")

# Botão para excluir o contrato
st.sidebar.header('Excluir Contrato')
contrato_excluir = st.sidebar.text_input('Número do Contrato para Excluir')
if st.sidebar.button('Excluir'):
    if contrato_excluir in df['CONTRATO Nº'].values:
        df = df[df['CONTRATO Nº'] != contrato_excluir]
        st.success('Contrato excluído com sucesso!')

        # Salve as alterações no arquivo Excel
        save_to_excel(df, "planilhas/dados_estruturados.xlsx")
    else:
        st.sidebar.error('Contrato não encontrado!')
