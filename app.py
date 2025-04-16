# app.py - Aplicativo de fluxo de caixa "Açaí Bom Sabor"
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import json

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(page_title="Açaí Bom Sabor", layout="centered")  # Deve ser a primeira linha de código

# --- TÍTULO DA PÁGINA ---
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

# --- CONEXÃO COM GOOGLE SHEETS ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Carregar credenciais do Secrets do Streamlit
try:
    creds = json.loads(st.secrets["google"]["credentials"])  # Leitura do JSON do segredo
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds, SCOPE)
    client = gspread.authorize(creds)
    st.write("Conectado com sucesso ao Google Sheets!")
except Exception as e:
    st.error(f"Erro ao conectar ao Google Sheets: {e}")
    client = None  # Garantir que a variável client não será usada sem sucesso na autenticação

# Se client for None, não prosseguir
if client is None:
    st.stop()

# --- ABRIR PLANILHA ---
try:
    # Abrir a planilha existente (Fluxo de Caixa Acai) e nova planilha
    sheet_1 = client.open("Fluxo de Caixa Acai")  # Planilha existente
    sheet_2 = client.open("Fluxo de Caixa Açaí 2")  # Nova planilha
    st.write(f"Conectado com as planilhas: Fluxo de Caixa Acai e Fluxo de Caixa Açaí 2")
except Exception as e:
    st.error(f"Erro ao abrir a planilha: {e}")
    sheet_1 = sheet_2 = None  # Garantir que as planilhas não serão usadas sem sucesso na conexão

# Se as planilhas não foram abertas, não prosseguir
if sheet_1 is None or sheet_2 is None:
    st.stop()

# --- ABAS DA NOVA PLANILHA ---
try:
    entradas_2 = sheet_2.worksheet("Entradas")  # Aba da nova planilha
    st.write("Aba 'Entradas' da nova planilha carregada com sucesso!")
except Exception as e:
    st.error(f"Erro ao acessar a aba 'Entradas' da nova planilha: {e}")
    entradas_2 = None  # Garantir que a variável entradas_2 não será usada sem sucesso na conexão

# Se a aba não foi carregada, não prosseguir
if entradas_2 is None:
    st.stop()

# --- ADICIONAR ENTRADA NA NOVA PLANILHA ---
data = datetime.now().strftime("%d/%m/%Y")
item = "AÇAÍ DE 10"  # Exemplo, substitua com a variável do seu selectbox
valor = 10  # Exemplo de valor, substitua pelo valor selecionado
try:
    entradas_2.append_row([data, item, valor])  # Adicionando na nova planilha
    st.success("Entrada registrada com sucesso na nova planilha!")
except Exception as e:
    st.error(f"Erro ao adicionar entrada na nova planilha: {e}")

# --- OBTER REGISTROS DA ABA 'ENTRADAS' DA NOVA PLANILHA ---
try:
    df_entradas_2 = pd.DataFrame(entradas_2.get_all_records())  # Obtendo os registros
    st.write("Dados da aba 'Entradas' da nova planilha:", df_entradas_2.head())  # Exibe os primeiros registros
except Exception as e:
    st.error(f"Erro ao obter registros da aba 'Entradas' da nova planilha: {e}")

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
