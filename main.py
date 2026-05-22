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
        anuncios_ref = db.collection("anuncios").order_by("data_postagem", direction="DESCENDING").limit(1)
        docs = anuncios_ref.stream()
        
        encontrou = False
        for doc in docs:
            dados = doc.to_dict()
            st.markdown(dados.get("conteudo", "Sem conteúdo para exibir."))
            data_post = dados.get("data_postagem")
            if data_post:
                st.caption(f"Atualizado em: {data_post.strftime('%d/%m/%Y %H:%M')}")
            encontrou = True
        
        if not encontrou:
            st.info("Nenhum anúncio disponível no momento.")

# --- LÓGICA DO RELATÓRIO ---
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
    
    nome_mes = meses[mes_anterior.month - 1].upper()
    ano = str(mes_anterior.year)
    return f"{nome_mes} {ano}"

# --- INTERFACE PRINCIPAL ---
def main():
    if "enviado" not in st.session_state: st.session_state.enviado = False
    
    tab1, tab2 = st.tabs(["📋 Relatório de Serviço", "📢 Anúncios"])

    with tab1:
        st.markdown("<h2 style='text-align: center;'>RELATÓRIO DE SERVIÇO DE CAMPO</h2>", unsafe_allow_html=True)
        mes_ref = obter_mes_referencia()
        
        if st.session_state.enviado:
            st.success("✅ Relatório enviado com sucesso!")
            if st.button("ENVIAR OUTRO"):
                st.session_state.enviado = False
                st.rerun()
        else:
            nome = st.text_input("Nome:")
            st.write(f"**Mês de Referência:** {mes_ref}")
            participou = st.checkbox("Participou do ministério?")
            estudos = st.number_input("Estudos Bíblicos", min_value=0, step=1)
            horas = st.number_input("Horas", min_value=0, step=1)
            obs = st.text_area("Observações:")
            
            if st.button("ENVIAR RELATÓRIO"):
                if nome:
                    dados = {
                        "nome": nome, "mes_referencia": mes_ref, "participou_ministerio": participou,
                        "estudos_biblicos": estudos, "horas": horas, "observacoes": obs,
                        "data_envio": datetime.datetime.now(), "status_pdf": "PENDENTE"
                    }
                    if salvar_relatorio(dados):
                        st.session_state.enviado = True
                        st.rerun()
                else:
                    st.error("O campo Nome é obrigatório.")

    with tab2:
        exibir_aba_anuncios()

if __name__ == "__main__":
    main()
