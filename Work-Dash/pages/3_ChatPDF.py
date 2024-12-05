import os
import time
import streamlit as st
from pathlib import Path
from utils import cria_chain_conversa, PASTA_ARQUIVOS

# Certifique-se de que o diretório PASTA_ARQUIVOS existe
PASTA_ARQUIVOS = Path("pdfs")  # Ajuste o caminho conforme necessário
PASTA_ARQUIVOS.mkdir(parents=True, exist_ok=True)  # Cria o diretório se não existir

def sidebar():
    """Função para a barra lateral onde os usuários podem fazer upload de PDFs."""
    uploaded_pdfs = st.file_uploader(
        'Adicione seus arquivos PDF', 
        type=['pdf'], 
        accept_multiple_files=True
    )
    
    # Limpa arquivos antigos e salva novos PDFs
    if uploaded_pdfs:
        for arquivo in PASTA_ARQUIVOS.glob('*.pdf'):
            arquivo.unlink()  # Remove arquivos antigos
        for pdf in uploaded_pdfs:
            with open(PASTA_ARQUIVOS / pdf.name, 'wb') as f:
                f.write(pdf.read())
    
    # Botão para inicializar ou atualizar o ChatBot
    label_botao = 'Inicializar ChatBot' if 'chain' not in st.session_state else 'Atualizar ChatBot'
    if st.button(label_botao, use_container_width=True):
        if len(list(PASTA_ARQUIVOS.glob('*.pdf'))) == 0:
            st.error('Adicione arquivos .pdf para inicializar o chatbot')
        else:
            st.success('Inicializando o ChatBot...')
            cria_chain_conversa()
            st.rerun()

def chat_window():
    """Função para a janela de chat onde os usuários interagem com o ChatBot."""
    st.header('🤖 Bem-vindo a AmbiChats', divider=True)

    if 'chain' not in st.session_state:
        st.error('Faça o upload de PDFs para começar!')
        st.stop()
    
    chain = st.session_state['chain']
    memory = chain.memory

    # Carrega mensagens anteriores
    mensagens = memory.load_memory_variables({})['chat_history']
    container = st.container()
    
    # Exibe mensagens anteriores
    for mensagem in mensagens:
        chat = container.chat_message(mensagem.type)
        chat.markdown(mensagem.content)

    # Entrada para nova mensagem
    nova_mensagem = st.chat_input('Converse com seus documentos...')
    if nova_mensagem:
        chat = container.chat_message('human')
        chat.markdown(nova_mensagem)
        chat = container.chat_message('ai')
        chat.markdown('Gerando resposta...')

        resposta = chain.invoke({'question': nova_mensagem})
        st.session_state['ultima_resposta'] = resposta
        st.rerun()

def main():
    """Função principal que executa a aplicação Streamlit."""
    with st.sidebar:
        sidebar()
    chat_window()

if __name__ == '__main__':
    main()
