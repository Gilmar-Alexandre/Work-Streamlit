import pandas as pd

# Dados de exemplo para a aba de contratos
dados_contratos = {
    'CONTRATO Nº': [],
    'EMPRESA': [],
    'SISTEMA': [],
    'INÍCIO': [],
    'TÉRMINO': [],
    'MÊS': [],
    'VIGÊNCIA': [],
    'ÍNDICE': [],
    'PERÍODO DE FATURAMENTO': [],
    'VALOR PAGO': [],
    'VALOR PAGO (POR 12 MESES)': [],
    'ÍNDICE PUBLICADO': [],
    'ÍNDICE APLICADO': [],
    'VALOR REAJUSTADO': [],
    'VALOR REAJUSTADO (POR 12 MESES)': [],
    'PEDIDO/ORDEM DE COMPRAS': [],
    'STATUS / AÇÃO': [],
    'DATA DA AÇÃO': [],
    'DIFERENÇA DE VALOR DE CONTRATO': []
}

# Dados de exemplo para a aba de histórico
dados_historico = {
    'CONTRATO Nº': [],
    'AÇÃO': [],
    'DATA': []
}

# Criação dos DataFrames
df_contratos = pd.DataFrame(dados_contratos)
df_historico = pd.DataFrame(dados_historico)

# Salvar os DataFrames em um arquivo Excel com múltiplas abas
with pd.ExcelWriter('planilhas/2024.xlsx', engine='openpyxl') as writer:
    df_contratos.to_excel(writer, index=False, sheet_name='Contratos')
    df_historico.to_excel(writer, index=False, sheet_name='Histórico')

print("Planilha Excel criada com sucesso!")