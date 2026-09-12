from datetime import date, datetime
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime,
    ForeignKey, Boolean, Text
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# ---------- TREINO ----------

class Rotina(Base):
    """Ex: Rotina A, B, C - um plano de treino"""
    __tablename__ = "rotinas"

    id = Column(Integer, primary_key=True)
    nome = Column(String(50), nullable=False)       # "Treino A", "Push", etc
    descricao = Column(Text)
    ativa = Column(Boolean, default=True)
    criada_em = Column(DateTime, default=datetime.utcnow)

    exercicios = relationship("RotinaExercicio", back_populates="rotina", cascade="all, delete-orphan")
    sessoes = relationship("SessaoTreino", back_populates="rotina")


class Exercicio(Base):
    """Catálogo de exercícios (cadastro único, reutilizado em várias rotinas)"""
    __tablename__ = "exercicios"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False, unique=True)
    grupo_muscular = Column(String(50))   # peito, costas, perna...
    equipamento = Column(String(50))      # barra, halter, máquina...

    rotina_vinculos = relationship("RotinaExercicio", back_populates="exercicio")
    series = relationship("SerieRealizada", back_populates="exercicio")


class RotinaExercicio(Base):
    """Associação: quais exercícios pertencem a uma rotina, em que ordem, com que meta"""
    __tablename__ = "rotina_exercicios"

    id = Column(Integer, primary_key=True)
    rotina_id = Column(Integer, ForeignKey("rotinas.id"), nullable=False)
    exercicio_id = Column(Integer, ForeignKey("exercicios.id"), nullable=False)
    ordem = Column(Integer, default=0)
    series_alvo = Column(Integer)
    reps_alvo = Column(String(20))    # "8-12" ou "10"
    carga_alvo = Column(Float)        # opcional, kg

    rotina = relationship("Rotina", back_populates="exercicios")
    exercicio = relationship("Exercicio", back_populates="rotina_vinculos")


class SessaoTreino(Base):
    """Uma sessão de treino realizada (ex: treino de hoje)"""
    __tablename__ = "sessoes_treino"

    id = Column(Integer, primary_key=True)
    rotina_id = Column(Integer, ForeignKey("rotinas.id"), nullable=True)
    data = Column(Date, default=date.today, nullable=False)
    observacoes = Column(Text)

    rotina = relationship("Rotina", back_populates="sessoes")
    series = relationship("SerieRealizada", back_populates="sessao", cascade="all, delete-orphan")


class SerieRealizada(Base):
    """Cada série executada dentro de uma sessão (o dado bruto pra gráfico de evolução)"""
    __tablename__ = "series_realizadas"

    id = Column(Integer, primary_key=True)
    sessao_id = Column(Integer, ForeignKey("sessoes_treino.id"), nullable=False)
    exercicio_id = Column(Integer, ForeignKey("exercicios.id"), nullable=False)
    numero_serie = Column(Integer, nullable=False)
    reps = Column(Integer)
    carga_kg = Column(Float)
    rpe = Column(Float)  # percepção de esforço, opcional

    sessao = relationship("SessaoTreino", back_populates="series")
    exercicio = relationship("Exercicio", back_populates="series")


# ---------- CORPO ----------

class PesoCorporal(Base):
    """Registro diário/periódico de peso"""
    __tablename__ = "peso_corporal"

    id = Column(Integer, primary_key=True)
    data = Column(Date, default=date.today, nullable=False, unique=True)
    peso_kg = Column(Float, nullable=False)


# ---------- HIDRATAÇÃO ----------

class ConsumoAgua(Base):
    """Registros de água ao longo do dia (pode ter vários por dia)"""
    __tablename__ = "consumo_agua"

    id = Column(Integer, primary_key=True)
    data = Column(Date, default=date.today, nullable=False)
    quantidade_ml = Column(Integer, nullable=False)
    registrado_em = Column(DateTime, default=datetime.utcnow)


# ---------- NUTRIÇÃO (TACO) ----------

class TacoAlimento(Base):
    """Tabela de referência TACO - valores por 100g, carregada uma vez via seed/import"""
    __tablename__ = "taco_alimentos"

    id = Column(Integer, primary_key=True)
    nome = Column(String(150), nullable=False)
    categoria = Column(String(80))
    kcal = Column(Float)
    proteina_g = Column(Float)
    carboidrato_g = Column(Float)
    lipideos_g = Column(Float)
    fibra_g = Column(Float)
    sodio_mg = Column(Float)

    consumos = relationship("ConsumoAlimento", back_populates="alimento")


class ConsumoAlimento(Base):
    """Log do que foi comido, referenciando a tabela TACO"""
    __tablename__ = "consumo_alimentos"

    id = Column(Integer, primary_key=True)
    alimento_id = Column(Integer, ForeignKey("taco_alimentos.id"), nullable=False)
    data = Column(Date, default=date.today, nullable=False)
    refeicao = Column(String(30))       # café, almoço, jantar, lanche
    quantidade_g = Column(Float, nullable=False)

    alimento = relationship("TacoAlimento", back_populates="consumos")


# ---------- METAS ----------

class MetaForca(Base):
    """Meta de força: levantar X kg com Y reps num exercício específico"""
    __tablename__ = "metas_forca"

    id = Column(Integer, primary_key=True)
    exercicio_id = Column(Integer, ForeignKey("exercicios.id"), nullable=False)
    carga_alvo_kg = Column(Float, nullable=False)
    reps_alvo = Column(Integer, nullable=False)
    data_criacao = Column(Date, default=date.today, nullable=False)
    prazo = Column(Date)                  # data limite opcional
    concluida = Column(Boolean, default=False)
    concluida_em = Column(Date)

    exercicio = relationship("Exercicio")


class MetaPesoCorporal(Base):
    """Meta de peso corporal: atingir X kg até uma data"""
    __tablename__ = "metas_peso_corporal"

    id = Column(Integer, primary_key=True)
    peso_alvo_kg = Column(Float, nullable=False)
    peso_inicial_kg = Column(Float)       # snapshot do peso no momento da criação
    data_criacao = Column(Date, default=date.today, nullable=False)
    prazo = Column(Date, nullable=False)  # "em quanto tempo" -> data limite
    concluida = Column(Boolean, default=False)
    concluida_em = Column(Date)


class MetaAgua(Base):
    """Meta diária de consumo de água"""
    __tablename__ = "metas_agua"

    id = Column(Integer, primary_key=True)
    quantidade_ml_alvo = Column(Integer, nullable=False)
    ativa_desde = Column(Date, default=date.today, nullable=False)
    ativa_ate = Column(Date)   # null = vigente até nova meta ser criada


class MetaMacro(Base):
    """Meta diária de macros (kcal, proteína, carbo, gordura)"""
    __tablename__ = "metas_macro"

    id = Column(Integer, primary_key=True)
    kcal_alvo = Column(Float)
    proteina_g_alvo = Column(Float)
    carboidrato_g_alvo = Column(Float)
    lipideos_g_alvo = Column(Float)
    ativa_desde = Column(Date, default=date.today, nullable=False)
    ativa_ate = Column(Date)   # null = vigente até nova meta ser criada