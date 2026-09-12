import streamlit as st
from datetime import date, timedelta
from database import repository as repo
from modules import visual_service as visual  

st.set_page_config(page_title="Metas e Calculadoras", page_icon="🎯", layout="wide")
visual.injetar_css()

st.title("🎯 Planejamento e Metas")
st.markdown("Calcule suas necessidades diárias e defina seus objetivos para o app acompanhar.")

# ============================================================
# 1. CALCULADORAS (SUGESTÕES)
# ============================================================
st.header("📐 Calculadoras de Estimativa")

with st.container(border=True):
    col_inputs, col_results = st.columns([1, 2], gap="large")
    
    with col_inputs:
        st.subheader("Seus Dados")
        peso = st.number_input("Peso (kg)", min_value=30.0, max_value=250.0, value=89.0, step=0.1)
        altura = st.number_input("Altura (cm)", min_value=100, max_value=250, value=186, step=1)
        idade = st.number_input("Idade", min_value=10, max_value=100, value=20, step=1)
        
        atividade = st.selectbox(
            "Nível de Atividade",
            [
                "Sedentário (pouco ou nenhum exercício)",
                "Levemente Ativo (exercício leve 1-3 dias/sem)",
                "Moderadamente Ativo (exercício mod. 3-5 dias/sem)",
                "Muito Ativo (exercício pesado 6-7 dias/sem)",
                "Extremamente Ativo (trabalho físico ou treino 2x/dia)"
            ],
            index=3
        )
        
        objetivo = st.selectbox(
            "Objetivo Atual", 
            ["Cutting (Perda de Gordura)", "Manutenção", "Lean Bulk (Ganho Limpo)"],
            index=0
        )

    with col_results:
        tmb = (10 * peso) + (6.25 * altura) - (5 * idade) + 5
        
        fator_atividade = {
            "Sedentário (pouco ou nenhum exercício)": 1.2,
            "Levemente Ativo (exercício leve 1-3 dias/sem)": 1.375,
            "Moderadamente Ativo (exercício mod. 3-5 dias/sem)": 1.55,
            "Muito Ativo (exercício pesado 6-7 dias/sem)": 1.725,
            "Extremamente Ativo (trabalho físico ou treino 2x/dia)": 1.9
        }[atividade]
        
        tdee = tmb * fator_atividade
        
        ajuste_calorico = {
            "Cutting (Perda de Gordura)": -500,
            "Manutenção": 0,
            "Lean Bulk (Ganho Limpo)": 300
        }[objetivo]
        
        calorias_alvo = tdee + ajuste_calorico
        agua_sugerida = peso * 35
        
        st.subheader("Gasto Energético Diário (TDEE)")
        st.markdown(f"Seu corpo gasta aproximadamente **{tdee:,.0f} kcal/dia** para manter o peso atual.")
        st.markdown(f"Para o objetivo de **{objetivo}**, sua meta sugerida é de **{calorias_alvo:,.0f} kcal/dia**.")
        
        st.divider()
        st.subheader("Distribuição de Macronutrientes")
        
        c_mod, c_low, c_high = st.columns(3)
        
        def render_macro_card(col, titulo, pct_prot, pct_fat, pct_carb):
            prot_g = (calorias_alvo * pct_prot) / 4
            fat_g = (calorias_alvo * pct_fat) / 9
            carb_g = (calorias_alvo * pct_carb) / 4
            
            with col:
                st.markdown(f"**{titulo}**")
                with st.container(border=True):
                    st.metric("Proteína (g)", f"{prot_g:.0f}g")
                    st.metric("Gorduras (g)", f"{fat_g:.0f}g")
                    st.metric("Carbos (g)", f"{carb_g:.0f}g")
        
        render_macro_card(c_mod, "Moderate Carb (30/35/35)", 0.30, 0.35, 0.35)
        render_macro_card(c_low, "Lower Carb (40/40/20)", 0.40, 0.40, 0.20)
        render_macro_card(c_high, "Higher Carb (30/20/50)", 0.30, 0.20, 0.50)
        
        st.caption("Atenção: A calculadora é uma estimativa. Ajuste os valores com base na sua resposta no espelho e na balança.")

# ============================================================
# 2. SALVAR METAS NO BANCO
# ============================================================
st.header("💾 Salvar Metas Ativas")
st.markdown("Preencha abaixo para ativar as metas no sistema.")

# Adicionamos a aba de Força aqui!
aba_macros, aba_agua, aba_peso, aba_forca = st.tabs(["🍽️ Macros & Kcal", "💧 Água", "⚖️ Peso Corporal", "🏋️ Metas de Força"])

with aba_macros:
    with st.form("form_meta_macros"):
        st.write("Defina sua meta diária nutricional:")
        col_k, col_p, col_c, col_g = st.columns(4)
        
        kcal_input = col_k.number_input("Calorias (kcal)", value=int(calorias_alvo), step=50)
        prot_input = col_p.number_input("Proteína (g)", value=int((calorias_alvo * 0.40)/4), step=5)
        carb_input = col_c.number_input("Carboidrato (g)", value=int((calorias_alvo * 0.20)/4), step=5)
        fat_input = col_g.number_input("Gordura (g)", value=int((calorias_alvo * 0.40)/9), step=5)
        
        if st.form_submit_button("Salvar Meta de Macros", type="primary"):
            repo.criar_meta_macro(kcal_input, prot_input, carb_input, fat_input)
            st.success("Meta de macros atualizada! O dashboard agora refletirá esses valores.")

