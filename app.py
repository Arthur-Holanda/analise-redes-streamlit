
import streamlit as st
import networkx as nx
import pandas as pd
from pyvis.network import Network
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
import os
import urllib.request # Biblioteca para fazer o download

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
""")

# --- ALTERAÇÃO PRINCIPAL AQUI ---
@st.cache_data
def carregar_grafo():
    """
    Carrega o grafo da rede de futebol.
    Como a função `football_graph` foi removida do networkx 3.x,
    este código baixa o arquivo de dados GML e o carrega.
    """
    # URL para o arquivo de dados oficial do grafo de futebol
    url = "https://github.com/networkx/networkx/raw/main/examples/data/football.gml"
    
    # Nome do arquivo que será salvo no ambiente do Colab
    file_path = "football.gml"
    
    # Baixa o arquivo da URL se ele ainda não existir no ambiente.
    # O decorator @st.cache_data garante que isso só aconteça uma vez por sessão.
    if not os.path.exists(file_path):
        st.info(f"Baixando o dataset de {url}...")
        urllib.request.urlretrieve(url, file_path)
        st.info("Download concluído.")

    # Carrega o grafo a partir do arquivo GML baixado
    # A opção label='id' garante que os nós sejam lidos como inteiros, o que é importante para este grafo.
    G = nx.read_gml(file_path, label='id')
    
    return G

# --- FIM DA ALTERAÇÃO ---

G_original = carregar_grafo()

st.sidebar.title("Opções de Visualização")
st.sidebar.markdown("Ajuste os parâmetros da rede e das análises.")

subset_escolha = st.sidebar.selectbox(
    "Selecione um subconjunto do grafo:",
    ("Grafo Completo", "Maior Componente Conectado")
)

if subset_escolha == "Maior Componente Conectado":
    # Garante que os componentes são para grafos não-dirigidos
    if nx.is_directed(G_original):
        componentes_gen = nx.weakly_connected_components(G_original)
    else:
        componentes_gen = nx.connected_components(G_original)
    
    componentes = list(componentes_gen)
    if componentes:
        maior_componente = max(componentes, key=len)
        G = G_original.subgraph(maior_componente)
    else:
        G = G_original
else:
    G = G_original

st.sidebar.info(f"O grafo selecionado possui **{G.number_of_nodes()}** nós e **{G.number_of_edges()}** arestas.")

st.header("1. Visualização Interativa da Rede")

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

st.header("2. Métricas Estruturais da Rede")
st.markdown("Análises que descrevem a estrutura geral do grafo.")

col1, col2, col3 = st.columns(3)
with col1:
    densidade = nx.density(G)
    st.metric(label="Densidade da Rede", value=f"{densidade:.4f}")
    st.markdown("**Significado:** Proporção de arestas existentes em relação ao número máximo de arestas possíveis.")
with col2:
    clustering_global = nx.transitivity(G)
    st.metric(label="Coeficiente de Clustering Global", value=f"{clustering_global:.4f}")
    st.markdown("**Significado:** Mede a tendência dos nós em um grafo de se agruparem.")
with col3:
    assortatividade = nx.degree_assortativity_coefficient(G)
    st.metric(label="Assortatividade de Grau", value=f"{assortatividade:.4f}")
    st.markdown("**Significado:** Preferência de nós se conectarem a outros de grau similar.")

if G.is_directed():
    num_scc = nx.number_strongly_connected_components(G)
    st.metric(label="Componentes Fortemente Conectados", value=num_scc)
    st.markdown("**Significado (Grafo Dirigido):** Número de subgrafos onde cada nó alcança qualquer outro no mesmo subgrafo.")
else:
    num_wcc = nx.number_connected_components(G)
    st.metric(label="Componentes Conectados", value=num_wcc)
    st.markdown("**Significado (Grafo Não-Dirigido):** Número de 'ilhas' ou subgrafos desconectados entre si.")

st.header("3. Distribuição de Grau dos Nós")

def plotar_distribuicao_grau(G):
    graus = [d for n, d in G.degree()]
    fig, ax = plt.subplots()
    ax.hist(graus, bins='auto', color='skyblue', alpha=0.7, rwidth=0.85)
    ax.set_title("Histograma da Distribuição de Grau")
    ax.set_xlabel("Grau")
    ax.set_ylabel("Frequência")
    st.pyplot(fig)
    st.markdown("**Significado:** Mostra quantos nós possuem um certo número de conexões.")

plotar_distribuicao_grau(G)

st.header("4. Análise de Centralidade")
st.markdown("Métricas que identificam os nós mais 'importantes' da rede.")

top_k = st.sidebar.slider("Selecione o número de Top-K nós para exibir:", 5, min(15, G.number_of_nodes()), 10)

tab1, tab2, tab3, tab4 = st.tabs(["Degree", "Closeness", "Betweenness", "Eigenvector"])

def exibir_ranking_centralidade(centralidade, nome_metrica):
    # Converte os nós para string para garantir a ordenação correta e exibição
    centralidade_str_keys = {str(k): v for k, v in centralidade.items()}
    df = pd.DataFrame(centralidade_str_keys.items(), columns=['Nó', 'Centralidade'])
    df_sorted = df.sort_values(by='Centralidade', ascending=False).head(top_k)
    st.dataframe(df_sorted.reset_index(drop=True), use_container_width=True)

with tab1:
    st.subheader("Degree Centrality")
    st.markdown("**Mede:** A popularidade de um nó (número de conexões).")
    degree_centrality = nx.degree_centrality(G)
    exibir_ranking_centralidade(degree_centrality, "Degree Centrality")

with tab2:
    st.subheader("Closeness Centrality")
    st.markdown("**Mede:** A eficiência de um nó em alcançar todos os outros.")
    closeness_centrality = nx.closeness_centrality(G)
    exibir_ranking_centralidade(closeness_centrality, "Closeness Centrality")

with tab3:
    st.subheader("Betweenness Centrality")
    st.markdown("**Mede:** A frequência com que um nó atua como 'ponte' entre outros.")
    betweenness_centrality = nx.betweenness_centrality(G)
    exibir_ranking_centralidade(betweenness_centrality, "Betweenness Centrality")

with tab4:
    st.subheader("Eigenvector Centrality")
    st.markdown("**Mede:** A influência de um nó, considerando a importância de seus vizinhos.")
    try:
        eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=1000, tol=1.0e-6, nstart=None, weight=None)
        exibir_ranking_centralidade(eigenvector_centrality, "Eigenvector Centrality")
    except nx.PowerIterationFailedConvergence:
        st.warning("O cálculo de Eigenvector Centrality não convergiu.")

