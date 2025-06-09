import streamlit as st
import pandas as pd
import altair as alt
import os
import time
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta

# Caminho da logo
logo_path = os.path.join(os.path.dirname(__file__), 'img', 'logo.png')

# Configurações da página
st.set_page_config(
    page_title="Projeto Extensor - Escola da Nuvem",
    page_icon=logo_path if os.path.exists(logo_path) else None,
    layout="wide"
)

# Inicializar o estado da página
if "page" not in st.session_state:
    st.session_state.page = "—"

# Injetar animação CSS uma única vez
def inject_animation_css():
    st.markdown("""
        <style>
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translate3d(0, 20px, 0);
            }
            to {
                opacity: 1;
                transform: translate3d(0, 0, 0);
            }
        }

        .fade-in {
            animation: fadeInUp 1s ease forwards;
            opacity: 0;
        }

        .fade-in-delay-1 { animation-delay: 0.3s; }
        .fade-in-delay-2 { animation-delay: 0.6s; }
        .fade-in-delay-3 { animation-delay: 0.9s; }

        /* Estilizando o elemento stDecoration */
        #stDecoration {
            background-color: #f5f5f5;  /* Altere a cor de fundo */
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);  /* Adiciona uma sombra sutil */
        }

        /* Outro exemplo de customização */
        .st-emotion-cache-1dp5vir {
            background-image: linear-gradient(90deg, #2569f3, #80d6ff);
        }

        /* Personalização do hover de texto em outros elementos */
        .st-emotion-cache-4rp1ik:hover {
            color: #0645c4;  /* Mudando a cor para azul no hover */
        }

        .st-emotion-cache-13lcgu3:hover {
            border-color: #1c83e1;  /* Mudando a borda para azul */
            color: #1c83e1;          /* Mudando a cor do texto para azul */
        }

        /* Estilo do botão quando o mouse está sobre ele (hover) */
        .stButton > button:hover {
            transform: scale(1.05);      /* Aumenta ligeiramente o tamanho */
        }

        /* Estilo do botão quando ele é pressionado (clicado) */
        .stButton > button:active {
            background-color: #1c83e1 !important;  /* Cor de fundo azul quando clicado */
            color: #ffffff !important;             /* Cor do texto branca quando clicado */
            transform: scale(0.98);                /* Dá um efeito de clique */
            border-color: #0645c4;
        }

        /* Mantendo a cor do botão após o clique usando o :focus */
        .stButton > button:focus {
            background-color: #1c83e1 !important;  /* Mantendo a cor azul após o clique */
            color: #ffffff !important;             /* Mantendo a cor do texto branca */
            outline: none;                         /* Remover o contorno padrão do foco */
            border-color: #0645c4;
        }

        .st-d5, .st-d6, .st-d7, .st-d8 {
        border-color: #1c83e1
        }

        .st-emotion-cache-4rp1ik:hover svg {
        fill: #0645c4
        }

        </style>
    """, unsafe_allow_html=True)

# Função para carregar os dados com cache (alunos)
@st.cache_data
def load_data():
    return pd.read_excel('alunos_pii_none.xlsx')

# Função para carregar os dados de desistência com cache
@st.cache_data
def load_desistencia_data():
    return pd.read_excel('desistencia.xlsx')

@st.cache_data
def carregar_dados():
    df = pd.read_excel("perfil_alunos_desistentes_limpo.xlsx")
    # Converter a coluna de datas para datetime, se ainda não estiver
    df['data_de_desistência_do_curso'] = pd.to_datetime(df['data_de_desistência_do_curso'], errors='coerce')
    return df

df = carregar_dados()

@st.cache_data
def load_desistencia2_data():
    return pd.read_excel('perfil_alunos_desistentes_limpo.xlsx')

df = load_desistencia2_data()

# Padroniza nomes colunas
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

# --- Faixa de Renda personalizada ---
def categorizar_renda(valor):
    try:
        if pd.isna(valor):
            return "Não informado"
        valor = str(valor).replace("R$", "").replace(".", "").replace(",", "").strip()
        valor = int(valor)
        if valor <= 1000:
            return "Até R$1.000"
        elif valor <= 2000:
            return "R$1.001 - R$2.000"
        elif valor <= 4000:
            return "R$2.001 - R$4.000"
        else:
            return "Acima de R$4.000"
    except:
        return "Não informado"

df["faixa_renda_familiar"] = df["renda_familiar_mensal_aproximada"].apply(categorizar_renda)

# --- Estágio ---
df['estágio'] = df['estágio'].fillna('Não informado').astype(str)

# Agrupar categorias semelhantes
def group_similar_categories(df):
    similar_groups = {
        'Pós graduação': ['Pós graduação', 'MBA', 'Mestrado', 'Pós-graduação'],
        'Ensino Superior': ['Superior Completo', 'Graduação'],
        'Ensino Médio': ['Ensino Médio Completo'],
        'Ensino Fundamental': ['Ensino Fundamental Completo', 'Fundamental'],
        'Outros': ['Outro', 'Não Especificado']
    }
    for new_category, categories in similar_groups.items():
        df['Escolaridade'] = df['Escolaridade'].replace(categories, new_category)
    return df

