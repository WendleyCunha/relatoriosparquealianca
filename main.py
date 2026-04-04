import streamlit as st

import datetime

import json

from google.cloud import firestore

from google.oauth2 import service_account



# --- CONFIGURAÇÃO DA PÁGINA ---

st.set_page_config(page_title="Relatório de Serviço", page_icon="📋")



# --- CONEXÃO COM FIRESTORE (REUTILIZANDO SUA TEXTKEY) ---

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

            # Gravando na coleção específica do projeto

            db.collection("relatorios_parque_alianca").add(dados)

            return True

        except Exception as e:

            st.error(f"Erro ao salvar: {e}")

    return False



# --- LÓGICA DO MÊS ANTERIOR AUTOMÁTICO ---

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

    # Título estilizado conforme a imagem

    st.markdown("<h2 style='text-align: center;'>RELATÓRIO DE SERVIÇO DE CAMPO</h2>", unsafe_allow_html=True)

    

    mes_ref = obter_mes_referencia()



    # Container para simular o visual do formulário impresso

    with st.container():

        nome = st.text_input("Nome:", placeholder="Digite seu nome completo")

        st.write(f"**Mês:** {mes_ref}")

        

        st.markdown("---")

        

        # Seção de Checkbox e Inputs Numéricos

        participou = st.checkbox("Marque se você participou em alguma modalidade do ministério durante o mês.")

        

        col1, col2 = st.columns([3, 1])

        with col1:

            st.write("Estudos bíblicos")

        with col2:

            estudos = st.number_input("", min_value=0, step=1, key="estudos", label_visibility="collapsed")

            

        col3, col4 = st.columns([3, 1])

        with col3:

            st.write("Horas (se for pioneiro auxiliar, regular, especial ou missionário em campo)")

        with col4:

            horas = st.number_input("", min_value=0, step=1, key="horas", label_visibility="collapsed")



        observacoes = st.text_area("Observações:", height=100)

        

        st.markdown("---")

        

        # Botão de Enviar

        if st.button("ENVIAR RELATÓRIO", use_container_width=True):

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

                    st.balloons()

                    st.success(f"Obrigado, {nome}! Seu relatório de {mes_ref} foi enviado com sucesso.")

                    st.info("Os dados foram organizados e estão prontos para o processamento do formulário S-4-T.")

            else:

                st.warning("Por favor, preencha o seu nome antes de enviar.")



    # Rodapé técnico

    st.caption("S-4-T 11/23 | Processamento em Tempo Real")



if __name__ == "__main__":

    main()
