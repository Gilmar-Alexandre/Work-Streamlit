import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(page_title="Gestão de Contratos", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel("planilhas/dados_estruturados.xlsx")
    return df

df = load_data()

def process_data(df):
    grouped_df = df.groupby('CONTRATO Nº').agg({
        'EMPRESA': 'first',
        'SISTEMA': 'first',
        'MÊS': 'first',
        'ÍNDICE': 'first',
        'VALOR PAGO\n(POR 12 MESES)': 'sum',
        'VALOR REAJUSTADO\n(POR 12 MESES)': 'sum',
        'PEDIDO/ORDEM DE COMPRAS': 'first',
        'STATUS / AÇÃO': 'first',
        'DATA DA AÇÃO': 'first',
        'DIFERENÇA DE VALOR DE CONTRATO': 'sum'
    }).reset_index()

    value_columns = [
        'VALOR PAGO\n(POR 12 MESES)',
        'VALOR REAJUSTADO\n(POR 12 MESES)',
        'DIFERENÇA DE VALOR DE CONTRATO'
    ]

    for col in value_columns:
        grouped_df[col] = grouped_df[col].astype(float)

    return grouped_df

grouped_df = process_data(df)

#Dashboard
st.header("Dashboard Contratos")

# Função para formatar valores no formato brasileiro
def format_currency(value):
    return f"R${value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Calculando os valores das métricas
valor_previsto = grouped_df['VALOR REAJUSTADO\n(POR 12 MESES)'].sum()
valor_renovado = grouped_df[grouped_df['STATUS / AÇÃO'] == 'RENOVADO']['VALOR REAJUSTADO\n(POR 12 MESES)'].sum()
valor_em_processo = grouped_df[grouped_df['STATUS / AÇÃO'] == 'EM PROCESSO']['VALOR REAJUSTADO\n(POR 12 MESES)'].sum()
valor_cancelado = grouped_df[grouped_df['STATUS / AÇÃO'] == 'CANCELADO']['VALOR REAJUSTADO\n(POR 12 MESES)'].sum()

# Calcular a diferença entre valor pago e valor reajustado para os cancelados
df_cancelado = grouped_df[grouped_df['STATUS / AÇÃO'] == 'CANCELADO']
diferenca_cancelado = (df_cancelado['VALOR REAJUSTADO\n(POR 12 MESES)'] - df_cancelado['VALOR PAGO\n(POR 12 MESES)']).sum()

# Calcular a diferença entre valor pago e valor reajustado para os renovados
df_renovado = grouped_df[grouped_df['STATUS / AÇÃO'] == 'RENOVADO']
diferenca_renovado = (df_renovado['VALOR REAJUSTADO\n(POR 12 MESES)'] - df_renovado['VALOR PAGO\n(POR 12 MESES)']).sum()

# Calcular a diferença entre valor pago e valor reajustado para os em processo
df_em_processo = grouped_df[grouped_df['STATUS / AÇÃO'] == 'EM PROCESSO']
diferenca_em_processo = (df_em_processo['VALOR REAJUSTADO\n(POR 12 MESES)'] - df_em_processo['VALOR PAGO\n(POR 12 MESES)']).sum()

# Layout das métricas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Valor Previsto", value=format_currency(valor_previsto))

with col2:
    st.metric(label="Valor Renovado", value=format_currency(valor_renovado), delta=format_currency(diferenca_renovado), delta_color="normal")

with col3:
    st.metric(label="Valor em Processo", value=format_currency(valor_em_processo), delta=format_currency(diferenca_em_processo), delta_color="normal")

with col4:
    st.metric(
        label="Valor Cancelado",
        value=format_currency(valor_cancelado),
        delta=format_currency(diferenca_cancelado),
        delta_color="inverse"
    )

# Barra Lateral
with st.sidebar:
    st.header("Filtros")
    
    status = grouped_df['STATUS / AÇÃO'].unique()
    selected_status = st.multiselect("Selecione o Status", options=status, default=status)
    
    meses = sorted(grouped_df['MÊS'].unique())
    selected_months = st.multiselect("Selecione o mês", options=meses, default=meses)

filtered_df = grouped_df[
    (grouped_df['STATUS / AÇÃO'].isin(selected_status)) &
    (grouped_df['MÊS'].isin(selected_months))
]

def plot_value_acrescentado(df):
    # Calculando a diferença (acréscimo no reajuste)
    df['ACRESCIMO_REAJUSTE'] = df['VALOR REAJUSTADO\n(POR 12 MESES)'] - df['VALOR PAGO\n(POR 12 MESES)']
    
    # Agrupando por MÊS para calcular a soma do acréscimo por mês
    monthly_acrescimento = df.groupby('MÊS').agg({'ACRESCIMO_REAJUSTE': 'sum'}).reset_index()

    # Criando o gráfico de linha suave
    fig = go.Figure()

    # Adicionando linha suave para o acréscimo
    fig.add_trace(go.Scatter(
        x=monthly_acrescimento['MÊS'],
        y=monthly_acrescimento['ACRESCIMO_REAJUSTE'],
        mode='lines+markers+text',
        line=dict(color='darkblue', width=2, shape='spline'),
        text=monthly_acrescimento['ACRESCIMO_REAJUSTE'],
        texttemplate='%{text:.2s}',  # Exibindo os valores em formato compacto (ex: R$ 1,2K)
        textposition='top center',
        marker=dict(symbol='circle', size=8, color='royalblue')
    ))

    # Total de acrescimento
    total_acrescimo = monthly_acrescimento['ACRESCIMO_REAJUSTE'].sum()

    # Adicionando anotação para mostrar o total de acréscimo
    fig.add_annotation(
        text=f"Total Acréscimo: {format_currency(total_acrescimo)}",
        xref="paper", yref="paper",
        x=0.5, y=1.1, showarrow=False,
        font=dict(size=18, color="white")
    )

    # Ajustando o layout
    fig.update_layout(
        title="Acréscimo no Reajuste por Mês",
        xaxis_title='Mês',
        yaxis_title='Valor Acrescentado (R$)',
        xaxis_tickformat='R$,.2f',
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showline=False, showgrid=False, zeroline=False),
        yaxis=dict(showline=False, showgrid=False, zeroline=False)
    )

    return fig

