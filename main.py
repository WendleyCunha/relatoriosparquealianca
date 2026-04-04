import streamlit as st
import datetime
import json
from google.cloud import firestore
from google.oauth2 import service_account

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Relatório de Serviço", page_icon="📋")

# --- ESTILIZAÇÃO CSS (Borda e Design) ---
st.markdown("""
    <style>
    .folha-relatorio {
        border: 2px solid black;
        padding: 20px;
        border-radius: 5px;
        background-color: white;
        color: black;
    }
    .stTextInput label, .stNumberInput label, .stTextArea label, .stCheckbox label {
        color: black !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE APOIO ---
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

def obter_mes_referencia():
    hoje = datetime.date.today()
    primeiro_dia_mes_atual = hoje.replace(day=1)
    mes_anterior = primeiro_dia_mes_atual - datetime.timedelta(days=1)
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    return f"{meses[mes_anterior.month - 1].upper()} {mes_anterior.year}"

# --- LÓGICA DE LIMPEZA (Reset) ---
def limpar_formulario():
    st.session_state["nome_input"] = ""
    st.session_state["estudos_input"] = 0
    st.session_state["horas_input"] = 0
    st.session_state["obs_input"] = ""
    st.session_state["participou_input"] = False
    st.session_state["enviado"] = True

# --- INTERFACE ---
def main():
    if "enviado" not in st.session_state:
        st.session_state["enviado"] = False

    mes_ref = obter_mes_referencia()

    # Título centralizado
    st.markdown("<h2 style='text-align: center; color: white;'>RELATÓRIO DE SERVIÇO DE CAMPO</h2>", unsafe_allow_html=True)

    # Se já foi enviado, mostra apenas o agradecimento (Efeito de esconder o form)
    if st.session_state["enviado"]:
        st.balloons()
        st.success(f"✅ Seu relatório de {mes_ref} foi enviado com sucesso!")
        st.info("Os dados foram organizados e estão prontos para o processamento do formulário S-4-T.")
        if st.button("Enviar outro relatório"):
            st.session_state["enviado"] = False
            st.rerun()
    else:
        # Início da Borda Preta (Container customizado)
        st.markdown('<div class="folha-relatorio">', unsafe_allow_html=True)
        
        with st.container():
            nome = st.text_input("Nome:", placeholder="Digite seu nome completo", key="nome_input", help="Campo obrigatório")
            st.markdown(f"<p style='color:black;'><b>Mês:</b> {mes_ref}</p>", unsafe_allow_html=True)
            
            st.markdown("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)
            
            participou = st.checkbox("Marque se você participou em alguma modalidade do ministério durante o mês.", key="participou_input")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("Estudos bíblicos")
            with col2:
                estudos = st.number_input("", min_value=0, step=1, key="estudos_input", label_visibility="collapsed")
                
            col3, col4 = st.columns([3, 1])
            with col3:
                st.write("Horas (se for pioneiro auxiliar, regular, especial ou missionário em campo)")
            with col4:
                horas = st.number_input("", min_value=0, step=1, key="horas_input", label_visibility="collapsed")

            observacoes = st.text_area("Observações:", height=100, key="obs_input")
            
            st.markdown("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)
            
            if st.button("ENVIAR RELATÓRIO", use_container_width=True, type="primary"):
                if nome:
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
                        limpar_formulario()
                        st.rerun()
                else:
                    st.error("⚠️ O campo 'Nome' é obrigatório!")

        st.markdown('</div>', unsafe_allow_html=True) # Fim da Borda Preta

    st.caption("S-4-T 11/23 | Processamento em Tempo Real")

if __name__ == "__main__":
    main()
