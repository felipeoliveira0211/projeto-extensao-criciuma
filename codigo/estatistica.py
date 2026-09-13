"""Etapa 2: quartis, valores atípicos, resumos e correlações."""

import pandas as pd

ALVO = 'valorEmpenho'


# 1. Calculamos os quartis no conjunto inteiro e em cada ano.
def quartis(base: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Usa a regra de 1,5 vezes o intervalo entre Q1 e Q3."""
    resumo = []
    atipicos = []
    grupos = [('Geral', base)] + [(str(ano), parte) for ano, parte in base.groupby('anoExercicio')]
    for periodo, parte in grupos:
        valores = parte[ALVO].dropna()
        q1, mediana, q3 = valores.quantile([.25, .5, .75])
        iqr = q3 - q1
        # A regra do boxplot chama de atípico alto o que passa deste limite.
        limite = q3 + 1.5 * iqr
        altos = parte.loc[parte[ALVO] > limite].copy()
        altos['periodo_referencia'] = periodo
        atipicos.append(altos)
        resumo.append({
            'periodo': periodo, 'registros': len(valores), 'q1': q1,
            'mediana': mediana, 'q3': q3, 'intervalo_interquartil': iqr,
            'limite_superior': limite, 'outliers_altos': len(altos),
            'percentual_registros': 100 * len(altos) / len(valores),
            'percentual_valor': 100 * altos[ALVO].sum() / valores.sum(),
        })
    return pd.DataFrame(resumo), pd.concat(atipicos, ignore_index=True)


# 2. Vemos quanto cada função, como Saúde ou Educação, representa no ano.
def por_funcao(base: pd.DataFrame) -> pd.DataFrame:
    tabela = base.groupby(['anoExercicio', 'descricaoFuncao'], dropna=False).agg(
        registros=(ALVO, 'size'), valor_empenhado=(ALVO, 'sum'),
        mediana=(ALVO, 'median'),
    ).reset_index()
    tabela['participacao_percentual'] = 100 * tabela.valor_empenhado / tabela.groupby(
        'anoExercicio').valor_empenhado.transform('sum')
    return tabela


# 3. Fazemos a mesma conta por mês para enxergar o calendário das despesas.
def por_mes(base: pd.DataFrame) -> pd.DataFrame:
    dados = base.copy()
    dados['mes'] = pd.to_datetime(dados.dataEmpenho, errors='coerce').dt.month
    tabela = dados.groupby(['anoExercicio', 'mes'], dropna=False).agg(
        registros=(ALVO, 'size'), valor_empenhado=(ALVO, 'sum'),
        mediana=(ALVO, 'median'),
    ).reset_index()
    tabela['participacao_percentual'] = 100 * tabela.valor_empenhado / tabela.groupby(
        'anoExercicio').valor_empenhado.transform('sum')
    return tabela


# 4. Escolhemos as variáveis que vamos comparar com o valor do empenho.
def montar_variaveis(base: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Define 25 candidatas e depois acrescenta dez categorias comuns."""
    nomes = ['valorLiquidadoEmpenho', 'valorPagoEmpenho', 'saldoAPagar',
             'ValorAnuladoEmpenho', 'valorPagoRestosEmpenho',
             'valorRestosAPagarNaoProcessados', 'valorRestosAPagarProcessados',
             'valorRestosAPagarCancelados', 'saldoALiquidar', 'saldoAPagarLiquidado',
             'linhas_acao', 'orcado_acao', 'orcado_atualizado_acao',
             'empenhado_acao', 'liquidado_acao', 'pago_acao']
    x = base[nomes].copy()
    # Da data, tiramos mês, trimestre e outras informações simples.
    data = pd.to_datetime(base.dataEmpenho, errors='coerce')
    x['mes'] = data.dt.month
    x['trimestre'] = data.dt.quarter
    x['dia_ano'] = data.dt.dayofyear
    x['dia_semana'] = data.dt.dayofweek
    x['ano'] = data.dt.year
    x['fim_ano'] = data.dt.month.ge(10).astype(int)
    # Para campos como contrato, usamos 1 quando há informação e 0 quando não há.
    for coluna in ['licitacao', 'contrato', 'numeroControleProcesso']:
        x['possui_' + coluna] = base[coluna].fillna('').astype(str).str.strip().ne('').astype(int)
    if len(x.columns) != 25:
        raise ValueError('A primeira rodada precisa de 25 variáveis.')
    # Na segunda rodada, acrescentamos dez grupos frequentes da base.
    categorias = {}
    for coluna in ['descricaoFuncao', 'grupoElemento']:
        for posicao, valor in enumerate(base[coluna].value_counts().head(5).index, 1):
            nome = f'{coluna}_top{posicao}'
            x[nome] = base[coluna].eq(valor).astype(int)
            categorias[nome] = str(valor)
    return x, categorias


# 5. Medimos a relação de cada variável com a variável alvo.
def correlacoes(base: pd.DataFrame) -> pd.DataFrame:
    x, categorias = montar_variaveis(base)
    alvo = base[ALVO]
    linhas = []
    for ordem, coluna in enumerate(x.columns, 1):
        valores = pd.to_numeric(x[coluna], errors='coerce')
        validos = valores.notna() & alvo.notna()
        # Sem variação nos valores, não existe correlação para calcular.
        if valores[validos].nunique() > 1:
            pearson = valores[validos].corr(alvo[validos])
            spearman = valores[validos].rank().corr(alvo[validos].rank())
        else:
            pearson = spearman = float('nan')
        linhas.append({
            'rodada': 1 if ordem <= 25 else 2,
            'variavel': coluna, 'categoria': categorias.get(coluna, ''),
            'n': int(validos.sum()), 'pearson': pearson, 'spearman': spearman,
            'acima_0_3': bool(abs(pearson) > .3),
        })
    return pd.DataFrame(linhas)


# 6. Separamos as correlações mais altas e alguns exemplos mais baixos.
def correlacoes_para_apresentar(tabela: pd.DataFrame) -> pd.DataFrame:
    """Mostra as fortes e exemplos fracos ligados à pergunta-problema."""
    exemplos = ['orcado_atualizado_acao', 'mes', 'possui_contrato',
                'descricaoFuncao_top3', 'grupoElemento_top1']
    escolhidas = tabela.loc[tabela.acima_0_3 | tabela.variavel.isin(exemplos)].copy()
    escolhidas['grupo'] = escolhidas.acima_0_3.map({True: 'Acima de 0,3', False: 'Abaixo de 0,3'})
    return escolhidas.sort_values('pearson', key=lambda coluna: coluna.abs(), ascending=False)