# Função para análise do índice de reajuste
def plot_index_analysis(df):
    index_summary = df.groupby('ÍNDICE').agg({
        'VALOR PAGO\n(POR 12 MESES)': 'mean',
        'VALOR REAJUSTADO\n(POR 12 MESES)': 'mean'
    }).reset_index()

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=index_summary['ÍNDICE'],
        y=index_summary['VALOR PAGO\n(POR 12 MESES)'],
        name='Valor Pago',
        marker_color='lightcyan'
    ))

    fig.add_trace(go.Scatter(
        x=index_summary['ÍNDICE'],
        y=index_summary['VALOR REAJUSTADO\n(POR 12 MESES)'],
        name='Valor Reajustado',
        mode='lines+markers',
        line=dict(color='darkblue', width=2),
    ))

    fig.update_layout(
        xaxis=dict(showline=False, showgrid=False, zeroline=False),
        yaxis=dict(showline=False, showgrid=False, zeroline=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    return fig


def plot_contracts_per_month(df):
    contracts_per_month = df.groupby('MÊS').size().reset_index(name='TOTAL DE CONTRATOS')

    months_order = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO',
                    'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
    contracts_per_month['MÊS'] = pd.Categorical(contracts_per_month['MÊS'], categories=months_order, ordered=True)
    contracts_per_month = contracts_per_month.sort_values('MÊS')

    fig = px.bar(contracts_per_month, x='MÊS', y='TOTAL DE CONTRATOS',
                 labels={'TOTAL DE CONTRATOS': 'Total de Contratos', 'MÊS': 'Mês'},
                 color='TOTAL DE CONTRATOS',
                 color_discrete_sequence=['royalblue'])

    fig.update_traces(texttemplate='%{y}', textposition='outside')

    fig.update_layout(
        title="Total de Contratos por Mês",
        xaxis=dict(showline=False, showgrid=False, zeroline=False),
        yaxis=dict(showline=False, showgrid=False, zeroline=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )

    return fig

def plot_pie_chart(df):
    status_counts = df['STATUS / AÇÃO'].value_counts().reset_index()
    status_counts.columns = ['STATUS / AÇÃO', 'COUNT']

    fig = go.Figure(go.Pie(
        labels=status_counts['STATUS / AÇÃO'],
        values=status_counts['COUNT'],
        hole=0.5,
        marker=dict(colors=['royalblue', 'darkblue', 'lightcyan']),
        textinfo='none'
    ))

    fig.update_layout(
        title="Distribuição por Status",
        annotations=[dict(text=f'Total: {status_counts["COUNT"].sum()}', x=0.5, y=0.5, font_size=18, showarrow=False)]
    )

    return fig

# Função para plotar gráfico de dispersão com linha de regressão
def plot_regression_chart(df):
    df['DIFERENÇA'] = df['VALOR REAJUSTADO\n(POR 12 MESES)'] - df['VALOR PAGO\n(POR 12 MESES)']

    X = df[['VALOR PAGO\n(POR 12 MESES)']]
    y = df['DIFERENÇA']

    reg = LinearRegression()
    reg.fit(X, y)

    df['PREDICTED_DIFERENÇA'] = reg.predict(X)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['VALOR PAGO\n(POR 12 MESES)'],
        y=df['DIFERENÇA'],
        mode='markers',
        name='Diferença Observada',
        marker=dict(color='royalblue', size=10, opacity=0.6),
        text=[f"Contrato: {row['CONTRATO Nº']}, Empresa: {row['EMPRESA']}" for idx, row in df.iterrows()]
    ))

    fig.add_trace(go.Scatter(
        x=df['VALOR PAGO\n(POR 12 MESES)'],
        y=df['PREDICTED_DIFERENÇA'],
        mode='lines',
        name='Diferença Estimada',
        line=dict(color='darkblue', width=2)
    ))

    fig.update_layout(
        title="Regressão Linear: Diferença de Valor em Relação ao Valor Pago",
        xaxis_title="Valor Pago (por 12 meses)",
        yaxis_title="Diferença de Valor",
        xaxis=dict(showline=True, showgrid=False, zeroline=False),
        yaxis=dict(showline=True, showgrid=False, zeroline=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig

# Gráficos no layout principal
col1, col2, col3= st.columns(3)

with col1:
    st.plotly_chart(plot_value_acrescentado(filtered_df), use_container_width=True)
with col2:
    st.plotly_chart(plot_pie_chart(filtered_df), use_container_width=True)
with col3:
    st.plotly_chart(plot_regression_chart(filtered_df), use_container_width=True)

col4, col5 = st.columns(2)

with col4:
    st.plotly_chart(plot_contracts_per_month(filtered_df), use_container_width=True)
with col5:
    st.plotly_chart(plot_index_analysis(filtered_df), use_container_width=True)
