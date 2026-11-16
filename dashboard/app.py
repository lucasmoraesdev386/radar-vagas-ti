"""Dashboard em Streamlit. Rode com: streamlit run dashboard/app.py"""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from radar import analise, banco  # noqa: E402

st.set_page_config(page_title="Radar do mercado de TI", layout="wide")
st.title("Radar do mercado de TI: estágio e júnior")

con = banco.conectar()
estados = [r[0] for r in con.execute("SELECT DISTINCT estado FROM vagas WHERE estado IS NOT NULL ORDER BY 1")]
estado = st.sidebar.selectbox("Estado", ["Todos"] + estados)
niveis = st.sidebar.multiselect("Nível", ["estagio", "junior", "pleno", "senior"], default=["estagio", "junior"])
estado = None if estado == "Todos" else estado

r = analise.resumo(con, estado)
if r["vagas"] == 0:
    st.info("O banco está vazio. Rode: python -m radar coletar")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Vagas coletadas", r["vagas"])
c2.metric("Empresas", r["empresas"])
c3.metric("Vagas com descrição", r["com_descricao"])

esq, dir_ = st.columns(2)
with esq:
    st.subheader("Tecnologias mais citadas")
    df = pd.DataFrame(analise.top_tecnologias(con, tuple(niveis) or ("junior",), estado, limite=20))
    if not df.empty:
        st.bar_chart(df.set_index("tecnologia")["pct"])
        st.caption("% das vagas com descrição que citam a tecnologia (menção, não requisito).")
with dir_:
    st.subheader("Vagas por modalidade")
    df = pd.DataFrame(analise.contagem_por(con, "modalidade", estado))
    st.bar_chart(df.set_index("grupo")["vagas"])

st.subheader("Vagas novas por semana")
df = pd.DataFrame(analise.novas_por_semana(con, estado))
st.line_chart(df.set_index("semana")["novas"])

st.subheader("Empresas que mais anunciam")
st.dataframe(pd.DataFrame(analise.top_empresas(con, estado, 15)), use_container_width=True)
