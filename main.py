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

# --- FUNÇÃO PARA LIMPAR FORMULÁRIO ---
def limpar_campos():
    st.session_state.nome_input = ""
    st.session_state.estudos = 0
    st.session_state.horas = 0
    st.session_state.participou = False
    st.session_state.obs = ""

# --- INTERFACE ---
def main():
    # Inicialização de estados para limpeza dos campos
    if "nome_input" not in st.session_state:
        st.session_state.nome_input = ""
    if "estudos" not in st.session_state:
        st.session_state.estudos = 0
    if "horas" not in st.session_state:
        st.session_state.horas = 0
    if "participou" not in st.session_state:
        st.session_state.participou = False
    if "obs" not in st.session_state:
        st.session_state.obs = ""

    # Título e Subtítulo (Ajuste conforme pedido 2)
    st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>RELATÓRIO DE SERVIÇO DE CAMPO</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #555; font-weight: normal; margin-top: 0;'>Parque Aliança (72249)</h4>", unsafe_allow_html=True)
    
    mes_ref = obter_mes_referencia()

    with st.container():
        # Nome Obrigatório (Ajuste 1)
        nome = st.text_input("Nome:", value=st.session_state.nome_input, key="nome_field", placeholder="Campo obrigatório")
        
        st.write(f"**Mês de Referência:** {mes_ref}")
        
        st.markdown("---")
        
        # Seção de Dados
        participou = st.checkbox("Marque se você participou em alguma modalidade do ministério durante o mês.", value=st.session_state.participou)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Estudos bíblicos")
        with col2:
            estudos = st.number_input("", min_value=0, step=1, value=st.session_state.estudos, key="estudos_input", label_visibility="collapsed")
            
        col3, col4 = st.columns([3, 1])
        with col3:
            st.write("Horas (Pioneiros/Missionários)")
        with col4:
            horas = st.number_input("", min_value=0, step=1, value=st.session_state.horas, key="horas_input", label_visibility="collapsed")

        observacoes = st.text_area("Observações:", value=st.session_state.obs, height=100)
        
        st.markdown("---")
        
        # Botão de Enviar
        if st.button("ENVIAR RELATÓRIO", use_container_width=True):
            # Validação de nome obrigatório (Ajuste 1)
            if nome.strip() == "":
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
                    # Efeito visual de sucesso (Ajuste 6)
                    st.balloons()
                    
                    # Pop-up de sucesso estilizado
                    st.toast(f"Relatório de {nome} enviado!")
                    
                    st.success(f"""
                        ### ✅ Relatório Enviado com Sucesso!
                        **Muito obrigado, {nome}!** Seu relatório referente a **{mes_ref}** foi registrado.
                    """)
                    
                    # Limpeza de dados (Ajuste 4)
                    st.session_state.nome_input = ""
                    st.session_state.estudos = 0
                    st.session_state.horas = 0
                    st.session_state.participou = False
                    st.session_state.obs = ""
                    
                    # Pequena pausa e recarrega para limpar visualmente os campos
                    time.sleep(3)
                    st.rerun()

    st.caption("S-4-T 11/23 | Processamento em Tempo Real")

if __name__ == "__main__":
    main()
