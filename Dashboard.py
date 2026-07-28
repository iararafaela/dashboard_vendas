# IMPORTANDO AS BIBLIOTECAS

import streamlit as st
import requests
import pandas as pd
import plotly.express as px 

# CONFIGURAÇÕES DE LAYOUT

st.set_page_config(layout='wide')

# FUNÇÕES

## Criando a função formata número
def formata_numero (valor, prefixo = ''):
    for unidade in['','mil']:
        if valor <1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

# Adicionando um Título no App
st.title('DASHBOARD DE VENDAS 🛒')

# Leitura dos Dados pela API (método get)
url = 'http://labdados.com/produtos'

# FILTROS

## Filtro Região
regioes = ['Brasil','Centro-Oeste','Nordeste','Norte','Sudeste', 'Sul']

st.sidebar.title ('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

## Filtro Ano
todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider ('Ano', 2020,2023)

## Adaptações na URL após inclusão dos filtros
query_string = {'região': regiao.lower(), 'ano': ano}
response =requests.get(url, params= query_string)

# CARREGAMENTO DOS DADOS
## Transformando os dados de Request > Json > DataFrame
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

## Filtro Vendedores

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores: 
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]



# TABELAS

## TABELAS RECEITA

### Tabela de Receita por Estado
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset= 'Local da compra')[['Local da compra','lat','lon']].merge(receita_estados, left_on='Local da compra',right_index=True).sort_values('Preço', ascending=False)

### Tabela de Receita Mensal
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'ME'))['Preço'].sum().reset_index()
receita_mensal ['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal ['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

### Tabela de Receita por Categoria do Produto
receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

## TABELAS VENDAS

### Tabela de Vendas por Estado
vendas_estados = pd.DataFrame(dados.groupby('Local da compra')[['Preço']].count())
vendas_estados = dados.drop_duplicates(subset= 'Local da compra')[['Local da compra','lat','lon']].merge(vendas_estados, left_on='Local da compra',right_index=True).sort_values('Preço', ascending=False)

### Tabela de Vendas Mensal
vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'ME'))['Preço'].count().reset_index())
vendas_mensal ['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal ['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

### Tabela de Vendas por Categoria do Produto
vendas_categorias = pd.DataFrame(dados.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço', ascending=False))

## TABELAS VENDEDORES

### Tabela vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum','count']))

# GRÁFICOS

## GRÁFICOS RECEITA

### Gráfico de Mapas - Receita por Estados
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                   scope = 'south america',
                                    fitbounds = 'locations', 
                                    size = 'Preço',
                                     template = 'seaborn',
                                      hover_name = 'Local da compra',
                                        hover_data = {'lat': False, 'lon': False},
                                        title = 'Receita por estado')

### Gráfico de Linhas - Receita Mensal
fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers = True,
                             range_y = (0,receita_mensal.max()),
                             color = 'Ano',
                             line_dash= 'Ano',
                             title = 'Receita Mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

### Gráfico de Barras - Receita por Estados (Top 5)
fig_receita_estados = px.bar(receita_estados.head(),
                                                x='Local da compra',
                                                y = 'Preço',
                                                text_auto= True,
                                                title= 'Top estados')
fig_receita_estados.update_layout(yaxis_title = 'Receita')

### Grafico de Barras - Receita por Categorias de Produtos
fig_receita_categorias = px.bar(receita_categorias,
                                                text_auto= True,
                                                title= 'Receita por Categorias')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')

## GRÁFICOS VENDAS

### Gráfico de Mapas - Vendas por Estados
fig_mapa_vendas = px.scatter_geo(vendas_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                   scope = 'south america',
                                    size = 'Preço',
                                     fitbounds = 'locations', 
                                     template = 'seaborn',
                                      hover_name = 'Local da compra',
                                        hover_data = {'lat': False, 'lon': False},
                                        title = 'Vendas por estado')

### Gráfico de Linhas - Vendas Mensal
fig_vendas_mensal = px.line(receita_mensal,
                             x = 'Mes',
                             y = 'Preço',
                             markers = True,
                             range_y = (0,vendas_mensal.max()),
                             color = 'Ano',
                             line_dash= 'Ano',
                             title = 'Quantidade de Vendas Mensal')
fig_vendas_mensal.update_layout(yaxis_title = 'Quantidade de vendas')

### Grafico de Barras - Vendas por Estados (Top 5)
fig_vendas_estados = px.bar(vendas_estados.head(),
                                                x='Local da compra',
                                                y = 'Preço',
                                                text_auto= True,
                                                title= 'Top estados')
fig_vendas_estados.update_layout(yaxis_title = 'Quantidade de vendas')

### Grafico de Barras - Vendas por Categorias de Produtos
fig_vendas_categorias = px.bar(vendas_categorias,
                                                text_auto= True,
                                                title= 'Vendas por Categorias')
fig_vendas_categorias.update_layout(yaxis_title = 'Quantidade de vendas')


# VISUALIZAÇÃO NO STREAMLIT

## CONSTRUINDOO DASHBOARD

### Construindo as Abas (Páginas)
aba1, aba2, aba3 = st.tabs(['Receita','Quantidade de vendas', 'Vendedores'])

### Página 1                       
with aba1:
    coluna1,coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita',formata_numero(dados['Preço'].sum(),'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)

    with coluna2:
        st.metric('Quantidade de vendas',formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)

### Página 2                       
with aba2:
    coluna1,coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita',formata_numero(dados['Preço'].sum(),'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width=True)
        st.plotly_chart(fig_vendas_estados, use_container_width=True)

    with coluna2:
        st.metric('Quantidade de vendas',formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width=True)
        st.plotly_chart(fig_vendas_categorias, use_container_width=True)
    
### Página 3                       
with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores',2, 10, 5)
    coluna1,coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita',formata_numero(dados['Preço'].sum(),'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
                                        x='sum',
                                        y=vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title=f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)


    with coluna2:
        st.metric('Quantidade de vendas',formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                                        x='count',
                                        y=vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title=f'Top {qtd_vendedores} vendedores (quantidade de vendas)')

        st.plotly_chart(fig_vendas_vendedores)
   










