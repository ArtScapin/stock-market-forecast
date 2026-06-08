# 📈 Stock Market Forecast — Previsão do Movimento de Preços de Ações com IA

> Trabalho de Conclusão de Curso — Tecnologia em Sistemas para Internet  
> Universidade Federal de Santa Maria (UFSM) — 2024  

---

## 📌 Sobre o Projeto

Este projeto desenvolve uma abordagem automatizada para **coleta, tratamento e análise de dados históricos de ações da B3 (Bolsa de Valores Brasileira)**, implementando e comparando três modelos de Inteligência Artificial na previsão do movimento de preços:

- **LSTM** (Long Short-Term Memory)
- **Prophet** (Meta/Facebook)
- **Random Forest**

Os modelos são avaliados em dois cenários distintos:

- **Previsões diárias** — prevê o comportamento do preço no próximo dia usando dados reais até o dia atual.
- **Previsões por período inteiro** — prevê tendências ao longo de um período sem atualizações dos dados reais, identificando movimentos de longo prazo.

O desempenho dos modelos é medido pelo **Erro Quadrático Médio (MSE)** e por um **Simulador de Operações Financeiras** desenvolvido do zero, que simula decisões de compra e venda com base nas previsões de cada modelo.

---

## 🗂️ Estrutura do Projeto

```
stock-market-forecast/
├── main.py                        # Menu principal e orquestração do fluxo
├── requirements.txt               # Dependências do projeto
├── .env.example                   # Modelo de configuração do banco de dados
└── providers/
    ├── collectingData.py          # Coleta de dados via API do Yahoo Finance
    ├── cleaningData.py            # Limpeza e tratamento dos dados
    ├── databaseConnection.py      # Conexão e operações com o banco PostgreSQL
    ├── modelLSTM.py               # Implementação do modelo LSTM
    ├── modelProphet.py            # Implementação do modelo Prophet
    ├── modelRandomForest.py       # Implementação do modelo Random Forest
    ├── calculateMSE.py            # Cálculo do Erro Quadrático Médio
    ├── buildGraphs.py             # Geração de gráficos comparativos
    └── simulator.py               # Simulador de Operações Financeiras
```

---

## ⚙️ Pré-requisitos

- Python 3.9+
- PostgreSQL
- GPU NVIDIA com CUDA (recomendado para o treinamento do LSTM; uso de `tensorflow-gpu`)

---

## 🚀 Instalação e Configuração

**1. Clone o repositório:**
```bash
git clone https://github.com/seu-usuario/stock-market-forecast.git
cd stock-market-forecast
```

**2. Instale as dependências:**
```bash
pip install -r requirements.txt
```

**3. Configure as variáveis de ambiente:**

Copie o arquivo `.env.example` para `.env` e preencha com os dados do seu banco PostgreSQL:
```
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nome_do_banco
```

**4. Execute o projeto:**
```bash
python main.py
```

---

## 🖥️ Como Usar

Ao executar `main.py`, um menu interativo é exibido com as seguintes opções:

```
-------- Serviços --------
1 - Download de dados
2 - Limpeza de dados
3 - Análise de dados
4 - Gerar gráficos das previsões
5 - Simulador de DayTrade
6 - Calcular MSE
0 - Sair
```

**Fluxo recomendado:**

1. **Download de dados** — informe os tickers desejados (ex: `PETR4,ITSA4,BOVA11`) e o período (padrão: 2020-01-01 a 2023-12-31).
2. **Limpeza de dados** — trata dados faltantes e duplicados.
3. **Análise de dados** — treina os modelos LSTM, Prophet e Random Forest e gera previsões.
4. **Gerar gráficos** — visualiza a comparação entre previsões e dados reais.
5. **Simulador de DayTrade** — simula uma carteira de R$ 100.000,00 seguindo as previsões de cada modelo.
6. **Calcular MSE** — exibe o Erro Quadrático Médio de cada modelo por ativo.

---

## 📦 Dependências

```
numpy~=1.26.4
pandas~=2.2.3
yfinance~=0.2.44
SQLAlchemy~=2.0.36
python-dotenv~=1.0.1
scikit-learn~=1.5.2
workalendar~=17.0.0
matplotlib~=3.9.2
tensorflow-gpu==2.10.0
prophet~=1.1.6
```

---

## ⚠️ Aviso

Este projeto foi desenvolvido com fins **acadêmicos e educacionais**. As previsões geradas pelos modelos **não devem ser utilizadas para tomada de decisões de investimento em cenários reais**, pois os modelos não foram desenvolvidos nem validados para garantir resultados consistentes no mercado financeiro.
