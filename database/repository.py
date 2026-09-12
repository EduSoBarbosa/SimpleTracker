from datetime import date
from sqlalchemy.orm import joinedload

from database.engine import get_session
from database.models import (
    Rotina, Exercicio, RotinaExercicio, SessaoTreino, SerieRealizada,
    PesoCorporal, ConsumoAgua, TacoAlimento, ConsumoAlimento,
    MetaForca, MetaPesoCorporal, MetaAgua, MetaMacro,
)


# ============================================================
# EXERCÍCIOS
# ============================================================

def criar_exercicio(nome, grupo_muscular=None, equipamento=None):
    session = get_session()
    try:
        ex = Exercicio(nome=nome, grupo_muscular=grupo_muscular, equipamento=equipamento)
        session.add(ex)
        session.commit()
        session.refresh(ex)
        return ex.id
    finally:
        session.close()


def listar_exercicios():
    session = get_session()
    try:
        return session.query(Exercicio).order_by(Exercicio.nome).all()
    finally:
        session.close()


def buscar_exercicio_por_nome(nome):
    session = get_session()
    try:
        return session.query(Exercicio).filter_by(nome=nome).first()
    finally:
        session.close()


# ============================================================
# ROTINAS
# ============================================================

def criar_rotina(nome, descricao=None):
    session = get_session()
    try:
        rotina = Rotina(nome=nome, descricao=descricao)
        session.add(rotina)
        session.commit()
        session.refresh(rotina)
        return rotina.id
    finally:
        session.close()


def listar_rotinas(somente_ativas=True):
    session = get_session()
    try:
        query = session.query(Rotina)
        if somente_ativas:
            query = query.filter_by(ativa=True)
        return query.order_by(Rotina.criada_em.desc()).all()
    finally:
        session.close()


def adicionar_exercicio_rotina(rotina_id, exercicio_id, ordem=0,
                                series_alvo=None, reps_alvo=None, carga_alvo=None):
    session = get_session()
    try:
        vinculo = RotinaExercicio(
            rotina_id=rotina_id,
            exercicio_id=exercicio_id,
            ordem=ordem,
            series_alvo=series_alvo,
            reps_alvo=reps_alvo,
            carga_alvo=carga_alvo,
        )
        session.add(vinculo)
        session.commit()
        return vinculo.id
    finally:
        session.close()


def obter_rotina_completa(rotina_id):
    """Retorna a rotina com exercícios (e seus dados) já carregados."""
    session = get_session()
    try:
        return (
            session.query(Rotina)
            .options(joinedload(Rotina.exercicios).joinedload(RotinaExercicio.exercicio))
            .filter_by(id=rotina_id)
            .first()
        )
    finally:
        session.close()
        
def alternar_status_rotina(rotina_id, ativa: bool):
    session = get_session()
    try:
        rotina = session.query(Rotina).filter_by(id=rotina_id).first()
        if rotina:
            rotina.ativa = ativa
            session.commit()
            return True
        return False
    finally:
        session.close()

def remover_exercicio_rotina(vinculo_id):
    session = get_session()
    try:
        vinculo = session.query(RotinaExercicio).filter_by(id=vinculo_id).first()
        if vinculo:
            session.delete(vinculo)
            session.commit()
            return True
        return False
    finally:
        session.close()


# ============================================================
# SESSÕES DE TREINO
# ============================================================

def criar_sessao(rotina_id=None, data_sessao=None, observacoes=None):
    session = get_session()
    try:
        sessao = SessaoTreino(
            rotina_id=rotina_id,
            data=data_sessao or date.today(),
            observacoes=observacoes,
        )
        session.add(sessao)
        session.commit()
        session.refresh(sessao)
        return sessao.id
    finally:
        session.close()


def registrar_serie(sessao_id, exercicio_id, numero_serie, reps=None, carga_kg=None, rpe=None):
    session = get_session()
    try:
        serie = SerieRealizada(
            sessao_id=sessao_id,
            exercicio_id=exercicio_id,
            numero_serie=numero_serie,
            reps=reps,
            carga_kg=carga_kg,
            rpe=rpe,
        )
        session.add(serie)
        session.commit()
        return serie.id
    finally:
        session.close()


