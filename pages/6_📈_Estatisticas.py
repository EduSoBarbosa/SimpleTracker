import streamlit as st
from datetime import date, timedelta
from modules import visual_service as visual  
from database import repository as repo
from modules import charts_service as charts

st.set_page_config(page_title="Analytics", page_icon="📈", layout="wide")
visual.injetar_css()

st.title("📈 Analytics e Desempenho")
st.markdown("Visualizações ricas de dados cruzando volume, carga, tendências corporais e aderência dietética.")

aba_forca, aba_peso, aba_nutri, aba_agua = st.tabs([
    "🏋️ Força & Volume", 
    "⚖️ Peso (Média Móvel)", 
    "🍽️ Nutrição (Kcal vs Macros)", 
    "💧 Hidratação"
])

# ============================================================
# 1. FORÇA E PROGRESSÃO (DUAL AXIS)
# ============================================================
with aba_forca:
    col_sel, col_chart = st.columns([1, 3])
    
    exercicios = repo.listar_exercicios()
    if exercicios:
        with col_sel:
            st.subheader("Análise Isolada")
            opcoes_ex = {e.nome: e.id for e in exercicios}
            ex_selecionado = st.selectbox("Selecione o Movimento", list(opcoes_ex.keys()))
            
            st.info(
                "💡 **Interpretação:**\n\n"
                "A linha verde brilhante calcula seu **1RM** projetado usando a fórmula de Epley. "
                "As barras de fundo mostram o **Volume Load** total do dia (Séries × Reps × Peso). "
                "Crescer os dois juntos é o ápice do *progressive overload*."
            )
            
        with col_chart:
            historico = repo.historico_exercicio(opcoes_ex[ex_selecionado])
            if historico:
                fig_1rm = charts.construir_grafico_forca_completo(historico)
                st.plotly_chart(fig_1rm, use_container_width=True, config={"displayModeBar": False}, theme=None)
            else:
                st.warning(f"Sem dados de hipertrofia suficientes para '{ex_selecionado}'.")
    else:
        st.info("Banco de exercícios vazio.")

# ============================================================
# 2. PESO CORPORAL (MÉDIA MÓVEL)
# ============================================================
with aba_peso:
    pesos = repo.listar_pesos()
    meta_ativa = repo.meta_peso_ativa()
    meta_kg = meta_ativa.peso_alvo_kg if meta_ativa else None
    
    if pesos:
        st.caption("A linha sólida filtra ruídos (como retenção hídrica) calculando a média dos últimos 7 dias de pesagem.")
        fig_peso = charts.construir_grafico_peso_avancado(pesos, meta_kg)
        st.plotly_chart(fig_peso, use_container_width=True, config={"displayModeBar": False}, theme=None)
    else:
        st.warning("Sem base de dados da balança.")

# ============================================================
# 3. NUTRIÇÃO (BARRAS EMPILHADAS + LINHA DE CALORIAS)
# ============================================================
with aba_nutri:
    dados_macros = []
    hoje = date.today()
    meta_macro = repo.meta_macro_ativa()
    teto_kcal = meta_macro.kcal_alvo if meta_macro else None
    
    for i in range(6, -1, -1):
        dia_alvo = hoje - timedelta(days=i)
        totais = repo.totais_macro_dia(dia_alvo)
        
        dados_macros.append({
            "data": dia_alvo.strftime("%d/%m"),
            "prot": totais["proteina_g"],
            "carb": totais["carboidrato_g"],
            "fat": totais["lipideos_g"],
            "kcal": totais["kcal"]
        })
        
    fig_macros = charts.construir_grafico_macros_avancado(dados_macros, teto_kcal)
    st.plotly_chart(fig_macros, use_container_width=True, config={"displayModeBar": False}, theme=None)

# ============================================================
# 4. ÁGUA (FORMATAÇÃO CONDICIONAL)
# ============================================================
with aba_agua:
    dados_agua = []
    hoje = date.today()
    meta_agua_obj = repo.meta_agua_ativa()
    meta_ml = meta_agua_obj.quantidade_ml_alvo if meta_agua_obj else None
    
    for i in range(6, -1, -1):
        dia_alvo = hoje - timedelta(days=i)
        total_ml = repo.total_agua_dia(dia_alvo)
        dados_agua.append({
            "data": dia_alvo.strftime("%d/%m"),
            "ml": total_ml
        })
        
    st.caption("As barras mudam dinamicamente para a cor de sucesso caso você tenha batido o *target* diário.")
    fig_agua = charts.construir_grafico_agua(dados_agua, meta_ml)
    st.plotly_chart(fig_agua, use_container_width=True, config={"displayModeBar": False}, theme=None)