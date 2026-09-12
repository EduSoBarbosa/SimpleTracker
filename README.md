# SimpleTracker 🦾

> **Um sistema local-first para registrar, acompanhar e analisar a evolução física através de dados.**

O **SimpleTracker** é um sistema de acompanhamento de **treinos, nutrição e composição corporal**, desenvolvido como o módulo de saúde física do **Evolution Lab**.

A proposta é simples: transformar registros do dia a dia em **dados estruturados que possam ser analisados ao longo do tempo**.

Em vez de apenas registrar "fiz supino hoje", o sistema organiza a evolução em diferentes níveis — exercícios, séries, volume, carga, composição corporal, alimentação e métricas de desempenho — criando uma base para análises mais avançadas no futuro.

> **Status:** 🚧 MVP em desenvolvimento

---

## 🎯 O que o SimpleTracker resolve?

Aplicativos de treino normalmente tratam cada informação de maneira isolada. O SimpleTracker foi pensado para centralizar esses dados em uma única aplicação.

### 🏋️ Treinos

* Cadastro e organização de rotinas
* Registro de sessões de treinamento
* Controle individual de séries
* Carga e repetições
* Acompanhamento de sobrecarga progressiva
* Cálculo de volume de treino
* Estimativa de 1RM através da fórmula de Epley

### 🍽️ Nutrição

* Registro de alimentos
* Controle de macronutrientes
* Integração com dados da **TACO**
* Persistência de informações nutricionais
* Suporte a alimentos personalizados

### ⚖️ Composição corporal

* Registro histórico de peso
* Acompanhamento de métricas corporais
* Comparação de evolução ao longo do tempo
* Médias móveis para reduzir ruído nas medições

### 📊 Analytics

O sistema transforma os registros em métricas e visualizações para responder perguntas como:

* Estou aumentando minha carga?
* Meu volume de treino está evoluindo?
* Como meu 1RM estimado está se comportando?
* Como meu peso está mudando ao longo das semanas?
* Existe alguma tendência de estagnação?

---

# 🖥️ Interface

A interface utiliza uma abordagem **Cyber Brutalist**, priorizando informação e contraste em vez do visual tradicional de aplicativos fitness.

A ideia é criar uma interface que pareça mais uma **ferramenta de análise** do que um aplicativo comercial de academia.

---

## 🏗️ Arquitetura

O projeto utiliza uma arquitetura **local-first**.

```text
SimpleTracker/
│
├── data/
│   └── taco_limpo.csv
│
├── database/
│   ├── app.py
│   ├── engine.py
│   ├── models.py
│   └── repository.py
│
├── modules/
│   ├── charts_service.py
│   └── visual_service.py
│
├── pages/
│   ├── 1_Rotinas.py
│   ├── 2_Treino_Atual.py
│   ├── 3_Alimentacao.py
│   ├── 4_Metas.py
│   ├── 5_Historico.py
│   └── 6_Estatisticas.py
│
├── Home.py
├── seed_taco.py
├── requirements.txt
└── README.md
```

A separação das responsabilidades permite que o MVP continue simples sem transformar toda a aplicação em um único arquivo.

### Camadas principais

**Interface**

`Streamlit`

Responsável pelas páginas, interação com o usuário e apresentação dos dados.

**Persistência**

`SQLite + SQLAlchemy`

Responsáveis pelo armazenamento local e pela abstração das operações com o banco de dados.

**Dados**

`TACO + dados registrados pelo usuário`

Base para o acompanhamento nutricional e histórico de evolução.

**Analytics**

`Python + Plotly`

Responsável pelos cálculos e visualizações de desempenho.

---

# 🛠️ Stack

| Tecnologia        | Utilização                        |
| ----------------- | --------------------------------- |
| 🐍 **Python**     | Linguagem principal               |
| 🎈 **Streamlit**  | Interface e execução da aplicação |
| 🗄️ **SQLite**    | Banco de dados local              |
| 🔗 **SQLAlchemy** | ORM e acesso ao banco             |
| 📊 **Plotly**     | Gráficos e visualizações          |
| 🍽️ **TACO**      | Dados de composição dos alimentos |
| 🎨 **CSS**        | Customização da interface         |

---

# 📈 Exemplo de análise

Um dos objetivos do sistema é ir além do simples armazenamento dos treinos.

A partir das séries registradas, o SimpleTracker pode calcular métricas como:

### Volume Load

```text
Volume = Σ (carga × repetições)
```

### 1RM estimado

Utilizando a fórmula de Epley:

```text
1RM = carga × (1 + repetições / 30)
```

