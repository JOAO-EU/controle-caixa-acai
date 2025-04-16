
# 🍧 Açaí Bom Sabor - Fluxo de Caixa

Aplicativo de fluxo de caixa desenvolvido em **Python com Streamlit**, voltado para controle financeiro diário de uma açaiteria.

## 🚀 Funcionalidades

- Registro de **entradas** com seleção de produtos
- Registro de **saídas** com descrição manual
- Gráficos de entradas e saídas mensais
- Cálculo automático de saldo
- Exportação de relatório em PDF
- Armazenamento de dados no Google Sheets

## 🛠 Tecnologias

- Python, Streamlit, Pandas, Plotly, FPDF, Google Sheets API

## 📦 Rodando localmente

```bash
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo
pip install -r requirements.txt
streamlit run app.py
```

> Lembre-se de colocar seu arquivo `credentials.json` na pasta `config/`.

## ☁️ Rodando no Streamlit Cloud

1. Faça upload para o GitHub
2. Crie o app no [Streamlit Cloud](https://streamlit.io/cloud)
3. Envie seu `credentials.json` via painel **Settings > Secrets**
