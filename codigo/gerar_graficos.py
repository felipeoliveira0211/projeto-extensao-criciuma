"""Gráficos da análise; cada função gera uma figura."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

AZUL = '#174a67'
LARANJA = '#d4843c'


# 1. Usamos as mesmas cores e letras em todos os gráficos.
def estilo():
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'figure.facecolor': 'white', 'axes.facecolor': 'white'})


# 2. Salvamos cada gráfico como imagem PNG.
def salvar(fig, caminho):
    fig.savefig(caminho, dpi=170, bbox_inches='tight')
    plt.close(fig)


# 3. O boxplot mostra a faixa central dos valores em cada ano.
def boxplot(base, caminho):
    estilo()
    fig, ax = plt.subplots(figsize=(8, 4.8))
    dados = [base.loc[base.anoExercicio.eq(a), 'valorEmpenho'].dropna().to_numpy()
             for a in [2024, 2025]]
    ax.boxplot(dados, tick_labels=['2024', '2025'], showfliers=False,
               patch_artist=True, boxprops={'facecolor': '#b9d4e0', 'edgecolor': AZUL},
               medianprops={'color': LARANJA, 'linewidth': 2})
    # A escala logarítmica ajuda a mostrar valores pequenos e grandes juntos.
    ax.set_yscale('log')
    ax.set_ylabel('Valor do empenho (R$, escala logarítmica)')
    ax.set_title('Distribuição dos valores por exercício')
    ax.text(.01, -.2, 'Pontos extremos ocultos para facilitar a leitura; contagem na tabela de quartis.',
            transform=ax.transAxes, fontsize=8, color='#555')
    salvar(fig, caminho)


# 4. Este gráfico mostra a parcela do ano registrada em cada mês.
def mensal(tabela, caminho):
    estilo()
    fig, ax = plt.subplots(figsize=(9, 4.8))
    for ano, cor in [(2024, AZUL), (2025, LARANJA)]:
        t = tabela[tabela.anoExercicio.eq(ano)].sort_values('mes')
        ax.plot(t.mes, t.participacao_percentual, marker='o', label=str(ano), color=cor)
    ax.set_xticks(range(1, 13))
    ax.set_xlabel('Mês do empenho')
    ax.set_ylabel('Parcela do valor anual (%)')
    ax.set_title('Distribuição mensal do valor registrado')
    ax.legend(frameon=False)
    ax.grid(axis='y', alpha=.2)
    salvar(fig, caminho)


# 5. Aqui comparamos as funções com maior valor registrado.
def areas(tabela, caminho):
    estilo()
    totais = tabela.groupby('descricaoFuncao').valor_empenhado.sum().nlargest(8).sort_values()
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.barh(totais.index, totais.values / 1e6, color=AZUL)
    ax.set_xlabel('Valor registrado em 2024–2025 (R$ milhões)')
    ax.set_title('Oito funções com maior valor de empenhos registrados')
    ax.grid(axis='x', alpha=.2)
    salvar(fig, caminho)


# 6. Contamos em quais funções aparecem mais valores atípicos altos.
def outliers_por_area(outliers, caminho):
    estilo()
    t = outliers[outliers.periodo_referencia.eq('Geral')]
    contagem = t.descricaoFuncao.value_counts().head(8).sort_values()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(contagem.index, contagem.values, color=LARANJA)
    ax.set_xlabel('Quantidade de valores acima do limite geral')
    ax.set_title('Valores atípicos altos por função')
    ax.grid(axis='x', alpha=.2)
    salvar(fig, caminho)


# 7. As linhas tracejadas marcam o limite de correlação de 0,3.
def correlacoes(tabela, caminho):
    estilo()
    t = tabela.sort_values('pearson')
    fig, ax = plt.subplots(figsize=(10, max(4.8, .38 * len(t) + 1)))
    cores = [AZUL if abs(v) > .3 else '#a8bac4' for v in t.pearson]
    ax.barh(t.variavel, t.pearson, color=cores)
    ax.axvline(.3, color=LARANJA, linestyle='--', linewidth=1)
    ax.axvline(-.3, color=LARANJA, linestyle='--', linewidth=1)
    ax.axvline(0, color='#444', linewidth=.7)
    ax.set_xlim(-1, 1)
    ax.set_xlabel('Correlação de Pearson com valorEmpenho')
    ax.set_title('Correlações selecionadas: fortes e abaixo do limite')
    salvar(fig, caminho)
