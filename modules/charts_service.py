import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, timedelta

# ==========================================
# CONFIGURAÇÃO CYBER BRUTALIST GLOBAL
# ==========================================
FONT_CONFIG = dict(family="'Space Mono', monospace", color="#000000", size=12)

HEATMAP_COLORSCALE = [
    [0.0, "rgba(0,0,0,0.05)"], # Quadrados vazios
    [0.25, "#d9ff4d"],         # 1 treino
    [0.5, "#CCFF00"],          # 2 treinos: Chartreuse (Verde Neon)
    [0.75, "#8A2BE2"],         # 3 treinos: Roxo Neon
    [1.0, "#000000"],          # 4+ treinos: Preto brutalista
]

def gerar_dados_heatmap(datas_treino, semanas=26):
    hoje = date.today()
    inicio = hoje - timedelta(weeks=semanas)
    dias_totais = (hoje - inicio).days + 1

    mapa_frequencia = {}
    for d in datas_treino:
        if d >= inicio:
            mapa_frequencia[d] = mapa_frequencia.get(d, 0) + 1

    z = []
    hover = []
    meses_labels = []
    mes_atual = -1

    for semana in range(semanas + 1):
        z_col = []
        hover_col = []
        
        dia_da_semana_inicio = inicio.weekday()
        
        for dia_semana in range(7):
            dias_avanco = (semana * 7) + dia_semana - dia_da_semana_inicio
            data_atual = inicio + timedelta(days=dias_avanco)

            if data_atual > hoje or data_atual < inicio:
                z_col.append(None)
                hover_col.append("")
            else:
                qtd = mapa_frequencia.get(data_atual, 0)
                z_col.append(qtd)
                txt = f"{data_atual.strftime('%d/%m/%Y')}: {qtd} treino(s)"
                hover_col.append(txt)

            if dia_semana == 0 and data_atual.month != mes_atual and data_atual <= hoje:
                meses_labels.append(data_atual.strftime("%b"))
                mes_atual = data_atual.month
            elif dia_semana == 0:
                meses_labels.append("")

        z.append(z_col)
        hover.append(hover_col)

    z_transposto = list(map(list, zip(*z)))
    hover_transposto = list(map(list, zip(*hover)))

    return z_transposto, hover_transposto, meses_labels

def construir_figura_heatmap(z, hover, meses_labels, altura=180):
    fig = go.Figure(
        data=go.Heatmap(
            z=z, text=hover, hoverinfo="text",
            colorscale=HEATMAP_COLORSCALE, showscale=False, xgap=3, ygap=3,
            zmin=0, zmax=4  # <--- FIX 1: Trava a escala (0 = Cinza, 4 = Preto)
        )
    )
    fig.update_layout(
        template="none", 
        height=altura, 
        margin=dict(l=30, r=10, t=10, b=30), # <--- FIX 2: Devolve a margem esquerda e inferior para os textos
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=FONT_CONFIG,
        xaxis=dict(
            tickmode="array", tickvals=[i for i, m in enumerate(meses_labels) if m],
            ticktext=[m for m in meses_labels if m], showgrid=False, zeroline=False,
            tickfont=dict(color="#000000", weight="bold")
        ),
        yaxis=dict(
            tickmode="array", tickvals=[0, 2, 4, 6],
            ticktext=["Dom", "Ter", "Qui", "Sáb"], showgrid=False, zeroline=False,
            autorange="reversed", tickfont=dict(color="#000000", weight="bold")
        ),
    )
    return fig

def calcular_streak(datas_treino):
    if not datas_treino: return 0
    datas_unicas = sorted(list(set(datas_treino)), reverse=True)
    hoje = date.today()
    streak = 0
    dia_esperado = hoje

    if datas_unicas[0] == hoje:
        streak = 1
        datas_unicas.pop(0)
        dia_esperado = hoje - timedelta(days=1)
    elif datas_unicas[0] == hoje - timedelta(days=1):
        dia_esperado = hoje - timedelta(days=1)
    else:
        return 0

    for d in datas_unicas:
        if d == dia_esperado:
            streak += 1
            dia_esperado -= timedelta(days=1)
        else:
            break
    return streak

def calcular_1rm(carga, reps):
    if not carga or not reps: return 0
    if reps == 1: return carga
    return carga * (1 + reps / 30.0)

def construir_grafico_forca_completo(historico_treino):
    if not historico_treino: return go.Figure()
        
    df = pd.DataFrame(historico_treino)
    df['1rm'] = df.apply(lambda row: calcular_1rm(row['carga_kg'], row['reps']), axis=1)
    df['volume'] = df['carga_kg'] * df['reps']

    df_grouped = df.groupby('data').agg({'1rm': 'max', 'volume': 'sum'}).reset_index()
    df_grouped = df_grouped.sort_values('data')

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=df_grouped['data'], y=df_grouped['volume'], name="Volume Total (kg)", 
        marker_color='rgba(204, 255, 0, 0.4)', marker_line_color='#000000', marker_line_width=2),
        secondary_y=False)

    fig.add_trace(go.Scatter(
        x=df_grouped['data'], y=df_grouped['1rm'], mode='lines+markers', name="1RM Estimado",
        line=dict(color='#8A2BE2', width=4, shape='spline'), 
        marker=dict(size=10, color='#8A2BE2', line=dict(color="#000000", width=2))),
        secondary_y=True)

    fig.update_layout(
        template="none", # <--- MATANDO O DARK MODE NATIVO
        title=dict(text="Força Absoluta vs Volume de Treino", font=dict(color="#000000", family="'Teko', sans-serif", size=24)),
        hovermode="x unified", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=50, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=FONT_CONFIG
    )
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black', tickfont=dict(color="#000000", weight="bold"))
    fig.update_yaxes(title_text="Volume (kg)", secondary_y=False, showgrid=False, tickfont=dict(color="#000000", weight="bold"), title_font=dict(color="#000000"))
    fig.update_yaxes(title_text="1RM (kg)", secondary_y=True, showgrid=True, gridcolor='rgba(0,0,0,0.2)', tickfont=dict(color="#000000", weight="bold"), title_font=dict(color="#000000"))
    return fig

