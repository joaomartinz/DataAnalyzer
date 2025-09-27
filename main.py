import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Data Analyzer", layout="wide")
st.title("📊 Data Analyzer - Upload CSV/Excel")

# Upload do arquivo
uploaded_file = st.file_uploader("Escolha um arquivo CSV ou Excel", type=["csv", "xlsx"])

if uploaded_file:
    if st.button("📂 Carregar arquivo"):
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.session_state["df"] = df
        st.success("Arquivo carregado!")

# Só mostra análises se já tiver arquivo carregado
if "df" in st.session_state:
    df = st.session_state["df"]

    st.subheader("Prévia dos dados")
    st.write(df.head())

    # ---------- FILTROS -----------
    st.subheader("Filtros")
    cols = st.columns(min(3, len(df.columns)))
    filtros = {}

    for i, col in enumerate(df.columns):
        unique_vals = df[col].dropna().unique()

        if len(unique_vals) <= 20:
            filtros[col] = cols[i % 3].multiselect(f"Filtrar {col}", unique_vals)
        else:
            if pd.api.types.is_numeric_dtype(df[col]):
                min_val, max_val = float(df[col].min()), float(df[col].max())
                filtros[col] = cols[i % 3].slider(f"Filtrar {col}", min_val, max_val, (min_val, max_val))

            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                min_date, max_date = df[col].min(), df[col].max()
                filtros[col] = cols[i % 3].date_input(f"Filtrar {col}", [min_date, max_date])
            else:
                filtros[col] = None

    # Aplicar filtros
    df_filtrado = df.copy()
    for col, val in filtros.items():
        if val:
            if isinstance(val, list) and len(val) == 2 and pd.api.types.is_numeric_dtype(df[col]):
                df_filtrado = df_filtrado[(df_filtrado[col] >= val[0]) & (df_filtrado[col] <= val[1])]
            elif isinstance(val, list) and len(val) == 2 and pd.api.types.is_datetime64_any_dtype(df[col]):
                df_filtrado = df_filtrado[(df_filtrado[col] >= pd.to_datetime(val[0])) &
                                          (df_filtrado[col] <= pd.to_datetime(val[0]))]
            elif isinstance(val, list) and len(val) > 0:
                df_filtrado = df_filtrado[df_filtrado[col].isin(val)]
    
    st.subheader("Dados filtrados")
    st.write(df_filtrado)