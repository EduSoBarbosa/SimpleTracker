import streamlit as st
import pandas as pd
from database import repository as repo
from modules import visual_service as visual  

# Configuração da página (mesmo padrão do main.py)
st.set_page_config(page_title="Gestão de Rotinas", page_icon="📋", layout="wide")
visual.injetar_css()

st.title("📋 Gestão de Rotinas e Exercícios")
st.markdown("Crie seus planos de treino, cadastre novos exercícios e defina suas metas de séries e cargas.")

# Abas para organizar o CRUD de forma limpa
aba_rotinas, aba_exercicios, aba_montar = st.tabs([
    "1️⃣ Minhas Rotinas", 
    "2️⃣ Banco de Exercícios",
    "3️⃣ Montar Treino" 
])

# ============================================================
# ABA 1: MINHAS ROTINAS
# ============================================================
with aba_rotinas:
    st.subheader("Criar Nova Rotina")
    with st.form("form_nova_rotina", clear_on_submit=True):
        nome_rotina = st.text_input("Nome da Rotina (ex: Treino A - Push, Treino B - Pull)")
        desc_rotina = st.text_area("Descrição ou Foco (opcional)")
        
        if st.form_submit_button("Salvar Rotina", type="primary"):
            if nome_rotina.strip():
                repo.criar_rotina(nome_rotina, desc_rotina)
                st.success(f"Rotina '{nome_rotina}' criada com sucesso!")
                st.rerun()
            else:
                st.warning("O nome da rotina é obrigatório.")
    
    st.divider()
    st.subheader("Rotinas Cadastradas")
    rotinas = repo.listar_rotinas(somente_ativas=False)
    
    if rotinas:
        for r in rotinas:
            with st.container(border=True):
                col1, col2, col3 = st.columns([4, 1, 1])
                
                col1.markdown(f"**{r.nome}**")
                if r.descricao:
                    col1.caption(r.descricao)
                
                status_badge = "🟢 Ativa" if r.ativa else "🔴 Inativa"
                col2.write(status_badge)
                
                # Botão para alternar status
                acao = "Desativar" if r.ativa else "Ativar"
                if col3.button(acao, key=f"btn_status_{r.id}", use_container_width=True):
                    repo.alternar_status_rotina(r.id, not r.ativa)
                    st.rerun()
    else:
        st.info("Nenhuma rotina cadastrada ainda.")

# ============================================================
# ABA 2: BANCO DE EXERCÍCIOS
# ============================================================
with aba_exercicios:
    st.subheader("Cadastrar Novo Exercício")
    with st.form("form_novo_exercicio", clear_on_submit=True):
        col_nome, col_grupo, col_equip = st.columns(3)
        
        nome_ex = col_nome.text_input("Nome do Exercício* (ex: Supino Reto)")
        grupo_ex = col_grupo.selectbox("Grupo Muscular", ["Peitoral", "Costas", "Pernas", "Ombros", "Biceps","Triceps" ,"Antebraço" ,"Core", "Cardio", "Outro"])
        equip_ex = col_equip.selectbox("Equipamento", ["Barra", "Halter", "Máquina", "Polia", "Peso Corporal", "Outro"])
        
        if st.form_submit_button("Salvar Exercício", type="primary"):
            if nome_ex.strip():
                if repo.buscar_exercicio_por_nome(nome_ex):
                    st.error("Já existe um exercício com este nome.")
                else:
                    repo.criar_exercicio(nome_ex, grupo_ex, equip_ex)
                    st.success(f"Exercício '{nome_ex}' cadastrado no banco!")
                    st.rerun()
            else:
                st.warning("O nome do exercício é obrigatório.")
    
    st.divider()
    st.subheader("Exercícios Cadastrados")
    exercicios = repo.listar_exercicios()
    
    if exercicios:
        # Usando Pandas para gerar uma tabela mais elegante no Streamlit
        df_ex = pd.DataFrame([{
            "Exercício": e.nome, 
            "Grupo": e.grupo_muscular, 
            "Equipamento": e.equipamento
        } for e in exercicios])
        st.dataframe(df_ex, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum exercício cadastrado no banco.")

# ============================================================
# ABA 3: MONTAR TREINO (Vínculo)
# ============================================================
with aba_montar:
    rotinas_ativas = repo.listar_rotinas(somente_ativas=True)
    exercicios = repo.listar_exercicios()
    
    if not rotinas_ativas:
        st.warning("⚠️ Você precisa criar e ativar pelo menos uma rotina na aba 'Minhas Rotinas'.")
    elif not exercicios:
        st.warning("⚠️ Você precisa cadastrar exercícios na aba 'Banco de Exercícios'.")
    else:
        # 1. Seleciona a Rotina alvo
        opcoes_rotina = {r.nome: r.id for r in rotinas_ativas}
        rotina_selecionada = st.selectbox("Selecione a Rotina para editar", list(opcoes_rotina.keys()))
        rotina_id = opcoes_rotina[rotina_selecionada]
        
        st.divider()
        
        col_form, col_lista = st.columns([1, 1], gap="large")
        
        # Lado esquerdo: Formulário para inserir exercício na rotina
        with col_form:
            st.subheader("Adicionar Exercício à Rotina")
            with st.form("form_add_exercicio", clear_on_submit=True):
                opcoes_ex = {e.nome: e.id for e in exercicios}
                ex_selecionado = st.selectbox("Escolha o Exercício", list(opcoes_ex.keys()))
                
                c_series, c_reps = st.columns(2)
                series = c_series.number_input("Séries Alvo", min_value=1, max_value=20, value=3)
                reps = c_reps.text_input("Reps Alvo (ex: 8-12)", value="8-12")
                
                carga = st.number_input("Carga Alvo (kg) - Opcional", min_value=0.0, step=1.0)
                
                if st.form_submit_button("Adicionar ao Treino", type="primary", use_container_width=True):
                    ex_id = opcoes_ex[ex_selecionado]
                    repo.adicionar_exercicio_rotina(
                        rotina_id=rotina_id, 
                        exercicio_id=ex_id, 
                        series_alvo=series, 
                        reps_alvo=reps, 
                        carga_alvo=carga if carga > 0 else None
                    )
                    st.success(f"'{ex_selecionado}' adicionado a {rotina_selecionada}!")
                    st.rerun()
        
        # Lado direito: Lista de exercícios atuais da rotina selecionada
        with col_lista:
            st.subheader(f"Exercícios em: {rotina_selecionada}")
            rotina_completa = repo.obter_rotina_completa(rotina_id)
            
            if rotina_completa and rotina_completa.exercicios:
                for vinculo in rotina_completa.exercicios:
                    with st.container(border=True):
                        c_info, c_btn = st.columns([5, 1])
                        
                        carga_str = f" • ⚖️ {vinculo.carga_alvo}kg" if vinculo.carga_alvo else ""
                        c_info.markdown(f"**{vinculo.exercicio.nome}**")
                        c_info.caption(f"🎯 {vinculo.series_alvo} séries x {vinculo.reps_alvo} reps {carga_str}")
                        
                        if c_btn.button("❌", key=f"del_vinc_{vinculo.id}", help="Remover exercício da rotina"):
                            repo.remover_exercicio_rotina(vinculo.id)
                            st.rerun()
            else:
                st.info("Nenhum exercício vinculado a esta rotina ainda.")