def listar_sessoes(limite=None):
    session = get_session()
    try:
        query = session.query(SessaoTreino).order_by(SessaoTreino.data.desc())
        if limite:
            query = query.limit(limite)
        return query.all()
    finally:
        session.close()


def obter_sessao_completa(sessao_id):
    """Retorna a sessão com todas as séries e seus exercícios já carregados."""
    session = get_session()
    try:
        return (
            session.query(SessaoTreino)
            .options(joinedload(SessaoTreino.series).joinedload(SerieRealizada.exercicio))
            .filter_by(id=sessao_id)
            .first()
        )
    finally:
        session.close()


def historico_exercicio(exercicio_id):
    """Lista (data, carga_kg, reps) de todas as séries de um exercício, ordenado por data.
    Base para gráficos de evolução de carga/volume no Plotly."""
    session = get_session()
    try:
        resultados = (
            session.query(SessaoTreino.data, SerieRealizada.carga_kg, SerieRealizada.reps)
            .join(SerieRealizada, SerieRealizada.sessao_id == SessaoTreino.id)
            .filter(SerieRealizada.exercicio_id == exercicio_id)
            .order_by(SessaoTreino.data.asc())
            .all()
        )
        return [{"data": r[0], "carga_kg": r[1], "reps": r[2]} for r in resultados]
    finally:
        session.close()


# ============================================================
# PESO CORPORAL
# ============================================================

def registrar_peso(peso_kg, data_registro=None):
    """Insere ou atualiza (upsert) o peso do dia, já que é único por data."""
    data_registro = data_registro or date.today()
    session = get_session()
    try:
        existente = session.query(PesoCorporal).filter_by(data=data_registro).first()
        if existente:
            existente.peso_kg = peso_kg
            session.commit()
            return existente.id
        novo = PesoCorporal(data=data_registro, peso_kg=peso_kg)
        session.add(novo)
        session.commit()
        session.refresh(novo)
        return novo.id
    finally:
        session.close()


def listar_pesos():
    session = get_session()
    try:
        return session.query(PesoCorporal).order_by(PesoCorporal.data.asc()).all()
    finally:
        session.close()


def peso_mais_recente():
    session = get_session()
    try:
        return session.query(PesoCorporal).order_by(PesoCorporal.data.desc()).first()
    finally:
        session.close()


# ============================================================
# ÁGUA
# ============================================================

def registrar_agua(quantidade_ml, data_registro=None):
    session = get_session()
    try:
        registro = ConsumoAgua(quantidade_ml=quantidade_ml, data=data_registro or date.today())
        session.add(registro)
        session.commit()
        return registro.id
    finally:
        session.close()


def total_agua_dia(data_consulta=None):
    session = get_session()
    try:
        data_consulta = data_consulta or date.today()
        registros = session.query(ConsumoAgua).filter_by(data=data_consulta).all()
        return sum(r.quantidade_ml for r in registros)
    finally:
        session.close()


def listar_agua_dia(data_consulta=None):
    session = get_session()
    try:
        data_consulta = data_consulta or date.today()
        return (
            session.query(ConsumoAgua)
            .filter_by(data=data_consulta)
            .order_by(ConsumoAgua.registrado_em.asc())
            .all()
        )
    finally:
        session.close()


# ============================================================
# TACO (ALIMENTOS)
# ============================================================

def importar_alimentos_taco(lista_alimentos):
    """lista_alimentos: lista de dicts com as chaves do TacoAlimento (bulk insert para o seed)."""
    session = get_session()
    try:
        objetos = [TacoAlimento(**item) for item in lista_alimentos]
        session.bulk_save_objects(objetos)
        session.commit()
        return len(objetos)
    finally:
        session.close()


def buscar_alimentos(termo):
    """Busca por nome (case-insensitive, parcial) - usado no autocomplete do app."""
    session = get_session()
    try:
        return (
            session.query(TacoAlimento)
            .filter(TacoAlimento.nome.ilike(f"%{termo}%"))
            .order_by(TacoAlimento.nome)
            .limit(20)
            .all()
        )
    finally:
        session.close()


