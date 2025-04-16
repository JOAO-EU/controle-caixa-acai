# app.py - Aplicativo de fluxo de caixa "Açaí Bom Sabor"
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import plotly.express as px
from fpdf import FPDF
import base64
import io

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(page_title="Açaí Bom Sabor", layout="centered")
st.title("🍇 Fluxo de Caixa - Açaí Bom Sabor")

# Cores do tema
st.markdown("""
    <style>
    .stApp {
        background-color: #faf7ff;
    }
    .css-18e3th9 {
        background-color: #ffffff;
        border: 2px solid #d1b3ff;
        border-radius: 15px;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

try:
    # Acesse as credenciais armazenadas no Secrets do Streamlit Cloud
    creds = json.loads(st.secrets["google"]["credentials"])

    # Defina o escopo de acesso ao Google Sheets
    SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Crie as credenciais a partir dos dados do Secrets
    CREDS = ServiceAccountCredentials.from_json_keyfile_dict(creds, SCOPE)

    # Autenticação com o Google Sheets
    CLIENT = gspread.authorize(CREDS)

    SHEET_NAME = "Fluxo de Caixa Acai"
    SHEET = CLIENT.open(SHEET_NAME)
    ENTRADAS = SHEET.worksheet("Entradas")
    SAIDAS = SHEET.worksheet("Saidas")
    
    st.success("Conexão bem-sucedida com o Google Sheets!")

except Exception as e:
    st.error(f"Ocorreu um erro ao tentar autenticar: {e}")

import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# --- CONEXÃO COM GOOGLE SHEETS ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Verificação de conexão com a planilha
try:
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
    client = gspread.authorize(creds)
    st.write("Conectado com sucesso ao Google Sheets!")
except Exception as e:
    st.error(f"Erro ao conectar ao Google Sheets: {e}")

# Tente abrir a planilha "Fluxo de Caixa Acai"
sheet_name = "Fluxo de Caixa Acai"
try:
    sheet = client.open(sheet_name)
    st.write(f"Conectado com a planilha: {sheet_name}")
except Exception as e:
    st.error(f"Erro ao abrir a planilha: {e}")

# Verificando as abas disponíveis na planilha
try:
    worksheet_list = sheet.worksheets()
    st.write("Abas disponíveis na planilha:", [worksheet.title for worksheet in worksheet_list])
except Exception as e:
    st.error(f"Erro ao verificar abas da planilha: {e}")
# Tente acessar a aba 'Entradas'
try:
    entradas = sheet.worksheet("Entradas")
    st.write("Aba 'Entradas' carregada com sucesso!")
except Exception as e:
    st.error(f"Erro ao acessar a aba 'Entradas': {e}")


# --- TABELA DE PRODUTOS ---
produtos = {
    "AÇAÍ DE 5": 5,
    "AÇAÍ DE 7": 7,
    "AÇAÍ DE 9": 9,
    "AÇAÍ DE 10": 10,
    "AÇAÍ DE 12": 12,
    "AÇAÍ DE 17": 17,
    "AÇAÍ DE 18": 18,
    "MARMITA P": 16,
    "MARMITA M": 25,
    "BARCA P": 25,
    "BARCA M": 50,
    "CASCÃO": 5,
    "CASCÃO TRUFADO": 8,
    "CASQUINHA": 3,
}

# --- ADICIONAR ENTRADA ---
st.subheader("💵 Adicionar Entrada")
col1, col2 = st.columns([2, 1])

with col1:
    item = st.selectbox("Produto", list(produtos.keys()))
with col2:
    if st.button("Registrar Entrada"):
        data = datetime.now().strftime("%d/%m/%Y")
        valor = produtos[item]
        ENTRADAS.append_row([data, item, valor])
        st.success("Entrada registrada!")

# --- ADICIONAR SAÍDA ---
st.subheader("💸 Adicionar Saída")
with st.form("form_saida"):
    desc_saida = st.text_input("Descrição")
    valor_saida = st.number_input("Valor (R$)", min_value=0.0, step=0.5)
    submitted = st.form_submit_button("Registrar Saída")
    if submitted:
        data = datetime.now().strftime("%d/%m/%Y")
        SAIDAS.append_row([data, desc_saida, valor_saida])
        st.success("Saída registrada!")

# --- GRÁFICOS E SALDO ---
st.subheader("📊 Relatório Mensal")
df_entradas = pd.DataFrame(ENTRADAS.get_all_records())
df_saidas = pd.DataFrame(SAIDAS.get_all_records())

if not df_entradas.empty:
    df_entradas['Valor'] = pd.to_numeric(df_entradas['Valor'])
    df_saidas['Valor'] = pd.to_numeric(df_saidas['Valor'])

    total_entradas = df_entradas['Valor'].sum()
    total_saidas = df_saidas['Valor'].sum()
    saldo = total_entradas - total_saidas

    st.metric("Saldo Atual", f"R$ {saldo:.2f}", delta=f"+{total_entradas - total_saidas:.2f}")

    df_entradas['Data'] = pd.to_datetime(df_entradas['Data'], dayfirst=True)
    df_saidas['Data'] = pd.to_datetime(df_saidas['Data'], dayfirst=True)

    df_entradas['Mês'] = df_entradas['Data'].dt.strftime('%Y-%m')
    df_saidas['Mês'] = df_saidas['Data'].dt.strftime('%Y-%m')

    entradas_mes = df_entradas.groupby('Mês')['Valor'].sum().reset_index()
    saidas_mes = df_saidas.groupby('Mês')['Valor'].sum().reset_index()

    fig = px.bar(entradas_mes, x='Mês', y='Valor', title="Entradas Mensais", color_discrete_sequence=['#9B59B6'])
    st.plotly_chart(fig)

    fig2 = px.bar(saidas_mes, x='Mês', y='Valor', title="Saídas Mensais", color_discrete_sequence=['#F39C12'])
    st.plotly_chart(fig2)

    # Exportar PDF
    st.subheader("🔗 Exportar Relatório em PDF")
    if st.button("Gerar PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Relatório - Açaí Bom Sabor", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Saldo Atual: R$ {saldo:.2f}", ln=True)

        pdf.cell(200, 10, txt="Entradas:", ln=True)
        for i, row in df_entradas.iterrows():
            pdf.cell(200, 8, txt=f"{row['Data'].strftime('%d/%m/%Y')} - {row['Produto']} - R$ {row['Valor']:.2f}", ln=True)

        pdf.cell(200, 10, txt="Saídas:", ln=True)
        for i, row in df_saidas.iterrows():
            pdf.cell(200, 8, txt=f"{row['Data'].strftime('%d/%m/%Y')} - {row['Descrição']} - R$ {row['Valor']:.2f}", ln=True)

        buffer = io.BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="relatorio-acai.pdf">Baixar PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
else:
    st.info("Nenhuma entrada registrada ainda. Comece adicionando vendas!")
