import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.express as px

# Definir o caminho do arquivo Excel
file_path = 'dados_limpos.xlsx'  # Substitua pelo caminho do seu arquivo

# Função para carregar dados
@st.cache(allow_output_mutation=True)
def load_data(file_path):
    df = pd.read_excel(file_path)
    return df

# Função para exibir filtros e aplicar no DataFrame
def filter_data(df):
    if df is not None:
        st.sidebar.subheader('Filtros')
        columns_to_filter = st.sidebar.multiselect('Selecione colunas para filtrar', df.columns)
        
        filtered_df = df.copy()
        for column in columns_to_filter:
            unique_values = filtered_df[column].unique()
            selected_values = st.sidebar.multiselect(f'Valores para {column}', unique_values, default=unique_values)
            filtered_df = filtered_df[filtered_df[column].isin(selected_values)]
        
        return filtered_df
    return df

# Função para criar gráficos
def create_charts(df):
    if df is not None:
        st.subheader('Gráficos')
        
        # Agrupamento de dados pela coluna 'CONTRATO Nº'
        groupby_column = 'CONTRATO Nº'
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
        aggregation_column = st.selectbox('Selecione a coluna para agregação', numeric_columns)
        
        # Agrupar dados
        grouped_df = df.groupby(groupby_column)[aggregation_column].sum().reset_index()
        
        # Criar gráfico de barras
        fig = px.bar(grouped_df, x=groupby_column, y=aggregation_column, title=f'Soma de {aggregation_column} por {groupby_column}')
        st.plotly_chart(fig)
        
        # Criar gráfico de pizza
        fig = px.pie(grouped_df, names=groupby_column, values=aggregation_column, title=f'Distribuição de {aggregation_column} por {groupby_column}')
        st.plotly_chart(fig)

# Layout da aplicação
st.title('Dashboard de Business Intelligence')

df = load_data(file_path)

if df is not None:
    tab1, tab2 = st.tabs(["Dados e Filtros", "Gráficos e Agrupamentos"])

    with tab1:
        st.header("Dados e Filtros")
        st.write("Edite os dados diretamente na tabela abaixo:")

        # Configurar a tabela AgGrid para edição
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination()
        gb.configure_default_column(editable=True)
        grid_options = gb.build()

        # Exibir a tabela AgGrid
        grid_response = AgGrid(df, gridOptions=grid_options, editable=True)
        df = grid_response['data']  # Atualiza o DataFrame com as edições feitas pelo usuário

        filtered_df = filter_data(df)
        st.subheader("Dados Filtrados")
        st.write(filtered_df)

        # Salvar alterações no DataFrame de volta para o arquivo Excel (opcional)
        if st.button('Salvar Alterações'):
            df.to_excel(file_path, index=False)
            st.success(f'Alterações salvas em {file_path}')

    with tab2:
        st.header("Gráficos e Agrupamentos")
        create_charts(filtered_df)
else:
    st.info('Por favor, carregue uma planilha Excel para começar.')