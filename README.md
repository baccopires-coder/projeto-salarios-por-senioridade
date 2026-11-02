# 📊 Quanto vale uma carreira em dados?

**Salários por área, região e senioridade no Brasil (State of Data 2025-2026)**

Dashboard interativo em Streamlit que explora a remuneração de profissionais de dados no Brasil é um Projeto desenvolvido no programa **Códigos do Amanhã 2026** (Ebanx em parceria com a How Bootcamps). A partir dos microdados da pesquisa **State of Data Brazil 2025-2026**. 

🔗 **App publicado:** `https://projeto-salarios-por-senioridade-sjpzwqwtfs4vujbg7o9pgx.streamlit.app/`

---

## 🎯 Sobre o projeto

### Problema

> Como a remuneração de profissionais de dados no Brasil varia conforme a área de atuação, a região e a senioridade? Qual desses três fatores pesa mais?

### Perguntas norteadoras

1. Qual é a distribuição de faixas salariais para cada cargo e nível (Júnior, Pleno, Sênior, Especialista/Staff+ e Gestão)?
2. A região onde a pessoa mora altera o salário típico, ou apenas a chance de chegar às faixas mais altas?
3. No mesmo nível, quanto os cargos de análise/BI se distanciam dos cargos de ciência, engenharia de dados e ML?

### Para quem é

- **Principal:** pessoas em início ou transição de carreira em dados, que precisam decidir qual trilha estudar (análise/BI, ciência ou engenharia de dados), que expectativa salarial ter em cada fase e se vale buscar vagas fora da sua região.
- **Secundário:** programas de formação e mentoria, e profissionais de RH, que ganham uma referência pública de faixas por cargo e nível.

---

## 🧪 Hipóteses de trabalho

As hipóteses abaixo vêm de uma análise exploratória inicial (faixa salarial convertida no ponto médio) e **ainda não são resultados**. Serão testadas empiricamente.

| # | Hipótese | Indício exploratório |
|---|----------|----------------------|
| H1 | A senioridade explica mais diferença salarial do que a região. | Mediana de R$ 5.000 (Júnior), R$ 7.000 (Pleno), R$ 10.000 (Sênior) e R$ 18.000 (Especialista/Staff+ e Gestão), contra R$ 10.000 em todas as regiões. |
| H2 | No mesmo nível, cargos de ciência, engenharia de dados e ML pagam mais do que cargos de análise/BI. | Entre Seniores, mediana de R$ 10.000 para Analista de Dados e de BI e R$ 14.000 para Cientista e Engenheiro de Dados. |
| H3 | A vantagem do Sudeste aparece na cauda de salários altos, não no salário típico. | Média do Sudeste de cerca de R$ 13.400, contra R$ 10.400 a R$ 11.700 nas demais regiões, com medianas iguais. |

---

## 🖥️ O que o dashboard mostra

**Filtros (barra lateral):** região, senioridade, tipo de contrato e porte da empresa. Sem nenhuma seleção, todos os valores são considerados.

**Métricas gerais:** salário médio, quantidade de dados analisados, total de respondentes e cargo mais frequente.

**Gráficos:**

- Top 10 cargos por salário médio
- Distribuição por faixa salarial
- Proporção por modelo de trabalho
- Mapa do Brasil com salário médio por estado
- Salário médio por senioridade
- Salário médio por tempo de experiência em dados

**Tabela** com os dados detalhados após os filtros.

---

## 🔧 Tratamento dos dados

Principais decisões aplicadas no `app.py`:

- **Somente quem vive no Brasil** (`1.g_vive_no_brasil == 1`).
- **Remoção de respondentes sem faixa salarial.**
- **Salário em faixas:** a pesquisa informa intervalos mensais, não valores exatos. Para calcular médias, usa-se o **ponto médio** de cada faixa (por exemplo, R$ 8.001 a R$ 12.000 vira R$ 10.000; "Acima de R$ 40.001" vira R$ 45.000). Isso é uma estimativa.
- **Correção de erros de digitação na base**, como uma faixa salarial escrita de forma inconsistente e uma faixa de número de funcionários com valor trocado.
- **Porte da empresa** agrupado por número de funcionários: Micro (1–10), Pequena (11–50), Média (51–100) e Grande (acima de 100). É uma aproximação da classificação do SEBRAE, ajustada às faixas da pesquisa.
- **Modelo de trabalho** com os rótulos simplificados.
- **Mínimo de 10 respondentes** por grupo para exibir o salário médio por cargo e por estado.

