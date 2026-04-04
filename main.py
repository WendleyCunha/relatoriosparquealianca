import streamlit as st
import datetime
import json
import time
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

# --- LÓGICA DO MÊS ANTERIOR (AUTO-AJUSTE) ---
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
    # Inicialização de estados para limpeza dos campos (Ponto 4)
    if "nome_val" not in st.session_state: st.session_state.nome_val = ""
    if "estudos_val" not in st.session_state: st.session_state.estudos_val = 0
    if "horas_val" not in st.session_state: st.session_state.horas_val = 0
    if "part_val" not in st.session_state: st.session_state.part_val = False
    if "obs_val" not in st.session_state: st.session_state.obs_val = ""

    # Título e Subtítulo (Ponto 2)
    st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>RELATÓRIO DE SERVIÇO DE CAMPO</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 20px; font-family: serif; font-style: italic; color: #555; margin-top: 0;'>Parque Aliança (72249)</p>", unsafe_allow_html=True)
    
    mes_ref = obter_mes_referencia()

    # Container principal do formulário
    placeholder_form = st.empty()

    with placeholder_form.container():
        nome = st.text_input("Nome:", value=st.session_state.nome_val, placeholder="Campo obrigatório")
        st.write(f"**Mês de Referência:** {mes_ref}")
        
        st.markdown("---")
        
        participou = st.checkbox("Marque se você participou em alguma modalidade do ministério durante o mês.", value=st.session_state.part_val)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Estudos bíblicos")
        with col2:
            estudos = st.number_input("", min_value=0, step=1, value=st.session_state.estudos_val, label_visibility="collapsed")
            
        col3, col4 = st.columns([3, 1])
        with col3:
            st.write("Horas (se for pioneiro auxiliar, regular, especial ou missionário em campo)")
        with col4:
            horas = st.number_input("", min_value=0, step=1, value=st.session_state.horas_val, label_visibility="collapsed")

        observacoes = st.text_area("Observações:", value=st.session_state.obs_val, height=100)
        
        st.markdown("---")
        
        if st.button("ENVIAR RELATÓRIO", use_container_width=True):
            if not nome.strip(): # Ponto 1: Nome Obrigatório
                st.error("⚠️ O campo 'Nome' é obrigatório!")
            else:
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
                    # Limpa o formulário visualmente escondendo o container
                    placeholder_form.empty()
                    
                    # Efeito visual (Ponto 6)
                    st.balloons()
                    
                    # Mensagem de Sucesso Estilizada (Destaque)
                    st.markdown(f"""
                        <div style="background-color: #d4edda; padding: 40px; border-radius: 15px; border-left: 10px solid #155724; box-shadow: 5px 5px 15px rgba(0,0,0,0.1); text-align: center;">
                            <h1 style="color: #155724; margin-top: 0;">✅ MUITO OBRIGADO!</h1>
                            <h3 style="color: #155724;">Seu relatório de {mes_ref} foi enviado.</h3>
                            <p style="color: #1c1e21; font-size: 18px;"><b>{nome}</b>, seus dados foram registrados com sucesso.</p>
                            <hr style="border: 0.5px solid #c3e6cb;">
                            <p style="color: #666;">Aguarde 15 segundos para uma nova submissão...</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Reset dos estados internos (Ponto 4)
                    st.session_state.nome_val = ""
                    st.session_state.estudos_val = 0
                    st.session_state.horas_val = 0
                    st.session_state.part_val = False
                    st.session_state.obs_val = ""
                    
                    # Pausa de 15 segundos na tela de agradecimento
                    time.sleep(15)
                    st.rerun()

    st.caption("S-4-T 11/23 | Parque Aliança | Processamento Digital")

if __name__ == "__main__":
    main()
