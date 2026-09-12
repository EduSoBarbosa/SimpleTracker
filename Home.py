from datetime import date

import streamlit as st

from database.engine import init_db
from database import repository as repo
from modules import visual_service as visual
from modules import charts_service as charts

FOTO_PERFIL_PATH = "foto_perfil/perfil.png"
NOME_USUARIO = "Nome do Usuário"

st.set_page_config(page_title="SimpleTracker", page_icon="💪", layout="wide")
init_db()


# ============================================================
# CABEÇALHO: foto de perfil + heatmap de frequência
# ============================================================

def renderizar_heatmap_frequencia():
    sessoes = repo.listar_sessoes()
    datas_treino = [s.data for s in sessoes]

    streak = charts.calcular_streak(datas_treino)
    total_ultimos_365 = len([d for d in datas_treino if (date.today() - d).days <= 365])

    st.markdown(
        f"**{NOME_USUARIO}** &nbsp;•&nbsp; "
        f'<span class="streak-badge">🔥 {streak} dia(s) seguidos</span> &nbsp;•&nbsp; '
        f"{total_ultimos_365} treinos nos últimos 365 dias",
        unsafe_allow_html=True,
    )

    z, hover, meses = charts.gerar_dados_heatmap(datas_treino, semanas=26)
    fig = charts.construir_figura_heatmap(z, hover, meses)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


# ============================================================
# DASHBOARD: cards de resumo
# ============================================================

def renderizar_dashboard():
    col1, col2, col3, col4 = st.columns(4)

    # --- Peso ---
    with col1:
        peso_atual = repo.peso_mais_recente()
        meta_peso = repo.meta_peso_ativa()
        if peso_atual:
            delta = None
            if meta_peso:
                diferenca = round(peso_atual.peso_kg - meta_peso.peso_alvo_kg, 1)
                delta = f"{diferenca:+.1f} kg da meta"
            st.metric("⚖️ Peso atual", f"{peso_atual.peso_kg:.1f} kg", delta)
        else:
            st.metric("⚖️ Peso atual", "sem registro")

    # --- Água ---
    with col2:
        total_agua = repo.total_agua_dia()
        meta_agua = repo.meta_agua_ativa()
        alvo_agua = meta_agua.quantidade_ml_alvo if meta_agua else 3000
        st.metric("💧 Água hoje", f"{total_agua} ml", f"meta: {alvo_agua} ml")
        st.progress(min(total_agua / alvo_agua, 1.0) if alvo_agua else 0)

    # --- Macros ---
    with col3:
        totais = repo.totais_macro_dia()
        meta_macro = repo.meta_macro_ativa()
        kcal_alvo = meta_macro.kcal_alvo if meta_macro and meta_macro.kcal_alvo else None
        if kcal_alvo:
            st.metric("🍽️ Kcal hoje", f"{totais['kcal']:.0f}", f"meta: {kcal_alvo:.0f}")
            st.progress(min(totais["kcal"] / kcal_alvo, 1.0))
        else:
            st.metric("🍽️ Kcal hoje", f"{totais['kcal']:.0f}", "sem meta definida")

    # --- Próximo treino ---
    with col4:
        rotinas = repo.listar_rotinas(somente_ativas=True)
        sessoes = repo.listar_sessoes(limite=1)
        if rotinas:
            if sessoes and sessoes[0].rotina_id:
                ids_ativas = [r.id for r in rotinas]
                if sessoes[0].rotina_id in ids_ativas:
                    idx_atual = ids_ativas.index(sessoes[0].rotina_id)
                    proxima = rotinas[(idx_atual + 1) % len(rotinas)]
                else:
                    proxima = rotinas[0]
            else:
                proxima = rotinas[0]
            st.metric("🏋️ Próximo treino", proxima.nome)
        else:
            st.metric("🏋️ Próximo treino", "nenhuma rotina")


# ============================================================
# OBJETIVOS EM ANDAMENTO (Metas e Força)
# ============================================================

