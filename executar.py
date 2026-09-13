"""Execute este arquivo para refazer dados tratados, cálculos e gráficos."""

import os
from pathlib import Path

import pandas as pd

from codigo import preparar_dados, estatistica


# Esta função evita repetir a mesma linha de código para salvar cada tabela.
def gravar(tabela: pd.DataFrame, caminho: Path) -> None:
    tabela.to_csv(caminho, index=False, encoding='utf-8-sig')


# Aqui formatamos números como valores em reais no resumo escrito.
def dinheiro(valor: float) -> str:
    return 'R$ ' + f'{valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


# Juntamos os principais resultados em um texto curto para leitura.
def escrever_resumo(pasta: Path, auditoria: dict, q: pd.DataFrame, corr: pd.DataFrame) -> None:
    geral = q.loc[q.periodo.eq('Geral')].iloc[0]
    fortes = corr.loc[corr.acima_0_3]
    texto = [
        '# Resultados iniciais', '',
        f"Base final: {auditoria['linhas_base_final']:,} linhas de execução (2024 e 2025).",
        f"Junção com ações: {auditoria['linhas_com_acao']:,} linhas encontradas; "
        f"{auditoria['linhas_sem_acao']} sem correspondência.",
        f"Chaves de empenho repetidas: {auditoria['linhas_com_chave_empenho_repetida']} linhas. "
        'A soma de valores por linha precisa de reconciliação antes de ser tratada como total de empenhos únicos.', '',
        '## Quartis e valores atípicos', '',
        f"Q1: {dinheiro(geral.q1)}; mediana: {dinheiro(geral.mediana)}; Q3: {dinheiro(geral.q3)}.",
        f"Limite superior: {dinheiro(geral.limite_superior)}. "
        f"Acima dele: {int(geral.outliers_altos):,} linhas "
        f"({geral.percentual_registros:.2f}% das linhas; {geral.percentual_valor:.2f}% do valor registrado).",
        'Valor atípico não significa despesa errada ou desnecessária.', '',
        '## Correlações', '',
        f"Variáveis examinadas: 25 na primeira rodada e 10 adicionais. "
        f"Coeficientes calculáveis: {int(corr.pearson.notna().sum())}. "
        f"Acima de 0,3 em módulo: {len(fortes)}.",
        'Variáveis acima do limite: ' + ', '.join(
            f"{linha.variavel} (r={linha.pearson:.3f})" for _, linha in fortes.iterrows()
        ) + '.',
        'A maioria dessas variáveis corresponde a etapas ou saldos do mesmo fluxo financeiro. '
        'A correlação não demonstra causa nem eficiência.',
        'A tabela correlacoes_para_apresentar.csv também inclui exemplos abaixo de 0,3: '
        'mês, função, contrato, grupo da despesa e orçamento atualizado da ação.', '',
        '## Leitura para o planejamento', '',
        'Os quartis mostram a faixa comum de valores. O resumo mensal revela quando os empenhos '
        'se concentram. O resumo por função mostra em quais áreas se registram maiores valores. '
        'Esses padrões podem orientar perguntas e previsões, mas precisam ser confrontados com '
        'o calendário orçamentário e com indicadores de serviços.',
    ]
    (pasta / 'resumo.md').write_text('\n'.join(texto) + '\n', encoding='utf-8')


# Este é o roteiro principal: pastas, dados, contas e gráficos.
def main() -> None:
    projeto = Path(__file__).resolve().parent
    originais = projeto / 'dados' / 'originais'
    tratados = projeto / 'dados' / 'tratados'
    resultados = projeto / 'resultados'
    figuras = projeto / 'graficos'
    resultados.mkdir(exist_ok=True)
    figuras.mkdir(exist_ok=True)

    # Mantém o cache da biblioteca gráfica dentro desta pasta do projeto.
    os.environ.setdefault('MPLCONFIGDIR', str(projeto / '.cache_matplotlib'))
    from codigo import gerar_graficos

    # Primeiro montamos a base tratada a partir dos CSVs originais.
    base, auditoria = preparar_dados.preparar(originais, tratados)
    # Depois calculamos os indicadores e escolhemos as correlações do gráfico.
    quartis, atipicos = estatistica.quartis(base)
    funcoes = estatistica.por_funcao(base)
    meses = estatistica.por_mes(base)
    correlacoes = estatistica.correlacoes(base)
    selecionadas = estatistica.correlacoes_para_apresentar(correlacoes)

    # Cada tabela vai para a pasta de resultados.
    gravar(quartis, resultados / 'quartis_outliers.csv')
    gravar(atipicos, resultados / 'outliers_altos.csv')
    gravar(funcoes, resultados / 'despesas_por_funcao.csv')
    gravar(meses, resultados / 'despesas_por_mes.csv')
    gravar(correlacoes, resultados / 'correlacoes_completas.csv')
    gravar(selecionadas, resultados / 'correlacoes_para_apresentar.csv')
    (resultados / 'auditoria.txt').write_text(
        '\n'.join(f'{nome}: {valor}' for nome, valor in auditoria.items()) + '\n',
        encoding='utf-8',
    )
    escrever_resumo(resultados, auditoria, quartis, correlacoes)

    # Por último, criamos as imagens na pasta de gráficos.
    gerar_graficos.boxplot(base, figuras / '01_boxplot_anos.png')
    gerar_graficos.mensal(meses, figuras / '02_distribuicao_mensal.png')
    gerar_graficos.areas(funcoes, figuras / '03_funcoes.png')
    gerar_graficos.outliers_por_area(atipicos, figuras / '04_outliers_por_funcao.png')
    gerar_graficos.correlacoes(selecionadas, figuras / '05_correlacoes_selecionadas.png')
    print('Projeto concluído. Veja as pastas dados/tratados, resultados e graficos.')


if __name__ == '__main__':
    main()