Isso permite acompanhar não apenas a carga utilizada em determinado treino, mas também uma **estimativa da evolução da força**.

---

# 🧠 Decisões de engenharia

### Por que Streamlit?

O objetivo inicial era validar rapidamente a ideia e construir um MVP funcional.

O Streamlit permite desenvolver a interface, controlar o fluxo da aplicação e apresentar os dados sem precisar manter simultaneamente:

```text
Frontend → API → Backend → Database
```

Para o estágio atual do projeto, essa simplicidade é uma vantagem.

---

### Por que SQLite?

O SimpleTracker foi pensado inicialmente como uma aplicação **local-first**.

SQLite oferece:

* Zero configuração de servidor
* Portabilidade
* Banco em um único arquivo
* Facilidade para desenvolvimento
* Boa integração com SQLAlchemy

A ideia é manter a aplicação simples enquanto a estrutura de dados permanece preparada para uma futura migração.

---

### Por que SQLAlchemy?

Mesmo utilizando SQLite, o projeto não depende diretamente de SQL espalhado pela aplicação.

O SQLAlchemy fornece uma camada de abstração que facilita:

* Modelagem dos dados
* Reutilização das operações
* Manutenção
* Testes
* Futura migração para outro banco

---

# 🎨 Design System

O SimpleTracker utiliza um design próprio inspirado em **Cyber Brutalism**.

Características principais:

* Alto contraste
* Tipografia monoespaçada
* Bordas rígidas
* Poucos elementos decorativos
* Hierarquia visual baseada em dados
* Interface deliberadamente diferente de aplicativos fitness tradicionais

A camada visual está concentrada principalmente em:

```text
modules/visual_service.py
```

Isso permite alterar a identidade visual sem espalhar CSS por toda a aplicação.

---

# ⚙️ Instalação

### Requisitos

* Python **3.10+**
* Git

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/simpletracker.git

cd simpletracker
```

### 2. Crie um ambiente virtual

Windows:

```bash
python -m venv venv
```

Ative:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv

source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Popule a base nutricional

```bash
python seed_taco.py
```

### 5. Execute a aplicação

```bash
streamlit run Home.py
```

A aplicação estará disponível em:

```text
http://localhost:8501
```

---

# 🔒 Dados e privacidade

O SimpleTracker segue uma abordagem **local-first**.

Os dados registrados pelo usuário permanecem armazenados localmente através do SQLite, evitando que informações pessoais de treino e composição corporal dependam de um serviço externo durante o uso do MVP.

Arquivos locais como:

```text
*.db
*.sqlite3
.env
venv/
__pycache__/
```

são excluídos do controle de versão através do `.gitignore`.

---

# 🛣️ Roadmap

O MVP atual serve principalmente como **infraestrutura de coleta de dados**.

Os próximos passos planejados são:

### Banco de dados

* [ ] Implementar migrações com Alembic
* [ ] Melhorar versionamento do schema
* [ ] Expandir relacionamentos entre entidades

### Analytics

* [ ] Mais métricas de performance
* [ ] Detecção de platôs
* [ ] Análise de tendências
* [ ] Métricas de recuperação
* [ ] Comparação de períodos

### Machine Learning

* [ ] Exportação estruturada dos dados
* [ ] Dataset próprio de treinamento
* [ ] Predição de possíveis platôs
* [ ] Análise de relação entre volume, alimentação e evolução
* [ ] Experimentação com modelos do Scikit-Learn

### Evolution Lab

* [ ] Separar backend e interface
* [ ] Criar API com FastAPI
* [ ] Permitir acesso aos dados por outros módulos
* [ ] Evoluir de aplicação local para plataforma integrada

---

# 🔮 Visão de longo prazo

O SimpleTracker não foi pensado para ser apenas um aplicativo de academia.

A ideia é utilizá-lo como uma **fonte estruturada de dados sobre performance física**.

```text
                 SIMPLETRACKER
                       │
       ┌───────────────┼───────────────┐
       │               │               │
    TREINOS         NUTRIÇÃO       COMPOSIÇÃO
       │               │               │
       └───────────────┼───────────────┘
                       │
                 DADOS HISTÓRICOS
                       │
                       ▼
                   ANALYTICS
                       │
                       ▼
                MACHINE LEARNING
                       │
                       ▼
                EVOLUTION LAB
```

A longo prazo, esses dados podem alimentar modelos capazes de encontrar padrões que seriam difíceis de perceber manualmente.

---

# 👨‍💻 Autor

**Eduardo**

Projeto desenvolvido como parte do ecossistema **Evolution Lab**.

---

## 📌 Licença

Este projeto está atualmente em desenvolvimento.

---

