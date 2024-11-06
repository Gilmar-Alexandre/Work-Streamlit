import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Gestão de Contratos", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel('dados_estruturados.xlsx')
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
st.header("Dashboard")

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

# Função para gerar gráficos
def plot_value_comparison(df):
    monthly_summary = df.groupby('MÊS').agg({
        'VALOR PAGO\n(POR 12 MESES)': 'sum',
        'VALOR REAJUSTADO\n(POR 12 MESES)': 'sum',
        'DIFERENÇA DE VALOR DE CONTRATO': 'sum'
    }).reset_index()

    fig = go.Figure()

    # Adicionando barras para VALOR PAGO
    fig.add_trace(go.Bar(
        y=monthly_summary['MÊS'],
        x=monthly_summary['VALOR PAGO\n(POR 12 MESES)'],
        name='Valor Pago',
        marker_color='lightcyan',
        orientation='h'
    ))

    # Adicionando linha para VALOR REAJUSTADO
    fig.add_trace(go.Scatter(
        y=monthly_summary['MÊS'],
        x=monthly_summary['VALOR REAJUSTADO\n(POR 12 MESES)'],
        name='Valor Reajustado',
        mode='lines+markers',
        line=dict(color='darkblue', width=2),
    ))

    total_reajustado = monthly_summary['VALOR REAJUSTADO\n(POR 12 MESES)'].sum()
    total_diferenca = monthly_summary['DIFERENÇA DE VALOR DE CONTRATO'].sum()

    # Adicionando anotação para mostrar os valores totais no topo do gráfico
    fig.add_annotation(
        text=f"Total Diferença: {format_currency(total_diferenca)}",
        xref="paper", yref="paper",
        x=0.5, y=1.1, showarrow=False,
        font=dict(size=18, color="white")
    )

    fig.update_layout(
        title='Valores Pagos e Reajustados por Mês',
        xaxis_title=None,
        yaxis_title=None,
        xaxis_tickformat='R$,.2f',
        barmode='group',
        showlegend=False,
        xaxis=dict(showline=False, showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showline=False, showgrid=False, zeroline=False, visible=False)
    )
    
    return fig

def plot_contracts_per_month(df):
    contracts_per_month = df.groupby('MÊS').size().reset_index(name='TOTAL DE CONTRATOS')

    months_order = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 
                    'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
    contracts_per_month['MÊS'] = pd.Categorical(contracts_per_month['MÊS'], categories=months_order, ordered=True)
    contracts_per_month = contracts_per_month.sort_values('MÊS')

    fig = px.bar(contracts_per_month, x='MÊS', y='TOTAL DE CONTRATOS', 
                 title='Total de Contratos por Mês',
                 labels={'TOTAL DE CONTRATOS': 'Total de Contratos', 'MÊS': 'Mês'},
                 color='TOTAL DE CONTRATOS',
                 color_discrete_map={'JANEIRO':'lightcyan',
                                     'FEVEREIRO':'cyan',
                                     'MARÇO':'royalblue',
                                     'ABRIL':'darkblue',
                                     'MAIO':'lightcyan',
                                     'JUNHO':'cyan',
                                     'JULHO':'royalblue',
                                     'AGOSTO':'darkblue',
                                     'SETEMBRO':'lightcyan',
                                     'OUTUBRO':'cyan',
                                     'NOVEMBRO':'royalblue',
                                     'DEZEMBRO':'darkblue'})

    fig.update_traces(texttemplate='%{y}', textposition='outside')

    fig.update_layout(
        xaxis=dict(showline=False, showgrid=False, zeroline=False),
        yaxis=dict(showline=False, showgrid=False, zeroline=False, title='Total de Contratos'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig

# Criar colunas

col1, col2, col3 = st.columns(3)

with col1:
    st.write("")  # Coluna vazia, se você quiser adicionar algo mais tarde.

with col2:
    st.write("")  # Coluna vazia, se você quiser adicionar algo mais tarde.

with col3:
    st.plotly_chart(plot_value_comparison(filtered_df), use_container_width=True)  # Gráfico que ocupa 1/3 da largura

# Gráfico que ocupa todo o espaço
st.plotly_chart(plot_contracts_per_month(filtered_df), use_container_width=True)
