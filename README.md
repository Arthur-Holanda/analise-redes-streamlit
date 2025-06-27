
#  Análise Interativa de Redes Complexas

Este projeto é uma aplicação web interativa desenvolvida com Streamlit para a análise e visualização de redes complexas, como parte da Atividade Prática da Unidade 2.

**Link da Aplicação:** [Adicione o link da sua aplicação Streamlit Cloud aqui após o deploy]

##  Descrição

A aplicação carrega um dataset de rede (por padrão, a rede de jogos de futebol americano universitário dos EUA) e permite que o usuário explore suas propriedades de forma interativa. É uma ferramenta educacional para entender conceitos fundamentais da Análise de Redes Complexas.

##  Funcionalidades

A aplicação permite ao usuário:

* **Visualizar o grafo** de forma interativa usando a biblioteca Pyvis.
* **Selecionar subconjuntos do grafo**, como o maior componente conectado ou um subgrafo de nós com alto grau.
* **Analisar métricas estruturais** da rede, como densidade, assortatividade e clustering global.
* **Visualizar a distribuição de grau** dos nós em um histograma (com distinção entre grau de entrada/saída para grafos dirigidos).
* **Comparar os nós mais importantes** da rede segundo 4 métricas de centralidade diferentes (Degree, Closeness, Betweenness, Eigenvector).
* **Filtrar os rankings de centralidade** para exibir o "Top-K" nós de interesse.

##  Tecnologias Utilizadas

* **Python**
* **Streamlit** - Para a construção da interface web.
* **NetworkX** - Para a modelagem e análise do grafo.
* **Pandas** - Para a manipulação de dados.
* **Pyvis** - Para a visualização interativa da rede.
* **Matplotlib** - Para a geração de gráficos estáticos (histograma).

##  Como Executar Localmente

Para executar este projeto em sua máquina local, siga os passos abaixo:

1.  **Clone este repositório:**
    ```bash
    git clone [https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git](https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git)
    ```

2.  **Navegue até a pasta do projeto:**
    ```bash
    cd NOME-DO-SEU-REPOSITORIO
    ```

3.  **Crie um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    ```

4.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Execute a aplicação Streamlit:**
    ```bash
    streamlit run app.py
    ```

Abra seu navegador e acesse o endereço local fornecido pelo Streamlit (geralmente `http://localhost:8501`).
