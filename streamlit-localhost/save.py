import streamlit as st
import pandas as pd
import altair as alt

# Dicionário com meses em português
meses_pt = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

def plot_desistencias_por_mes_altair(df):
    df_filtrado = df[
        (df['estágio'].isin(['Desistiu', 'Desistência'])) & 
        (pd.to_datetime(df['data_de_desistência_do_curso']).dt.year != 2026)
    ].copy()

    df_filtrado['data_de_desistência_do_curso'] = pd.to_datetime(df_filtrado['data_de_desistência_do_curso'])
    df_filtrado['ano_mes_period'] = df_filtrado['data_de_desistência_do_curso'].dt.to_period('M')

    desistencias_por_mes = df_filtrado.groupby('ano_mes_period').size()

    min_periodo = min(desistencias_por_mes.index.min(), pd.Period('2024-10', freq='M'))
    max_periodo = desistencias_por_mes.index.max()
    periodos_completos = pd.period_range(min_periodo, max_periodo, freq='M')
    desistencias_por_mes = desistencias_por_mes.reindex(periodos_completos, fill_value=0)

    formatted_index = [
        f"{meses_pt[period.month]}/{str(period.year)[-2:]}" for period in desistencias_por_mes.index
    ]

    df_final = desistencias_por_mes.to_frame(name='Desistências por Mês/Ano')
    df_final['mes_ano'] = formatted_index

    chart = alt.Chart(df_final).mark_line(point=True).encode(
        x=alt.X('mes_ano:N', title='Mês/Ano', sort=formatted_index, axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('Desistências por Mês/Ano:Q', title='Número de desistências'),
        tooltip=['mes_ano', 'Desistências por Mês/Ano']
    ).properties(
        title='Desistências por Mês/Ano',
        width=800,
        height=400
    ).interactive()

    return chart, df_final.set_index('mes_ano')

def plot_desistencias_por_motivo_altair(df):
    df['data_de_desistência_do_curso'] = pd.to_datetime(df['data_de_desistência_do_curso'])
    df = df[
        (df['estágio'].isin(['Desistiu', 'Desistência'])) & 
        (df['data_de_desistência_do_curso'].dt.year != 2026)
    ].copy()

    df['motivo_da_desistência'] = df['motivo_da_desistência'].replace({
        'Motivos de sáude/pessoal': 'Motivos de saúde/pessoal',
        'Motivos de saúde/pessoal.': 'Motivos de saúde/pessoal'
    })

    df['ano_mes_period'] = df['data_de_desistência_do_curso'].dt.to_period('M')

    pivot = df.groupby(['ano_mes_period', 'motivo_da_desistência']).size().reset_index(name='contagem')

    min_periodo = min(pivot['ano_mes_period'].min(), pd.Period('2024-10', freq='M'))
    max_periodo = pivot['ano_mes_period'].max()
    periodos_completos = pd.period_range(min_periodo, max_periodo, freq='M')

    motivos = pivot['motivo_da_desistência'].unique()
    full_index = pd.MultiIndex.from_product([periodos_completos, motivos], names=['ano_mes_period', 'motivo_da_desistência'])
    pivot_full = pivot.set_index(['ano_mes_period', 'motivo_da_desistência']).reindex(full_index, fill_value=0).reset_index()

    pivot_full['mes_ano'] = pivot_full['ano_mes_period'].apply(lambda p: f"{meses_pt[p.month]}/{str(p.year)[-2:]}")

    meses_excluir = ['Dezembro/22', 'Janeiro/23', 'Agosto/22']
    pivot_full = pivot_full[~pivot_full['mes_ano'].isin(meses_excluir)]

    pivot_full = pivot_full[pivot_full['motivo_da_desistência'] != 'Evasão sem justificativa/sem retorno']

    chart = alt.Chart(pivot_full).mark_bar().encode(
        x=alt.X(
            'mes_ano:N',
            sort=sorted(
                pivot_full['mes_ano'].unique(),
                key=lambda x: (int('20' + x.split('/')[1]), list(meses_pt.values()).index(x.split('/')[0]))
            ),
            title='Mês/Ano',
            axis=alt.Axis(labelAngle=-45)
        ),
        y=alt.Y('contagem:Q', title='Número de desistências'),
        color=alt.Color(
            'motivo_da_desistência:N',
            title='Motivo da Desistência',
            legend=alt.Legend(
                orient="bottom",
                padding=20,
                symbolSize=100,
                labelFontSize=12,
                labelLimit=300,
                columns=2
            )
        ),
        tooltip=['mes_ano', 'motivo_da_desistência', 'contagem']
    ).properties(
        title='Desistências por período por motivo',
        width=800,
        height=600
    ).interactive()

    return chart

def plot_desistencias_por_sexo_altair(df):
    df = df.copy()
    df['data_de_desistência_do_curso'] = pd.to_datetime(df['data_de_desistência_do_curso'], errors='coerce')
    df = df[
        (df['estágio'].isin(['Desistiu', 'Desistência'])) &
        (df['data_de_desistência_do_curso'].dt.year != 2026) &
        (df['sexo'].notna())
    ]

    df['ano_mes'] = df['data_de_desistência_do_curso'].dt.to_period('M')

    pivot = df.groupby(['ano_mes', 'sexo']).size().reset_index(name='contagem')

    min_periodo = min(pivot['ano_mes'].min(), pd.Period('2024-10', freq='M'))
    max_periodo = pivot['ano_mes'].max()
    periodos = pd.period_range(min_periodo, max_periodo, freq='M')

    sexos_desejados = ['Feminino', 'Masculino', 'Não binário']
    index_completo = pd.MultiIndex.from_product([periodos, sexos_desejados], names=['ano_mes', 'sexo'])
    pivot = pivot.set_index(['ano_mes', 'sexo']).reindex(index_completo, fill_value=0).reset_index()

    pivot['mes_ano'] = pivot['ano_mes'].apply(lambda p: f"{meses_pt[p.month]}/{str(p.year)[2:]}")
    
    # Remover meses irrelevantes
    meses_remover = ['Agosto/22', 'Dezembro/22', 'Janeiro/23', 'Agosto/24', 'Setembro/24', 'Outubro/24', 'Novembro/24']
    pivot = pivot[~pivot['mes_ano'].isin(meses_remover)]

    cores_dict = {
        'Feminino': "#f35656",
        'Masculino': "#5f5ff5",
        'Não binário': "#ced6ce"
    }

    chart = alt.Chart(pivot).mark_bar().encode(
        x=alt.X(
            'mes_ano:N',
            title='Mês/Ano',
            sort=sorted(pivot['mes_ano'].unique(), key=lambda x: (int('20' + x.split('/')[1]), list(meses_pt.values()).index(x.split('/')[0]))),
            axis=alt.Axis(labelAngle=-45)
        ),
        y=alt.Y('contagem:Q', title='Número de desistências'),
        color=alt.Color('sexo:N', scale=alt.Scale(domain=list(cores_dict.keys()), range=list(cores_dict.values())), title='Sexo'),
        tooltip=['mes_ano', 'sexo', 'contagem']
    ).properties(
        title='Desistências por período e sexo',
        width=800,
        height=500
    ).interactive()

    return chart

# --- Streamlit app --- 
st.set_page_config(
    page_title="Dashboard de Desistências",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📉 Análise de Desistências ao Longo do Tempo")
st.markdown("""Este dashboard mostra a evolução do número de desistências por mês/ano e por motivo, considerando alunos que desistiram ou tiveram desistência registrada (excluindo o ano de 2026).""")

try:
    # Carregando os dados
    df = pd.read_excel('desistencia.xlsx')  # Altere o caminho se necessário

    # Gráfico 1: desistências por mês/ano
    chart1, df_desistencias = plot_desistencias_por_mes_altair(df)
    st.altair_chart(chart1, use_container_width=True)

    # Tabela resumida (ordenada e filtrada)
    df_desistencias_sorted = df_desistencias.sort_values(by='Desistências por Mês/Ano', ascending=False)
    df_desistencias_filtrado = df_desistencias_sorted.drop(index=['Dezembro/22', 'Janeiro/23'], errors='ignore')
    st.subheader("Dados resumidos de desistências por mês")
    st.dataframe(df_desistencias_filtrado, width=600)

    # Gráfico 2: desistências por motivo
    chart2 = plot_desistencias_por_motivo_altair(df)
    st.altair_chart(chart2, use_container_width=True)

    # Gráfico 3: desistências por sexo
    chart3 = plot_desistencias_por_sexo_altair(df)
    st.altair_chart(chart3, use_container_width=True)

except FileNotFoundError:
    st.error("Arquivo 'desistencia.xlsx' não encontrado. Por favor, coloque o arquivo na mesma pasta do app.")
except Exception as e:
    st.error(f"Erro ao processar os dados: {e}")