from datetime import date
import streamlit as st
import pandas as pd
from modules import visual_service as visual  
from database import repository as repo

st.set_page_config(page_title="Diário Alimentar", page_icon="🍽️", layout="wide")
visual.injetar_css()
st.title("🍽️ Diário Alimentar e Macros")

# ============================================================
# 1. RESUMO DOS MACROS DO DIA (DASHBOARD NUTRICIONAL)
# ============================================================
st.subheader("Resumo de Hoje")

totais = repo.totais_macro_dia()
meta = repo.meta_macro_ativa()

# Valores padrão de meta caso não existam no banco
meta_kcal = meta.kcal_alvo if meta and meta.kcal_alvo else 2500
meta_prot = meta.proteina_g_alvo if meta and meta.proteina_g_alvo else 160
meta_carb = meta.carboidrato_g_alvo if meta and meta.carboidrato_g_alvo else 250
meta_gord = meta.lipideos_g_alvo if meta and meta.lipideos_g_alvo else 70

col1, col2, col3, col4 = st.columns(4)

def exibir_macro(coluna, titulo, consumido, alvo, unidade="g"):
    with coluna:
        st.metric(titulo, f"{consumido:.0f} {unidade}", f"Meta: {alvo:.0f} {unidade}")
        progresso = min(consumido / alvo, 1.0) if alvo > 0 else 0
        st.progress(progresso)

exibir_macro(col1, "🔥 Calorias", totais["kcal"], meta_kcal, "kcal")
exibir_macro(col2, "🥩 Proteínas", totais["proteina_g"], meta_prot)
exibir_macro(col3, "🍞 Carboidratos", totais["carboidrato_g"], meta_carb)
exibir_macro(col4, "🥑 Gorduras", totais["lipideos_g"], meta_gord)

st.divider()

# ============================================================
# 2. ADICIONAR NOVA REFEIÇÃO (BUSCA NA TACO)
# ============================================================
col_add, col_lista = st.columns([1, 2], gap="large")

with col_add:
    st.subheader("Registrar Consumo")
    
    # Motor de busca
    termo_busca = st.text_input("🔍 Buscar alimento", placeholder="Ex: frango, arroz, whey...")
    
    if termo_busca:
        resultados = repo.buscar_alimentos(termo_busca)
        
        if resultados:
            with st.form("form_consumo", clear_on_submit=True):
                opcoes = {
                    f"{a.nome} ({a.kcal or 0:.0f} kcal/100g)": a.id 
                    for a in resultados
                }
                
                escolha = st.selectbox("Selecione o alimento exato", list(opcoes.keys()))
                refeicao = st.selectbox("Refeição", ["Café da Manhã", "Almoço", "Lanche", "Jantar", "Pré-Treino", "Pós-Treino"])
                quantidade = st.number_input("Quantidade (gramas/ml)", min_value=1.0, value=100.0, step=10.0)
                
                submit = st.form_submit_button("Salvar Refeição", type="primary", use_container_width=True)
                
                if submit:
                    repo.registrar_consumo(
                        alimento_id=opcoes[escolha],
                        quantidade_g=quantidade,
                        refeicao=refeicao
                    )
                    st.success("Refeição registrada!")
                    st.rerun()
        else:
            st.warning("Nenhum alimento encontrado com esse nome.")
    
    # Novo bloco: Formulário oculto para cadastrar alimentos fora da base
    with st.expander("➕ Não achou? Cadastre um alimento"):
        with st.form("form_novo_alimento", clear_on_submit=True):
            st.caption("Insira os valores nutricionais referentes a **100g** ou **100ml** do produto.")
            novo_nome = st.text_input("Nome do Alimento (ex: Whey Protein Growth)")
            
            c1, c2 = st.columns(2)
            c3, c4 = st.columns(2)
            
            novo_kcal = c1.number_input("Kcal", min_value=0.0, step=1.0)
            novo_prot = c2.number_input("Proteína (g)", min_value=0.0, step=0.1)
            novo_carb = c3.number_input("Carboidrato (g)", min_value=0.0, step=0.1)
            novo_gord = c4.number_input("Gordura (g)", min_value=0.0, step=0.1)
            
            if st.form_submit_button("Salvar no Banco de Alimentos", use_container_width=True):
                if novo_nome.strip():
                    repo.criar_alimento_customizado(
                        nome=novo_nome.strip(),
                        kcal=novo_kcal,
                        proteina_g=novo_prot,
                        carboidrato_g=novo_carb,
                        lipideos_g=novo_gord
                    )
                    st.success(f"'{novo_nome}' salvo! Digite o nome na busca acima para consumir.")
                else:
                    st.error("O nome do alimento é obrigatório.")

# ============================================================
# 3. HISTÓRICO DO QUE VOCÊ COMEU HOJE
# ============================================================
with col_lista:
    st.subheader(f"Refeições de Hoje ({date.today().strftime('%d/%m/%Y')})")
    
    consumos = repo.listar_consumo_dia()
    
    if consumos:
        dados_tabela = []
        for c in consumos:
            fator = c.quantidade_g / 100.0
            dados_tabela.append({
                "Refeição": c.refeicao.title() if c.refeicao else "-",
                "Alimento": c.alimento.nome,
                "Qtd": f"{c.quantidade_g:.0f} g",
                "Kcal": f"{(c.alimento.kcal or 0) * fator:.1f}",
                "Prot (g)": f"{(c.alimento.proteina_g or 0) * fator:.1f}",
                "Carb (g)": f"{(c.alimento.carboidrato_g or 0) * fator:.1f}",
                "Gord (g)": f"{(c.alimento.lipideos_g or 0) * fator:.1f}"
            })
            
        df = pd.DataFrame(dados_tabela)
        
        # Exibe o dataframe de forma estilizada
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    else:
        st.info("Nenhuma refeição registrada hoje. Comece adicionando ao lado!")