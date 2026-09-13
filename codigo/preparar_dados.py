"""Etapa 1: ler, limpar e unir as duas tabelas públicas."""

from pathlib import Path
import pandas as pd

ANOS_ANALISADOS = (2024, 2025)


# 1. Procuramos cada CSV pelo tipo de tabela e pelo ano.
def ler_csv(pasta: Path, tipo: str, ano: int) -> pd.DataFrame:
    caminho = pasta / f'{tipo}_{ano}.csv'
    if not caminho.exists():
        raise FileNotFoundError(f'Arquivo não encontrado: {caminho}')
    return pd.read_csv(caminho, low_memory=False)


# 2. Valores em dinheiro precisam ser números para entrar nas contas.
def converter_valores(tabela: pd.DataFrame) -> pd.DataFrame:
    """Transforma colunas monetárias em números, sem alterar o CSV original."""
    for coluna in tabela.columns:
        if coluna.lower().startswith(('valor', 'saldo')):
            tabela[coluna] = pd.to_numeric(tabela[coluna], errors='coerce')
    return tabela


# 3. Juntamos os anos completos de cada tabela.
def preparar(pasta_originais: Path, pasta_tratados: Path) -> tuple[pd.DataFrame, dict]:
    execucao = pd.concat([
        ler_csv(pasta_originais, 'execucao_detalhada', ano)
        for ano in ANOS_ANALISADOS
    ], ignore_index=True)
    acoes = pd.concat([
        ler_csv(pasta_originais, 'despesas_programas_acoes', ano)
        for ano in ANOS_ANALISADOS
    ], ignore_index=True)
    execucao = converter_valores(execucao)
    acoes = converter_valores(acoes)

    # 4. Uma ação aparece várias vezes na tabela de programas. Primeiro
    # resumimos essas linhas para a união não duplicar os registros.
    resumo_acoes = acoes.groupby(
        ['nomeEntidade', 'ano', 'idAcao'], dropna=False
    ).agg(
        linhas_acao=('idDespesa', 'size'),
        orcado_acao=('valorOrcado', 'sum'),
        orcado_atualizado_acao=('valorOrcadoAtualizado', 'sum'),
        empenhado_acao=('valorEmpenhadoAtualizado', 'sum'),
        liquidado_acao=('valorLiquidadoAtualizado', 'sum'),
        pago_acao=('valorPagoAtualizado', 'sum'),
    ).reset_index()

    # 5. As colunas usadas na união precisam ter o mesmo tipo de dado.
    for tabela, colunas in (
        (execucao, ['anoExercicio', 'idProjetoAtividade']),
        (resumo_acoes, ['ano', 'idAcao']),
    ):
        for coluna in colunas:
            tabela[coluna] = pd.to_numeric(tabela[coluna], errors='coerce').astype('Int64')

    # 6. Ligamos cada linha de execução à ação correspondente.
    base = execucao.merge(
        resumo_acoes,
        how='left',
        left_on=['nomeEntidade', 'anoExercicio', 'idProjetoAtividade'],
        right_on=['nomeEntidade', 'ano', 'idAcao'],
        validate='many_to_one',
        indicator=True,
    )
    if len(base) != len(execucao):
        raise ValueError('A junção alterou a quantidade de linhas da execução.')

    # 7. Guardamos algumas contagens para conferir se a união deu certo.
    auditoria = {
        'linhas_execucao': len(execucao),
        'linhas_programas_acoes': len(acoes),
        'linhas_base_final': len(base),
        'linhas_com_acao': int(base['_merge'].eq('both').sum()),
        'linhas_sem_acao': int(base['_merge'].eq('left_only').sum()),
        'linhas_com_chave_empenho_repetida': int(execucao.duplicated(
            ['nomeEntidade', 'anoExercicio', 'numeroEmpenho'], keep=False
        ).sum()),
    }
    # 8. Salvamos a nova base; os arquivos originais ficam intactos.
    pasta_tratados.mkdir(parents=True, exist_ok=True)
    base.drop(columns=['_merge', 'ano', 'idAcao'], inplace=True)
    base.to_csv(pasta_tratados / 'base_analitica.csv', index=False, encoding='utf-8-sig')
    return base, auditoria
