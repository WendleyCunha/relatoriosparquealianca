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



# --- LÓGICA DO MÊS ANTERIOR ---

def obter_mes_referencia():

    hoje = datetime.date.today()

    primeiro_dia_mes_atual = hoje.replace(day=1)

    mes_anterior = primeiro_dia_mes_atual - datetime.timedelta(days=1)

    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",

             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

    return f"{meses[mes_anterior.month - 1].upper()} {mes_anterior.year}"



# --- INTERFACE ---

def main():

    # Inicialização de estados

    if "nome_val" not in st.session_state: st.session_state.nome_val = ""

    if "estudos_val" not in st.session_state: st.session_state.estudos_val = 0

    if "horas_val" not in st.session_state: st.session_state.horas_val = 0

    if "part_val" not in st.session_state: st.session_state.part_val = False

    if "obs_val" not in st.session_state: st.session_state.obs_val = ""

    if "enviado" not in st.session_state: st.session_state.enviado = False

    if "ultimo_nome" not in st.session_state: st.session_state.ultimo_nome = ""



    # Título e Subtítulo

    st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>RELATÓRIO DE SERVIÇO DE CAMPO</h2>", unsafe_allow_html=True)

    st.markdown("<p style='text-align: center; font-size: 20px; font-family: serif; font-style: italic; color: #555; margin-top: 0;'>Congregação Parque Aliança (72249)</p>", unsafe_allow_html=True)

    

    mes_ref = obter_mes_referencia()



    # Espaço para o formulário ou mensagem de sucesso

    placeholder = st.empty()



    if st.session_state.enviado:

        # MENSAGEM DE SUCESSO PERSONALIZADA

        st.balloons()

        placeholder.markdown(f"""

            <div style="background-color: #d4edda; padding: 40px; border-radius: 15px; border-left: 10px solid #155724; box-shadow: 5px 5px 15px rgba(0,0,0,0.1); text-align: center;">

                <h1 style="color: #155724; margin-top: 0;">✅ MUITO OBRIGADO!</h1>

                <h2 style="color: #155724; text-transform: uppercase;">{st.session_state.ultimo_nome}</h2>

                <h3 style="color: #155724;">Seu relatório de {mes_ref} foi enviado.</h3>

                <p style="color: #1c1e21; font-size: 18px;">Os dados foram registrados com sucesso.</p>

                <hr style="border: 0.5px solid #c3e6cb;">

                <p style="color: #666;">Aguarde 15 segundos para finalizar...</p>

            </div>

        """, unsafe_allow_html=True)

        

        time.sleep(15)

        st.session_state.enviado = False

        st.session_state.ultimo_nome = "" # Limpa o nome para a próxima pessoa

        st.rerun()



    else:

        with placeholder.container():

            nome = st.text_input("Nome:", value=st.session_state.nome_val, placeholder="Campo obrigatório", key="txt_nome")

            st.write(f"**Mês de Referência:** {mes_ref}")

            

            st.markdown("---")

            

            participou = st.checkbox("Marque se você participou em alguma modalidade do ministério durante o mês.", value=st.session_state.part_val, key="chk_part")

            

            col1, col2 = st.columns([3, 1])

            with col1:

                st.write("Estudos bíblicos")

            with col2:

                estudos = st.number_input("Estudos", min_value=0, step=1, value=st.session_state.estudos_val, label_visibility="collapsed", key="num_estudos")

                

            col3, col4 = st.columns([3, 1])

            with col3:

                st.write("Horas (Pioneiros/Missionários)")

            with col4:

                horas = st.number_input("Horas", min_value=0, step=1, value=st.session_state.horas_val, label_visibility="collapsed", key="num_horas")



            observacoes = st.text_area("Observações:", value=st.session_state.obs_val, height=100, key="txt_obs")

            

            st.markdown("---")

            

            if st.button("ENVIAR RELATÓRIO", use_container_width=True):

                if not nome.strip():

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

                        # SALVA O NOME PARA MOSTRAR NA PRÓXIMA TELA

                        st.session_state.ultimo_nome = nome

                        

                        # Limpa os estados para o próximo uso

                        st.session_state.nome_val = ""

                        st.session_state.estudos_val = 0

                        st.session_state.horas_val = 0

                        st.session_state.part_val = False

                        st.session_state.obs_val = ""

                        st.session_state.enviado = True

                        st.rerun()



    st.caption("S-4-T 11/23 | Parque Aliança | Processamento Digital")



if __name__ == "__main__":

    main()
