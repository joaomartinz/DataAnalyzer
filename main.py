import pandas as pd
import streamlit as st
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


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
            if isinstance(val, (list, tuple)) and len(val) == 2 and pd.api.types.is_numeric_dtype(df[col]):
                df_filtrado = df_filtrado[(df_filtrado[col] >= val[0]) & (df_filtrado[col] <= val[1])]
            elif isinstance(val, list) and len(val) == 2 and pd.api.types.is_datetime64_any_dtype(df[col]):
                df_filtrado = df_filtrado[(df_filtrado[col] >= pd.to_datetime(val[0])) &
                                          (df_filtrado[col] <= pd.to_datetime(val[0]))]
            elif isinstance(val, list) and len(val) > 0:
                df_filtrado = df_filtrado[df_filtrado[col].isin(val)]

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado encontrado após aplicar os filtros.")
    else:
        st.subheader("Dados filtrados")
        st.write(df_filtrado)
    
    # ---------- ESTATÍSTICAS -----------
    st.subheader("Estatísticas básicas")
    st.write(df_filtrado.describe())

    # ---------- ANÁLISE EXPLORATÓRIA ----------
    st.subheader("Análise Exploratória dos Dados")

    st.markdown("** Quantidade de valores duplicados por coluna:**")
    duplicados = {col: df_filtrado[col].duplicated().sum() for col in df_filtrado.columns}
    st.write(pd.DataFrame.from_dict(duplicados, orient="index", columns=["Duplicados"]))

    st.markdown("** Valores máximos e mínimos por coluna numérica:**")
    if not df_filtrado.select_dtypes(include=np.number).empty:
        max_min = pd.DataFrame({
            "Máximo": df_filtrado.select_dtypes(include=np.number).max(),
            "Mínimo": df_filtrado.select_dtypes(include=np.number).min()
        })
        st.write(max_min)

    st.markdown("** Média, Mediana e Moda:**")
    if not df_filtrado.select_dtypes(include=np.number).empty:
        moda = df_filtrado.mode(numeric_only=True)
        if not moda.empty:
            moda = moda.iloc[0]
        else:
            moda = pd.Series([np.nan] * len(df_filtrado.select_dtypes(include=np.number).columns),
                             index=df_filtrado.select_dtypes(include=np.number).columns)

        stats = pd.DataFrame({
            "Média": df_filtrado.mean(numeric_only=True),
            "Mediana": df_filtrado.median(numeric_only=True),
            "Moda":moda
        })
        st.write(stats)

    st.markdown("**Desvio padrão e n° de valores únicos por coluna:**")
    std_unique = pd.DataFrame({
        "Desvio Padrão": df_filtrado.std(numeric_only=True),
        "Valores Únicos": df_filtrado.nunique()
    })
    st.write(std_unique)

    st.markdown("** Valores em branco por coluna:**")
    nulos = df_filtrado.isnull().sum()
    st.write(nulos[nulos > 0] if nulos.sum() > 0 else "Nenhum valor nulo encontrado")

       # ---------- GRÁFICOS ----------
    st.subheader("📊 Gráficos Automáticos")

    colunas_numericas = [c for c in df_filtrado.columns if pd.api.types.is_numeric_dtype(df_filtrado[c])]
    colunas_categoricas = [c for c in df_filtrado.columns if df_filtrado[c].dtype == "object"]

    # Gráficos para colunas numéricas
    for col in colunas_numericas:
        st.markdown(f"### 🔹 {col} (Numérica)")
        fig, ax = plt.subplots(figsize=(4, 2))
        sns.histplot(df[col], kde=True, ax=ax)
        plt.title(f"Distribuição de {col}")
        ax.set_title(plt.gcf())
        st.pyplot(fig, width="content")
       
        
    # Gráficos para colunas categóricas
    for col in colunas_categoricas:
        st.markdown(f"### 🔹 {col} (Categórica)")
        fig, ax = plt.subplots(figsize=(4,2))
        df[col].value_counts().plot(kind="bar")
        plt.title(f"Frequência de {col}")
        ax.set_title(plt.gcf())
        st.pyplot(fig, width="content")

    # ---------- EXPORTAÇÃO ----------
    st.subheader("📂 Exportar Dados")
    csv = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Baixar CSV", data=csv, file_name="dados_filtrados.csv", mime="text/csv")



  
    
