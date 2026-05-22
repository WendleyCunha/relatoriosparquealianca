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

# --- LÓGICA DE EXIBIÇÃO DOS ANÚNCIOS ---
def exibir_aba_anuncios():
    st.subheader("📢 Quadro de Anúncios")
    db = inicializar_db()
    if db:
        # Busca o anúncio mais recente
        anuncios_ref = db.collection("anuncios").order_by("data_postagem", direction="DESCENDING").limit(1)
        docs = anuncios_ref.stream()
        
        encontrou = False
        for doc in docs:
            dados = doc.to_dict()
            st.markdown(dados.get("conteudo", "Sem conteúdo para exibir."))
            st.caption(f"Atualizado em: {dados.get('data_postagem').strftime('%d/%m/%Y %H:%M')}")
            encontrou = True
        
        if not encontrou:
            st.info("Nenhum anúncio disponível no momento.")

# --- LÓGICA DO RELATÓRIO (EXISTENTE) ---
def salvar_relatorio(dados):
    db = inicializar_db()
    if db:
        try:
            db.collection("relatorios_parque_alianca").add(dados)
            return True
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")
    return False

# --- LÓGICA DO MÊS ANTERIOR ---
def obter_mes_referencia():
    hoje = datetime.date.today()
    primeiro_dia_mes_atual = hoje.replace(day=1)
    mes_anterior = primeiro_dia_mes_atual - datetime.timedelta(days=1)
    
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    # Extraímos o mês e o ano separadamente para evitar erros
    nome_mes = meses[mes_anterior.month - 1].upper()
    ano = mes_anterior.year
    
    return f"{nome_mes} {ano}"
# --- INTERFACE PRINCIPAL ---
def main():
    # Inicialização de estados
    if "nome_val" not in st.session_state: st.session_state.nome_val = ""
    if "estudos_val" not in st.session_state: st.session_state.estudos_val = 0
    if "horas_val" not in st.session_state: st.session_state.horas_val = 0
    if "part_val" not in st.session_state: st.session_state.part_val = False
    if "obs_val" not in st.session_state: st.session_state.obs_val = ""
    if "enviado" not in st.session_state: st.session_state.enviado = False
    if "ultimo_nome" not in st.session_state: st.session_state.ultimo_nome = ""

    # Criando as Abas
    tab1, tab2 = st.tabs(["📋 Relatório de Serviço", "📢 Anúncios"])

    with tab1:
        st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>RELATÓRIO DE SERVIÇO DE CAMPO</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 20px; font-family: serif; font-style: italic; color: #555; margin-top: 0;'>Congregação Parque Aliança (72249)</p>", unsafe_allow_html=True)
        
        mes_ref = obter_mes_referencia()
        placeholder = st.empty()

        if st.session_state.enviado:
            st.balloons()
            with placeholder.container():
                st.markdown(f"""
                    <div style="background-color: #d4edda; padding: 40px; border-radius: 15px; border-left: 10px solid #155724; box-shadow: 5px 5px 15px rgba(0,0,0,0.1); text-align: center;">
                        <h1 style="color: #155724; margin-top: 0;">✅ MUITO OBRIGADO!</h1>
                        <h2 style="color: #155724; text-transform: uppercase;">{st.session_state.ultimo_nome}</h2>
                        <h3 style="color: #155724;">Seu relatório de {mes_ref} foi enviado.</h3>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("ENVIAR OUTRO RELATÓRIO", use_container_width=True):
                    st.session_state.enviado = False
                    st.rerun()
        else:
            with placeholder.container():
                nome = st.text_input("Nome:", value=st.session_state.nome_val, key="txt_nome")
                st.write(f"**Mês de Referência:** {mes_ref}")
                participou = st.checkbox("Participou do ministério?", key="chk_part")
                estudos = st.number_input("Estudos Bíblicos", min_value=0, key="num_estudos")
                horas = st.number_input("Horas", min_value=0, key="num_horas")
                observacoes = st.text_area("Observações:", key="txt_obs")
                
                if st.button("ENVIAR RELATÓRIO", use_container_width=True):
                    dados_final = {
                        "nome": nome, "mes_referencia": mes_ref, "participou_ministerio": participou,
                        "estudos_biblicos": estudos, "horas": horas, "observacoes": observacoes,
                        "data_envio": datetime.datetime.now(), "status_pdf": "PENDENTE"
                    }
                    if salvar_relatorio(dados_final):
                        st.session_state.enviado = True
                        st.rerun()

    with tab2:
        exibir_aba_anuncios()

if __name__ == "__main__":
    main()
