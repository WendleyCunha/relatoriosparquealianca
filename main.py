import streamlit as st
import datetime
import json
from google.cloud import firestore
from google.oauth2 import service_account

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Relatório de Serviço", page_icon="📋")

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

# --- LÓGICA DO MÊS ANTERIOR (Ponto 3) ---
def obter_mes_referencia():
    hoje = datetime.date.today()
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
    # Inicializa o estado de sucesso para controle de exibição e limpeza
    if "form_pode_exibir" not in st.session_state:
        st.session_state.form_pode_exibir = True

    # 2 - Cabeçalho com Letra Melhorada e Identificação da Congregação
    st.markdown("<h2 style='text-align: center; margin-bottom: 0px;'>RELATÓRIO DE SERVIÇO DE CAMPO</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 22px; font-family: serif; font-style: italic; color: #555;'>Parque Aliança (72249)</p>", unsafe_allow_html=True)
    
    mes_ref = obter_mes_referencia()

    # 6 - Mensagem de Sucesso Estilizada (Tipo Pop-up com Sombra)
    if not st.session_state.form_pode_exibir:
        st.balloons()
        st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 40px; border-radius: 15px; border-left: 10px solid #28a745; box-shadow: 5px 5px 15px rgba(0,0,0,0.1); margin-top: 20px;">
                <h1 style="color: #28a745; margin-top: 0;">Obrigado!</h1>
                <h3 style="color: #31333F;">Seu relatório de {mes_ref} foi enviado.</h3>
                <p style="color: #555;">Os dados já estão disponíveis para o processamento do formulário S-4-T.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        if st.button("ENVIAR OUTRO RELATÓRIO", use_container_width=True):
            st.session_state.form_pode_exibir = True
            st.rerun()
    
    else:
        # 4 - O uso do 'st.form' com 'clear_on_submit=True' garante a limpeza dos campos
        with st.form("meu_formulario_limpo", clear_on_submit=True):
            
            # 1 - Nome obrigatório
            nome = st.text_input("Nome:", placeholder="Digite seu nome completo")
            st.markdown(f"**Mês de Referência:** `{mes_ref}`")
            
            st.markdown("---")
            
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
            
            st.markdown("---")
            
            # Botão de Enviar dentro do Form
            enviar = st.form_submit_button("ENVIAR RELATÓRIO", use_container_width=True)
            
            if enviar:
                if nome.strip(): # 1 - Validação de nome obrigatório
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
                        st.session_state.form_pode_exibir = False
                        st.rerun()
                else:
                    st.error("⚠️ O campo 'Nome' é obrigatório para o envio.")

    # Rodapé técnico
    st.write("")
    st.caption("S-4-T 11/23 | Parque Aliança | Processamento Digital")

if __name__ == "__main__":
    main()