def intro():
    st.markdown('<h1 class="custom-title fade-in fade-in-delay-1">Análise dos dados da Escola da Nuvem</h1>', unsafe_allow_html=True)
    st.markdown('<p class="fade-in fade-in-delay-2">Bem-vindo ao nosso sistema dedicado à análise detalhada dos dados de desistência da Escola da Nuvem. Nesta plataforma, você terá acesso a informações valiosas sobre os diversos aspectos das bases de dados da instutição. Nosso principal objetivo é oferecer uma visão clara e profunda das estatísticas e insights que podem ajudar a melhorar as práticas educacionais e direcionar decisões estratégicas para o futuro. Prepare-se para explorar, compreender e interagir com os dados de forma dinâmica e envolvente!</p>', unsafe_allow_html=True)

    # Dados preparados (igual ao seu código)
    desistencias_por_estado = df.groupby('estado').size().reset_index(name='contagem')
    contagem_faixa_etaria = df['faixa_etária'].value_counts().reset_index()
    contagem_faixa_etaria.columns = ['faixa_etária', 'quantidade']
    contagem_origem_sexo = df.groupby(['origem', 'sexo']).size().reset_index(name='quantidade')
    contagem_motivo = df['motivo_da_desistência'].value_counts().reset_index()
    contagem_motivo.columns = ['motivo_da_desistência', 'quantidade']
    contagem_motivo['fração'] = contagem_motivo['quantidade'] / contagem_motivo['quantidade'].sum()

    df['data_de_desistência_do_curso'] = pd.to_datetime(df['data_de_desistência_do_curso'], errors='coerce')
    df['ano'] = df['data_de_desistência_do_curso'].dt.year
    df['mes'] = df['data_de_desistência_do_curso'].dt.month
    grouped = df.groupby(['ano', 'mes']).size().reset_index(name='quantidade')
    monthly_dismissals = grouped[grouped['quantidade'] > 25]
    monthly_dismissals['data'] = pd.to_datetime(monthly_dismissals.rename(columns={'ano':'year','mes':'month'})[['year','month']].assign(day=1))
    monthly_dismissals['mes_ano'] = monthly_dismissals['data'].dt.strftime('%b/%Y')

    # Métricas numéricas
    total_desistentes = len(df)
    media_idade = df['idade'].dropna().mean() if 'idade' in df.columns else None
    seis_meses_atras = datetime.now() - timedelta(days=180)
    desistentes_6meses = df[df['data_de_desistência_do_curso'] >= seis_meses_atras].shape[0]

    # Gráficos
    chart1 = alt.Chart(desistencias_por_estado).mark_bar(color='#1c83e1').encode(
        x=alt.X('contagem:Q', title='Desistências'),
        y=alt.Y('estado:N', sort='-x', title='Estado'),
        tooltip=['estado', 'contagem']
    ).properties(width=350, height=250, title='Desistências por Estado')

    chart2 = alt.Chart(contagem_faixa_etaria).mark_bar().encode(
    x=alt.X('faixa_etária:N', sort='-y', title='Faixa Etária', axis=alt.Axis(labelAngle=-40)),
    y=alt.Y('quantidade:Q', title='Quantidade'),
    color=alt.Color('quantidade:Q', scale=alt.Scale(scheme='blues'), legend=None),  # aqui
    tooltip=['faixa_etária', 'quantidade']
    ).properties(width=400, height=250, title='Faixa Etária dos Desistentes').configure_title(
        fontSize=14, anchor='start', offset=10
    )

    chart3 = alt.Chart(contagem_origem_sexo).mark_bar().encode(
        x=alt.X('origem:N', title='Origem', axis=alt.Axis(labelAngle=-40)),
        y=alt.Y('quantidade:Q', title='Quantidade'),
        color=alt.Color('sexo:N', title='Sexo'),
        tooltip=['origem', 'sexo', 'quantidade']
    ).properties(width=400, height=250, title='Origem dos Alunos Desistentes').configure_title(
        fontSize=14, anchor='start', offset=10
    )

    chart4 = alt.Chart(contagem_motivo).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field='fração', type='quantitative'),
        color=alt.Color(field='motivo_da_desistência', type='nominal', legend=alt.Legend(title="Motivo da Desistência")),
        tooltip=['motivo_da_desistência', 'quantidade', alt.Tooltip('fração', format='.2%')]
    ).properties(width=350, height=300, title='Motivos de Desistência')

    chart5 = alt.Chart(monthly_dismissals).mark_line(point=True).encode(
        x=alt.X('mes_ano:N', title='Mês/Ano', sort=None),
        y=alt.Y('quantidade:Q', title='Quantidade'),
        tooltip=['mes_ano', 'quantidade']
    ).properties(width=720, height=250, title='Desistências por Período').configure_axis(labelAngle=-45)

    # Layout gráficos principais em colunas (chart1, chart2, chart3)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.altair_chart(chart1, use_container_width=True)
    with col2:
        st.altair_chart(chart2, use_container_width=True)
    with col3:
        st.altair_chart(chart3, use_container_width=True)

    col_motivo, spacer, col_metrics = st.columns([1, 0.1, 1])

    with col_motivo:
        st.altair_chart(chart4, use_container_width=True)

    with spacer:
        st.write("")  # Coluna só para espaçamento vazio

    with col_metrics:
        col1, col2, col3 = st.columns(3)

        col1.metric("Total de Desistentes", f"{total_desistentes}")
        col2.metric("Desistentes Últimos 6 Meses", f"{desistentes_6meses}")
        
        if media_idade is not None:
            col3.metric("Média de Idade", f"{media_idade:.1f} anos")
        else:
            col3.empty()

    # Gráfico maior
    st.altair_chart(chart5, use_container_width=True)

