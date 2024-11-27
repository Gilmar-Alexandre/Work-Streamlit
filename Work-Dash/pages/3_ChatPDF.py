import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(page_title="Gestão de Contratos", layout="wide")

# Função para carregar dados
@st.cache_data
def load_data():
    # Substitua pelo caminho do seu arquivo Excel
    df = pd.read_excel("planilhas/2024.xlsx")
    return df

df = load_data()

# Processamento de dados
def process_data(df):
    # Calcular valor médio por sistema
    valor_medio_sistema = df.groupby('SISTEMA')['VALOR PAGO\n(POR 12 MESES)'].mean().reset_index()
    valor_medio_sistema['PERCENTUAL'] = (valor_medio_sistema['VALOR PAGO\n(POR 12 MESES)'] / valor_medio_sistema['VALOR PAGO\n(POR 12 MESES)'].sum()) * 100

    # Proporção dos índices de reajuste
    proporcao_indices = df['ÍNDICE'].value_counts(normalize=True).reset_index()
    proporcao_indices.columns = ['ÍNDICE', 'PROPORÇÃO']

    # Preparar dados para regressão
    df['DIFERENÇA'] = df['VALOR REAJUSTADO\n(POR 12 MESES)'] - df['VALOR PAGO\n(POR 12 MESES)']
    X = df[['VALOR PAGO\n(POR 12 MESES)']]
    y = df['DIFERENÇA']
    reg = LinearRegression().fit(X, y)
    df['PREDICTED_DIFERENÇA'] = reg.predict(X)

    # Quantidade de contratos por mês
    contratos_por_mes = df.groupby(['MÊS', 'STATUS / AÇÃO']).size().unstack(fill_value=0)

    return valor_medio_sistema, proporcao_indices, df, contratos_por_mes

valor_medio_sistema, proporcao_indices, df, contratos_por_mes = process_data(df)

# Parte Superior (4 Gráficos em Colunas)
st.header("Análise de Contratos")

col1, col2, col3, col4 = st.columns(4)

with col1:
    fig1 = px.bar(valor_medio_sistema, y='SISTEMA', x='PERCENTUAL', orientation='h', title="Valor Médio por Sistema (%)")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.pie(proporcao_indices, values='PROPORÇÃO', names='ÍNDICE', title="Proporção dos Índices de Reajuste")
    st.plotly_chart(fig2, use_container_width=True)

with col3:
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=df['VALOR PAGO\n(POR 12 MESES)'], y=df['DIFERENÇA'], mode='markers', name='Diferença Observada'))
    fig3.add_trace(go.Scatter(x=df['VALOR PAGO\n(POR 12 MESES)'], y=df['PREDICTED_DIFERENÇA'], mode='lines', name='Diferença Estimada'))
    fig3.update_layout(title="Comparativo entre Valor Pago e Reajuste", xaxis_title="Valor Pago", yaxis_title="Diferença")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.write("Placeholder para futuros gráficos")

# Parte Inferior (2 Colunas)
st.header("Análise Temporal")

col5, col6 = st.columns(2)

with col5:
    fig5 = px.bar(contratos_por_mes, barmode='stack', title="Quantidade de Contratos por Mês")
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    # Supondo que você tenha dados históricos para 2022 e 2023
    # Aqui você pode adicionar a lógica para previsão usando ARIMA ou outro modelo
    st.write("Placeholder para análise histórica e previsão")

# Implementação de previsão (exemplo simplificado)
# Aqui você pode adicionar a lógica para previsão usando ARIMA ou outro modelo
# Exemplo: st.write("Previsão para 2024: ...")

