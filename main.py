import streamlit as st
import datetime
import json
from google.cloud import firestore
from google.oauth2 import service_account

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Relatório de Serviço", page_icon="📋")

# --- ESTILIZAÇÃO CSS (Borda Preta e Visual de Papel) ---
st.markdown("""
    <style>
    /* Borda preta em volta do formulário */
    div[data-testid="stForm"] {
        border: 2px solid black !important;
        padding: 30px !important;
        border-radius: 5px !important;
        background-color: white !important;
    }
    /* Forçar textos internos a ficarem pretos para contraste no fundo branco */
    .stMarkdown, p, label {
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO COM FIRESTORE ---
def inicializar_db():
    if "db" not in st.session_state:
        try:
            key_dict = json.loads(st.secrets["textkey"])
            creds = service_account.Credentials.from_service_account_info(key_dict)
            st.session_state.db = firestore.Client(credentials=creds, project="wendleydesenvolvimento")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
            return None
    return st.session_state.db

def salvar_relatorio(dados):
    db = inicializar_db()
    if db:
        try:
            db.collection("relatorios_parque_alianca").add(dados)
            return True
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")
    return False

# --- LÓGICA DO MÊS ANTERIOR (Ex: Se hoje é Maio, mostra Abril) ---
def obter_mes_referencia():
    hoje = datetime.date.today()
    # Pega o primeiro dia do mês atual e subtrai 1 dia para cair no mês anterior
    primeiro_dia_mes_atual = hoje.replace(day=1)
    mes_anterior = primeiro_dia_mes_atual - datetime.timedelta(days=1)
    
    meses = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]
    
    nome_mes = meses[mes_anterior.month - 1]
    ano = mes_anterior.year
    return f"{nome_mes.upper()} {ano}"

# --- INTERFACE ---
def main():
    # Inicializa controle de exibição
    if "sucesso" not in st.session_state:
        st.session_state.sucesso = False

    # 2 - Cabeçalho com Letra Melhorada
    st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>RELATÓRIO DE SERVIÇO DE CAMPO</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 20px; font-family: serif; font-style: italic;'>Parque Aliança (72249)</p>", unsafe_allow_html=True)
    
    mes_ref = obter_mes_referencia()

    # 6 - Mensagem de Sucesso Estilizada (Efeito Pop-up/Sombra)
    if st.session_state.sucesso:
        st.balloons()
        st.markdown("""
            <div style="background-color: #d4edda; padding: 30px; border-radius: 10px; border: 2px solid #155724; text-align: center; box-shadow: 10px 10px 20px rgba(0,0,0,0.2);">
                <h1 style="color: #155724;">✅ MUITO OBRIGADO!</h1>
                <p style="color: #155724; font-size: 18px;">Seu relatório de <b>""" + mes_ref + """</b> foi enviado com sucesso.</p>
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("ENVIAR OUTRO RELATÓRIO"):
            st.session_state.sucesso = False
            st.rerun()
    
    else:
        # 4 - clear_on_submit=True garante que os dados sejam limpos ao enviar
        with st.form("form_relatorio", clear_on_submit=True):
            
            # 1 - Nome obrigatório (validado no botão abaixo)
            nome = st.text_input("Nome:", placeholder="Digite seu nome completo")
            st.write(f"**Mês de Referência:** {mes_ref}")
            
            st.markdown("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)
            
            participou = st.checkbox("Marque se você participou em alguma modalidade do ministério durante o mês.")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("Estudos bíblicos")
            with col2:
                estudos = st.number_input("", min_value=0, step=1, label_visibility="collapsed")
                
            col3, col4 = st.columns([3, 1])
            with col3:
                st.write("Horas (se for pioneiro auxiliar, regular, especial ou missionário em campo)")
            with col4:
                horas = st.number_input("", min_value=0, step=1, label_visibility="collapsed")

            observacoes = st.text_area("Observações:", height=100)
            
            st.markdown("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)
            
            # Botão de submissão do formulário
            enviar = st.form_submit_button("ENVIAR RELATÓRIO", use_container_width=True)

            if enviar:
                if nome.strip(): # Valida se o nome não está vazio
                    dados_final = {
                        "nome": nome,
                        "mes_referencia": mes_ref,
                        "participou_ministerio": participou,
                        "estudos_biblicos": estudos,
                        "horas": horas,
                        "observacoes": observacoes,
                        "data_envio": datetime.datetime.now(),
                        "status_pdf": "PENDENTE"
                    }
                    
                    if salvar_relatorio(dados_final):
                        st.session_state.sucesso = True
                        st.rerun()
                else:
                    st.error("⚠️ O campo 'Nome' é obrigatório!")

    st.caption("S-4-T 11/23 | Processamento em Tempo Real")

if __name__ == "__main__":
    main()
