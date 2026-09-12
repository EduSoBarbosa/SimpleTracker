Lógica das decisões:

Sem tabela User: uso pessoal não precisa disso; economiza joins.

Rotina → RotinaExercicio → Exercicio: separa o catálogo de exercícios (reutilizável) do plano (meta por rotina) e da execução real (SerieRealizada), que é o dado que vai alimentar os gráficos Plotly de evolução de carga/volume.

TacoAlimento fica isolada: é uma tabela de referência estática (import único da base TACO em CSV/Excel), separada do log de consumo — assim você não duplica os dados nutricionais a cada refeição registrada.

PesoCorporal com unique=True na data: assume um registro por dia (pode mudar pra DateTime se quiser múltiplos registros/dia).