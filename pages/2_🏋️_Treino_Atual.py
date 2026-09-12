from datetime import date
import streamlit as st
from database import repository as repo
from modules import visual_service as visual  

st.set_page_config(page_title="Treino Atual", page_icon="🏋️", layout="wide")
visual.injetar_css()

st.title("🏋️ Treino em Andamento")

# 1. RECUPERA A SESSÃO ATIVA
sessao_id = st.session_state.get("sessao_ativa_id")

# Fallback: Se recarregou a página e perdeu o state, tenta achar o treino criado hoje
if not sessao_id:
    sessoes_hoje = [s for s in repo.listar_sessoes(limite=5) if s.data == date.today()]
    if sessoes_hoje:
        sessao_id = sessoes_hoje[0].id
        st.session_state["sessao_ativa_id"] = sessao_id
    else:
        st.warning("Nenhum treino iniciado. Vá para a página inicial (Dashboard) para iniciar um treino de hoje.")
        st.stop()

# 2. BUSCA OS DADOS DA SESSÃO E DA ROTINA NO BANCO
sessao = repo.obter_sessao_completa(sessao_id)
if not sessao or not sessao.rotina_id:
    st.error("Erro ao carregar a sessão ou a rotina associada.")
    st.stop()

rotina = repo.obter_rotina_completa(sessao.rotina_id)
series_realizadas = sessao.series # As séries que já foram inseridas no banco hoje

st.subheader(f"Rotina: {rotina.nome}")
st.divider()

# 3. RENDERIZA OS EXERCÍCIOS E OS FORMULÁRIOS DE SÉRIE (1 SÉRIE = 1 INSERT)
for vinculo in rotina.exercicios:
    ex = vinculo.exercicio
    
    st.markdown(f"### 🎯 {ex.nome}")
    
    carga_meta = f" @ {vinculo.carga_alvo}kg" if vinculo.carga_alvo else ""
    st.caption(f"**Meta:** {vinculo.series_alvo} séries x {vinculo.reps_alvo} reps{carga_meta}")
    
    # Filtra no banco as séries que você já fez hoje para este exercício específico
    series_ex = [s for s in series_realizadas if s.exercicio_id == ex.id]
    series_ex.sort(key=lambda x: x.numero_serie)
    
    # Mostra o histórico do que já foi feito na sessão atual
    if series_ex:
        for s in series_ex:
            st.markdown(f"✅ **Série {s.numero_serie}:** {s.carga_kg} kg  ×  {s.reps} reps")
    
    # Calcula qual é o número da série que você vai inserir agora
    prox_serie = len(series_ex) + 1
    
    # Se ainda não bateu a meta de séries (ou se quiser fazer extras), exibe o form
    with st.form(key=f"form_serie_{ex.id}", clear_on_submit=True):
        col1, col2, col3 = st.columns([1, 1, 2])
        
        reps_feitas = col1.number_input(f"Reps (Série {prox_serie})", min_value=0, step=1, value=0, key=f"reps_{ex.id}")
        carga_feita = col2.number_input("Carga (kg)", min_value=0.0, step=0.5, value=float(vinculo.carga_alvo or 0.0), key=f"carga_{ex.id}")
        
        # O botão do formulário faz o INSERT exato de 1 linha na tabela SerieRealizada
        submit = col3.form_submit_button("Registrar Série", type="secondary")
        if submit:
            if reps_feitas > 0:
                repo.registrar_serie(
                    sessao_id=sessao.id,
                    exercicio_id=ex.id,
                    numero_serie=prox_serie,
                    reps=reps_feitas,
                    carga_kg=carga_feita
                )
                st.toast(f"Série {prox_serie} de {ex.nome} salva!")
                st.rerun() # Atualiza a tela para mostrar a série concluída e preparar a próxima
            else:
                st.error("Insira a quantidade de repetições.")
    
    st.divider()

# 4. BOTÃO PARA ENCERRAR A SESSÃO
if st.button("Finalizar Treino 🎉", type="primary", use_container_width=True):
    st.session_state.pop("sessao_ativa_id", None)
    st.balloons()
    st.success("Treino finalizado com sucesso! Vá descansar.")