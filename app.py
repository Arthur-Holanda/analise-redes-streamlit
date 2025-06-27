
import streamlit as st
import networkx as nx
import pandas as pd
from pyvis.network import Network
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import os
import urllib.request
import zipfile

# --- Configuração da Página ---
st.set_page_config(
    page_title="Análise de Redes Complexas",
    page_icon="🕸️",
    layout="wide",
)

st.title("🕸️ Análise Interativa de Redes Complexas")
st.markdown("""
Esta aplicação utiliza `Streamlit` e `Pyvis` para visualizar e analisar grafos de redes complexas.
Explore as métricas estruturais, a distribuição de grau e a centralidade dos nós.
Dataset: [Football](https://public.websites.umich.edu/~mejn/netdata/)
Aluno: Arthur Holanda
""")

# --- FUNÇÃO DE CARREGAMENTO DO GRAFO ---
@st.cache_data
def carregar_grafo():
    """
    Carrega o grafo da rede de futebol a partir de uma fonte estável.
    O arquivo original está em formato .zip, então ele é baixado e descompactado.
    """
    url = "http://www-personal.umich.edu/~mejn/netdata/football.zip"
    zip_path = "football.zip"
    gml_path = "football.gml"

    if not os.path.exists(gml_path):
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extract(gml_path)
        os.remove(zip_path)

    G = nx.read_gml(gml_path, label='id')
    return G

# --- LÓGICA DA BARRA LATERAL (SIDEBAR) E FILTRAGEM ---
G_original = carregar_grafo()

st.sidebar.title("Opções de Visualização")
st.sidebar.markdown("Selecione um subconjunto do grafo para análise.")

# Opção para escolher o tipo de subconjunto
subset_escolha = st.sidebar.selectbox(
    "Selecione um tipo de filtro:",
    ("Grafo Completo", "Maior Componente Conectado", "Subgrafo de Alto Grau")
)

# Lógica de filtragem
if subset_escolha == "Maior Componente Conectado":
    # Lida com grafos dirigidos e não-dirigidos
    if G_original.is_directed():
        componentes = list(nx.weakly_connected_components(G_original))
    else:
        componentes = list(nx.connected_components(G_original))
    
    if componentes:
        maior_componente = max(componentes, key=len)
        G = G_original.subgraph(maior_componente).copy() # Usar .copy() para evitar "view"
    else:
        G = G_original.copy()
elif subset_escolha == "Subgrafo de Alto Grau":
    min_grau = st.sidebar.slider("Selecione o grau mínimo:", 0, 50, 10)
    nos_alto_grau = [n for n, d in G_original.degree() if d >= min_grau]
    G = G_original.subgraph(nos_alto_grau).copy()
else:
    G = G_original.copy()

st.sidebar.info(f"O grafo em análise possui **{G.number_of_nodes()}** nós e **{G.number_of_edges()}** arestas.")