with aba_agua:
    with st.form("form_meta_agua"):
        st.write("Defina sua meta diária de hidratação:")
        st.info(f"💡 Sugestão para o seu peso: **{agua_sugerida:,.0f} ml** por dia.")
        
        agua_input = st.number_input("Meta de Água (ml)", value=int(agua_sugerida), step=100)
        
        if st.form_submit_button("Salvar Meta de Água", type="primary"):
            repo.criar_meta_agua(agua_input)
            st.success("Meta de água atualizada!")

with aba_peso:
    with st.form("form_meta_peso"):
        st.write("Defina seu próximo objetivo na balança:")
        col_pa, col_pz = st.columns(2)
        
        peso_alvo = col_pa.number_input("Peso Alvo (kg)", min_value=30.0, max_value=200.0, value=85.0, step=0.5)
        prazo_alvo = col_pz.date_input("Prazo para atingir", value=date.today() + timedelta(days=90))
        
        if st.form_submit_button("Salvar Meta de Peso", type="primary"):
            repo.criar_meta_peso(peso_alvo_kg=peso_alvo, prazo=prazo_alvo)
            st.success(f"Meta definida! Rumo aos {peso_alvo} kg.")

# ============================================================
# NOVA ABA: METAS DE FORÇA
# ============================================================
with aba_forca:
    st.subheader("💪 Novo Desafio de PR")
    
    exercicios = repo.listar_exercicios()
    
    if not exercicios:
        st.warning("⚠️ Você precisa cadastrar exercícios primeiro na página de Rotinas.")
    else:
        with st.form("form_meta_forca", clear_on_submit=True):
            opcoes_ex = {e.nome: e.id for e in exercicios}
            ex_selecionado = st.selectbox("Exercício", list(opcoes_ex.keys()))
            
            col_c, col_r, col_p = st.columns(3)
            carga_alvo = col_c.number_input("Carga Alvo (kg)", min_value=0.0, step=1.0)
            reps_alvo = col_r.number_input("Reps Alvo", min_value=1, step=1, value=1)
            prazo = col_p.date_input("Prazo (Opcional)", value=date.today() + timedelta(days=60))
            
            if st.form_submit_button("Lançar Desafio", type="primary"):
                if carga_alvo > 0:
                    repo.criar_meta_forca(opcoes_ex[ex_selecionado], carga_alvo, reps_alvo, prazo)
                    st.success(f"Meta de força para {ex_selecionado} registrada! Bora treinar.")
                    st.rerun()
                else:
                    st.error("Insira uma carga válida.")
        
        st.divider()
        
        # Puxamos TODAS as metas passando somente_pendentes=False
        todas_metas = repo.listar_metas_forca(somente_pendentes=False)
        metas_pendentes = [m for m in todas_metas if not m.concluida]
        metas_concluidas = [m for m in todas_metas if m.concluida]
        
        col_pendentes, col_batidas = st.columns(2, gap="large")
        
        # Lado Esquerdo: Metas ativas
        with col_pendentes:
            st.subheader("⏳ Em Busca do PR")
            if metas_pendentes:
                for m in metas_pendentes:
                    with st.container(border=True):
                        st.markdown(f"**{m.exercicio.nome}**")
                        st.write(f"🎯 Meta: **{m.carga_alvo_kg} kg** × **{m.reps_alvo} reps**")
                        if m.prazo:
                            # Muda a cor do texto se o prazo estiver perto ou vencido
                            dias_restantes = (m.prazo - date.today()).days
                            if dias_restantes < 0:
                                st.error(f"⚠️ Prazo vencido ({m.prazo.strftime('%d/%m/%Y')})")
                            elif dias_restantes <= 7:
                                st.warning(f"⏳ Terminando em {dias_restantes} dias")
                            else:
                                st.caption(f"📅 Prazo: {m.prazo.strftime('%d/%m/%Y')}")
                        
                        if st.button("🔥 Bati essa meta!", key=f"concluir_{m.id}", use_container_width=True):
                            repo.concluir_meta_forca(m.id)
                            st.balloons() # Celebração na tela
                            st.rerun()
            else:
                st.info("Nenhum desafio em aberto no momento.")
                
        # Lado Direito: Hall da Fama
        with col_batidas:
            st.subheader("🏆 Hall da Fama")
            if metas_concluidas:
                # Mostra as mais recentes primeiro
                metas_concluidas.sort(key=lambda x: x.concluida_em or date.min, reverse=True)
                for m in metas_concluidas:
                    with st.container(border=True):
                        # Card com visual de sucesso
                        st.markdown(f"### 🎉 {m.exercicio.nome}")
                        st.success(f"💪 **Alcançou:** {m.carga_alvo_kg} kg × {m.reps_alvo} reps")
                        if m.concluida_em:
                            st.caption(f"✅ Conquistado em: {m.concluida_em.strftime('%d/%m/%Y')}")
            else:
                st.info("Sinta o gosto da vitória! Suas metas batidas aparecerão aqui.")