def construir_grafico_peso_avancado(pesos, meta_kg=None):
    if not pesos: return go.Figure()
        
    df = pd.DataFrame([{"data": p.data, "peso": p.peso_kg} for p in pesos]).sort_values('data')
    df['media_movel'] = df['peso'].rolling(window=7, min_periods=1).mean()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['data'], y=df['peso'], mode='markers', name='Peso Real',
        marker=dict(color='rgba(0, 0, 0, 0.4)', size=8, line=dict(color="#000000", width=1))
    ))

    fig.add_trace(go.Scatter(
        x=df['data'], y=df['media_movel'], mode='lines', name='Média Móvel (7 Dias)',
        line=dict(color='#8A2BE2', width=4, shape='spline')
    ))

    if meta_kg:
        fig.add_hline(y=meta_kg, line_dash="dash", line_color="#CCFF00", line_width=3,
                      annotation_text=f"Meta: {meta_kg}kg", annotation_font_color="#000000", annotation_bgcolor="#CCFF00")

    fig.update_layout(
        template="none", # <--- MATANDO O DARK MODE NATIVO
        title=dict(text="Tendência de Composição Corporal", font=dict(color="#000000", family="'Teko', sans-serif", size=24)),
        hovermode="x unified", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=50, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=FONT_CONFIG
    )
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black', tickfont=dict(color="#000000", weight="bold"))
    fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.2)', title_text="Peso (kg)", tickfont=dict(color="#000000", weight="bold"), title_font=dict(color="#000000"))
    return fig

def construir_grafico_macros_avancado(dados_macros, meta_kcal=None):
    if not dados_macros: return go.Figure()
    df = pd.DataFrame(dados_macros)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(x=df['data'], y=df['prot'], name='Proteína', marker_color='#8A2BE2', marker_line_color='#000000', marker_line_width=2), secondary_y=False)
    fig.add_trace(go.Bar(x=df['data'], y=df['carb'], name='Carboidrato', marker_color='#FFFFFF', marker_line_color='#000000', marker_line_width=2), secondary_y=False)
    fig.add_trace(go.Bar(x=df['data'], y=df['fat'], name='Gordura', marker_color='#CCFF00', marker_line_color='#000000', marker_line_width=2), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=df['data'], y=df['kcal'], mode='lines+markers', name='Total (Kcal)',
        line=dict(color='#000000', width=3, dash='dot'), marker=dict(size=8, color="#000000")
    ), secondary_y=True)

    if meta_kcal:
        fig.add_hline(y=meta_kcal, line_dash="solid", line_color="#000000", line_width=2,
                      annotation_text="Teto Calórico", annotation_font_color="#000000", annotation_bgcolor="#FFFFFF", secondary_y=True)

    fig.update_layout(
        template="none", # <--- MATANDO O DARK MODE NATIVO
        title=dict(text="Assinatura Metabólica (Últimos 7 dias)", font=dict(color="#000000", family="'Teko', sans-serif", size=24)),
        barmode='stack', hovermode="x unified", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=50, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=FONT_CONFIG
    )
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black', tickfont=dict(color="#000000", weight="bold"))
    fig.update_yaxes(title_text="Volume Macros (g)", secondary_y=False, showgrid=False, tickfont=dict(color="#000000", weight="bold"), title_font=dict(color="#000000"))
    fig.update_yaxes(title_text="Energia (Kcal)", secondary_y=True, showgrid=True, gridcolor='rgba(0,0,0,0.2)', tickfont=dict(color="#000000", weight="bold"), title_font=dict(color="#000000"))
    return fig

def construir_grafico_agua(dados_agua, meta_ml=None):
    if not dados_agua: return go.Figure()
    df = pd.DataFrame(dados_agua)

    cores = ['#CCFF00' if (meta_ml and val >= meta_ml) else '#FFFFFF' for val in df['ml']]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['data'], y=df['ml'], name="Água (ml)",
        marker_color=cores, text=df['ml'], textposition='auto',
        textfont=dict(color="#000000", weight="bold"),
        marker_line_color='#000000', marker_line_width=2
    ))

    if meta_ml:
        fig.add_hline(y=meta_ml, line_dash="dash", line_color="#000000", line_width=2, 
                      annotation_text=f"Meta: {meta_ml}ml", annotation_font_color="#000000", annotation_bgcolor="#CCFF00")

    fig.update_layout(
        template="none", # <--- MATANDO O DARK MODE NATIVO
        title=dict(text="Score de Hidratação Diária", font=dict(color="#000000", family="'Teko', sans-serif", size=24)),
        hovermode="x", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=50, b=0), font=FONT_CONFIG
    )
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black', tickfont=dict(color="#000000", weight="bold"))
    fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.2)', title_text="Volume (ml)", tickfont=dict(color="#000000", weight="bold"), title_font=dict(color="#000000"))
    return fig