def listar_alimentos(categoria=None):
    session = get_session()
    try:
        query = session.query(TacoAlimento)
        if categoria:
            query = query.filter_by(categoria=categoria)
        return query.order_by(TacoAlimento.nome).all()
    finally:
        session.close()
        
def criar_alimento_customizado(nome, kcal, proteina_g, carboidrato_g, lipideos_g):
    session = get_session()
    try:
        # Verifica se já existe para evitar duplicação
        existente = session.query(TacoAlimento).filter(TacoAlimento.nome.ilike(nome)).first()
        if existente:
            return existente.id
            
        novo_alimento = TacoAlimento(
            nome=f"{nome} (Customizado)", # Tag para identificar facilmente na busca
            categoria="Customizado",
            kcal=kcal,
            proteina_g=proteina_g,
            carboidrato_g=carboidrato_g,
            lipideos_g=lipideos_g
        )
        session.add(novo_alimento)
        session.commit()
        return novo_alimento.id
    finally:
        session.close()


# ============================================================
# CONSUMO DE ALIMENTOS
# ============================================================

def registrar_consumo(alimento_id, quantidade_g, refeicao=None, data_registro=None):
    session = get_session()
    try:
        registro = ConsumoAlimento(
            alimento_id=alimento_id,
            quantidade_g=quantidade_g,
            refeicao=refeicao,
            data=data_registro or date.today(),
        )
        session.add(registro)
        session.commit()
        return registro.id
    finally:
        session.close()


def listar_consumo_dia(data_consulta=None):
    session = get_session()
    try:
        data_consulta = data_consulta or date.today()
        return (
            session.query(ConsumoAlimento)
            .options(joinedload(ConsumoAlimento.alimento))
            .filter_by(data=data_consulta)
            .all()
        )
    finally:
        session.close()


def totais_macro_dia(data_consulta=None):
    """Soma kcal/proteína/carbo/lipídeos consumidos no dia, calculado
    proporcionalmente à quantidade_g (valores TACO são por 100g)."""
    session = get_session()
    try:
        data_consulta = data_consulta or date.today()
        registros = (
            session.query(ConsumoAlimento)
            .options(joinedload(ConsumoAlimento.alimento))
            .filter_by(data=data_consulta)
            .all()
        )
        totais = {"kcal": 0.0, "proteina_g": 0.0, "carboidrato_g": 0.0, "lipideos_g": 0.0}
        for r in registros:
            fator = r.quantidade_g / 100.0
            totais["kcal"] += (r.alimento.kcal or 0) * fator
            totais["proteina_g"] += (r.alimento.proteina_g or 0) * fator
            totais["carboidrato_g"] += (r.alimento.carboidrato_g or 0) * fator
            totais["lipideos_g"] += (r.alimento.lipideos_g or 0) * fator
        return totais
    finally:
        session.close()


# ============================================================
# METAS - FORÇA
# ============================================================

def criar_meta_forca(exercicio_id, carga_alvo_kg, reps_alvo, prazo=None):
    session = get_session()
    try:
        meta = MetaForca(
            exercicio_id=exercicio_id,
            carga_alvo_kg=carga_alvo_kg,
            reps_alvo=reps_alvo,
            prazo=prazo,
        )
        session.add(meta)
        session.commit()
        return meta.id
    finally:
        session.close()


def listar_metas_forca(somente_pendentes=True):
    session = get_session()
    try:
        query = session.query(MetaForca).options(joinedload(MetaForca.exercicio))
        if somente_pendentes:
            query = query.filter_by(concluida=False)
        return query.all()
    finally:
        session.close()


def concluir_meta_forca(meta_id):
    session = get_session()
    try:
        meta = session.query(MetaForca).filter_by(id=meta_id).first()
        if meta:
            meta.concluida = True
            meta.concluida_em = date.today()
            session.commit()
        return meta is not None
    finally:
        session.close()


# ============================================================
# METAS - PESO CORPORAL
# ============================================================