def renderizar_metas_e_desafios():
    st.markdown("### 🎯 Objetivos em Andamento")
    col_metas, col_forca = st.columns(2, gap="large")

    with col_metas:
        st.markdown("##### 📌 Foco Atual")
        meta_peso = repo.meta_peso_ativa()
        meta_macro = repo.meta_macro_ativa()

        with st.container(border=True):
            if meta_peso:
                dias_restantes = (meta_peso.prazo - date.today()).days if meta_peso.prazo else 0
                st.markdown(f"**⚖️ Peso Alvo:** {meta_peso.peso_alvo_kg} kg *(Prazo: {dias_restantes} dias)*")
            else:
                st.markdown("**⚖️ Peso Alvo:** Não definido")

            if meta_macro:
                st.markdown(f"**🍽️ Macros:** {meta_macro.kcal_alvo} kcal (P: {meta_macro.proteina_g_alvo}g | C: {meta_macro.carboidrato_g_alvo}g | G: {meta_macro.lipideos_g_alvo}g)")
            else:
                st.markdown("**🍽️ Macros:** Não definidos")

    with col_forca:
        st.markdown("##### 🏋️ Marcos de Força a Bater")
        metas_forca = repo.listar_metas_forca(somente_pendentes=True)

        with st.container(border=True):
            if metas_forca:
                # Mostra apenas as 4 primeiras para não quebrar a altura do container
                for m in metas_forca[:4]:
                    dias_txt = ""
                    if m.prazo:
                        dias = (m.prazo - date.today()).days
                        dias_txt = f" *(⏳ {dias}d)*" if dias >= 0 else " *(⚠️ Vencido)*"
                    st.markdown(f"- **{m.exercicio.nome}**: {m.carga_alvo_kg}kg x {m.reps_alvo}{dias_txt}")
                
                if len(metas_forca) > 4:
                    st.caption(f"+ {len(metas_forca)-4} outras metas pendentes (veja na página Metas)")
            else:
                st.markdown("Nenhum PR pendente. Defina novos desafios na página de Metas!")


# ============================================================
# AÇÕES RÁPIDAS (inserts)
# ============================================================

def renderizar_acoes_rapidas():
    st.markdown("### Registrar agora")
    aba_peso, aba_agua, aba_refeicao, aba_treino = st.tabs(
        ["⚖️ Peso", "💧 Água", "🍽️ Refeição", "🏋️ Treino"]
    )

    # --- Peso ---
    with aba_peso:
        with st.form("form_peso", clear_on_submit=True):
            peso_valor = st.number_input("Peso (kg)", min_value=0.0, max_value=300.0, step=0.1)
            enviado = st.form_submit_button("Salvar peso")
            if enviado and peso_valor > 0:
                repo.registrar_peso(peso_valor)
                st.success(f"Peso de {peso_valor} kg registrado!")
                st.rerun()

    # --- Água ---
    with aba_agua:
        st.write("Adicionar rápido:")
        botoes = st.columns(4)
        valores_rapidos = [200, 300, 500, 750]
        for col, valor in zip(botoes, valores_rapidos):
            with col:
                if st.button(f"+{valor} ml", key=f"agua_{valor}", width="stretch"):
                    repo.registrar_agua(valor)
                    st.toast(f"+{valor} ml registrados!")
                    st.rerun()

        with st.expander("Outra quantidade"):
            qtd_custom = st.number_input("ml", min_value=0, max_value=5000, step=50, key="agua_custom")
            if st.button("Registrar", key="btn_agua_custom") and qtd_custom > 0:
                repo.registrar_agua(qtd_custom)
                st.success(f"{qtd_custom} ml registrados!")
                st.rerun()

    # --- Refeição ---
    with aba_refeicao:
        termo = st.text_input("Buscar alimento", placeholder="ex: arroz, frango, banana...")
        if termo:
            resultados = repo.buscar_alimentos(termo)
            if resultados:
                opcoes = {f"{a.nome} ({a.categoria})": a.id for a in resultados}
                escolha = st.selectbox("Selecione o alimento", list(opcoes.keys()))
                col_a, col_b = st.columns(2)
                with col_a:
                    quantidade = st.number_input("Quantidade (g)", min_value=1, value=100, step=10)
                with col_b:
                    refeicao = st.selectbox("Refeição", ["café da manhã", "almoço", "lanche", "jantar"])
                if st.button("Registrar consumo"):
                    repo.registrar_consumo(opcoes[escolha], quantidade, refeicao=refeicao)
                    st.success(f"{escolha} registrado!")
                    st.rerun()
            else:
                st.info("Nenhum alimento encontrado com esse termo.")

    # --- Treino ---
    with aba_treino:
        rotinas = repo.listar_rotinas(somente_ativas=True)
        if rotinas:
            opcoes_rotina = {r.nome: r.id for r in rotinas}
            escolha_rotina = st.selectbox("Rotina de hoje", list(opcoes_rotina.keys()))
            if st.button("Iniciar treino de hoje", type="primary"):
                sessao_id = repo.criar_sessao(rotina_id=opcoes_rotina[escolha_rotina])
                st.session_state["sessao_ativa_id"] = sessao_id
                st.success(
                    f"Treino '{escolha_rotina}' iniciado! "
                    "Vá para a página de Treino para registrar as séries."
                )
        else:
            st.info("Nenhuma rotina cadastrada ainda.")


# ============================================================
# LAYOUT PRINCIPAL
# ============================================================

def main():
    visual.injetar_css()

    col_foto, col_heatmap = st.columns([1, 4])
    with col_foto:
        visual.renderizar_foto_perfil(FOTO_PERFIL_PATH, NOME_USUARIO)
    with col_heatmap:
        renderizar_heatmap_frequencia()

    st.divider()
    renderizar_dashboard()
    
    st.divider()
    renderizar_metas_e_desafios()

    st.divider()
    renderizar_acoes_rapidas()


if __name__ == "__main__":
    main()