def desistencias():
    inject_animation_css()

    st.markdown('<h1 class="custom-title fade-in fade-in-delay-1">Dados Escola da Nuvem - Desistências</h1>', unsafe_allow_html=True)

    st.markdown('''<p class="fade-in fade-in-delay-2">
        Nesta página, apresentamos uma análise detalhada das desistências dos alunos da Escola da Nuvem, 
        focando nos estados com maior incidência. O objetivo é identificar padrões e gerar insights estratégicos 
        para apoiar a retenção dos estudantes e melhorar a eficácia dos programas educacionais da iniciativa.
    </p>''', unsafe_allow_html=True)

    with st.spinner("Carregando dados..."):
        time.sleep(2)

    df_desistencia = load_desistencia_data()
    df_desistencia = df_desistencia[df_desistencia['motivo_da_desistência'].notna()]

    desistencias_por_estado = df_desistencia.groupby('estado').size().reset_index(name='contagem')
    desistencias_por_estado = desistencias_por_estado.sort_values(by='contagem', ascending=False).head(10)

    #--------------- GRÁFICO 1 ---------------#

    # Gráfico (full width)
    chart = alt.Chart(desistencias_por_estado).mark_bar(color='#1c83e1').encode(
        x=alt.X('contagem:Q', title='Número de desistências'),
        y=alt.Y('estado:N', sort='-x', title='Estado'),
        tooltip=[alt.Tooltip('estado:N', title='Estado'),
                alt.Tooltip('contagem:Q', title='Número de Desistências')]
    ).properties(
        width=800,
        height=400,
        title='Gráfico dos estados com mais desistências'
    ).configure_title(
        fontSize=24,  # tamanho maior do título
        fontWeight='bold',
        anchor='start',  # alinhamento do título
    )

    # Envolvendo o gráfico numa div com margem-top para espaçamento
    st.markdown(
        """
        <div style="margin-top: -10px;">
        """,
        unsafe_allow_html=True
    )

    st.altair_chart(chart, use_container_width=True)

    st.markdown(
        """
        </div>
        """,
        unsafe_allow_html=True
    )

    # Disposição em colunas para tabela e expanders ao lado, com títulos estilizados
    col1, col2 = st.columns([2.5, 2])  # proporção 2:3 para expanders maiores

    df_tabela = desistencias_por_estado.rename(columns={'estado': 'Estado', 'contagem': 'Quantidade de Desistências'})
    df_tabela.index = range(1, len(df_tabela) + 1)  # índice começa em 1

    with col1:
        st.markdown('<span style="font-size: 24px;"><b>Tabela dos dados de desistências</b></span>', unsafe_allow_html=True)
        st.dataframe(df_tabela, use_container_width=True)

    with col2:
        st.markdown('<span style="font-size: 24px;"><b>Insights e Resultados</b></span>', unsafe_allow_html=True)
        with st.expander("🔎Insights obtidos", expanded=False):
            st.markdown("""
            O estado de **São Paulo** apresenta o maior número de desistências, com **315 casos**, representando uma parcela significativa do total. Isso sugere que ações focadas especificamente nesse estado devem ser priorizadas, seja com mais suporte, acompanhamento individual ou adaptações no conteúdo.

            O **Rio de Janeiro** vem em segundo lugar, com **71 desistências**, seguido por **Pernambuco (46)** e **Minas Gerais (42)**. Esses números mostram a necessidade de atenção regionalizada, principalmente no Sudeste e Nordeste, onde os índices são mais altos.

            Estados como **Ceará (29)**, **Distrito Federal (26)** e **Bahia (23)** apresentam níveis intermediários de desistência. É recomendável que a Escola da Nuvem explore causas mais específicas nessas localidades, como infraestrutura de acesso, carga horária ou apoio ao aluno.

            Já o **Rio Grande do Sul (21)**, **Paraná (19)** e **Espírito Santo (18)** fecham o ranking do top 10. Apesar de números menores, o fato de estarem entre os maiores índices absolutos ainda justifica a atenção.

            Esses dados reforçam a importância de desenvolver estratégias regionais de retenção, considerando as realidades socioeconômicas e culturais de cada estado. Programas de mentoria, flexibilização da carga horária, apoio técnico e acompanhamento pedagógico podem ajudar a reduzir as taxas de evasão de forma mais eficaz.

            Também é recomendável realizar análises periódicas desses dados e implementar pesquisas de satisfação e motivos de desistência para aprimorar continuamente a experiência dos alunos.
            """)
        with st.expander("📈Gráfico da distribuição percentual das desistências por estado", expanded=False):
            desistencias_por_estado['percentual'] = (desistencias_por_estado['contagem'] / desistencias_por_estado['contagem'].sum()) * 100

            # Container com altura fixa e scroll vertical
            st.markdown("""
            <div style="max-height: 300px; overflow-y: auto;">
            """, unsafe_allow_html=True)

            pie_chart = alt.Chart(desistencias_por_estado).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="contagem", type="quantitative"),
            color=alt.Color(field="estado", type="nominal", legend=alt.Legend(title="Legenda")),
            tooltip=[alt.Tooltip("estado:N", title="Estado"), alt.Tooltip("percentual:Q", format=".2f", title="Percentual (%)")]
        ).properties(
            width=350,
            height=195,
        ).configure_title(
            fontSize=14,
            anchor="start"
        ).configure_legend(
            labelFontSize=12  # diminui o tamanho da fonte da legenda
        )

            st.altair_chart(pie_chart)

            st.markdown("</div>", unsafe_allow_html=True)

    #--------------- GRÁFICO 2 ---------------#

    # Preparar os dados
    contagem_faixa_etaria = df['faixa_etária'].value_counts().reset_index()
    contagem_faixa_etaria.columns = ['faixa_etária', 'quantidade']

    # Criar o gráfico Altair com gradiente nas barras
    chart = alt.Chart(contagem_faixa_etaria).mark_bar().encode(
        x=alt.X('faixa_etária:N', sort='-y', title='Faixa etária'),
        y=alt.Y('quantidade:Q', title='Quantidade'),
        color=alt.Color('quantidade:Q', scale=alt.Scale(scheme='blues'), legend=alt.Legend(title='Quantidade')),
        tooltip=[
            alt.Tooltip('faixa_etária:N', title='Faixa etária'),
            alt.Tooltip('quantidade:Q', title='Quantidade')
        ]
    ).properties(
        width=700,
        height=400,
        title='Gráfico da faixa etária dos desistentes'
    ).configure_title(
        fontSize=24,
        fontWeight='bold',
        anchor='start'
    ).configure_axis(
        labelFontSize=14,
        titleFontSize=16
    )

    # Espaço com margin-top para o gráfico
    st.markdown(
        """
        <div style="margin-top: 15px;">
        """,
        unsafe_allow_html=True
    )

    # Renderizar gráfico
    st.altair_chart(chart, use_container_width=True)

    # Fechar div
    st.markdown("</div>", unsafe_allow_html=True)

    # Disposição em colunas para tabela e expanders ao lado, com títulos estilizados
    col1, col2 = st.columns([2.5, 2])

    with col1:
        st.markdown('<span style="font-size: 24px;"><b>Tabela da faixa etária dos desistentes</b></span>', unsafe_allow_html=True)
        # Exibir tabela dos dados do gráfico
        df_tabela = contagem_faixa_etaria.rename(columns={
            'faixa_etária': 'Faixa Etária',
            'quantidade': 'Quantidade'
        })
        df_tabela.index = range(1, len(df_tabela) + 1)
        st.dataframe(df_tabela, use_container_width=True)

    with col2:
        st.markdown('<span style="font-size: 24px;"><b>Insights e Resultados</b></span>', unsafe_allow_html=True)
        with st.expander("🔎Insights obtidos", expanded=False):
            st.markdown("""
            A análise da faixa etária dos desistentes revela que o maior grupo está entre **30 a 39 anos**, com **129 casos**, seguido pelas faixas **25 a 29 anos (90 desistências)** e **20 a 24 anos (79 desistências)**. Isso indica que a maioria dos desistentes está em idade produtiva e possivelmente conciliando estudos com trabalho e outras responsabilidades.

            As faixas de **40 a 49 anos (52 desistências)** e **15 a 19 anos (22 desistências)** apresentam números menores, mas ainda relevantes. Para o público mais jovem, é possível que desafios relacionados à adaptação ao formato de ensino remoto ou a outras questões pessoais impactem a retenção.

            As desistências nas faixas **50 a 59 anos (20)**, **Menos de 15 anos (2)** e **60 anos ou mais (1)** são mais pontuais, indicando que o público mais sênior é menor, mas ainda deve ser considerado em estratégias específicas.

            Esses dados sugerem que a Escola da Nuvem deve desenvolver estratégias flexíveis que atendam especialmente às necessidades dos adultos jovens e de meia-idade, que enfrentam múltiplas demandas. Programas de mentoria, horários mais flexíveis, suporte tecnológico e acompanhamento individualizado podem ser eficazes para aumentar a retenção desses grupos.

            Além disso, promover pesquisas para entender os motivos específicos das desistências em cada faixa etária pode fornecer insights valiosos para melhorias contínuas no ambiente educacional e nas políticas de apoio ao aluno.

            O foco em adaptações pedagógicas, comunicação assertiva e suporte emocional pode ajudar a reduzir as desistências, contribuindo para uma experiência mais satisfatória e inclusiva na Escola da Nuvem.
            """)
        # Dados fornecidos das faixas etárias
        dados_faixa_etaria = {
            'faixa_etária': [
                'Menos de 15 Anos', '15 a 19 anos', '20 a 24 anos', '25 a 29 anos',
                '30 a 39 anos', '40 a 49 anos', '50 a 59 anos', '60 anos ou mais'
            ],
            'quantidade': [2, 22, 79, 90, 129, 52, 20, 1]
        }

        df_faixa_etaria = pd.DataFrame(dados_faixa_etaria)

        # Ordenar faixas etárias para o eixo X
        ordem_faixa_etaria = [
            'Menos de 15 Anos', '15 a 19 anos', '20 a 24 anos', '25 a 29 anos',
            '30 a 39 anos', '40 a 49 anos', '50 a 59 anos', '60 anos ou mais'
        ]

        # Container com altura fixa e scroll vertical
        with st.expander("📈 Gráfico de desistências com média de desistências por faixa etária", expanded=False):
            st.markdown("""
                <div style="max-height: 400px; overflow-y: auto;">
            """, unsafe_allow_html=True)

            # Cálculo da média
            media_desistencias = df_faixa_etaria['quantidade'].mean()

            # Gráfico de barras
            barras = alt.Chart(df_faixa_etaria).mark_bar(color='#1c83e1').encode(
                x=alt.X('faixa_etária:N', sort=ordem_faixa_etaria, title='Faixa Etária'),
                y=alt.Y('quantidade:Q', title='Quantidade de Desistentes'),
                tooltip=[
                    alt.Tooltip('faixa_etária:N', title='Faixa Etária'),
                    alt.Tooltip('quantidade:Q', title='Quantidade')
                ]
            )

            # Linha da média
            linha_media = alt.Chart(pd.DataFrame({
                'media': [media_desistencias]
            })).mark_rule(color='red', strokeDash=[5,5]).encode(
                y='media:Q'
            ).properties(
                title='Gráfico de desistências com linha de média'
            )

            # Combinação dos dois gráficos
            grafico = (barras + linha_media).properties(
                width=700,
                height=400
            ).configure_title(
                fontSize=18,
                fontWeight='bold',
                anchor='start'
            ).configure_axis(
                labelFontSize=12,
                titleFontSize=14
            )

            # Renderizar gráfico
            st.altair_chart(grafico, use_container_width=True)

            st.markdown("</div>", unsafe_allow_html=True)

    #--------------- GRÁFICO 3 ---------------#

    # Exemplo de agrupamento para stacked bar
    contagem_origem_sexo = df.groupby(['origem', 'sexo']).size().reset_index(name='quantidade')

    chart_stacked_bar = alt.Chart(contagem_origem_sexo).mark_bar().encode(
        x=alt.X('origem:N', title='Origem'),
        y=alt.Y('quantidade:Q', title='Quantidade'),
        color=alt.Color('sexo:N', title='Sexo'),
        tooltip=[
            alt.Tooltip('origem:N', title='Origem'),
            alt.Tooltip('sexo:N', title='Sexo'),
            alt.Tooltip('quantidade:Q', title='Quantidade')
        ]
    ).properties(
        width=700,
        height=400,
        title='Gráfico da origem dos alunos desistentes'
    ).configure_title(
        fontSize=24,
        fontWeight='bold',
        anchor='start'
    ).configure_axis(
        labelFontSize=14,
        titleFontSize=16
    )

    st.markdown("<div style='margin-top: 25px;'>", unsafe_allow_html=True)
    st.altair_chart(chart_stacked_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Disposição em colunas para tabela e expanders ao lado, com títulos estilizados
    col1, col2 = st.columns([2.5, 2])

    # Preparar os dados para o gráfico e a tabela
    contagem_origem = df['origem'].value_counts().reset_index()
    contagem_origem.columns = ['origem', 'quantidade']

    with col1:
        st.markdown('<span style="font-size: 24px;"><b>Tabela da origem dos alunos desistentes</b></span>', unsafe_allow_html=True)
        
        # Preparar a tabela
        df_tabela_origem = contagem_origem.rename(columns={
            'origem': 'Origem',
            'quantidade': 'Quantidade'
        })
        
        df_tabela_origem.index = range(1, len(df_tabela_origem) + 1)
        
        st.dataframe(df_tabela_origem, use_container_width=True)

    with col2:
        st.markdown('<span style="font-size: 24px;"><b>Insights e Resultados</b></span>', unsafe_allow_html=True)
        with st.expander("🔎Insights obtidos", expanded=False):
            st.markdown("""
            A análise das origens dos alunos desistentes indica que a maior parte das desistências vem de indicações de amigos e familiares, com **256 casos**, seguida pelo LinkedIn (**146 desistências**) e grupos ou organizações das quais os alunos participam (**118 desistências**).

            Esses dados sugerem que, apesar da força do marketing boca a boca e redes sociais profissionais, há uma concentração de desistências vindo desses canais que merecem atenção especial.

            O LinkedIn, como plataforma profissional, pode ser uma boa fonte de captação, mas a taxa de desistência relativamente alta indica que talvez a expectativa dos alunos captados por lá não esteja alinhada com o conteúdo ou formato do curso.

            A presença de desistências vindas de canais digitais de busca (**Google, Bing, etc.**) e e-mail marketing da Escola da Nuvem reforça a necessidade de revisar a comunicação e o processo de onboarding para esses alunos.

            Observa-se ainda desistências de origens variadas, como eventos online, redes sociais e parceiros institucionais, indicando que múltiplos pontos de contato precisam de acompanhamento.

            **Recomendações:**
            - **Aprimorar o alinhamento de expectativa**: Garantir que a comunicação inicial, especialmente via LinkedIn e indicações, seja clara sobre o formato, conteúdo e compromissos do curso.
            - **Fortalecer o suporte inicial e acompanhamento personalizado** para alunos vindos das fontes com maiores desistências, focando em entender e mitigar causas comuns de evasão.
            - **Investir em estratégias de engajamento e retenção específicas para canais digitais**, com materiais educativos, tutoria e suporte técnico.
            - **Realizar pesquisas qualitativas com alunos desistentes de cada origem** para identificar problemas específicos e ajustar a estratégia de marketing e retenção.
            - **Potencializar parcerias e eventos online**, garantindo que a mensagem e as expectativas sejam alinhadas para reduzir desistências.
            """)

        with st.expander("📈 Gráfico linha do tempo das desistências", expanded=False):
            st.markdown("""<div style="max-height: 450px; overflow-y: auto;">""", unsafe_allow_html=True)
            
            # Agrupar por data e contar desistências
            df_timeline = df.groupby('data_de_desistência_do_curso').size().reset_index(name='quantidade')
            # Ordenar por data (caso não esteja ordenado)
            df_timeline = df_timeline.sort_values('data_de_desistência_do_curso')

            # Gráfico de linha Altair
            linha_tempo = alt.Chart(df_timeline).mark_line(point=True).encode(
                x=alt.X('data_de_desistência_do_curso:T', title='Data da Desistência', axis=alt.Axis(format='%d/%m/%Y')),
                y=alt.Y('quantidade:Q', title='Quantidade de Desistências'),
                tooltip=[
                    alt.Tooltip('data_de_desistência_do_curso:T', title='Data', format='%d/%m/%Y'),
                    alt.Tooltip('quantidade:Q', title='Quantidade')
                ]
            ).properties(
                width=700,
                height=400,
                title='Linha do Tempo das Desistências'
            ).configure_title(
                fontSize=18,
                fontWeight='bold',
                anchor='start'
            ).configure_axis(
                labelFontSize=12,
                titleFontSize=14
            )

            st.altair_chart(linha_tempo, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    #--------------- GRÁFICO 4 ---------------#
    
    contagem_motivo = df['motivo_da_desistência'].value_counts().reset_index()
    contagem_motivo.columns = ['motivo_da_desistência', 'quantidade']

    # Calcular a fração para cada motivo
    contagem_motivo['fração'] = contagem_motivo['quantidade'] / contagem_motivo['quantidade'].sum()

    # Calcular ângulo inicial e final para cada fatia
    contagem_motivo['ângulo_inicial'] = contagem_motivo['fração'].cumsum() - contagem_motivo['fração']
    contagem_motivo['ângulo_final'] = contagem_motivo['fração'].cumsum()

    # Criar gráfico de pizza com marca arc
    pizza = alt.Chart(contagem_motivo).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field='fração', type='quantitative'),
        color=alt.Color(field='motivo_da_desistência', type='nominal', legend=alt.Legend(title="Motivo da Desistência")),
        tooltip=[
            alt.Tooltip('motivo_da_desistência:N', title='Motivo'),
            alt.Tooltip('quantidade:Q', title='Quantidade'),
            alt.Tooltip('fração:Q', title='Percentual', format='.2%')
        ]
    ).properties(
        width=400,
        height=400,
        title='Gráfico dos motivos de desistência'
    ).configure_title(
        fontSize=24,
        fontWeight='bold',
        anchor='start'
    )

    # Espaço com margin-top para o gráfico
    st.markdown(
        """
        <div style="margin-top: 15px;">
        """,
        unsafe_allow_html=True
    )

    st.altair_chart(pizza, use_container_width=True)

    # Disposição em colunas para tabela e expanders ao lado, com títulos estilizados
    col1, col2 = st.columns([2.5, 2])

    # Preparar os dados para o gráfico e a tabela
    contagem_motivo = df['motivo_da_desistência'].value_counts().reset_index()
    contagem_motivo.columns = ['motivo_da_desistência', 'quantidade']

    with col1:
        st.markdown('<span style="font-size: 24px;"><b>Tabela dos Motivos de Desistência</b></span>', unsafe_allow_html=True)

        df_tabela_motivo = contagem_motivo.rename(columns={
            'motivo_da_desistência': 'Motivo da Desistência',
            'quantidade': 'Quantidade'
        })

        df_tabela_motivo.index = range(1, len(df_tabela_motivo) + 1)

        st.dataframe(df_tabela_motivo, use_container_width=True)

    with col2:
        st.markdown('<span style="font-size: 24px;"><b>Insights e Resultados</b></span>', unsafe_allow_html=True)
        with st.expander("🔎Insights obtidos", expanded=False):
            st.markdown("""
            A análise das origens dos alunos desistentes indica que a maior parte das desistências vem de indicações de amigos e familiares, com **256 casos**, seguida pelo LinkedIn (**146 desistências**) e grupos ou organizações das quais os alunos participam (**118 desistências**).

            Esses dados sugerem que, apesar da força do marketing boca a boca e redes sociais profissionais, há uma concentração de desistências vindo desses canais que merecem atenção especial.

            O LinkedIn, como plataforma profissional, pode ser uma boa fonte de captação, mas a taxa de desistência relativamente alta indica que talvez a expectativa dos alunos captados por lá não esteja alinhada com o conteúdo ou formato do curso.

            A presença de desistências vindas de canais digitais de busca (**Google, Bing, etc.**) e e-mail marketing da Escola da Nuvem reforça a necessidade de revisar a comunicação e o processo de onboarding para esses alunos.

            Observa-se ainda desistências de origens variadas, como eventos online, redes sociais e parceiros institucionais, indicando que múltiplos pontos de contato precisam de acompanhamento.

            **Recomendações:**
            - **Aprimorar o alinhamento de expectativa**: Garantir que a comunicação inicial, especialmente via LinkedIn e indicações, seja clara sobre o formato, conteúdo e compromissos do curso.
            - **Fortalecer o suporte inicial e acompanhamento personalizado** para alunos vindos das fontes com maiores desistências, focando em entender e mitigar causas comuns de evasão.
            - **Investir em estratégias de engajamento e retenção específicas para canais digitais**, com materiais educativos, tutoria e suporte técnico.
            - **Realizar pesquisas qualitativas com alunos desistentes de cada origem** para identificar problemas específicos e ajustar a estratégia de marketing e retenção.
            - **Potencializar parcerias e eventos online**, garantindo que a mensagem e as expectativas sejam alinhadas para reduzir desistências.
            """)

        with st.expander("📈 Gráfico das desistências por motivo e faixa de renda", expanded=False):
            st.markdown("""<div style="max-height: 450px; overflow-y: auto;">""", unsafe_allow_html=True)

            # Filtrar faixas de renda específicas
            faixas_renda_desejadas = ['Até R$1.000', 'R$1.001 - R$2.000', 'R$2.001 - R$4.000', 'Acima de R$4.000']
            df_filtered = df[df['faixa_renda_familiar'].isin(faixas_renda_desejadas)]

            # Agrupar por motivo e faixa de renda, contar desistências
            heatmap_data = (
                df_filtered
                .groupby(['motivo_da_desistência', 'faixa_renda_familiar'])
                .size()
                .reset_index(name='quantidade')
            )

            # Pivotar para matriz
            heatmap_pivot = heatmap_data.pivot(index='faixa_renda_familiar', columns='motivo_da_desistência', values='quantidade').fillna(0)

            # Transformar para formato longo
            heatmap_long = heatmap_pivot.reset_index().melt(id_vars='faixa_renda_familiar', var_name='Motivo da Desistência', value_name='Quantidade')

            # Gráfico heatmap Altair
            heatmap_chart = alt.Chart(heatmap_long).mark_rect().encode(
                x=alt.X('Motivo da Desistência:N', title=None, axis=alt.Axis(labels=False, ticks=False)),  # Remove rótulos e ticks do eixo X
                y=alt.Y('faixa_renda_familiar:N', title=None, axis=alt.Axis(labels=False, ticks=False)),  # Remove rótulos e ticks do eixo Y
                color=alt.Color('Quantidade:Q', scale=alt.Scale(scheme='blues'), title='Quantidade de Desistências'),
                tooltip=[
                    alt.Tooltip('faixa_renda_familiar:N', title='Faixa de Renda Familiar'),
                    alt.Tooltip('Motivo da Desistência:N', title='Motivo'),
                    alt.Tooltip('Quantidade:Q', title='Quantidade')
                ]
            ).properties(
                width=700,
                height=300,
                title='Heatmap das Desistências por Motivo e Faixa de Renda'
            ).configure_title(
                fontSize=18,
                fontWeight='bold',
                anchor='start'
            )

            st.altair_chart(heatmap_chart, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    #--------------- GRÁFICO 5 ---------------#

    # Garantir que a coluna de data está no formato datetime
    df['data_de_desistência_do_curso'] = pd.to_datetime(df['data_de_desistência_do_curso'], errors='coerce')
    df['ano'] = df['data_de_desistência_do_curso'].dt.year
    df['mes'] = df['data_de_desistência_do_curso'].dt.month

    # Agrupar os dados
    grouped = df.groupby(['ano', 'mes', 'motivo_da_desistência']).size().reset_index(name='quantidade')
    monthly_dismissals = grouped.groupby(['ano', 'mes']).agg({'quantidade': 'sum'}).reset_index()

    # Filtrar para quantidades acima de 25
    filtered_monthly_dismissals = monthly_dismissals[monthly_dismissals['quantidade'] > 25]

    # Corrigir colunas para criar a data
    filtered_monthly_dismissals['data'] = pd.to_datetime(
        filtered_monthly_dismissals.rename(columns={'ano': 'year', 'mes': 'month'})[['year', 'month']].assign(day=1)
    )

    # Criar coluna mes/ano no formato 'Jan/2023'
    filtered_monthly_dismissals['mes_ano'] = filtered_monthly_dismissals['data'].dt.strftime('%b/%Y')

    # Encontrar os dois maiores picos
    top2 = filtered_monthly_dismissals.nlargest(2, 'quantidade')

    # Marcar se é um dos maiores picos
    filtered_monthly_dismissals['is_top'] = filtered_monthly_dismissals['data'].isin(top2['data'])

    # Criar gráfico de linha com Altair
    linha = alt.Chart(filtered_monthly_dismissals).mark_line(point=True).encode(
        x=alt.X('mes_ano:N', title='Mês/Ano', sort=None),
        y=alt.Y('quantidade:Q', title='Quantidade de Desistências'),
        tooltip=[
            alt.Tooltip('mes_ano:N', title='Mês/Ano'),
            alt.Tooltip('quantidade:Q', title='Quantidade')
        ]
    ).properties(
        width=600,
        height=400,
        title='Gráfico de desistências por período do ano'
    )

    # Configurações adicionais do gráfico
    grafico = linha.configure_axis(
        labelAngle=-45
    ).configure_title(
        fontSize=24,
        anchor='start',
        fontWeight='bold'
    ).configure_view(
        strokeWidth=0
    )

    # Espaço com margin-top para o gráfico
    st.markdown(
        """
        <div style="margin-top: 15px;">
        """,
        unsafe_allow_html=True
    )

    # Exibir no Streamlit
    st.altair_chart(grafico, use_container_width=True)

    # Disposição em colunas para tabela e expanders ao lado, com títulos estilizados
    col1, col2 = st.columns([2.5, 2])

    with col1:
        st.markdown('<span style="font-size: 24px;"><b>Tabela de desistências por período do ano</b></span>', unsafe_allow_html=True)

        # Selecionar colunas relevantes
        tabela = filtered_monthly_dismissals[['mes_ano', 'quantidade']].copy()

        # Renomear colunas para exibição
        tabela = tabela.rename(columns={
            'mes_ano': 'Mês/Ano',
            'quantidade': 'Quantidade de Desistências'
        })

        # Exibir a tabela dentro do col1, logo abaixo do markdown
        st.dataframe(tabela, use_container_width=True)

    with col2:
        st.markdown('<span style="font-size: 24px;"><b>Insights e Resultados</b></span>', unsafe_allow_html=True)
        with st.expander("🔎Insights obtidos", expanded=False):
            st.markdown("""
            A análise das origens dos alunos desistentes indica que a maior parte das desistências vem de indicações de amigos e familiares, com **256 casos**, seguida pelo LinkedIn (**146 desistências**) e grupos ou organizações das quais os alunos participam (**118 desistências**).

            Esses dados sugerem que, apesar da força do marketing boca a boca e redes sociais profissionais, há uma concentração de desistências vindo desses canais que merecem atenção especial.

            O LinkedIn, como plataforma profissional, pode ser uma boa fonte de captação, mas a taxa de desistência relativamente alta indica que talvez a expectativa dos alunos captados por lá não esteja alinhada com o conteúdo ou formato do curso.

            A presença de desistências vindas de canais digitais de busca (**Google, Bing, etc.**) e e-mail marketing da Escola da Nuvem reforça a necessidade de revisar a comunicação e o processo de onboarding para esses alunos.

            Observa-se ainda desistências de origens variadas, como eventos online, redes sociais e parceiros institucionais, indicando que múltiplos pontos de contato precisam de acompanhamento.

            ### 📈 Padrões e tendências identificadas:
            - **Outubro** foi o mês com maior número de desistências nos dois anos analisados (**76 em 2023** e **40 em 2024**), indicando um padrão sazonal relevante.
            - O volume de desistências tende a **crescer no segundo semestre**, especialmente entre **junho e novembro**.
            - Houve uma **redução gradual** nas desistências de junho e julho de 2023 para os mesmos meses de 2024 (de **33 para 26** em junho e **48 para 29** em julho), o que pode indicar efeitos positivos de ajustes recentes.
            - A **queda entre setembro e fevereiro** sugere que as festas de fim de ano e férias podem impactar tanto no número de novas inscrições quanto na evasão.

            ### ✅ Recomendações específicas:
            - **Antecipar ações de retenção** entre agosto e novembro: aplicar mentorias, eventos motivacionais e reforço na comunicação personalizada.
            - **Revisar a abordagem de onboarding** para alunos oriundos de LinkedIn e indicações, com foco em alinhar expectativas.
            - **Criar estratégias específicas para outubro**, mês que historicamente apresenta os maiores índices de desistência.
            - **Acompanhar qualitativamente os motivos de desistência** via pesquisas rápidas, especialmente nos meses críticos.
            - **Potencializar o suporte inicial** para reduzir a evasão já nos primeiros meses de participação, especialmente após picos anteriores.

            ### 🎯 Plano tático para outubro:
            - Realizar webinars com ex-alunos bem-sucedidos.
            - Reforçar conteúdos sobre gestão de tempo e compromisso.
            - Implementar campanhas motivacionais e de conscientização sobre a importância de concluir o curso.

            """)

        with st.expander("📈 Gráfico das desistências por período do ano e motivo", expanded=False):
            st.markdown("""<div style="max-height: 450px; overflow-y: auto;">""", unsafe_allow_html=True)

            # Garantir que a coluna de data é datetime
            df['data_de_desistência_do_curso'] = pd.to_datetime(df['data_de_desistência_do_curso'], errors='coerce')

            # Filtrar linhas com data válida e motivo não nulo
            df_filtered = df.dropna(subset=['data_de_desistência_do_curso', 'motivo_da_desistência'])

            # Criar coluna 'ano_mes' com formato "YYYY-MM"
            df_filtered['ano_mes'] = df_filtered['data_de_desistência_do_curso'].dt.to_period('M').astype(str)

            # Agrupar por ano_mes e motivo da desistência, contando quantidade
            desistencias_por_motivo_mes = (
                df_filtered
                .groupby(['ano_mes', 'motivo_da_desistência'])
                .size()
                .reset_index(name='quantidade')
            )

            # Ordenar pelo período para garantir sequência correta
            desistencias_por_motivo_mes = desistencias_por_motivo_mes.sort_values('ano_mes')

            # Gráfico de barras empilhadas Altair
            stacked_bar = alt.Chart(desistencias_por_motivo_mes).mark_bar().encode(
                x=alt.X('ano_mes:T', title='Mês/Ano'),
                y=alt.Y('quantidade:Q', title='Quantidade de Desistências'),
                color=alt.Color('motivo_da_desistência:N', title='Motivo da Desistência'),
                tooltip=[
                    alt.Tooltip('ano_mes:T', title='Mês/Ano'),
                    alt.Tooltip('motivo_da_desistência:N', title='Motivo da Desistência'),
                    alt.Tooltip('quantidade:Q', title='Quantidade')
                ]
            ).properties(
                width=700,
                height=400,
                title='Desistências por Motivo ao longo do Tempo (Mês/Ano)'
            ).configure_title(
                fontSize=18,
                fontWeight='bold',
                anchor='start'
            )

            st.altair_chart(stacked_bar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# Mapeamento das páginas
page_names_to_funcs = {
    "—": intro,
    "Desistências": desistencias
}

# Sidebar com logo
try:
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, width=100)
except Exception:
    st.sidebar.warning("Logo não pôde ser carregada.")

st.sidebar.markdown("""
**Bem-vindo ao Projeto Extensor**  
Escolha uma visualização para explorar os dados de desistências da Escola da Nuvem.
""")

# Selectbox com controle de estado
selected = st.sidebar.selectbox(
    "Escolha uma visualização",
    options=page_names_to_funcs.keys(),
    index=list(page_names_to_funcs.keys()).index(st.session_state.page)
)
if selected != st.session_state.page:
    st.session_state.page = selected
    st.rerun()

# Renderizar página atual
page_names_to_funcs[st.session_state.page]()