def criar_meta_peso(peso_alvo_kg, prazo, peso_inicial_kg=None):
    if peso_inicial_kg is None:
        recente = peso_mais_recente()
        peso_inicial_kg = recente.peso_kg if recente else None

    session = get_session()
    try:
        meta = MetaPesoCorporal(
            peso_alvo_kg=peso_alvo_kg,
            peso_inicial_kg=peso_inicial_kg,
            prazo=prazo,
        )
        session.add(meta)
        session.commit()
        return meta.id
    finally:
        session.close()


def meta_peso_ativa():
    session = get_session()
    try:
        return (
            session.query(MetaPesoCorporal)
            .filter_by(concluida=False)
            .order_by(MetaPesoCorporal.data_criacao.desc())
            .first()
        )
    finally:
        session.close()


def concluir_meta_peso(meta_id):
    session = get_session()
    try:
        meta = session.query(MetaPesoCorporal).filter_by(id=meta_id).first()
        if meta:
            meta.concluida = True
            meta.concluida_em = date.today()
            session.commit()
        return meta is not None
    finally:
        session.close()


# ============================================================
# METAS - ÁGUA
# ============================================================

def criar_meta_agua(quantidade_ml_alvo):
    """Encerra a meta de água vigente (se houver) e cria uma nova."""
    session = get_session()
    try:
        vigente = (
            session.query(MetaAgua)
            .filter_by(ativa_ate=None)
            .order_by(MetaAgua.ativa_desde.desc())
            .first()
        )
        if vigente:
            vigente.ativa_ate = date.today()

        nova = MetaAgua(quantidade_ml_alvo=quantidade_ml_alvo)
        session.add(nova)
        session.commit()
        return nova.id
    finally:
        session.close()


def meta_agua_ativa():
    session = get_session()
    try:
        return session.query(MetaAgua).filter_by(ativa_ate=None).first()
    finally:
        session.close()


# ============================================================
# METAS - MACRO
# ============================================================

def criar_meta_macro(kcal_alvo=None, proteina_g_alvo=None, carboidrato_g_alvo=None, lipideos_g_alvo=None):
    """Encerra a meta de macro vigente (se houver) e cria uma nova."""
    session = get_session()
    try:
        vigente = (
            session.query(MetaMacro)
            .filter_by(ativa_ate=None)
            .order_by(MetaMacro.ativa_desde.desc())
            .first()
        )
        if vigente:
            vigente.ativa_ate = date.today()

        nova = MetaMacro(
            kcal_alvo=kcal_alvo,
            proteina_g_alvo=proteina_g_alvo,
            carboidrato_g_alvo=carboidrato_g_alvo,
            lipideos_g_alvo=lipideos_g_alvo,
        )
        session.add(nova)
        session.commit()
        return nova.id
    finally:
        session.close()


def meta_macro_ativa():
    session = get_session()
    try:
        return session.query(MetaMacro).filter_by(ativa_ate=None).first()
    finally:
        session.close()
        

# ============================================================
# EXCLUSÕES (LOGBOOK)
# ============================================================

def remover_serie(serie_id):
    session = get_session()
    try:
        serie = session.query(SerieRealizada).filter_by(id=serie_id).first()
        if serie:
            session.delete(serie)
            session.commit()
            return True
        return False
    finally:
        session.close()

def remover_consumo_agua(agua_id):
    session = get_session()
    try:
        registro = session.query(ConsumoAgua).filter_by(id=agua_id).first()
        if registro:
            session.delete(registro)
            session.commit()
            return True
        return False
    finally:
        session.close()

def remover_consumo_alimento(consumo_id):
    session = get_session()
    try:
        registro = session.query(ConsumoAlimento).filter_by(id=consumo_id).first()
        if registro:
            session.delete(registro)
            session.commit()
            return True
        return False
    finally:
        session.close()

def remover_peso(peso_id):
    session = get_session()
    try:
        registro = session.query(PesoCorporal).filter_by(id=peso_id).first()
        if registro:
            session.delete(registro)
            session.commit()
            return True
        return False
    finally:
        session.close()