# --- 1. VISUALIZAÇÃO DA REDE ---
st.header("1. Visualização Interativa da Rede")
if G.number_of_nodes() > 0:
    def visualizar_rede_pyvis(G):
        net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white", notebook=True, directed=nx.is_directed(G))
        net.from_nx(G)
        net.show_buttons(filter_=['physics'])

        file_path = "pyvis_graph.html"
        net.save_graph(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        components.html(source_code, height=650)
        os.remove(file_path)

    visualizar_rede_pyvis(G)
else:
    st.warning("O subgrafo selecionado não possui nós. Por favor, ajuste os filtros.")


# --- 2. MÉTRICAS ESTRUTURAIS ---
st.header("2. Métricas Estruturais da Rede")
if G.number_of_nodes() > 0:
    st.markdown("Análises que descrevem a estrutura geral do grafo.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        densidade = nx.density(G)
        st.metric(label="Densidade da Rede", value=f"{densidade:.4f}")
        st.markdown("**Significado:** Proporção de arestas existentes em relação ao máximo possível.")
    with col2:
        clustering_global = nx.transitivity(G)
        st.metric(label="Coeficiente de Clustering Global", value=f"{clustering_global:.4f}")
        st.markdown("**Significado:** Mede a tendência dos nós de se agruparem em triângulos.")
    with col3:
        assortatividade = nx.degree_assortativity_coefficient(G)
        st.metric(label="Assortatividade de Grau", value=f"{assortatividade:.4f}")
        st.markdown("**Significado:** Preferência de nós se conectarem a outros de grau similar.")

    # Lógica aprimorada para Componentes
    if G.is_directed():
        num_wcc = nx.number_weakly_connected_components(G)
        st.metric(label="Componentes Fracamente Conectados", value=num_wcc)
        st.markdown("**Significado:** Número de 'ilhas' ignorando a direção das arestas.")

        num_scc = nx.number_strongly_connected_components(G)
        st.metric(label="Componentes Fortemente Conectados", value=num_scc)
        st.markdown("**Significado:** Número de subgrafos onde cada nó alcança qualquer outro.")
    else:
        num_cc = nx.number_connected_components(G)
        st.metric(label="Componentes Conectados", value=num_cc)
        st.markdown("**Significado:** Número de 'ilhas' ou subgrafos desconectados entre si.")
else:
    st.info("Não há nós no grafo selecionado para calcular métricas.")

# --- 3. DISTRIBUIÇÃO DE GRAU ---
st.header("3. Distribuição de Grau dos Nós")
if G.number_of_nodes() > 0:
    def plotar_distribuicao_grau(G):
        if G.is_directed():
            in_degrees = [d for n, d in G.in_degree()]
            out_degrees = [d for n, d in G.out_degree()]
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            ax1.hist(in_degrees, bins='auto', color='skyblue', alpha=0.7, rwidth=0.85)
            ax1.set_title("Distribuição de Grau de Entrada (In-Degree)")
            ax1.set_xlabel("Grau de Entrada")
            ax1.set_ylabel("Frequência")
            
            ax2.hist(out_degrees, bins='auto', color='salmon', alpha=0.7, rwidth=0.85)
            ax2.set_title("Distribuição de Grau de Saída (Out-Degree)")
            ax2.set_xlabel("Grau de Saída")
            ax2.set_ylabel("Frequência")
            
            st.pyplot(fig)
            st.markdown("**Significado:** Para grafos dirigidos, analisamos as conexões que **chegam** (in-degree) e que **saem** (out-degree) de cada nó.")

        else:
            graus = [d for n, d in G.degree()]
            fig, ax = plt.subplots()
            ax.hist(graus, bins='auto', color='skyblue', alpha=0.7, rwidth=0.85)
            ax.set_title("Histograma da Distribuição de Grau Total")
            ax.set_xlabel("Grau")
            ax.set_ylabel("Frequência")
            st.pyplot(fig)
            st.markdown("**Significado:** Mostra quantos nós possuem um certo número de conexões.")

    plotar_distribuicao_grau(G)
else:
    st.info("Não há nós no grafo selecionado para plotar a distribuição de grau.")

# --- 4. ANÁLISE DE CENTRALIDADE ---
st.header("4. Análise de Centralidade")
if G.number_of_nodes() > 0:
    st.markdown("Métricas que identificam os nós mais 'importantes' da rede. Use o slider para definir quantos nós exibir no ranking.")
    
    # Slider de Top-K reintroduzido na área principal
    top_k = st.slider("Selecione o número de Top-K nós para exibir no ranking:", 5, min(20, G.number_of_nodes()), 10)

    tab1, tab2, tab3, tab4 = st.tabs(["Degree", "Closeness", "Betweenness", "Eigenvector"])
    
    # --- FUNÇÃO ATUALIZADA PARA MOSTRAR NOME DO TIME ---
    def exibir_ranking_centralidade(G, centralidade):
        # Cria uma lista de dicionários para construir o DataFrame
        dados_ranking = []
        for node_id, centr_value in centralidade.items():
            # Acessa o atributo 'label' do nó, que contém o nome do time
            # Usa .get() para segurança, caso o atributo não exista
            nome_time = G.nodes[node_id].get('label', str(node_id))
            dados_ranking.append({
                'Time': nome_time,
                'Nó ID': node_id,
                'Centralidade': centr_value
            })

        df = pd.DataFrame(dados_ranking)
        
        # Ordena o DataFrame pela centralidade
        df_sorted = df.sort_values(by='Centralidade', ascending=False).head(top_k)
        
        # Formata e exibe o DataFrame
        df_sorted['Centralidade'] = df_sorted['Centralidade'].round(4)
        df_display = df_sorted[['Time', 'Nó ID', 'Centralidade']]
        st.dataframe(df_display.reset_index(drop=True), use_container_width=True)

    with tab1:
        st.subheader("Degree Centrality")
        st.markdown("**Mede:** A popularidade de um nó (número de conexões).")
        degree_centrality = nx.degree_centrality(G)
        exibir_ranking_centralidade(G, degree_centrality)

    with tab2:
        st.subheader("Closeness Centrality")
        st.markdown("**Mede:** A eficiência de um nó em alcançar todos os outros.")
        closeness_centrality = nx.closeness_centrality(G)
        exibir_ranking_centralidade(G, closeness_centrality)

    with tab3:
        st.subheader("Betweenness Centrality")
        st.markdown("**Mede:** A frequência com que um nó atua como 'ponte' entre outros.")
        betweenness_centrality = nx.betweenness_centrality(G)
        exibir_ranking_centralidade(G, betweenness_centrality)

    with tab4:
        st.subheader("Eigenvector Centrality")
        st.markdown("**Mede:** A influência de um nó, considerando a importância de seus vizinhos.")
        try:
            eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=1000, tol=1.0e-6)
            exibir_ranking_centralidade(G, eigenvector_centrality)
        except (nx.PowerIterationFailedConvergence, nx.NetworkXError):
            st.warning("O cálculo de Eigenvector Centrality não convergiu ou não é aplicável a este subgrafo.")
else:
    st.info("Não há nós no grafo selecionado para calcular as centralidades.")
