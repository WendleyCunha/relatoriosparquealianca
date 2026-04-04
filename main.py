import streamlit as st
import datetime
import json
from google.cloud import firestore
from google.oauth2 import service_account

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Relatório de Serviço", page_icon="📋")

# --- ESTILIZAÇÃO CSS (Borda Preta e Ajustes) ---
st.markdown("""
    <style>
    /* Estiliza o formulário para parecer papel com borda preta */
    div[data-testid="stForm"] {
        border: 2px solid black !important;
        padding: 30px !important;
        border-radius: 0px !important;
        background-color: white !important;
    }
    /* Deixa os textos internos pretos para contraste */
    .stMarkdown, p, label {
        color: black !important;
    }
    /* Esconde o botão padrão de submit do form para usarmos o nosso customizado se necessário, 
       mas aqui vamos manter o padrão para garantir o reset */
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

# --- INTERFACE PRINCIPAL ---
def main():
    # Inicializa o estado de envio se não existir
    if "form_enviado" not in st.session_state:
        st.session_state.form_enviado = False

    st.markdown("<h2 style='text-align: center; color: white;'>RELATÓRIO DE SERVIÇO DE CAMPO</h2>", unsafe_allow_html=True)
    
    mes_ref = obter_mes_referencia()

    # 3. LÓGICA DE "SOMBRA D'ÁGUA" (Esconde o formulário após enviar)
    if st.session_state.form_enviado:
        st.balloons()
        st.success(f"✅ Obrigado! Seu relatório de {mes_ref} foi enviado.")
        st.info("O formulário foi limpo para o próximo uso.")
        
        if st.button("Enviar Novo Relatório"):
            st.session_state.form_enviado = False
            st.rerun()
    else:
        # 2. BORDA PRETA (via st.form)
        with st.form("meu_formulario", clear_on_submit=True):
            # 4. NOME OBRIGATÓRIO
            nome = st.text_input("Nome:", placeholder="Digite seu nome completo")
            st.write(f"**Mês:** {mes_ref}")
            
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
                        st.session_state.form_enviado = True
                        st.rerun() # Reinicia para aplicar o efeito de sumir o form
                else:
                    st.error("⚠️ O campo 'Nome' é obrigatório!")

    st.caption("S-4-T 11/23 | Processamento em Tempo Real")

if __name__ == "__main__":
    main()
