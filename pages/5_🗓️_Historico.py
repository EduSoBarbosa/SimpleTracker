import streamlit as st
from datetime import date
from modules import visual_service as visual  
from database import repository as repo

st.set_page_config(page_title="Histórico Diário", page_icon="🗓️", layout="wide")
visual.injetar_css()

st.title("🗓️ Caderneta (Logbook)")
st.markdown("Consulte os dados de qualquer dia ou apague registros inseridos acidentalmente.")

# Seletor de data centralizado
col_vazia1, col_calendario, col_vazia2 = st.columns([1, 2, 1])
with col_calendario:
    data_selecionada = st.date_input("Selecione a data para inspecionar:", value=date.today())

st.divider()

col_esq, col_dir = st.columns(2, gap="large")

# ============================================================
# LADO ESQUERDO: TREINO E ÁGUA
# ============================================================
with col_esq:
    st.subheader("🏋️ Treinos")
    sessoes = [s for s in repo.listar_sessoes() if s.data == data_selecionada]
    
    if not sessoes:
        st.info("Nenhum treino registrado neste dia.")
    else:
        for sessao in sessoes:
            sessao_completa = repo.obter_sessao_completa(sessao.id)
            nome_rotina = sessao_completa.rotina.nome if sessao_completa.rotina else "Treino Avulso"
            
            with st.expander(f"Sessão: {nome_rotina}", expanded=True):
                if sessao_completa.series:
                    # Agrupa as séries pelo nome do exercício para ficar organizado
                    exercicios_dict = {}
                    for serie in sessao_completa.series:
                        nome_ex = serie.exercicio.nome
                        if nome_ex not in exercicios_dict:
                            exercicios_dict[nome_ex] = []
                        exercicios_dict[nome_ex].append(serie)
                    
                    for ex_nome, series_ex in exercicios_dict.items():
                        st.markdown(f"**{ex_nome}**")
                        # Ordena para garantir que Série 1 apareça antes da Série 2
                        for s in sorted(series_ex, key=lambda x: x.numero_serie):
                            c1, c2 = st.columns([4, 1])
                            c1.write(f"Série {s.numero_serie}: {s.carga_kg} kg × {s.reps} reps")
                            if c2.button("🗑️", key=f"del_serie_{s.id}", help="Excluir série"):
                                repo.remover_serie(s.id)
                                st.rerun()
                else:
                    st.caption("Sessão iniciada, mas nenhuma série foi gravada.")

    st.subheader("💧 Água")
    aguas = repo.listar_agua_dia(data_selecionada)
    if not aguas:
        st.info("Nenhum consumo de água registrado.")
    else:
        total_agua = sum(a.quantidade_ml for a in aguas)
        st.markdown(f"**Total do dia:** {total_agua} ml")
        for a in aguas:
            c1, c2 = st.columns([4, 1])
            hora = a.registrado_em.strftime("%H:%M") if a.registrado_em else "--:--"
            c1.write(f"• {a.quantidade_ml} ml ({hora})")
            if c2.button("🗑️", key=f"del_agua_{a.id}"):
                repo.remover_consumo_agua(a.id)
                st.rerun()

# ============================================================
# LADO DIREITO: ALIMENTAÇÃO E PESO
# ============================================================
with col_dir:
    st.subheader("🍽️ Alimentação")
    consumos = repo.listar_consumo_dia(data_selecionada)
    if not consumos:
        st.info("Nenhuma refeição registrada neste dia.")
    else:
        totais = repo.totais_macro_dia(data_selecionada)
        st.markdown(f"**Kcal:** {totais['kcal']:.0f} | **P:** {totais['proteina_g']:.0f}g | **C:** {totais['carboidrato_g']:.0f}g | **G:** {totais['lipideos_g']:.0f}g")
        
        for c in consumos:
            with st.container(border=True):
                c1, c2 = st.columns([5, 1])
                fator = c.quantidade_g / 100.0
                kcal = (c.alimento.kcal or 0) * fator
                
                c1.markdown(f"**{c.refeicao.title()}**: {c.alimento.nome}")
                c1.caption(f"{c.quantidade_g:.0f}g — {kcal:.0f} kcal")
                
                if c2.button("🗑️", key=f"del_alimento_{c.id}"):
                    repo.remover_consumo_alimento(c.id)
                    st.rerun()

    st.subheader("⚖️ Peso Corporal")
    # Busca manual simples para não criar função extra no repo à toa
    pesos = [p for p in repo.listar_pesos() if p.data == data_selecionada]
    if not pesos:
        st.info("Nenhum peso registrado neste dia.")
    else:
        for p in pesos:
            with st.container(border=True):
                c1, c2 = st.columns([5, 1])
                c1.markdown(f"**{p.peso_kg:.1f} kg**")
                if c2.button("🗑️", key=f"del_peso_{p.id}"):
                    repo.remover_peso(p.id)
                    st.rerun()