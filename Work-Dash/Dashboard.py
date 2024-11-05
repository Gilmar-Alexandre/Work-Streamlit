import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Gestão de Contratos", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel('dados_estruturados.xlsx')
    return df

df = load_data()

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

# Convertemos as colunas de valor para float e formatamos
value_columns = [
    'VALOR PAGO\n(POR 12 MESES)',
    'VALOR REAJUSTADO\n(POR 12 MESES)',
    'DIFERENÇA DE VALOR DE CONTRATO'
]

for col in value_columns:
    grouped_df[col] = grouped_df[col].astype(float)

# Calculando os valores das métricas
valor_previsto = grouped_df['VALOR REAJUSTADO\n(POR 12 MESES)'].sum()
valor_renovado = grouped_df[grouped_df['STATUS / AÇÃO'] == 'RENOVADO']['VALOR REAJUSTADO\n(POR 12 MESES)'].sum()
valor_em_processo = grouped_df[grouped_df['STATUS / AÇÃO'] == 'EM PROCESSO']['VALOR REAJUSTADO\n(POR 12 MESES)'].sum()
valor_cancelado = grouped_df[grouped_df['STATUS / AÇÃO'] == 'CANCELADO']['VALOR REAJUSTADO\n(POR 12 MESES)'].sum()

# Calcular a diferença entre valor pago e valor reajustado para os cancelados
df_cancelado = grouped_df[grouped_df['STATUS / AÇÃO'] == 'CANCELADO']
diferenca_cancelado = (df_cancelado['VALOR PAGO\n(POR 12 MESES)'] - df_cancelado['VALOR REAJUSTADO\n(POR 12 MESES)']).sum()

# Layout das métricas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Valor Previsto", value=f"R${valor_previsto:,.2f}")

with col2:
    st.metric(label="Valor Renovado", value=f"R${valor_renovado:,.2f}")

with col3:
    st.metric(label="Valor em Processo", value=f"R${valor_em_processo:,.2f}")

with col4:
    st.metric(
        label="Valor Cancelado", 
        value=f"R${valor_cancelado:,.2f}", 
        delta=f"R${diferenca_cancelado:,.2f}",
        delta_color="inverse"  # Define a cor do delta
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

# Gráfico de Valores Pagos e Reajustados
monthly_summary = filtered_df.groupby('MÊS').agg({
    'VALOR PAGO\n(POR 12 MESES)': 'sum',
    'VALOR REAJUSTADO\n(POR 12 MESES)': 'sum'
}).reset_index()

fig = go.Figure()

fig.add_trace(go.Bar(
    x=monthly_summary['VALOR PAGO\n(POR 12 MESES)'],
    y=monthly_summary['MÊS'],
    name='Valor Pago',
    marker_color='blue',
    orientation='h'
))

fig.add_trace(go.Scatter(
    x=monthly_summary['VALOR REAJUSTADO\n(POR 12 MESES)'],
    y=monthly_summary['MÊS'],
    name='Valor Reajustado',
    mode='lines+markers',
    line=dict(color='red', width=2),
    orientation='h'
))

fig.update_layout(
    title='Valores Pagos e Reajustados por Mês',
    barmode='group',
    yaxis_tickformat='R$,.2f',
    xaxis=dict(showline=True, showgrid=True, zeroline=True),
    yaxis=dict(showline=True, showgrid=True, zeroline=True)
)

# Gráfico de Total de Contratos
contracts_per_month = filtered_df.groupby('MÊS').size().reset_index(name='TOTAL DE CONTRATOS')

months_order = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 
                'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
contracts_per_month['MÊS'] = pd.Categorical(contracts_per_month['MÊS'], categories=months_order, ordered=True)
contracts_per_month = contracts_per_month.sort_values('MÊS')

fig_total = px.bar(contracts_per_month, x='MÊS', y='TOTAL DE CONTRATOS', 
                   title='Total de Contratos por Mês',
                   labels={'TOTAL DE CONTRATOS': 'Total de Contratos', 'MÊS': 'Mês'},
                   color='TOTAL DE CONTRATOS',
                   color_continuous_scale=px.colors.sequential.Plasma)

for index, row in contracts_per_month.iterrows():
    fig_total.add_annotation(
        x=row['MÊS'], 
        y=row['TOTAL DE CONTRATOS'] + 0.5,  
        text=str(row['TOTAL DE CONTRATOS']), 
        showarrow=False, 
        font=dict(size=18, color='white'), 
        yshift=5,  
        align="center"  
    )

# Criar colunas
st.header("Dashboard")
col1, col2, col3 = st.columns(3)

with col1:
    st.plotly_chart(fig, use_container_width=True)  # Gráfico que ocupa 1/3 da largura

with col2:
    st.write("")  # Coluna vazia, se você quiser adicionar algo mais tarde.

with col3:
    st.write("")  # Coluna vazia, se você quiser adicionar algo mais tarde.

# Gráfico que ocupa todo o espaço
st.plotly_chart(fig_total, use_container_width=True)
