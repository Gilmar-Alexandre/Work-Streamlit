import pandas as pd
import streamlit as st
import pandas as pd
import time

@st.cache_data
def load_data():
    df = pd.read_excel('dados.xlsx')
    time.sleep(5)
    return df
df = load_data()
st.session_state["df"] = df




