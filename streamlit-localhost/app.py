import streamlit as st
import pandas as pd
import altair as alt

st.title("Análise de Desistências por Motivo e Período")

# Caminho do arquivo Excel (ajuste se precisar)
caminho_arquivo = 'desistencia.xlsx'

try:
    df = pd.read_excel(caminho_arquivo)

    df_filtrado = df[
        (df['estágio'].isin(['Desistiu', 'Desistência'])) &
        (pd.to_datetime(df['data_de_desistência_do_curso']).dt.year != 2026)
    ].copy()

    df_filtrado['data_de_desistência_do_curso'] = pd.to_datetime(df_filtrado['data_de_desistência_do_curso'])
    df_filtrado['ano_mes'] = df_filtrado['data_de_desistência_do_curso'].dt.to_period('M')

    df_selecionado = df_filtrado[['proprietário_do_matrícula', 'data_de_desistência_do_curso',
                                  'estágio', 'ano_mes', 'motivo_da_desistência',
                                  'sexo', 'renda_individual_mensal', 'situação_de_emprego_atual']].copy()

    df_selecionado['motivo_da_desistência'] = df_selecionado['motivo_da_desistência'].replace({
        'Motivos de sáude/pessoal': 'Motivos de saúde/pessoal',
        'Motivos de saúde/pessoal.': 'Motivos de saúde/pessoal'
    })

    # Agrupar por ano_mes e motivo_da_desistência
    pivot = df_selecionado.groupby(['ano_mes', 'motivo_da_desistência']).size().unstack(fill_value=0)

    min_periodo = min(pivot.index.min(), pd.Period('2024-10', freq='M'))
    max_periodo = pivot.index.max()
    periodos_completos = pd.period_range(min_periodo, max_periodo, freq='M')
    pivot = pivot.reindex(periodos_completos, fill_value=0)

    meses_pt = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

    formatted_index = [f"{meses_pt[p.month - 1]}/{str(p.year)[2:]}" for p in pivot.index]
    pivot.index = formatted_index

    evasao_sem_justificativa_total = pivot.get('Evasão sem justificativa/sem retorno', pd.Series([0])).sum()

    # Remover categoria e meses indesejados para gráfico
    pivot_grafico = pivot.drop(columns=['Evasão sem justificativa/sem retorno'], errors='ignore')
    meses_para_remover = ['Agosto/22', 'Dezembro/22', 'Janeiro/23']
    pivot_grafico = pivot_grafico.drop(index=meses_para_remover, errors='ignore')

    # Definir nome do índice para melt funcionar
    pivot_grafico.index.name = 'ano_mes'

    # Transformar pivot para formato "long" para Altair
    df_long = pivot_grafico.reset_index().melt(id_vars='ano_mes', var_name='Motivo', value_name='Desistências')

    # Gráfico de barras empilhadas com Altair
    chart = alt.Chart(df_long).mark_bar().encode(
        x=alt.X('ano_mes:N', title='Mês/Ano', sort=list(pivot_grafico.index)),
        y=alt.Y('Desistências:Q', title='Número de desistências'),
        color=alt.Color('Motivo:N', title='Motivo da Desistência'),
        tooltip=['ano_mes', 'Motivo', 'Desistências']
    ).properties(
        width=700,
        height=400,
        title='Desistências por período por motivo'
    ).configure_axisX(
        labelAngle=45,
        labelAlign='left'
    )

    st.altair_chart(chart, use_container_width=True)

    st.subheader("Resumo das desistências por motivo (excluindo 'Evasão sem justificativa/sem retorno')")
    total_por_motivo = pivot.sum()
    for motivo, total in total_por_motivo.items():
        if motivo != 'Evasão sem justificativa/sem retorno':
            st.write(f"- **{motivo}**: {total}")

    st.write(f"**Total de desistências por evasão sem justificativa/sem retorno:** {evasao_sem_justificativa_total}")

except FileNotFoundError:
    st.error(f"Arquivo '{caminho_arquivo}' não encontrado. Coloque o arquivo na mesma pasta do app ou ajuste o caminho.")