---

## 🛠️ Tecnologias

- Python
- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Plotly](https://plotly.com/python/)

---

## 📁 Estrutura do repositório

```
salarios_por_senioridade/
├── app.py                 # aplicação Streamlit
├── requirements.txt       # dependências
├── README.md
├── .gitignore
└── dados/
    ├── final dataset - state of data 2025-2026 - kaggle.csv
    └── brasil_estados.geojson   # opcional: se ausente, é baixado da internet
```

---

## ▶️ Como rodar localmente

1. Clone o repositório:

   ```bash
   git clone https://github.com/SEU-USUARIO/salarios_por_senioridade.git
   cd salarios_por_senioridade
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   # Linux/macOS
   source .venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Garanta que o dataset esteja em `dados/` com o nome `final dataset - state of data 2025-2026 - kaggle.csv`. Ele pode ser baixado no [Kaggle](https://www.kaggle.com/datasets/datahackers/state-of-data-brazil-2025-2026/data).

5. Execute o app:

   ```bash
   streamlit run app.py
   ```

O app abre em `http://localhost:8501`.

> O app usa recursos recentes do Streamlit (`st.pills` e `width="stretch"` nos gráficos). Se der erro, atualize com `pip install --upgrade streamlit`.

---

## ⚠️ Limitações

- **Salário em faixas, não em valor exato.** As medianas ficam em degraus e os extremos exigem suposições.
- **Viés de amostragem.** A pesquisa é voluntária e autodeclarada, então não representa todo o mercado. O Sudeste concentra cerca de 62% das respostas, e o Norte tem poucas.
- **Células pequenas nos cruzamentos.** Ao cruzar cargo, nível e região, muitos grupos ficam com poucas respostas.
- **Dados ausentes e estruturais.** Parte dos respondentes não informou salário, e gestores não têm cargo e nível preenchidos.
- **Vínculos pouco comparáveis.** CLT, PJ, servidor público, estagiário e trabalho remoto para o exterior têm lógicas salariais distintas.
- **Defasagem temporal.** Os valores se referem ao fim de 2025 e não devem ser lidos como o mercado atual sem ressalvas.

---

## 🔒 Ética e privacidade (LGPD)

- Os microdados são públicos e foram divulgados pela organizadora **sem campos de identificação direta**, como nome e e-mail. Mesmo assim, o risco de reidentificação é tratado como ponto de atenção.
- Atributos sensíveis presentes no arquivo (gênero, cor/raça e deficiência) **não fazem parte do escopo** e não são usados nos cruzamentos de salário.
- Não há tentativa de reidentificar respondentes nem de cruzar o dataset com outras bases pessoais.
- A fonte é citada em todos os produtos do projeto, e a licença do dataset deve ser respeitada.

---

## 👥 Equipe

- Bacco Pires
- Loredana Neves
- Andrea Hidalgo

Todos os integrantes trabalham em todas as etapas, e cada entrega é revisada por outra pessoa da equipe.

---

## 📚 Fontes e créditos

- **Dados:** [State of Data Brazil 2025-2026, Data Hackers (Kaggle)](https://www.kaggle.com/datasets/datahackers/state-of-data-brazil-2025-2026/data)
- **Divulgação dos microdados:** [Data Hackers News](https://www.datahackers.news/p/dados-da-pesquisa-state-of-data-liberados)
- **Relatório:** State of Data Brazil 2025/2026, Data Hackers + Bain & Company
- **Mapa dos estados:** GeoJSON do repositório [click_that_hood](https://github.com/codeforamerica/click_that_hood)

Os direitos sobre a pesquisa e seus dados pertencem aos seus autores (Data Hackers e Bain & Company). Este projeto é uma análise independente, feita para fins educacionais.
