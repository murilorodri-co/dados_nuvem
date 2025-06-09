import streamlit as st
import pandas as pd
import altair as alt

# Carregar os dados
df = pd.read_excel('desistencia.xlsx')

# Filtrar apenas desistências e excluir ano 2026
df_filtrado = df[
    (df['estágio'].isin(['Desistiu', 'Desistência'])) &
    (pd.to_datetime(df['data_de_desistência_do_curso']).dt.year != 2026)
].copy()

df_filtrado['data_de_desistência_do_curso'] = pd.to_datetime(df_filtrado['data_de_desistência_do_curso'])
df_filtrado['ano_mes'] = df_filtrado['data_de_desistência_do_curso'].dt.to_period('M')

df_desistencias = df_filtrado.groupby('ano_mes').size().reset_index(name='Desistências por Mês/Ano')
df_desistencias['ano_mes_ordem'] = df_desistencias['ano_mes'].dt.to_timestamp()

# Dicionário manual com nomes corretos dos meses em português
meses_pt = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro"
}

# Função para formatar "Mês/Ano" manualmente
def formatar_ano_mes(periodo):
    ano = periodo.year % 100  # pegar os 2 últimos dígitos do ano
    mes = meses_pt[periodo.month]
    return f"{mes}/{ano:02d}"

# Aplicar formatação manual
df_desistencias['ano_mes_formatado'] = df_desistencias['ano_mes'].apply(formatar_ano_mes)

# Plot com ordenação temporal correta
chart = alt.Chart(df_desistencias).mark_line(point=True).encode(
    x=alt.X('ano_mes_formatado:N', title='Mês/Ano',
            sort=list(df_desistencias.sort_values('ano_mes_ordem')['ano_mes_formatado'])),
    y=alt.Y('Desistências por Mês/Ano:Q', title='Número de Desistências'),
    tooltip=['ano_mes_formatado', 'Desistências por Mês/Ano']
).properties(
    width=700,
    height=400,
    title='Desistências por Mês/Ano'
)

st.altair_chart(chart, use_container_width=True)